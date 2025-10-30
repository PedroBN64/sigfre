# views/cadastro_funcionario.py
import customtkinter as ctk
import tkinter.messagebox as msgbox  # <-- USA TKINTER NATIVO
from database.db import conectar

def abrir_tela_cadastro(root):
    janela = ctk.CTkToplevel(root)
    janela.geometry("500x550")
    janela.title("Cadastrar Funcionário")
    janela.grab_set()

    # Campos
    ctk.CTkLabel(janela, text="Nome:", font=("Arial", 12)).pack(pady=8)
    entry_nome = ctk.CTkEntry(janela, width=320, placeholder_text="Ex: Maria Silva")
    entry_nome.pack(pady=5)

    ctk.CTkLabel(janela, text="RG:", font=("Arial", 12)).pack(pady=8)
    entry_rg = ctk.CTkEntry(janela, width=320, placeholder_text="Ex: 12345678")
    entry_rg.pack(pady=5)

    ctk.CTkLabel(janela, text="Cargo/Função:", font=("Arial", 12)).pack(pady=8)
    entry_cargo = ctk.CTkEntry(janela, width=320, placeholder_text="Ex: Professora")
    entry_cargo.pack(pady=5)

    ctk.CTkLabel(janela, text="Contrato:", font=("Arial", 12)).pack(pady=8)
    entry_contrato = ctk.CTkEntry(janela, width=320, placeholder_text="Ex: CLT")
    entry_contrato.pack(pady=5)

    ctk.CTkLabel(janela, text="Carga Horária:", font=("Arial", 12)).pack(pady=8)
    entry_carga = ctk.CTkEntry(janela, width=320, placeholder_text="Ex: 40h semanais")
    entry_carga.pack(pady=5)

    def salvar():
        nome = entry_nome.get().strip()
        rg = entry_rg.get().strip()
        cargo = entry_cargo.get().strip()
        contrato = entry_contrato.get().strip()
        carga = entry_carga.get().strip()

        if not nome or not rg:
            msgbox.showwarning("Atenção", "Nome e RG são obrigatórios!")
            return

        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO funcionarios (nome, rg, cargo, contrato, carga_horaria)
            VALUES (?, ?, ?, ?, ?)
            """, (nome, rg, cargo, contrato, carga))
            conn.commit()
            conn.close()
            msgbox.showinfo("Sucesso", "Funcionário cadastrado com sucesso!")
            janela.destroy()
        except Exception as e:
            msgbox.showerror("Erro", f"Erro ao salvar:\n{str(e)}")

    frame_botoes = ctk.CTkFrame(janela)
    frame_botoes.pack(pady=20)

    btn_salvar = ctk.CTkButton(
        frame_botoes, text="Salvar", command=salvar,
        fg_color="green", hover_color="darkgreen", width=140
    )
    btn_salvar.pack(side="left", padx=10)

    btn_cancelar = ctk.CTkButton(
        frame_botoes, text="Cancelar", command=janela.destroy,
        fg_color="gray", hover_color="darkgray", width=140
    )
    btn_cancelar.pack(side="left", padx=10)
