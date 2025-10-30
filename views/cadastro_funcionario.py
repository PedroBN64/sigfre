# views/cadastro_funcionario.py
import customtkinter as ctk
from database.db import conectar

def abrir_tela_cadastro(root):
    janela = ctk.CTkToplevel(root)
    janela.geometry("500x500")
    janela.title("Cadastrar Funcionário")

    # Campos
    ctk.CTkLabel(janela, text="Nome:").pack(pady=5)
    entry_nome = ctk.CTkEntry(janela, width=300)
    entry_nome.pack(pady=5)

    ctk.CTkLabel(janela, text="RG:").pack(pady=5)
    entry_rg = ctk.CTkEntry(janela, width=300)
    entry_rg.pack(pady=5)

    ctk.CTkLabel(janela, text="Cargo/Função:").pack(pady=5)
    entry_cargo = ctk.CTkEntry(janela, width=300)
    entry_cargo.pack(pady=5)

    ctk.CTkLabel(janela, text="Contrato:").pack(pady=5)
    entry_contrato = ctk.CTkEntry(janela, width=300)
    entry_contrato.pack(pady=5)

    ctk.CTkLabel(janela, text="Carga Horária:").pack(pady=5)
    entry_carga = ctk.CTkEntry(janela, width=300)
    entry_carga.pack(pady=5)

    def salvar():
        nome = entry_nome.get()
        rg = entry_rg.get()
        cargo = entry_cargo.get()
        contrato = entry_contrato.get()
        carga = entry_carga.get()

        if nome and rg:
            try:
                conn = conectar()
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO funcionarios (nome, rg, cargo, contrato, carga_horaria)
                VALUES (?, ?, ?, ?, ?)
                """, (nome, rg, cargo, contrato, carga))
                conn.commit()
                conn.close()
                ctk.CTkMessagebox.show_info("Sucesso", "Funcionário cadastrado!")
                janela.destroy()
            except Exception as e:
                ctk.CTkMessagebox.show_error("Erro", f"Erro ao salvar: {e}")
        else:
            ctk.CTkMessagebox.show_warning("Atenção", "Nome e RG são obrigatórios!")

    btn_salvar = ctk.CTkButton(janela, text="Salvar", command=salvar)
    btn_salvar.pack(pady=20)
