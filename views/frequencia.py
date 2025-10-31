import customtkinter as ctk
from database.db import conectar
from tkinter import ttk
import tkinter.messagebox as tk_messagebox
import tkinter as tk
import re

def abrir_tela_frequencia(root, atualizar_lista=None):
    """Abre a janela de registro de faltas."""
    janela = ctk.CTkToplevel(root)
    janela.geometry("900x650")  # Tamanho inicial menor
    janela.title("Registrar Faltas")
    janela.transient(root)
    janela.grab_set()
    janela.focus_force()
    
    # Permitir maximizar
    janela.minsize(900, 650)
    janela.resizable(True, True)  # Permitir redimensionar

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

    # Conexão com banco
    conn = conectar()
    cursor = conn.cursor()
    
    # VERIFICAR E CRIAR COLUNA DETALHES SE NECESSÁRIO
    try:
        cursor.execute("PRAGMA table_info(frequencia)")
        colunas = [col[1] for col in cursor.fetchall()]
        if 'detalhes' not in colunas:
            cursor.execute("ALTER TABLE frequencia ADD COLUMN detalhes TEXT")
            conn.commit()
            print("Coluna 'detalhes' adicionada à tabela frequencia")
    except Exception as e:
        print(f"Erro ao verificar coluna detalhes: {e}")

    cursor.execute("SELECT id, nome FROM funcionarios ORDER BY nome")
    funcs = cursor.fetchall()

    if not funcs:
        safe_messagebox("warn", "Aviso", "Cadastre funcionários primeiro!")
        conn.close()
        janela.destroy()
        return

    # Lista de justificativas padrão + personalizadas
    justificativas_padrao = [
        "AM", "AB", "TRE", "SOL", "Declaração", "INJ", "FH", 
        "Folga Aniversário", "Atestado", "Falta Justificada", "Licença-Prêmio"
    ]
    
    # Carregar justificativas personalizadas do banco (se existir)
    justificativas_personalizadas = []
    try:
        cursor.execute("SELECT nome FROM justificativas_personalizadas")
        justificativas_personalizadas = [row[0] for row in cursor.fetchall()]
    except:
        pass
    
    justificativas_completas = justificativas_padrao + justificativas_personalizadas

    # ========== FRAME PRINCIPAL COM SCROLL ==========
    # Frame principal que vai conter tudo
    main_container = ctk.CTkFrame(janela)
    main_container.pack(fill="both", expand=True, padx=10, pady=10)

    # Canvas para scroll
    canvas = tk.Canvas(main_container, bg='#2b2b2b', highlightthickness=0)
    scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
    scrollable_frame = ctk.CTkFrame(canvas)

    # Configurar o scroll
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Empacotar canvas e scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Configurar scroll com mouse wheel
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # ========== CONTEÚDO DA JANELA ==========
    # Título
    ctk.CTkLabel(scrollable_frame, text="REGISTRAR FALTAS", 
                font=("Arial", 18, "bold")).pack(pady=15)

    # ========== PESQUISA DE FUNCIONÁRIO ==========
    frame_pesquisa = ctk.CTkFrame(scrollable_frame)
    frame_pesquisa.pack(pady=10, fill="x", padx=10)

    ctk.CTkLabel(frame_pesquisa, text="Pesquisar Funcionário:", 
                font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 8))

    entry_pesquisa = ctk.CTkEntry(frame_pesquisa, 
                                 placeholder_text="Digite o nome do funcionário...", 
                                 height=35, 
                                 font=("Arial", 12))
    entry_pesquisa.pack(fill="x", pady=5)
    entry_pesquisa.focus()

    # Lista de funcionários
    frame_lista_funcs = ctk.CTkFrame(scrollable_frame)
    frame_lista_funcs.pack(pady=10, fill="x", padx=10)

    ctk.CTkLabel(frame_lista_funcs, text="Funcionários:", 
                font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))

    tree_funcs = ttk.Treeview(frame_lista_funcs, columns=("nome",), show="tree", height=6)
    tree_funcs.heading("#0", text="Funcionários")
    tree_funcs.column("#0", width=400)
    tree_funcs.pack(side="left", fill="both", expand=True)

    scrollbar_funcs = ttk.Scrollbar(frame_lista_funcs, orient="vertical", command=tree_funcs.yview)
    scrollbar_funcs.pack(side="right", fill="y")
    tree_funcs.configure(yscrollcommand=scrollbar_funcs.set)

    # ========== FORMULÁRIO DE FALTAS ==========
    frame_form = ctk.CTkFrame(scrollable_frame)
    frame_form.pack(pady=15, fill="x", padx=10)

    ctk.CTkLabel(frame_form, text="Dados da Falta:", 
                font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))

    # Linha 1 - Data
    frame_data = ctk.CTkFrame(frame_form)
    frame_data.pack(fill="x", pady=8, padx=10)

    ctk.CTkLabel(frame_data, text="Data (DD/MM/AAAA):", 
                font=("Arial", 12, "bold"), width=180).pack(side="left", padx=(0, 10))
    
    entry_data = ctk.CTkEntry(frame_data, 
                             width=150, 
                             placeholder_text="15/08/2025", 
                             height=35,
                             font=("Arial", 12))
    entry_data.pack(side="left")

    # Linha 2 - Justificativa
    frame_just = ctk.CTkFrame(frame_form)
    frame_just.pack(fill="x", pady=8, padx=10)

    ctk.CTkLabel(frame_just, text="Justificativa:", 
                font=("Arial", 12, "bold"), width=180).pack(side="left", padx=(0, 10))
    
    combo_just = ctk.CTkComboBox(frame_just, 
                                values=justificativas_completas, 
                                width=250, 
                                height=35,
                                font=("Arial", 12))
    combo_just.pack(side="left", padx=(0, 10))
    combo_just.set("AM")
    
    btn_nova_just = ctk.CTkButton(frame_just, 
                                 text="+ Nova", 
                                 width=80, 
                                 height=35,
                                 command=lambda: adicionar_justificativa(),
                                 fg_color="#4CAF50", 
                                 hover_color="#45a049",
                                 font=("Arial", 11))
    btn_nova_just.pack(side="left")

    # ========== CAMPOS ESPECIAIS DINÂMICOS ==========
    frame_especiais = ctk.CTkFrame(scrollable_frame)
    frame_especiais.pack(pady=10, fill="x", padx=10)

    # Variáveis para campos especiais
    label_especial = ctk.CTkLabel(frame_especiais, text="", font=("Arial", 12, "bold"))
    entry_especial = ctk.CTkEntry(frame_especiais, 
                                 width=300, 
                                 height=35,
                                 font=("Arial", 12))
    label_info = ctk.CTkLabel(frame_especiais, text="", font=("Arial", 11), text_color="gray")

    def mostrar_campos_especiais(justificativa):
        """Mostra campos especiais baseado na justificativa selecionada."""
        # Esconde todos os campos primeiro
        label_especial.pack_forget()
        entry_especial.pack_forget()
        label_info.pack_forget()
        entry_especial.delete(0, "end")
        
        if justificativa == "Licença-Prêmio":
            label_especial.configure(text="Período (DD/MM/AAAA a DD/MM/AAAA):")
            entry_especial.configure(placeholder_text="Ex: 15/08/2025 a 20/08/2025")
            label_info.configure(text="Informe o período completo da licença")
            
            label_especial.pack(anchor="w", pady=(10, 5))
            entry_especial.pack(anchor="w", pady=(0, 5), fill="x")
            label_info.pack(anchor="w")
            
        elif justificativa == "FH":
            label_especial.configure(text="Horas de Falta:")
            entry_especial.configure(placeholder_text="Ex: 1h30min ou 2h ou 45min")
            label_info.configure(text="Use formato: XhYmin (ex: 1h30min, 2h, 45min)")
            
            label_especial.pack(anchor="w", pady=(10, 5))
            entry_especial.pack(anchor="w", pady=(0, 5), fill="x")
            label_info.pack(anchor="w")

    # ========== TABELA DE FALTAS REGISTRADAS ==========
    frame_tabela_faltas = ctk.CTkFrame(scrollable_frame)
    frame_tabela_faltas.pack(pady=15, fill="x", padx=10)

    ctk.CTkLabel(frame_tabela_faltas, text="Faltas Registradas:", 
                font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 8))

    # Frame para a tabela com scroll própria
    frame_tabela_container = ctk.CTkFrame(frame_tabela_faltas)
    frame_tabela_container.pack(fill="x", pady=5)

    tree_faltas = ttk.Treeview(frame_tabela_container, 
                              columns=("data", "justificativa", "detalhes"), 
                              show="headings", 
                              height=6)
    tree_faltas.heading("data", text="Data")
    tree_faltas.heading("justificativa", text="Justificativa")
    tree_faltas.heading("detalhes", text="Detalhes")
    tree_faltas.column("data", width=120, anchor="center")
    tree_faltas.column("justificativa", width=150, anchor="center")
    tree_faltas.column("detalhes", width=250, anchor="center")
    tree_faltas.pack(side="left", fill="both", expand=True)

    scrollbar_faltas = ttk.Scrollbar(frame_tabela_container, orient="vertical", command=tree_faltas.yview)
    scrollbar_faltas.pack(side="right", fill="y")
    tree_faltas.configure(yscrollcommand=scrollbar_faltas.set)

    # ========== FUNÇÕES ==========
    funcionario_selecionado = {"id": None, "nome": None}

    def atualizar_lista_funcionarios(pesquisa=""):
        """Atualiza a lista de funcionários baseada na pesquisa."""
        for item in tree_funcs.get_children():
            tree_funcs.delete(item)
            
        for func in funcs:
            nome = func[1]
            if pesquisa.lower() in nome.lower():
                tree_funcs.insert("", "end", text=nome, values=(nome,), tags=(func[0],))

    def on_funcionario_selecionado(event):
        """Quando um funcionário é selecionado na lista."""
        selection = tree_funcs.selection()
        if selection:
            item = tree_funcs.item(selection[0])
            funcionario_selecionado["id"] = item["tags"][0]
            funcionario_selecionado["nome"] = item["text"]
            carregar_faltas_funcionario()

    def carregar_faltas_funcionario():
        """Carrega as faltas do funcionário selecionado."""
        for item in tree_faltas.get_children():
            tree_faltas.delete(item)
            
        if funcionario_selecionado["id"]:
            try:
                cursor.execute("SELECT data, justificativa, detalhes FROM frequencia WHERE funcionario_id=? ORDER BY data DESC", 
                              (funcionario_selecionado["id"],))
                for row in cursor.fetchall():
                    # Se detalhes for None, mostra string vazia
                    detalhes = row[2] if row[2] else ""
                    tree_faltas.insert("", "end", values=(row[0], row[1], detalhes))
            except Exception as e:
                print(f"Erro ao carregar faltas: {e}")
                # Fallback para versão antiga sem coluna detalhes
                try:
                    cursor.execute("SELECT data, justificativa FROM frequencia WHERE funcionario_id=? ORDER BY data DESC", 
                                  (funcionario_selecionado["id"],))
                    for row in cursor.fetchall():
                        tree_faltas.insert("", "end", values=(row[0], row[1], ""))
                except Exception as e2:
                    print(f"Erro no fallback: {e2}")

    def adicionar_justificativa():
        """Abre janela para adicionar nova justificativa."""
        janela_just = ctk.CTkToplevel(janela)
        janela_just.geometry("450x250")
        janela_just.title("Nova Justificativa")
        janela_just.transient(janela)
        janela_just.grab_set()
        janela_just.resizable(False, False)  # Não redimensionável
        
        ctk.CTkLabel(janela_just, text="Nova Justificativa:", 
                    font=("Arial", 16, "bold")).pack(pady=20)
        
        entry_nova_just = ctk.CTkEntry(janela_just, 
                                      width=350, 
                                      height=40,
                                      placeholder_text="Digite a nova justificativa...", 
                                      font=("Arial", 12))
        entry_nova_just.pack(pady=15)
        entry_nova_just.focus()
        
        def salvar_justificativa():
            nova_just = entry_nova_just.get().strip()
            if not nova_just:
                tk_messagebox.showwarning("Aviso", "Digite uma justificativa!")
                return
                
            if nova_just in justificativas_completas:
                tk_messagebox.showwarning("Aviso", "Esta justificativa já existe!")
                return
                
            try:
                cursor.execute("CREATE TABLE IF NOT EXISTS justificativas_personalizadas (id INTEGER PRIMARY KEY, nome TEXT UNIQUE)")
                cursor.execute("INSERT OR IGNORE INTO justificativas_personalizadas (nome) VALUES (?)", (nova_just,))
                conn.commit()
                
                justificativas_completas.append(nova_just)
                combo_just.configure(values=justificativas_completas)
                combo_just.set(nova_just)
                
                tk_messagebox.showinfo("Sucesso", "Justificativa adicionada com sucesso!")
                janela_just.destroy()
                
            except Exception as e:
                tk_messagebox.showerror("Erro", f"Erro ao salvar justificativa:\n{e}")
        
        frame_btn_just = ctk.CTkFrame(janela_just)
        frame_btn_just.pack(pady=20)
        
        ctk.CTkButton(frame_btn_just, text="SALVAR", 
                     command=salvar_justificativa,
                     fg_color="green", 
                     hover_color="darkgreen",
                     width=120,
                     height=35).pack(side="left", padx=10)
        
        ctk.CTkButton(frame_btn_just, text="CANCELAR", 
                     command=janela_just.destroy,
                     fg_color="gray", 
                     hover_color="darkgray",
                     width=120,
                     height=35).pack(side="left", padx=10)

    def validar_periodo_licenca(periodo):
        """Valida o formato do período da licença."""
        padrao = r'^\d{2}/\d{2}/\d{4} a \d{2}/\d{2}/\d{4}$'
        return re.match(padrao, periodo) is not None

    def validar_horas_falta(horas):
        """Valida o formato das horas de falta."""
        padrao = r'^(\d+h(\d+min)?|\d+min)$'
        if re.match(padrao, horas):
            return True
        return False

    def salvar_falta():
        """Salva uma nova falta."""
        if not funcionario_selecionado["id"]:
            safe_messagebox("error", "Erro", "Selecione um funcionário!")
            return

        data = entry_data.get().strip()
        just = combo_just.get()
        detalhes = entry_especial.get().strip()

        if not data or not just:
            safe_messagebox("error", "Erro", "Preencha todos os campos!")
            return

        # Valida data
        if len(data) != 10 or data[2] != "/" or data[5] != "/":
            safe_messagebox("error", "Erro", "Data deve ser DD/MM/AAAA!")
            return

        # Validações especiais
        if just == "Licença-Prêmio":
            if not detalhes:
                safe_messagebox("error", "Erro", "Informe o período da licença!")
                return
            if not validar_periodo_licenca(detalhes):
                safe_messagebox("error", "Erro", "Período deve ser: DD/MM/AAAA a DD/MM/AAAA")
                return
        
        elif just == "FH":
            if not detalhes:
                safe_messagebox("error", "Erro", "Informe as horas de falta!")
                return
            if not validar_horas_falta(detalhes):
                safe_messagebox("error", "Erro", "Formato inválido! Use: 1h30min, 2h, 45min")
                return

        try:
            # Verifica duplicidade
            cursor.execute("SELECT id FROM frequencia WHERE funcionario_id=? AND data=?", 
                          (funcionario_selecionado["id"], data))
            if cursor.fetchone():
                safe_messagebox("warn", "Aviso", "Já existe falta nesta data!")
                return

            # Insere no banco
            cursor.execute("INSERT INTO frequencia (funcionario_id, data, justificativa, detalhes) VALUES (?, ?, ?, ?)", 
                          (funcionario_selecionado["id"], data, just, detalhes if detalhes else None))
            conn.commit()
            
            safe_messagebox("success", "Sucesso", "Falta registrada!")
            entry_data.delete(0, "end")
            entry_especial.delete(0, "end")
            carregar_faltas_funcionario()
            if atualizar_lista:
                root.after(200, atualizar_lista)
                
        except Exception as e:
            safe_messagebox("error", "Erro", f"Erro ao salvar:\n{e}")

    def apagar_falta():
        """Apaga a falta selecionada."""
        if not funcionario_selecionado["id"]:
            safe_messagebox("error", "Erro", "Selecione um funcionário!")
            return

        sel = tree_faltas.selection()
        if not sel:
            safe_messagebox("warn", "Aviso", "Selecione uma falta!")
            return

        data = tree_faltas.item(sel[0])["values"][0]
        justificativa = tree_faltas.item(sel[0])["values"][1]
        
        if tk_messagebox.askyesno("Confirmar", f"Apagar falta de {data} - {justificativa}?"):
            try:
                cursor.execute("DELETE FROM frequencia WHERE funcionario_id=? AND data=?", 
                              (funcionario_selecionado["id"], data))
                conn.commit()
                carregar_faltas_funcionario()
                if atualizar_lista:
                    root.after(200, atualizar_lista)
                safe_messagebox("success", "Sucesso", "Falta apagada!")
            except Exception as e:
                safe_messagebox("error", "Erro", f"Erro ao apagar:\n{e}")

    # ========== CONFIGURAR EVENTOS ==========
    entry_pesquisa.bind("<KeyRelease>", lambda e: atualizar_lista_funcionarios(entry_pesquisa.get().strip()))
    tree_funcs.bind("<<TreeviewSelect>>", on_funcionario_selecionado)

    # Monitora mudanças na combobox
    def on_justificativa_change(*args):
        mostrar_campos_especiais(combo_just.get())
    
    combo_just.bind("<<ComboboxSelected>>", on_justificativa_change)
    combo_just.bind("<KeyRelease>", on_justificativa_change)

    # ========== BOTÕES ==========
    frame_botoes = ctk.CTkFrame(scrollable_frame)
    frame_botoes.pack(pady=20, fill="x", padx=10)

    ctk.CTkButton(frame_botoes, text="SALVAR FALTA", 
                  command=salvar_falta,
                  fg_color="green", 
                  hover_color="darkgreen", 
                  width=160, 
                  height=40,
                  font=("Arial", 12, "bold")).pack(side="left", padx=15)
    
    ctk.CTkButton(frame_botoes, text="APAGAR FALTA", 
                  command=apagar_falta,
                  fg_color="red", 
                  hover_color="darkred", 
                  width=160, 
                  height=40,
                  font=("Arial", 12, "bold")).pack(side="left", padx=15)
    
    ctk.CTkButton(frame_botoes, text="FECHAR", 
                  command=lambda: janela.after(150, janela.destroy),
                  fg_color="gray", 
                  hover_color="darkgray", 
                  width=160, 
                  height=40,
                  font=("Arial", 12, "bold")).pack(side="left", padx=15)

    # ========== INICIALIZAÇÃO ==========
    atualizar_lista_funcionarios()  # Carrega todos os funcionários inicialmente
    mostrar_campos_especiais("AM")  # Inicializa campos especiais

    def fechar_seguro():
        """Fecha a janela de forma segura."""
        try:
            conn.close()
            janela.destroy()
        except:
            pass

    janela.protocol("WM_DELETE_WINDOW", fechar_seguro)