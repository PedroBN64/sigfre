import customtkinter as ctk
from views.cadastro_funcionario import abrir_tela_cadastro
from views.frequencia import abrir_tela_frequencia
from views.editar_funcionario import abrir_tela_editar
from reports.gerar_pdf import gerar_folha
from database.db import conectar
from tkinter import ttk, Menu
from ttkthemes import ThemedStyle
import tkinter.messagebox as tk_messagebox

def atualizar_tabela(tree, conn, filtro=""):
    """Atualiza a tabela de funcionários."""
    for item in tree.get_children():
        tree.delete(item)
    
    cursor = conn.cursor()
    query = "SELECT id, nome, rg, cargo, contrato, carga_horaria FROM funcionarios"
    params = []
    
    if filtro:
        query += " WHERE nome LIKE ? OR rg LIKE ?"
        params = [f"%{filtro}%", f"%{filtro}%"]
        
    cursor.execute(query, params)
    
    for i, row in enumerate(cursor.fetchall()):
        # CORREÇÃO: Garantir que o ID seja sempre a primeira tag
        item_id = row[0]  # ID como inteiro (não precisa converter para string)
        color_tag = "odd" if i % 2 == 0 else "even"
        
        # Insere com ID como primeira tag e cor como segunda
        tree.insert("", "end", values=row[1:], tags=(item_id, color_tag))
    
    tree.tag_configure("odd", background="#2b2b2b")
    tree.tag_configure("even", background="#1e1e1e")

def criar_tela_principal(root):
    """Cria a tela principal do sistema."""
    # Usar uma lista para armazenar a conexão (truque para bypass do nonlocal)
    conn_ref = [conectar()]
    
    def get_conn():
        """Retorna a conexão atual."""
        return conn_ref[0]
    
    def set_conn(new_conn):
        """Define uma nova conexão."""
        # Fecha a conexão antiga se existir
        if conn_ref[0]:
            try:
                conn_ref[0].close()
            except:
                pass
        conn_ref[0] = new_conn
    
    # Configurar tema
    style = ThemedStyle(root)
    style.set_theme("equilux")

    frame = ctk.CTkFrame(root)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    # Título
    ctk.CTkLabel(frame, text="SIGFRE - Sistema de Folha", 
                font=ctk.CTkFont(size=22, weight="bold")).pack(pady=15)

    # Filtro
    frame_filtro = ctk.CTkFrame(frame)
    frame_filtro.pack(pady=10, fill="x", padx=10)
    
    ctk.CTkLabel(frame_filtro, text="Buscar:").pack(side="left", padx=10)
    
    entry_filtro = ctk.CTkEntry(frame_filtro, width=300, placeholder_text="Nome ou RG...")
    entry_filtro.pack(side="left", padx=5, fill="x", expand=True)

    def aplicar_filtro(event=None):
        atualizar_tabela(tree, get_conn(), entry_filtro.get().strip())

    entry_filtro.bind("<KeyRelease>", aplicar_filtro)

    ctk.CTkButton(frame_filtro, text="Limpar", width=80,
                  command=lambda: (entry_filtro.delete(0, "end"), 
                                  atualizar_tabela(tree, get_conn()))).pack(side="right", padx=10)

    # Botões principais
    frame_botoes = ctk.CTkFrame(frame)
    frame_botoes.pack(pady=10, fill="x", padx=10)

    def callback_atualizacao():
        """Callback CORRIGIDO para atualizar a tabela."""
        try:
            # Fecha a conexão atual e cria uma nova
            current_conn = get_conn()
            if current_conn:
                current_conn.close()
            
            # Cria nova conexão
            nova_conn = conectar()
            set_conn(nova_conn)
            
            # Atualiza a tabela
            atualizar_tabela(tree, nova_conn, entry_filtro.get().strip())
            
        except Exception as e:
            print(f"Erro ao atualizar tabela: {e}")
            # Tenta recriar a conexão em caso de erro
            try:
                nova_conn = conectar()
                set_conn(nova_conn)
                atualizar_tabela(tree, nova_conn, entry_filtro.get().strip())
            except Exception as e2:
                print(f"Erro crítico ao recriar conexão: {e2}")

    ctk.CTkButton(frame_botoes, text="Cadastrar", 
                  command=lambda: abrir_tela_cadastro(root, callback_atualizacao),
                  fg_color="#1f6aa5", hover_color="#16527c", width=160).pack(side="left", padx=10)
    
    ctk.CTkButton(frame_botoes, text="Faltas", 
                  command=lambda: abrir_tela_frequencia(root, callback_atualizacao),
                  fg_color="#ff9800", hover_color="#cc7a00", width=160).pack(side="left", padx=10)
    
    ctk.CTkButton(frame_botoes, text="Editar/Apagar", 
                  command=lambda: abrir_tela_editar(root, tree, get_conn(), callback_atualizacao),
                  fg_color="#9c27b0", hover_color="#7b1fa2", width=160).pack(side="left", padx=10)
    
    ctk.CTkButton(frame_botoes, text="Gerar Folha", 
                  command=lambda: abrir_janela_mes_ano(root),
                  fg_color="green", hover_color="darkgreen", width=160).pack(side="left", padx=10)

    # Tabela
    columns = ("nome", "rg", "cargo", "contrato", "carga_horaria")
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
    
    for col, text in zip(columns, ["Nome", "RG", "Cargo", "Contrato", "Carga Horária"]):
        tree.heading(col, text=text)
        tree.column(col, width=160, anchor="center")
    
    tree.pack(pady=15, fill="both", expand=True, padx=10)

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    # ========== NOVAS FUNCIONALIDADES ==========

    def get_selected_funcionario_id():
        """Retorna o ID do funcionário selecionado na tabela."""
        sel = tree.selection()
        if not sel:
            return None
        
        item = tree.item(sel[0])
        tags = item["tags"]
        func_id = None
        
        # Encontra o ID nas tags
        for tag in tags:
            if isinstance(tag, int):
                func_id = tag
                break
            elif isinstance(tag, str) and tag.isdigit():
                func_id = int(tag)
                break
        
        if func_id is None and tags:
            try:
                first_tag = tags[0]
                if isinstance(first_tag, int):
                    func_id = first_tag
                elif isinstance(first_tag, str) and first_tag.isdigit():
                    func_id = int(first_tag)
            except (ValueError, IndexError):
                pass
        
        return func_id

    def on_double_click(event):
        """Abre tela de faltas com duplo clique em qualquer linha."""
        item = tree.identify_row(event.y)
        if item:
            # Seleciona o item clicado
            tree.selection_set(item)
            # Verifica se tem um funcionário selecionado
            if get_selected_funcionario_id():
                # Abre a tela de faltas
                abrir_tela_frequencia(root, callback_atualizacao)
            else:
                tk_messagebox.showwarning("Aviso", "Selecione um funcionário válido!")

    def show_context_menu(event):
        """Mostra menu de contexto com botão direito."""
        item = tree.identify_row(event.y)
        if item:
            # Seleciona o item clicado
            tree.selection_set(item)
            
            # Verifica se tem um funcionário selecionado
            func_id = get_selected_funcionario_id()
            if not func_id:
                tk_messagebox.showwarning("Aviso", "Selecione um funcionário válido!")
                return
            
            # Cria menu de contexto
            context_menu = Menu(root, tearoff=0, font=("Arial", 10))
            context_menu.add_command(
                label="📝 Editar Funcionário", 
                command=lambda: abrir_editar_selecionado()
            )
            context_menu.add_separator()
            context_menu.add_command(
                label="❌ Excluir Funcionário", 
                command=lambda: excluir_funcionario_selecionado()
            )
            context_menu.add_separator()
            context_menu.add_command(
                label="📋 Registrar Faltas", 
                command=lambda: abrir_tela_frequencia(root, callback_atualizacao)
            )
            
            # Mostra o menu na posição do clique
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()

    def abrir_editar_selecionado():
        """Abre tela de edição para o funcionário selecionado."""
        func_id = get_selected_funcionario_id()
        if func_id:
            abrir_tela_editar(root, tree, get_conn(), callback_atualizacao)
        else:
            tk_messagebox.showwarning("Aviso", "Selecione um funcionário primeiro!")

    def excluir_funcionario_selecionado():
        """Exclui funcionário selecionado diretamente do menu de contexto."""
        func_id = get_selected_funcionario_id()
        if not func_id:
            tk_messagebox.showwarning("Aviso", "Selecione um funcionário primeiro!")
            return

        # Pega o nome do funcionário para a confirmação
        sel = tree.selection()
        item = tree.item(sel[0])
        nome_funcionario = item["values"][0]  # Primeira coluna é o nome
        
        resposta = tk_messagebox.askyesno(
            "Confirmar Exclusão", 
            f"Tem certeza que deseja APAGAR:\n\n"
            f"Nome: {nome_funcionario}\n\n"
            f"TODAS as faltas registradas também serão apagadas!\n"
            f"Esta ação NÃO pode ser desfeita!",
            icon="warning"
        )
        
        if resposta:
            # Cria uma NOVA conexão para a operação
            nova_conn = conectar()
            cursor = nova_conn.cursor()
            
            try:
                # Verifica se o funcionário existe
                cursor.execute("SELECT nome FROM funcionarios WHERE id = ?", (func_id,))
                funcionario_existe = cursor.fetchone()
                
                if not funcionario_existe:
                    tk_messagebox.showerror("Erro", "Funcionário não encontrado!")
                    nova_conn.close()
                    return
                
                # Apaga primeiro as faltas
                cursor.execute("DELETE FROM frequencia WHERE funcionario_id = ?", (func_id,))
                
                # Apaga o funcionário
                cursor.execute("DELETE FROM funcionarios WHERE id = ?", (func_id,))
                linhas_afetadas = cursor.rowcount
                
                if linhas_afetadas > 0:
                    nova_conn.commit()
                    tk_messagebox.showinfo("Sucesso", "Funcionário apagado com sucesso!")
                    
                    # Atualiza a tabela
                    if callback_atualizacao:
                        callback_atualizacao()
                else:
                    tk_messagebox.showerror("Erro", "Nenhum funcionário foi apagado!")
                    
            except Exception as e:
                tk_messagebox.showerror("Erro", f"Erro ao apagar:\n{str(e)}")
            finally:
                nova_conn.close()

    # ========== CONFIGURAR EVENTOS DA TABELA ==========

    # Duplo clique - Abre tela de faltas
    tree.bind("<Double-1>", on_double_click)
    
    # Clique direito - Menu de contexto
    tree.bind("<Button-3>", show_context_menu)  # Button-3 é botão direito

    # ========== FIM DAS NOVAS FUNCIONALIDADES ==========

    # Carregar dados iniciais
    atualizar_tabela(tree, get_conn())

    def abrir_janela_mes_ano(parent):
        """Abre janela para gerar folha PDF."""
        janela = ctk.CTkToplevel(parent)
        janela.geometry("400x280")
        janela.title("Gerar Folha")
        janela.transient(parent)
        janela.grab_set()
        janela.focus_force()

        ctk.CTkLabel(janela, text="Mês e Ano", font=("Arial", 16, "bold")).pack(pady=20)

        frame_campos = ctk.CTkFrame(janela)
        frame_campos.pack(pady=10, padx=20)

        ctk.CTkLabel(frame_campos, text="Mês (01-12):").grid(row=0, column=0, padx=15, pady=10, sticky="e")
        entry_mes = ctk.CTkEntry(frame_campos, width=100, placeholder_text="08")
        entry_mes.grid(row=0, column=1, padx=15, pady=10)

        ctk.CTkLabel(frame_campos, text="Ano:").grid(row=1, column=0, padx=15, pady=10, sticky="e")
        entry_ano = ctk.CTkEntry(frame_campos, width=100, placeholder_text="2025")
        entry_ano.grid(row=1, column=1, padx=15, pady=10)

        def gerar_pdf():
            """Gera o PDF da folha."""
            mes = entry_mes.get().strip()
            ano = entry_ano.get().strip()
            
            if not (mes.isdigit() and 1 <= int(mes) <= 12 and ano.isdigit() and len(ano) == 4):
                tk_messagebox.showerror("Erro", "Mês deve ser 01-12 e Ano com 4 dígitos!")
                return
            
            try:
                gerar_folha(mes.zfill(2), ano)
                tk_messagebox.showinfo("Sucesso", "PDF gerado com sucesso!")
                janela.after(150, janela.destroy)
            except Exception as e:
                tk_messagebox.showerror("Erro", f"Erro ao gerar PDF:\n{e}")

        frame_btn = ctk.CTkFrame(janela)
        frame_btn.pack(pady=20)
        
        ctk.CTkButton(frame_btn, text="GERAR PDF", command=gerar_pdf,
                      fg_color="green", hover_color="darkgreen").pack(side="left", padx=10)
        
        ctk.CTkButton(frame_btn, text="CANCELAR", 
                      command=lambda: janela.after(150, janela.destroy),
                      fg_color="gray", hover_color="darkgray").pack(side="left", padx=10)

    def fechar_aplicacao():
        """Fecha a aplicação corretamente."""
        try:
            current_conn = get_conn()
            if current_conn:
                current_conn.close()
        except:
            pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", fechar_aplicacao)