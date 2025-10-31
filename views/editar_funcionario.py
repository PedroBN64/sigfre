import customtkinter as ctk
from database.db import conectar
import tkinter.messagebox as tk_messagebox
import tkinter as tk

def abrir_tela_editar(root, tree, conn, atualizar_lista=None):
    """Abre janela para editar/apagar funcionário."""
    sel = tree.selection()
    if not sel:
        tk_messagebox.showwarning("Aviso", "Selecione um funcionário!")
        return

    item = tree.item(sel[0])
    
    # CORREÇÃO: Pegar o ID correto das tags - agora tratando tanto string quanto int
    tags = item["tags"]
    func_id = None
    
    for tag in tags:
        # Se for string numérica ou já for inteiro
        if isinstance(tag, int):
            func_id = tag
            break
        elif isinstance(tag, str) and tag.isdigit():
            func_id = int(tag)
            break
    
    # Se não encontrou ID, tenta pegar a primeira tag
    if func_id is None and tags:
        try:
            first_tag = tags[0]
            if isinstance(first_tag, int):
                func_id = first_tag
            elif isinstance(first_tag, str) and first_tag.isdigit():
                func_id = int(first_tag)
        except (ValueError, IndexError):
            pass
    
    if func_id is None:
        tk_messagebox.showerror("Erro", "Não foi possível identificar o funcionário!")
        return

    valores = item["values"]   # Valores atuais

    janela = ctk.CTkToplevel(root)
    janela.geometry("520x620")
    janela.title("Editar Funcionário")
    janela.transient(root)
    janela.grab_set()
    janela.focus_force()

    def safe_messagebox(kind: str, title: str, msg: str):
        """Exibe mensagem com fallback seguro."""
        try:
            janela.focus_force()
            if kind == "success":
                tk_messagebox.showinfo(title, msg)
            elif kind == "warn":
                tk_messagebox.showwarning(title, msg)
            else:
                tk_messagebox.showerror(title, msg)
        except tk.TclError:
            print(f"{title}: {msg}")

    campos = [
        ("Nome completo:", "EX: MARIA SILVA"),
        ("RG:", "EX: 12.345.678-9"), 
        ("Cargo/Função:", "EX: PROFESSORA"),
        ("Contrato:", "EX: CLT"),
        ("Carga Horária:", "EX: 40H SEMANAIS")
    ]

    entries = {}
    for (label, placeholder), valor in zip(campos, valores):
        ctk.CTkLabel(janela, text=label, font=("Arial", 13, "bold")).pack(pady=(18, 5))
        entry = ctk.CTkEntry(janela, width=380, placeholder_text=placeholder, font=("Arial", 12))
        entry.insert(0, valor if valor else "")  # Insere valor atual ou string vazia
        entry.pack(pady=5)
        entries[label] = entry

    def salvar_edicao():
        """Salva as alterações do funcionário."""
        dados = {k: v.get().strip().upper() for k, v in entries.items()}
        nome = dados["Nome completo:"]
        rg = dados["RG:"]

        if not nome or not rg:
            safe_messagebox("error", "Erro", "Nome e RG são obrigatórios!")
            return

        # Cria uma NOVA conexão para a operação
        nova_conn = conectar()
        cursor = nova_conn.cursor()
        
        try:
            # VERIFICAÇÃO CORRIGIDA: Só alerta se o RG pertence a OUTRO funcionário
            cursor.execute("SELECT nome FROM funcionarios WHERE rg = ? AND id != ?", (rg, func_id))
            existente = cursor.fetchone()
            
            if existente:
                safe_messagebox("warn", "Duplicidade", f"RG {rg} já pertence a {existente[0]}!")
                nova_conn.close()
                return

            # ATUALIZA os dados
            cursor.execute("""
                UPDATE funcionarios 
                SET nome = ?, rg = ?, cargo = ?, contrato = ?, carga_horaria = ?
                WHERE id = ?
            """, (
                nome, 
                rg, 
                dados["Cargo/Função:"], 
                dados["Contrato:"],
                dados["Carga Horária:"],
                func_id  # ID do funcionário sendo editado
            ))
            
            nova_conn.commit()
            safe_messagebox("success", "Sucesso", "Funcionário atualizado com sucesso!")
            nova_conn.close()
            
            # Fecha a janela e atualiza a tabela
            janela.after(150, janela.destroy)
            if atualizar_lista:
                root.after(200, atualizar_lista)  # Atualiza a tabela principal
                
        except Exception as e:
            safe_messagebox("error", "Erro", f"Erro ao atualizar:\n{str(e)}")
            nova_conn.close()

    def apagar_funcionario():
        """Apaga funcionário e suas faltas."""
        # Pega o nome atual para confirmar
        nome_atual = entries["Nome completo:"].get().strip()
        rg_atual = entries["RG:"].get().strip()
        
        if not nome_atual:
            nome_atual = "este funcionário"
            
        resposta = tk_messagebox.askyesno(
            "Confirmar Exclusão", 
            f"Tem certeza que deseja APAGAR:\n\n"
            f"Nome: {nome_atual}\n"
            f"RG: {rg_atual}\n\n"
            f"TODAS as faltas registradas também serão apagadas!\n"
            f"Esta ação NÃO pode ser desfeita!",
            icon="warning"
        )
        
        if resposta:
            # Cria uma NOVA conexão para a operação
            nova_conn = conectar()
            cursor = nova_conn.cursor()
            
            try:
                print(f"Tentando apagar funcionário ID: {func_id}")  # DEBUG
                
                # PRIMEIRO: Verifica se o funcionário existe
                cursor.execute("SELECT nome FROM funcionarios WHERE id = ?", (func_id,))
                funcionario_existe = cursor.fetchone()
                
                if not funcionario_existe:
                    safe_messagebox("error", "Erro", "Funcionário não encontrado!")
                    nova_conn.close()
                    return
                
                print(f"Funcionário encontrado: {funcionario_existe[0]}")  # DEBUG
                
                # SEGUNDO: Conta quantas faltas serão apagadas
                cursor.execute("SELECT COUNT(*) FROM frequencia WHERE funcionario_id = ?", (func_id,))
                total_faltas = cursor.fetchone()[0]
                print(f"Faltas a serem apagadas: {total_faltas}")  # DEBUG
                
                # TERCEIRO: Apaga primeiro as faltas (devido à chave estrangeira)
                if total_faltas > 0:
                    cursor.execute("DELETE FROM frequencia WHERE funcionario_id = ?", (func_id,))
                    print(f"Faltas apagadas: {cursor.rowcount}")  # DEBUG
                
                # QUARTO: Apaga o funcionário
                cursor.execute("DELETE FROM funcionarios WHERE id = ?", (func_id,))
                linhas_afetadas = cursor.rowcount
                print(f"Funcionários apagados: {linhas_afetadas}")  # DEBUG
                
                if linhas_afetadas > 0:
                    nova_conn.commit()
                    safe_messagebox("success", "Sucesso", "Funcionário apagado com sucesso!")
                    
                    # Fecha a janela e atualiza a tabela
                    janela.after(150, janela.destroy)
                    if atualizar_lista:
                        root.after(200, atualizar_lista)  # Atualiza a tabela principal
                else:
                    safe_messagebox("error", "Erro", "Nenhum funcionário foi apagado!")
                    
            except Exception as e:
                safe_messagebox("error", "Erro", f"Erro ao apagar:\n{str(e)}")
                print(f"Erro detalhado: {e}")  # DEBUG
            finally:
                nova_conn.close()

    # Botões
    frame_btn = ctk.CTkFrame(janela)
    frame_btn.pack(pady=30)

    ctk.CTkButton(
        frame_btn, 
        text="SALVAR ALTERAÇÕES", 
        command=salvar_edicao,
        fg_color="green", 
        hover_color="darkgreen", 
        width=180
    ).pack(side="left", padx=8)

    ctk.CTkButton(
        frame_btn, 
        text="APAGAR FUNCIONÁRIO", 
        command=apagar_funcionario,
        fg_color="red", 
        hover_color="darkred", 
        width=180
    ).pack(side="left", padx=8)

    ctk.CTkButton(
        frame_btn, 
        text="CANCELAR", 
        command=lambda: janela.after(150, janela.destroy),
        fg_color="gray", 
        hover_color="darkgray", 
        width=120
    ).pack(side="left", padx=8)

    # Focar no primeiro campo
    entries["Nome completo:"].focus()