# views/cadastro_funcionario.py
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox  # <-- AGORA FUNCIONA!
from database.db import conectar

def abrir_tela_cadastro(root, atualizar_lista=None):
    janela = ctk.CTkToplevel(root)
    janela.geometry("500x580")
    janela.title("Cadastrar Funcionário")
    janela.grab_set()
    janela.focus()

    # Campos com placeholder
    campos = [
        ("Nome completo:", "Ex: Maria Silva"),
        ("RG:", "Ex: 12.345.678-9"),
        ("Cargo/Função:", "Ex: Professora"),
        ("Contrato:", "Ex: CLT"),
        ("Carga Horária:", "Ex: 40h semanais")
    ]

    entries = {}
    for i, (label, placeholder) in enumerate(campos):
        ctk.CTkLabel(janela, text=label, font=("Arial", 13, "bold")).pack(pady=(15,5))
        entry = ctk.CTkEntry(janela, width=350, placeholder_text=placeholder, font=("Arial", 12))
        entry.pack(pady=5)
        entries[label] = entry

    def salvar():
        dados = {k: v.get().strip() for k, v in entries.items()}
        if not dados["Nome completo:"] or not dados["RG:"]:
            CTkMessagebox(title="Erro", message="Nome e RG são obrigatórios!", icon="cancel")
            return

        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO funcionarios (nome, rg, cargo, contrato, carga_horaria)
            VALUES (?, ?, ?, ?, ?)
            """, (
                dados["Nome completo:"],
                dados["RG:"],
                dados["Cargo/Função:"],
                dados["Contrato:"],
                dados["Carga Horária:"]
            ))
            conn.commit()
            conn.close()
            CTkMessagebox(title="Sucesso!", message="Funcionário cadastrado!", icon="check")
            janela.destroy()
            if atualizar_lista:
                atualizar_lista()
        except Exception as e:
            CTkMessagebox(title="Erro", message=f"Erro: {str(e)}", icon="cancel")

    frame_btn = ctk.CTkFrame(janela)
    frame_btn.pack(pady=25)

    ctk.CTkButton(frame_btn, text="SALVAR", command=salvar,
                  fg_color="green", hover_color="darkgreen", width=150).pack(side="left", padx=10)
    ctk.CTkButton(frame_btn, text="CANCELAR", command=janela.destroy,
                  fg_color="gray", hover_color="darkgray", width=150).pack(side="left", padx=10)
