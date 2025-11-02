# views/lancar_aulas_eventuais.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from tkinter import ttk, messagebox
from database.db import conectar
from datetime import datetime, timedelta

class GerenciadorAulasEventuais:
    def __init__(self, root, professor_id, professor_nome):
        self.root = root
        self.professor_id = professor_id
        self.professor_nome = professor_nome
        self.janela = None
        self.mes_filtro = datetime.now().month
        self.ano_filtro = datetime.now().year
        
    def abrir_tela(self):
        """Abre a tela de lançamento de aulas"""
        self.janela = ctk.CTkToplevel(self.root)
        self.janela.title(f"Aulas Eventuais - {self.professor_nome}")
        self.janela.geometry("1100x750")
        self.janela.transient(self.root)
        self.janela.grab_set()
        
        self._criar_interface()
        self._carregar_aulas()
        
    def _criar_interface(self):
        """Cria a interface otimizada"""
        main_frame = ctk.CTkFrame(self.janela)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Título
        ctk.CTkLabel(main_frame, text=f"📚 LANÇAMENTO DE AULAS - {self.professor_nome.upper()}", 
                     font=("Arial", 16, "bold")).pack(pady=10)
        
        # Filtro por mês/ano
        frame_filtro = ctk.CTkFrame(main_frame)
        frame_filtro.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(frame_filtro, text="📅 FILTRAR POR MÊS/ANO:", 
                    font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
        
        frame_filtro_campos = ctk.CTkFrame(frame_filtro)
        frame_filtro_campos.pack(fill="x", pady=5)
        
        # Mês
        ctk.CTkLabel(frame_filtro_campos, text="Mês:", width=50).pack(side="left", padx=5)
        self.combo_mes = ctk.CTkComboBox(frame_filtro_campos, 
                                       values=["01", "02", "03", "04", "05", "06", 
                                              "07", "08", "09", "10", "11", "12"],
                                       width=80, height=35)
        self.combo_mes.set(f"{self.mes_filtro:02d}")
        self.combo_mes.pack(side="left", padx=5)
        
        # Ano
        ctk.CTkLabel(frame_filtro_campos, text="Ano:", width=50).pack(side="left", padx=5)
        anos = [str(year) for year in range(2020, 2031)]
        self.combo_ano = ctk.CTkComboBox(frame_filtro_campos, values=anos, width=80, height=35)
        self.combo_ano.set(str(self.ano_filtro))
        self.combo_ano.pack(side="left", padx=5)
        
        # Botão aplicar filtro
        ctk.CTkButton(frame_filtro_campos, text="🔍 APLICAR FILTRO", 
                     command=self._aplicar_filtro, width=120, height=35).pack(side="left", padx=10)
        
        # Botão mês atual
        ctk.CTkButton(frame_filtro_campos, text="📅 MÊS ATUAL", 
                     command=self._mes_atual, width=100, height=35).pack(side="left", padx=5)
        
        # Container com duas colunas
        container_principal = ctk.CTkFrame(main_frame)
        container_principal.pack(fill="both", expand=True, pady=10)
        
        # ========== COLUNA ESQUERDA - FORMULÁRIO ==========
        coluna_esquerda = ctk.CTkFrame(container_principal)
        coluna_esquerda.pack(side="left", fill="both", padx=(0, 10))
        
        frame_form = ctk.CTkFrame(coluna_esquerda)
        frame_form.pack(fill="both", pady=10, padx=10)
        
        ctk.CTkLabel(frame_form, text="➕ NOVA AULA", 
                    font=("Arial", 14, "bold")).pack(anchor="w", pady=10)
        
        # Formulário
        form_grid = ctk.CTkFrame(frame_form)
        form_grid.pack(fill="x", pady=10)
        
        # Professor Substituído
        ctk.CTkLabel(form_grid, text="Professor Substituído:", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=8)
        self.entry_prof_substituido = ctk.CTkEntry(form_grid, width=250, placeholder_text="Nome do professor titular", height=35)
        self.entry_prof_substituido.grid(row=0, column=1, sticky="we", padx=5, pady=8)
        
        # Data
        ctk.CTkLabel(form_grid, text="Data da Aula:", font=("Arial", 11, "bold")).grid(row=1, column=0, sticky="w", padx=5, pady=8)
        frame_data = ctk.CTkFrame(form_grid)
        frame_data.grid(row=1, column=1, sticky="we", padx=5, pady=8)
        
        self.entry_data = ctk.CTkEntry(frame_data, width=120, placeholder_text="DD/MM/AAAA", height=35)
        self.entry_data.pack(side="left")
        
        ctk.CTkButton(frame_data, text="Hoje", width=60, height=35,
                     command=self._preencher_data_hoje).pack(side="left", padx=5)
        
        # Turmas
        ctk.CTkLabel(form_grid, text="Turmas:", font=("Arial", 11, "bold")).grid(row=2, column=0, sticky="w", padx=5, pady=8)
        self.entry_turmas = ctk.CTkEntry(form_grid, width=250, 
                                       placeholder_text="Ex: 1A 2B 3A 4C 5B, Pré I A, Pré II B", height=35)
        self.entry_turmas.grid(row=2, column=1, sticky="we", padx=5, pady=8)
        
        # Quantidade de Aulas
        ctk.CTkLabel(form_grid, text="Qtd. de Aulas:", font=("Arial", 11, "bold")).grid(row=3, column=0, sticky="w", padx=5, pady=8)
        self.entry_qtd_aulas = ctk.CTkEntry(form_grid, width=100, placeholder_text="Ex: 5", height=35)
        self.entry_qtd_aulas.grid(row=3, column=1, sticky="w", padx=5, pady=8)
        
        # Observações
        ctk.CTkLabel(form_grid, text="Observações:", font=("Arial", 11, "bold")).grid(row=4, column=0, sticky="w", padx=5, pady=8)
        self.entry_observacoes = ctk.CTkEntry(form_grid, width=250, placeholder_text="Observações adicionais...", height=35)
        self.entry_observacoes.grid(row=4, column=1, sticky="we", padx=5, pady=8)
        
        form_grid.columnconfigure(1, weight=1)
        
        # Botões do formulário
        frame_botoes_form = ctk.CTkFrame(frame_form)
        frame_botoes_form.pack(fill="x", pady=15)
        
        ctk.CTkButton(frame_botoes_form, text="✅ LANÇAR AULA", command=self._lancar_aula,
                     fg_color="#27ae60", hover_color="#219955", width=140, height=38,
                     font=("Arial", 12, "bold")).pack(side="left", padx=5)
        
        ctk.CTkButton(frame_botoes_form, text="🔄 LIMPAR", command=self._limpar_formulario,
                     fg_color="#95a5a6", hover_color="#7f8c8d", width=100, height=38,
                     font=("Arial", 12)).pack(side="left", padx=5)
        
        # ========== COLUNA DIREITA - LISTA ==========
        coluna_direita = ctk.CTkFrame(container_principal)
        coluna_direita.pack(side="right", fill="both", expand=True)
        
        # Cabeçalho da lista
        frame_cabecalho = ctk.CTkFrame(coluna_direita)
        frame_cabecalho.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(frame_cabecalho, text="📋 AULAS LANÇADAS", 
                    font=("Arial", 14, "bold")).pack(side="left", pady=10)
        
        # Resumo
        self.label_resumo = ctk.CTkLabel(frame_cabecalho, text="Total: 0 aulas", 
                                       font=("Arial", 12, "bold"), text_color="#2ecc71")
        self.label_resumo.pack(side="right", padx=10)
        
        # Lista de aulas
        frame_lista = ctk.CTkFrame(coluna_direita)
        frame_lista.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Treeview
        self.tree_aulas = ttk.Treeview(frame_lista, 
                                     columns=("id", "prof_substituido", "data", "turmas", "aulas", "observacoes", "registro"),
                                     show="headings", height=18)
        
        self.tree_aulas.heading("id", text="ID")
        self.tree_aulas.heading("prof_substituido", text="Professor Substituído")
        self.tree_aulas.heading("data", text="Data")
        self.tree_aulas.heading("turmas", text="Turmas")
        self.tree_aulas.heading("aulas", text="Aulas")
        self.tree_aulas.heading("observacoes", text="Observações")
        self.tree_aulas.heading("registro", text="Registro")
        
        self.tree_aulas.column("id", width=50, anchor="center")
        self.tree_aulas.column("prof_substituido", width=180)
        self.tree_aulas.column("data", width=100, anchor="center")
        self.tree_aulas.column("turmas", width=200)
        self.tree_aulas.column("aulas", width=80, anchor="center")
        self.tree_aulas.column("observacoes", width=150)
        self.tree_aulas.column("registro", width=100, anchor="center")
        
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree_aulas.yview)
        self.tree_aulas.configure(yscrollcommand=scrollbar.set)
        
        self.tree_aulas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botões de ação
        frame_botoes_acao = ctk.CTkFrame(coluna_direita)
        frame_botoes_acao.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(frame_botoes_acao, text="✏️ EDITAR AULA", command=self._editar_aula,
                     fg_color="#f39c12", hover_color="#d68910", width=120, height=38,
                     font=("Arial", 12)).pack(side="left", padx=3)
        
        ctk.CTkButton(frame_botoes_acao, text="❌ EXCLUIR AULA", command=self._excluir_aula,
                     fg_color="#e74c3c", hover_color="#c0392b", width=120, height=38,
                     font=("Arial", 12)).pack(side="left", padx=3)
        
        ctk.CTkButton(frame_botoes_acao, text="📊 GERAR FOLHA", command=self._gerar_folha_pagamento,
                     fg_color="#3498db", hover_color="#2980b9", width=120, height=38,
                     font=("Arial", 12)).pack(side="left", padx=3)
        
        # Eventos
        self.tree_aulas.bind("<Double-1>", lambda e: self._editar_aula())
        self.combo_mes.bind("<<ComboboxSelected>>", lambda e: self._aplicar_filtro())
        self.combo_ano.bind("<<ComboboxSelected>>", lambda e: self._aplicar_filtro())
        
    def _aplicar_filtro(self):
        """Aplica o filtro por mês/ano"""
        try:
            self.mes_filtro = int(self.combo_mes.get())
            self.ano_filtro = int(self.combo_ano.get())
            self._carregar_aulas()
        except ValueError:
            messagebox.showerror("Erro", "Mês ou ano inválido!")
            
    def _mes_atual(self):
        """Define o filtro para o mês atual"""
        hoje = datetime.now()
        self.combo_mes.set(f"{hoje.month:02d}")
        self.combo_ano.set(str(hoje.year))
        self._aplicar_filtro()
        
    def _preencher_data_hoje(self):
        """Preenche com a data atual"""
        self.entry_data.delete(0, "end")
        self.entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
    def _carregar_aulas(self):
        """Carrega a lista de aulas do professor filtrada por mês/ano"""
        for item in self.tree_aulas.get_children():
            self.tree_aulas.delete(item)
            
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, professor_substituido, data_aula, turmas, quantidade_aulas, observacoes, data_registro
            FROM aulas_eventuais 
            WHERE professor_eventual_id = ? 
            AND substr(data_aula, 4, 2) = ? AND substr(data_aula, 7, 4) = ?
            ORDER BY data_aula DESC
        ''', (self.professor_id, f"{self.mes_filtro:02d}", str(self.ano_filtro)))
        
        total_aulas = 0
        for aula in cursor.fetchall():
            self.tree_aulas.insert("", "end", values=aula)
            total_aulas += aula[4]  # quantidade_aulas
            
        conn.close()
        
        # Atualizar resumo
        mes_nome = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                   "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"][self.mes_filtro - 1]
        self.label_resumo.configure(text=f"Total {mes_nome}: {total_aulas} aulas")
        
    def _validar_data(self, data):
        """Valida o formato da data"""
        try:
            datetime.strptime(data, "%d/%m/%Y")
            return True
        except ValueError:
            return False
            
    def _lancar_aula(self):
        """Lança uma nova aula"""
        prof_substituido = self.entry_prof_substituido.get().strip().upper()  # Maiúsculas
        data = self.entry_data.get().strip()
        turmas = self.entry_turmas.get().strip().upper()  # Maiúsculas
        qtd_aulas = self.entry_qtd_aulas.get().strip()
        observacoes = self.entry_observacoes.get().strip()
        
        # Validações
        if not prof_substituido:
            messagebox.showwarning("Aviso", "Informe o professor substituído!")
            return
            
        if not data or not self._validar_data(data):
            messagebox.showwarning("Aviso", "Data inválida! Use DD/MM/AAAA")
            return
            
        if not turmas:
            messagebox.showwarning("Aviso", "Informe as turmas!")
            return
            
        if not qtd_aulas or not qtd_aulas.isdigit():
            messagebox.showwarning("Aviso", "Informe a quantidade de aulas!")
            return
            
        try:
            conn = conectar()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO aulas_eventuais 
                (professor_eventual_id, professor_substituido, data_aula, turmas, quantidade_aulas, observacoes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.professor_id, prof_substituido, data, turmas, int(qtd_aulas), observacoes or None))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Sucesso", "Aula lançada com sucesso!")
            self._limpar_formulario()
            self._carregar_aulas()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao lançar aula:\n{e}")
            
    def _limpar_formulario(self):
        """Limpa o formulário"""
        self.entry_prof_substituido.delete(0, "end")
        self.entry_data.delete(0, "end")
        self.entry_turmas.delete(0, "end")
        self.entry_qtd_aulas.delete(0, "end")
        self.entry_observacoes.delete(0, "end")
        
    def _editar_aula(self):
        """Edita aula selecionada"""
        selection = self.tree_aulas.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma aula para editar!")
            return
            
        messagebox.showinfo("Edição", "Funcionalidade de edição em desenvolvimento!")
        
    def _excluir_aula(self):
        """Exclui aula selecionada"""
        selection = self.tree_aulas.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma aula para excluir!")
            return
            
        aula_id = self.tree_aulas.item(selection[0])["values"][0]
        prof_substituido = self.tree_aulas.item(selection[0])["values"][1]
        data = self.tree_aulas.item(selection[0])["values"][2]
        
        if messagebox.askyesno("Confirmar", f"Excluir aula de {data} - {prof_substituido}?"):
            try:
                conn = conectar()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM aulas_eventuais WHERE id = ?", (aula_id,))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Sucesso", "Aula excluída com sucesso!")
                self._carregar_aulas()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir aula:\n{e}")
                
    def _gerar_folha_pagamento(self):
        """Gera folha de pagamento do mês"""
        from views.folha_pagamento_eventuais import FolhaPagamentoEventuais
        folha = FolhaPagamentoEventuais(self.root, self.mes_filtro, self.ano_filtro)
        folha.abrir_tela()