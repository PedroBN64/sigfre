# views/cadastro_funcionario.py
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from database.db import conectar
import tkinter.messagebox as tk_messagebox  # fallback seguro
import tkinter as tk


def abrir_tela_cadastro(root, atualizar_lista=None):
    """Abre a janela de cadastro de funcionário."""
    janela = ctk.CTkToplevel(root)
    janela.geometry("520x620")
    janela.title("Cadastrar Funcionário")
    janela.transient(root)
    janela.grab_set()  # impede interação com a principal até fechar
    janela.focus_force()

    campos = [
        ("Nome completo:", "EX: MARIA SILVA"),
        ("RG:", "EX: 12.345.678-9"),
        ("Cargo/Função:", "EX: PROFESSORA"),
        ("Contrato:", "EX: CLT"),
        ("Carga Horária:", "EX: 40H SEMANAIS")
    ]

    entries = {}
    for label, placeholder in campos:
        ctk.CTkLabel(janela, text=label, font=("Arial", 13, "bold")).pack(pady=(18, 5))
        entry = ctk.CTkEntry(janela, width=380, placeholder_text=placeholder, font=("Arial", 12))
        entry.pack(pady=5)
        entries[label] = entry

    def safe_messagebox(kind: str, title: str, msg: str):
        """Exibe uma CTkMessagebox e faz fallback em caso de erro de foco."""
        try:
            janela.focus_force()
            CTkMessagebox(
                title=title,
                message=msg,
                icon="check" if kind == "success" else ("warning" if kind == "warn" else "cancel")
            )
        except tk.TclError:
            if kind == "success":
                tk_messagebox.showinfo(title, msg)
            elif kind == "warn":
                tk_messagebox.showwarning(title, msg)
            else:
                tk_messagebox.showerror(title, msg)

    def salvar():
        """Valida e salva os dados do funcionário."""
        dados = {k: v.get().strip().upper() for k, v in entries.items()}
        nome = dados["Nome completo:"]
        rg = dados["RG:"]

        if not nome or not rg:
            safe_messagebox("error", "Erro", "Nome e RG são obrigatórios!")
            return

        conn = conectar()
        cursor = conn.cursor()

        # Verifica duplicidade por RG
        cursor.execute("SELECT nome FROM funcionarios WHERE rg = ?", (rg,))
        existente = cursor.fetchone()
        if existente:
            safe_messagebox("warn", "Duplicidade", f"RG {rg} já cadastrado para {existente[0]}!")
            conn.close()
            return

        try:
            cursor.execute("""
                INSERT INTO funcionarios (nome, rg, cargo, contrato, carga_horaria)
                VALUES (?, ?, ?, ?, ?)
            """, (
                nome,
                rg,
                dados["Cargo/Função:"],
                dados["Contrato:"],
                dados["Carga Horária:"]
            ))
            conn.commit()
            safe_messagebox("success", "Sucesso!", "Funcionário cadastrado com sucesso!")
            janela.after(150, janela.destroy)  # evita erro de foco ao fechar
            if atualizar_lista:
                root.after(200, atualizar_lista)  # atualiza tabela após fechar
        except Exception as e:
            safe_messagebox("error", "Erro", f"Erro ao salvar:\n{e}")
        finally:
            conn.close()

    # === Botões ===
    frame_btn = ctk.CTkFrame(janela)
    frame_btn.pack(pady=30)

    ctk.CTkButton(
        frame_btn,
        text="SALVAR",
        command=salvar,
        fg_color="green",
        hover_color="darkgreen",
        width=160
    ).pack(side="left", padx=12)

    ctk.CTkButton(
        frame_btn,
        text="CANCELAR",
        command=janela.destroy,
        fg_color="gray",
        hover_color="darkgray",
        width=160
    ).pack(side="left", padx=12)
