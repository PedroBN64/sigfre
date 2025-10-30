# views/tela_principal.py
import customtkinter as ctk
from views.cadastro_funcionario import abrir_tela_cadastro

def criar_tela_principal(root):
    frame = ctk.CTkFrame(root)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    label = ctk.CTkLabel(
        frame,
        text="SIGFRE\nSistema de Gestão de Frequência Escolar",
        font=ctk.CTkFont(size=20, weight="bold")
    )
    label.pack(pady=20)

    btn_cadastro = ctk.CTkButton(
        frame,
        text="Cadastrar Funcionário",
        width=200,
        height=40,
        command=lambda: abrir_tela_cadastro(root)
    )
    btn_cadastro.pack(pady=10)

    btn_folha = ctk.CTkButton(
        frame,
        text="Gerar Folha de Pagamento",
        width=200,
        height=40
    )
    btn_folha.pack(pady=10)

    btn_relatorio = ctk.CTkButton(
        frame,
        text="Consultar Relatórios",
        width=200,
        height=40
    )
    btn_relatorio.pack(pady=10)
