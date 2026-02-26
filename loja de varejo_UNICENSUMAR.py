import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURAÇÕES Gerais
# ==========================================
NOME_BANCO = 'loja_varejo.db'
TITULO_SISTEMA = "Sistema de Gestão - felipe piassi - ATIVIDADE 1 - FUNDAMENTOS DE BIG DATA"
MOEDA = "R$"
COR_BOTAO_SALVAR = "#27ae60"
COR_BOTAO_EXCLUIR = "#c0392b"
COR_BOTAO_VENDA = "#2980b9"

# --- BANCO DE DADOS ---
def conectar():
    return sqlite3.connect(NOME_BANCO)

def inicializar_db():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            preco REAL NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER,
            quantidade INTEGER NOT NULL,
            valor_total REAL NOT NULL,
            origem TEXT NOT NULL,
            data_venda DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
    ''')
    conexao.commit()
    conexao.close()

# --- INTERFACE GRÁFICA ---
class AppVarejo:
    def __init__(self, janela):
        self.janela = janela
        self.janela.title(TITULO_SISTEMA)
        self.janela.geometry("850x650")
        
        self.notebook = ttk.Notebook(janela)
        self.notebook.pack(expand=True, fill='both')

        self.aba_estoque = ttk.Frame(self.notebook)
        self.aba_vendas = ttk.Frame(self.notebook)
        
        self.notebook.add(self.aba_estoque, text="📦 Estoque e Cadastro")
        self.notebook.add(self.aba_vendas, text="💰 Histórico de Vendas")

        self.setup_aba_estoque()
        self.setup_aba_vendas()
        self.carregar_dados()

    def setup_aba_estoque(self):
        # Formulário
        frame_form = tk.LabelFrame(self.aba_estoque, text="Novo Produto", padx=10, pady=10)
        frame_form.pack(pady=10, fill="x", padx=10)

        tk.Label(frame_form, text="Nome:").grid(row=0, column=0)
        self.entrada_nome = tk.Entry(frame_form, width=25)
        self.entrada_nome.grid(row=0, column=1, padx=5)

        tk.Label(frame_form, text="Qtd:").grid(row=0, column=2)
        self.entrada_qtd = tk.Entry(frame_form, width=8)
        self.entrada_qtd.grid(row=0, column=3, padx=5)

        tk.Label(frame_form, text="Preço:").grid(row=0, column=4)
        self.entrada_preco = tk.Entry(frame_form, width=10)
        self.entrada_preco.grid(row=0, column=5, padx=5)

        btn_cadastrar = tk.Button(frame_form, text="CADASTRAR", command=self.salvar_dados, bg=COR_BOTAO_SALVAR, fg="white")
        btn_cadastrar.grid(row=0, column=6, padx=10)

        # Tabela
        self.tabela = ttk.Treeview(self.aba_estoque, columns=("ID", "Nome", "Qtd", "Preço"), show='headings')
        self.tabela.heading("ID", text="ID")
        self.tabela.heading("Nome", text="Produto")
        self.tabela.heading("Qtd", text="Estoque")
        self.tabela.heading("Preço", text=f"Preço ({MOEDA})")
        self.tabela.pack(padx=10, pady=10, fill="both", expand=True)

        # Botões de Ação
        frame_botoes = tk.Frame(self.aba_estoque)
        frame_botoes.pack(pady=10)

        tk.Button(frame_botoes, text="🛒 REGISTRAR VENDA", command=self.abrir_janela_venda, 
                  bg=COR_BOTAO_VENDA, fg="white", font=("Arial", 10, "bold"), width=20).pack(side="left", padx=5)
        
        tk.Button(frame_botoes, text="🗑️ EXCLUIR PRODUTO", command=self.deletar_produto, 
                  bg=COR_BOTAO_EXCLUIR, fg="white", font=("Arial", 10, "bold"), width=20).pack(side="left", padx=5)

    def setup_aba_vendas(self):
        self.tabela_vendas = ttk.Treeview(self.aba_vendas, columns=("ID", "Data", "Produto", "Qtd", "Total", "Origem"), show='headings')
        for col in self.tabela_vendas["columns"]:
            self.tabela_vendas.heading(col, text=col)
        self.tabela_vendas.pack(padx=10, pady=10, fill="both", expand=True)

        tk.Button(self.aba_vendas, text="⚠️ ESTORNAR VENDA (DEVOLVER AO ESTOQUE)", 
                  command=self.estornar_venda, bg=COR_BOTAO_EXCLUIR, fg="white").pack(pady=10)

    # --- LÓGICA DE EXCLUSÃO ---
    def deletar_produto(self):
        selecionado = self.tabela.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um item para deletar!")
            return
        
        item = self.tabela.item(selecionado)['values']
        id_produto = item[0]
        nome_produto = item[1]

        confirmar = messagebox.askyesno("Confirmar", f"Deseja realmente excluir '{nome_produto}'?\nIsso não afetará o histórico de vendas passadas.")
        
        if confirmar:
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute('DELETE FROM produtos WHERE id = ?', (id_produto,))
            conexao.commit()
            conexao.close()
            self.carregar_dados()
            messagebox.showinfo("Sucesso", "Produto removido do estoque.")

    def estornar_venda(self):
        selecionado = self.tabela_vendas.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma venda para estornar!")
            return
        
        venda = self.tabela_vendas.item(selecionado)['values']
        id_venda = venda[0]
        nome_prod = venda[2]
        qtd_estorno = venda[3]

        if messagebox.askyesno("Estorno", f"Deseja cancelar esta venda?\n{qtd_estorno} unidade(s) de '{nome_prod}' voltarão ao estoque."):
            conexao = conectar()
            cursor = conexao.cursor()
            
            
            cursor.execute('SELECT id FROM produtos WHERE nome = ?', (nome_prod,))
            res = cursor.fetchone()
            
            if res:
                id_prod = res[0]
                #  Devolve ao estoque
                cursor.execute('UPDATE produtos SET quantidade = quantidade + ? WHERE id = ?', (qtd_estorno, id_prod))
                #  Remove a venda
                cursor.execute('DELETE FROM vendas WHERE id = ?', (id_venda,))
                conexao.commit()
                messagebox.showinfo("Sucesso", "Venda estornada e estoque atualizado!")
            else:
                messagebox.showerror("Erro", "Produto não encontrado no estoque atual para estorno.")
            
            conexao.close()
            self.carregar_dados()

    # ---  (SALVAR/CARREGAR/VENDA) ---
    def carregar_dados(self):
        for i in self.tabela.get_children(): self.tabela.delete(i)
        for i in self.tabela_vendas.get_children(): self.tabela_vendas.delete(i)
        
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute('SELECT * FROM produtos')
        for row in cursor.fetchall():
            self.tabela.insert("", tk.END, values=(row[0], row[1], row[2], f"{MOEDA} {row[3]:.2f}"))

        cursor.execute('''
            SELECT v.id, v.data_venda, p.nome, v.quantidade, v.valor_total, v.origem 
            FROM vendas v JOIN produtos p ON v.produto_id = p.id
            ORDER BY v.data_venda DESC
        ''')
        for row in cursor.fetchall():
            self.tabela_vendas.insert("", tk.END, values=row)
        conexao.close()

    def salvar_dados(self):
        try:
            nome = self.entrada_nome.get()
            qtd = int(self.entrada_qtd.get())
            preco = float(self.entrada_preco.get().replace(',', '.'))
            if nome:
                conexao = conectar()
                cursor = conexao.cursor()
                cursor.execute('INSERT INTO produtos (nome, quantidade, preco) VALUES (?, ?, ?)', (nome, qtd, preco))
                conexao.commit()
                conexao.close()
                self.carregar_dados()
                self.entrada_nome.delete(0, tk.END)
                self.entrada_qtd.delete(0, tk.END)
                self.entrada_preco.delete(0, tk.END)
        except:
            messagebox.showerror("Erro", "Preencha os campos corretamente!")

    def abrir_janela_venda(self):
        selecionado = self.tabela.selection()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um produto!")
            return
        
        id_p, nome, estoque, preco_str = self.tabela.item(selecionado)['values']
        
        janela_v = tk.Toplevel(self.janela)
        janela_v.title("Registrar Venda")
        janela_v.geometry("250x200")

        tk.Label(janela_v, text=f"Produto: {nome}").pack()
        ent_q = tk.Entry(janela_v)
        ent_q.pack(pady=5)
        ent_q.insert(0, "1")

        origem = ttk.Combobox(janela_v, values=["Física", "Online"])
        origem.set("Física")
        origem.pack(pady=5)

        def confirmar():
            q = int(ent_q.get())
            if q <= int(estoque):
                p_float = float(preco_str.replace(MOEDA, '').replace(',', '.').strip())
                total = q * p_float
                conexao = conectar()
                cursor = conexao.cursor()
                cursor.execute('INSERT INTO vendas (produto_id, quantidade, valor_total, origem) VALUES (?, ?, ?, ?)', (id_p, q, total, origem.get()))
                cursor.execute('UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?', (q, id_p))
                conexao.commit()
                conexao.close()
                self.carregar_dados()
                janela_v.destroy()
            else: messagebox.showerror("Erro", "Estoque insuficiente!")

        tk.Button(janela_v, text="VENDER", command=confirmar, bg=COR_BOTAO_VENDA, fg="white").pack(pady=10)

if __name__ == "__main__":
    inicializar_db()
    root = tk.Tk()
    app = AppVarejo(root)
    root.mainloop()