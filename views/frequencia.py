import customtkinter as ctk
from database.db import conectar
from tkinter import ttk, Listbox, simpledialog
import tkinter.messagebox as messagebox
import re
from datetime import datetime, timedelta

class GerenciadorFrequencia:
    def __init__(self, root, atualizar_lista=None):
        self.root = root
        self.atualizar_lista = atualizar_lista
        self.janela = None
        self.conn = None
        self.cursor = None
        self.funcionario_selecionado = None
        
    def abrir_tela(self):
        """Abre a janela de forma simples e rápida"""
        self.janela = ctk.CTkToplevel(self.root)
        self.janela.title("Registro de Faltas")
        self.janela.geometry("700x500")
        self.janela.minsize(700, 500)
        self.janela.transient(self.root)
        self.janela.grab_set()
        
        # Conexão com banco
        self.conn = conectar()
        self.cursor = self.conn.cursor()
        
        # Verificar e criar coluna detalhes se necessário
        self._verificar_coluna_detalhes()
        
        # Carregar dados
        self._carregar_dados()
        
        # Criar interface
        self._criar_interface()
        self.entry_pesquisa.focus()
        
    def _verificar_coluna_detalhes(self):
        """Verifica e cria a coluna detalhes se não existir"""
        try:
            self.cursor.execute("PRAGMA table_info(frequencia)")
            colunas = [col[1] for col in self.cursor.fetchall()]
            if 'detalhes' not in colunas:
                self.cursor.execute("ALTER TABLE frequencia ADD COLUMN detalhes TEXT")
                self.conn.commit()
                print("Coluna 'detalhes' adicionada à tabela frequencia")
        except Exception as e:
            print(f"Erro ao verificar coluna detalhes: {e}")

    def _carregar_dados(self):
        """Carrega dados básicos"""
        self.cursor.execute("SELECT id, nome FROM funcionarios ORDER BY nome")
        self.funcionarios = self.cursor.fetchall()
        
        if not self.funcionarios:
            messagebox.showwarning("Aviso", "Nenhum funcionário cadastrado!")
            self.janela.destroy()
            return
            
        self.justificativas = ["AM", "AB", "TRE", "SOL", "Declaração", "INJ", "FH", "Folga Aniversário", "Atestado", "Falta Justificada", "Licença-Prêmio"]

    def _criar_interface(self):
        """Interface simples e funcional"""
        main_frame = ctk.CTkFrame(self.janela)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        ctk.CTkLabel(main_frame, text="REGISTRO DE FALTAS", 
                    font=("Arial", 14, "bold")).pack(pady=5)
        
        # === SELEÇÃO DE FUNCIONÁRIO ===
        frame_selecao = ctk.CTkFrame(main_frame)
        frame_selecao.pack(fill="x", pady=5)
        
        self.entry_pesquisa = ctk.CTkEntry(frame_selecao, placeholder_text="🔍 Pesquisar funcionário...")
        self.entry_pesquisa.pack(fill="x", pady=2)
        self.entry_pesquisa.bind("<KeyRelease>", self._filtrar_funcionarios)
        
        # Lista de funcionários
        frame_lista = ctk.CTkFrame(frame_selecao, height=100)
        frame_lista.pack(fill="x", pady=2)
        frame_lista.pack_propagate(False)
        
        self.lista_funcionarios = Listbox(frame_lista, font=("Arial", 9), height=5)
        scroll_func = ttk.Scrollbar(frame_lista, command=self.lista_funcionarios.yview)
        self.lista_funcionarios.configure(yscrollcommand=scroll_func.set)
        
        self.lista_funcionarios.pack(side="left", fill="both", expand=True)
        scroll_func.pack(side="right", fill="y")
        self.lista_funcionarios.bind("<<ListboxSelect>>", self._selecionar_funcionario)
        
        # === FORMULÁRIO SIMPLES ===
        frame_form = ctk.CTkFrame(main_frame)
        frame_form.pack(fill="x", pady=5)
        
        # Linha 1 - Data
        frame_data = ctk.CTkFrame(frame_form)
        frame_data.pack(fill="x", pady=2)
        
        ctk.CTkLabel(frame_data, text="Data:", width=40).pack(side="left")
        self.entry_data = ctk.CTkEntry(frame_data, placeholder_text="DD/MM/AAAA", width=100)
        self.entry_data.pack(side="left", padx=5)
        
        btn_hoje = ctk.CTkButton(frame_data, text="Hoje", width=50, command=self._data_hoje)
        btn_hoje.pack(side="left", padx=2)
        
        # Linha 2 - Justificativa
        frame_just = ctk.CTkFrame(frame_form)
        frame_just.pack(fill="x", pady=2)
        
        ctk.CTkLabel(frame_just, text="Justificativa:", width=80).pack(side="left")
        self.combo_just = ctk.CTkComboBox(frame_just, values=self.justificativas, width=150)
        self.combo_just.set("AM")
        self.combo_just.pack(side="left", padx=5)
        
        # Botões principais
        frame_botoes = ctk.CTkFrame(frame_form)
        frame_botoes.pack(fill="x", pady=10)
        
        ctk.CTkButton(frame_botoes, text="SALVAR FALTA", command=self._salvar_falta,
                     fg_color="#27ae60", width=120, height=35).pack(side="left", padx=5)
        ctk.CTkButton(frame_botoes, text="LIMPAR", command=self._limpar,
                     fg_color="#7f8c8d", width=80, height=35).pack(side="left", padx=5)
        ctk.CTkButton(frame_botoes, text="NOVA JUSTIF.", command=self._nova_justificativa,
                     fg_color="#3498db", width=100, height=35).pack(side="left", padx=5)
        
        # === LISTA DE FALTAS ===
        frame_faltas = ctk.CTkFrame(main_frame)
        frame_faltas.pack(fill="both", expand=True, pady=5)
        
        ctk.CTkLabel(frame_faltas, text="FALTAS REGISTRADAS:", 
                    font=("Arial", 11, "bold")).pack(anchor="w")
        
        # Tabela de faltas
        self.tree_faltas = ttk.Treeview(frame_faltas, columns=("data", "justificativa", "detalhes"), 
                                       show="headings", height=8)
        self.tree_faltas.heading("data", text="Data")
        self.tree_faltas.heading("justificativa", text="Justificativa")
        self.tree_faltas.heading("detalhes", text="Detalhes")
        
        self.tree_faltas.column("data", width=80, anchor="center")
        self.tree_faltas.column("justificativa", width=100, anchor="center")
        self.tree_faltas.column("detalhes", width=150, anchor="center")
        
        scroll_faltas = ttk.Scrollbar(frame_faltas, command=self.tree_faltas.yview)
        self.tree_faltas.configure(yscrollcommand=scroll_faltas.set)
        
        self.tree_faltas.pack(side="left", fill="both", expand=True)
        scroll_faltas.pack(side="right", fill="y")
        
        # Botão excluir
        ctk.CTkButton(frame_faltas, text="EXCLUIR FALTA SELECIONADA", 
                     command=self._excluir_falta, fg_color="#e74c3c", width=180, height=30).pack(pady=5)
        
        # Inicializar
        self._atualizar_lista_funcionarios()
        self.janela.protocol("WM_DELETE_WINDOW", self._fechar)

    def _atualizar_lista_funcionarios(self, filtro=""):
        """Atualiza lista de funcionários"""
        self.lista_funcionarios.delete(0, "end")
        for func_id, nome in self.funcionarios:
            if not filtro or filtro.lower() in nome.lower():
                self.lista_funcionarios.insert("end", nome)

    def _filtrar_funcionarios(self, event=None):
        """Filtra funcionários em tempo real"""
        self._atualizar_lista_funcionarios(self.entry_pesquisa.get())

    def _selecionar_funcionario(self, event):
        """Seleciona funcionário"""
        selection = self.lista_funcionarios.curselection()
        if selection:
            nome = self.lista_funcionarios.get(selection[0])
            for func_id, func_nome in self.funcionarios:
                if func_nome == nome:
                    self.funcionario_selecionado = {"id": func_id, "nome": nome}
                    self._carregar_faltas()
                    break

    def _carregar_faltas(self):
        """Carrega faltas do funcionário"""
        if not self.funcionario_selecionado:
            return
            
        self.tree_faltas.delete(*self.tree_faltas.get_children())
            
        try:
            # Tenta carregar com a coluna detalhes
            self.cursor.execute(
                "SELECT data, justificativa, detalhes FROM frequencia WHERE funcionario_id = ? ORDER BY data DESC",
                (self.funcionario_selecionado["id"],)
            )
            
            for data, just, detalhes in self.cursor.fetchall():
                detalhes_str = detalhes if detalhes else ""
                self.tree_faltas.insert("", "end", values=(data, just, detalhes_str))
                
        except Exception as e:
            # Fallback para versão sem coluna detalhes
            try:
                self.cursor.execute(
                    "SELECT data, justificativa FROM frequencia WHERE funcionario_id = ? ORDER BY data DESC",
                    (self.funcionario_selecionado["id"],)
                )
                
                for data, just in self.cursor.fetchall():
                    self.tree_faltas.insert("", "end", values=(data, just, ""))
            except Exception as e2:
                print(f"Erro ao carregar faltas (fallback): {e2}")

    def _perguntar_horas_fh(self):
        """Pergunta quantas horas descontar para FH"""
        dialog = ctk.CTkInputDialog(
            text="Quantas horas de falta?\n\nExemplos:\n• 2h (2 horas)\n• 1h30min (1 hora e 30 minutos)\n• 45min (45 minutos)",
            title="Horas de Falta - FH"
        )
        
        horas_texto = dialog.get_input()
        
        if horas_texto and horas_texto.strip():
            horas_texto = horas_texto.strip()
            
            # Validar formato
            if not re.match(r'^(\d+h(\d+min)?|\d+min)$', horas_texto):
                messagebox.showwarning("Formato inválido", 
                    "Use um destes formatos:\n• 2h (2 horas)\n• 1h30min (1h30min)\n• 45min (45 minutos)")
                return None
                
            return horas_texto
        return None

    def _perguntar_periodo_licenca(self, data_inicio):
        """Pergunta até que dia vai a licença"""
        try:
            # Converter data de início
            data_obj = datetime.strptime(data_inicio, "%d/%m/%Y")
            data_sugerida = data_obj + timedelta(days=4)  # Sugere 5 dias no total
            
            dialog = ctk.CTkInputDialog(
                text=f"Licença começando em {data_inicio}\n\nAté que dia vai a licença? (DD/MM/AAAA)\n\nSugestão: {data_sugerida.strftime('%d/%m/%Y')}",
                title="Período da Licença"
            )
            
            data_fim = dialog.get_input()
            
            if data_fim and data_fim.strip():
                data_fim = data_fim.strip()
                
                # Validar data
                if not re.match(r'^\d{2}/\d{2}/\d{4}$', data_fim):
                    messagebox.showwarning("Data inválida", "Data deve estar no formato DD/MM/AAAA")
                    return None
                    
                # Verificar se data fim é depois da data início
                data_fim_obj = datetime.strptime(data_fim, "%d/%m/%Y")
                if data_fim_obj < data_obj:
                    messagebox.showwarning("Data inválida", "Data de término deve ser após a data de início")
                    return None
                    
                return data_fim
                
        except ValueError:
            messagebox.showwarning("Data inválida", "Data em formato incorreto")
            
        return None

    def _data_hoje(self):
        """Preenche com data atual"""
        self.entry_data.delete(0, "end")
        self.entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))

    def _nova_justificativa(self):
        """Adiciona nova justificativa"""
        nova = simpledialog.askstring("Nova Justificativa", "Digite a nova justificativa:")
        if nova and nova.strip():
            nova = nova.strip()
            if nova not in self.justificativas:
                self.justificativas.append(nova)
                self.combo_just.configure(values=self.justificativas)
                self.combo_just.set(nova)
                messagebox.showinfo("Sucesso", "Justificativa adicionada!")

    def _validar_dados_basicos(self):
        """Validação básica dos dados"""
        if not self.funcionario_selecionado:
            return False, "Selecione um funcionário!"
            
        data = self.entry_data.get().strip()
        if not data:
            return False, "Informe a data!"
            
        if not re.match(r'^\d{2}/\d{2}/\d{4}$', data):
            return False, "Data deve ser DD/MM/AAAA!"
            
        justificativa = self.combo_just.get()
        if not justificativa:
            return False, "Selecione uma justificativa!"
            
        return True, data, justificativa

    def _salvar_falta(self):
        """Salva falta com lógica inteligente"""
        # Validação básica
        resultado = self._validar_dados_basicos()
        if not resultado[0]:
            messagebox.showwarning("Aviso", resultado[1])
            return
            
        valido, data, justificativa = resultado
        
        try:
            detalhes = None
            
            # Lógica para FH - Perguntar horas
            if justificativa == "FH":
                horas_texto = self._perguntar_horas_fh()
                if not horas_texto:
                    return  # Usuário cancelou
                detalhes = horas_texto
                
            # Lógica para Licença-Prêmio - Perguntar período
            elif justificativa == "Licença-Prêmio":
                data_fim = self._perguntar_periodo_licenca(data)
                if not data_fim:
                    return  # Usuário cancelou
                
                # Para Licença-Prêmio: salva apenas 1 linha com o período completo
                detalhes = f"{data} a {data_fim}"
                
            # Salvar falta
            if not self._salvar_falta_unica(data, justificativa, detalhes):
                return
                    
            messagebox.showinfo("Sucesso", "Falta registrada!")
            self._carregar_faltas()
            self._limpar()
            
            if self.atualizar_lista:
                self.root.after(50, self.atualizar_lista)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")

    def _salvar_falta_unica(self, data, justificativa, detalhes=None):
        """Salva uma única falta no banco"""
        try:
            # Verificar duplicata
            self.cursor.execute(
                "SELECT id FROM frequencia WHERE funcionario_id = ? AND data = ?",
                (self.funcionario_selecionado["id"], data)
            )
            
            if self.cursor.fetchone():
                messagebox.showwarning("Aviso", f"Já existe falta para {data}!")
                return False
                
            # Inserir
            self.cursor.execute(
                "INSERT INTO frequencia (funcionario_id, data, justificativa, detalhes) VALUES (?, ?, ?, ?)",
                (self.funcionario_selecionado["id"], data, justificativa, detalhes)
            )
            self.conn.commit()
            return True
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar falta: {e}")
            return False

    def _excluir_falta(self):
        """Exclui falta selecionada"""
        if not self.funcionario_selecionado:
            messagebox.showwarning("Aviso", "Selecione um funcionário!")
            return
            
        selection = self.tree_faltas.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma falta!")
            return
            
        item = self.tree_faltas.item(selection[0])
        data = item["values"][0]
        justificativa = item["values"][1]
        
        if messagebox.askyesno("Confirmar", f"Excluir {justificativa} de {data}?"):
            try:
                self.cursor.execute(
                    "DELETE FROM frequencia WHERE funcionario_id = ? AND data = ?",
                    (self.funcionario_selecionado["id"], data)
                )
                self.conn.commit()
                self._carregar_faltas()
                if self.atualizar_lista:
                    self.root.after(50, self.atualizar_lista)
                messagebox.showinfo("Sucesso", "Falta excluída!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir: {e}")

    def _limpar(self):
        """Limpa formulário"""
        self.entry_data.delete(0, "end")
        self.combo_just.set("AM")

    def _fechar(self):
        """Fecha janela"""
        try:
            if self.conn:
                self.conn.close()
            if self.janela:
                self.janela.destroy()
        except:
            pass


def abrir_tela_frequencia(root, atualizar_lista=None):
    """Função principal"""
    app = GerenciadorFrequencia(root, atualizar_lista)
    app.abrir_tela()