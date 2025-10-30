# views/tela_principal.py
import customtkinter as ctk
from customtkinter import CTkTable  # TABELA MODERNA
from views.cadastro_funcionario import abrir_tela_cadastro
from reports.gerar_pdf import gerar_folha
from database.db import conectar
from CTkMessagebox import CTkMessagebox

def atualizar_tabela(table, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT nome, rg, cargo, contrato, carga_horaria FROM funcionarios")
    dados = cursor.fetchall()
    
    # Limpa tabela
    table.delete(*table.get_children())
    
    # Preenche
    for row in dados:
        table.insert("", "end", values=row)

def criar_tela_principal(root):
    conn = conectar()

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
        command=lambda: abrir_tela_cadastro(root, lambda: atualizar_tabela(table, conn)),
        fg_color="#1f6aa5", width=200
    ).pack(side="left", padx=15)

    ctk.CTkButton(
        frame_botoes,
        text="Gerar Folha de Pagamento",
        command=lambda: gerar_folha_dialog(),
        fg_color="green", width=200
    ).pack(side="left", padx=15)

    # Tabela (CTkTable)
    columns = ["Nome", "RG", "Cargo", "Contrato", "Carga Horária"]
    table = CTkTable(
        master=frame,
        row=15,
        column=5,
        values=[columns],
        header_color="#1f6aa5",
        corner_radius=8
    )
    table.pack(pady=20, fill="both", expand=True)

    # Atualiza tabela
    atualizar_tabela(table, conn)

    def gerar_folha_dialog():
        dialog = ctk.CTkInputDialog(text="Mês (ex: 08):", title="Mês da Folha")
        mes = dialog.get_input()
        if not mes: return

        dialog = ctk.CTkInputDialog(text="Ano (ex: 2025):", title="Ano da Folha")
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
            CTkMessagebox(title="Erro", message=f"Erro ao gerar PDF:\n{e}", icon="cancel")

    # Fecha conexão ao sair
    root.protocol("WM_DELETE_WINDOW", lambda: (conn.close(), root.destroy()))
