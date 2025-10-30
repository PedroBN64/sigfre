# views/tela_principal.py
import customtkinter as ctk
from views.cadastro_funcionario import abrir_tela_cadastro
from reports.gerar_pdf import gerar_folha
from database.db import conectar
import tkinter as tk

def atualizar_lista(tree, conn):
    for item in tree.get_children():
        tree.delete(item)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, rg, cargo, contrato, carga_horaria FROM funcionarios")
    for row in cursor.fetchall():
        tree.insert("", "end", values=row[1:])  # sem ID

def criar_tela_principal(root):
    conn = conectar()

    frame = ctk.CTkFrame(root)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    ctk.CTkLabel(frame, text="SIGFRE - Folha de Pagamento Escolar",
                 font=ctk.CTkFont(size=22, weight="bold")).pack(pady=10)

    # Botões superiores
    frame_top = ctk.CTkFrame(frame)
    frame_top.pack(pady=10, fill="x")

    ctk.CTkButton(frame_top, text="Cadastrar Funcionário",
                  command=lambda: abrir_tela_cadastro(root, lambda: atualizar_lista(tree, conn)),
                  fg_color="blue").pack(side="left", padx=10)

    ctk.CTkButton(frame_top, text="Gerar Folha de Pagamento",
                  command=lambda: gerar_folha_com_dados(),
                  fg_color="green").pack(side="left", padx=10)

    # Tabela
    columns = ("nome", "rg", "cargo", "contrato", "carga_horaria")
    tree = tk.Treeview(frame, columns=columns, show="headings", height=15)
    for col in columns:
        tree.heading(col, text=col.replace("_", " ").title())
        tree.column(col, width=150, anchor="center")
    tree.pack(pady=20, fill="both", expand=True)

    scrollbar = ctk.CTkScrollbar(frame, command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    atualizar_lista(tree, conn)

    def gerar_folha_com_dados():
        mes = ctk.CTkInputDialog(text="Mês (ex: 08):", title="Mês").get_input()
        ano = ctk.CTkInputDialog(text="Ano (ex: 2025):", title="Ano").get_input()
        if not mes or not ano:
            return
        cursor = conn.cursor()
        cursor.execute("SELECT nome, rg, cargo, contrato, carga_horaria FROM funcionarios")
        dados = [{"nome": r[0], "rg": r[1], "cargo": r[2], "contrato": r[3], "carga_horaria": r[4], "observacoes": ""} for r in cursor.fetchall()]
        gerar_folha(mes, ano, dados)

    root.protocol("WM_DELETE_WINDOW", conn.close)
