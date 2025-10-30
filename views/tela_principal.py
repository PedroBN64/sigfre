# views/tela_principal.py
import customtkinter as ctk
from views.cadastro_funcionario import abrir_tela_cadastro
from reports.gerar_pdf import gerar_folha
from database.db import conectar
from CTkMessagebox import CTkMessagebox
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle

def atualizar_tabela(tree, conn):
    # Limpa
    for item in tree.get_children():
        tree.delete(item)
    
    cursor = conn.cursor()
    cursor.execute("SELECT nome, rg, cargo, contrato, carga_horaria FROM funcionarios")
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)

def criar_tela_principal(root):
    conn = conectar()

    # Tema escuro para Treeview
    style = ThemedStyle(root)
    style.set_theme("equilux")  # Tema escuro bonito

    # Frame principal
    frame = ctk.CTkFrame(root)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    # Título
    ctk.CTkLabel(
        frame,
        text="SIGFRE - Sistema de Folha de Pagamento",
        font=ctk.CTkFont(size=22, weight="bold")
    ).pack(pady=15)

    # Botões
    frame_botoes = ctk.CTkFrame(frame)
    frame_botoes.pack(pady=10, fill="x")

    ctk.CTkButton(
        frame_botoes,
        text="Cadastrar Funcionário",
        command=lambda: abrir_tela_cadastro(root, lambda: atualizar_tabela(tree, conn)),
        fg_color="#1f6aa5", width=220
    ).pack(side="left", padx=15)

    ctk.CTkButton(
        frame_botoes,
        text="Gerar Folha de Pagamento",
        command=lambda: gerar_folha_dialog(),
        fg_color="green", width=220
    ).pack(side="left", padx=15)

    # Treeview com tema
    columns = ("nome", "rg", "cargo", "contrato", "carga_horaria")
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)
    
    # Cabeçalhos
    for col in columns:
        nome_col = col.replace("_", " ").title()
        tree.heading(col, text=nome_col)
        tree.column(col, width=150, anchor="center")

    tree.pack(pady=20, fill="both", expand=True)

    # Scrollbar
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    # Atualiza lista
    atualizar_tabela(tree, conn)

    def gerar_folha_dialog():
        dialog = ctk.CTkInputDialog(text="Mês (ex: 08):", title="Mês")
        mes = dialog.get_input()
        if not mes: return

        dialog = ctk.CTkInputDialog(text="Ano (ex: 2025):", title="Ano")
        ano = dialog.get_input()
        if not ano: return

        cursor = conn.cursor()
        cursor.execute("SELECT nome, rg, cargo, contrato, carga_horaria FROM funcionarios")
        dados = [
            {
                "nome": r[0],
                "rg": r[1],
                "cargo": r[2],
                "contrato": r[3],
                "carga_horaria": r[4],
                "observacoes": ""
            } for r in cursor.fetchall()
        ]

        try:
            gerar_folha(mes, ano, dados)
            CTkMessagebox(title="Sucesso!", message="Folha gerada com sucesso!", icon="check")
        except Exception as e:
            CTkMessagebox(title="Erro", message=f"Erro: {e}", icon="cancel")

    # Fecha conexão
    root.protocol("WM_DELETE_WINDOW", lambda: (conn.close(), root.destroy()))
