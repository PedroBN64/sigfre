# views/professores_eventuais.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from tkinter import ttk, messagebox
from database.db import conectar
import re
from datetime import datetime

class GerenciadorProfessoresEventuais:
    def __init__(self, root):
        self.root = root
        self.janela = None
        self.professor_selecionado = None
        self.modo_edicao = False
        
    def abrir_tela(self):
        """Abre a tela de gerenciamento de professores eventuais"""
        self.janela = ctk.CTkToplevel(self.root)
        self.janela.title("Professores Eventuais - Cadastro")
        self.janela.geometry("1200x700")
        self.janela.transient(self.root)
        self.janela.grab_set()
        
        self._criar_interface()
        self._carregar_professores()
        
    def _criar_interface(self):
        """Cria a interface otimizada"""
        # Container principal com duas colunas
        main_container = ctk.CTkFrame(self.janela)
        main_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Título
        ctk.CTkLabel(main_container, text="GESTÃO DE PROFESSORES EVENTUAIS", 
                     font=("Arial", 18, "bold")).pack(pady=15)
        
        # Frame com duas colunas
        frame_duas_colunas = ctk.CTkFrame(main_container)
        frame_duas_colunas.pack(fill="both", expand=True, pady=10)
        
        # ========== COLUNA ESQUERDA - FORMULÁRIO ==========
        coluna_esquerda = ctk.CTkFrame(frame_duas_colunas)
        coluna_esquerda.pack(side="left", fill="both", padx=(0, 10))
        
        # Formulário de cadastro
        frame_form = ctk.CTkFrame(coluna_esquerda)
        frame_form.pack(fill="x", pady=10, padx=10)
        
        self.label_titulo_form = ctk.CTkLabel(frame_form, text="📝 CADASTRAR PROFESSOR", 
                    font=("Arial", 14, "bold"))
        self.label_titulo_form.pack(anchor="w", pady=10)
        
        # Grid do formulário
        form_grid = ctk.CTkFrame(frame_form)
        form_grid.pack(fill="x", pady=10)
        
        # Nome
        ctk.CTkLabel(form_grid, text="Nome Completo:", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=8)
        self.entry_nome = ctk.CTkEntry(form_grid, width=280, placeholder_text="Digite o nome completo...", height=35)
        self.entry_nome.grid(row=0, column=1, sticky="we", padx=5, pady=8)
        
        # CPF
        ctk.CTkLabel(form_grid, text="CPF:", font=("Arial", 11, "bold")).grid(row=1, column=0, sticky="w", padx=5, pady=8)
        self.entry_cpf = ctk.CTkEntry(form_grid, width=150, placeholder_text="000.000.000-00", height=35)
        self.entry_cpf.grid(row=1, column=1, sticky="w", padx=5, pady=8)
        
        # Telefone
        ctk.CTkLabel(form_grid, text="Telefone:", font=("Arial", 11, "bold")).grid(row=2, column=0, sticky="w", padx=5, pady=8)
        self.entry_telefone = ctk.CTkEntry(form_grid, width=150, placeholder_text="(00) 00000-0000", height=35)
        self.entry_telefone.grid(row=2, column=1, sticky="w", padx=5, pady=8)
        
        # Email
        ctk.CTkLabel(form_grid, text="Email:", font=("Arial", 11, "bold")).grid(row=3, column=0, sticky="w", padx=5, pady=8)
        self.entry_email = ctk.CTkEntry(form_grid, width=280, placeholder_text="email@exemplo.com", height=35)
        self.entry_email.grid(row=3, column=1, sticky="we", padx=5, pady=8)
        
        # Configurar grid para expansão
        form_grid.columnconfigure(1, weight=1)
        
        # Botões do formulário
        frame_botoes_form = ctk.CTkFrame(frame_form)
        frame_botoes_form.pack(fill="x", pady=15)
        
        self.btn_cadastrar = ctk.CTkButton(frame_botoes_form, text="✅ CADASTRAR", command=self._cadastrar_professor,
                     fg_color="#27ae60", hover_color="#219955", width=140, height=38,
                     font=("Arial", 12, "bold"))
        self.btn_cadastrar.pack(side="left", padx=5)
        
        self.btn_limpar = ctk.CTkButton(frame_botoes_form, text="🔄 LIMPAR", command=self._limpar_formulario,
                     fg_color="#95a5a6", hover_color="#7f8c8d", width=100, height=38,
                     font=("Arial", 12))
        self.btn_limpar.pack(side="left", padx=5)
        
        self.btn_cancelar_edicao = ctk.CTkButton(frame_botoes_form, text="❌ CANCELAR", command=self._cancelar_edicao,
                     fg_color="#e74c3c", hover_color="#c0392b", width=100, height=38,
                     font=("Arial", 12))
        self.btn_cancelar_edicao.pack(side="left", padx=5)
        self.btn_cancelar_edicao.pack_forget()  # Escondido inicialmente
        
        # ========== COLUNA DIREITA - LISTA ==========
        coluna_direita = ctk.CTkFrame(frame_duas_colunas)
        coluna_direita.pack(side="right", fill="both", expand=True)
        
        # Cabeçalho da lista
        frame_cabecalho_lista = ctk.CTkFrame(coluna_direita)
        frame_cabecalho_lista.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(frame_cabecalho_lista, text="📋 PROFESSORES CADASTRADOS", 
                    font=("Arial", 14, "bold")).pack(side="left", pady=10)
        
        # Botão atualizar
        ctk.CTkButton(frame_cabecalho_lista, text="🔄 Atualizar", command=self._carregar_professores,
                     width=100, height=30).pack(side="right", padx=5)
        
        # Lista de professores
        frame_lista = ctk.CTkFrame(coluna_direita)
        frame_lista.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Treeview
        self.tree_professores = ttk.Treeview(frame_lista, columns=("id", "nome", "cpf", "telefone", "email", "ativo", "cadastro"), 
                                           show="headings", height=15)
        
        self.tree_professores.heading("id", text="ID")
        self.tree_professores.heading("nome", text="Nome")
        self.tree_professores.heading("cpf", text="CPF")
        self.tree_professores.heading("telefone", text="Telefone")
        self.tree_professores.heading("email", text="Email")
        self.tree_professores.heading("ativo", text="Ativo")
        self.tree_professores.heading("cadastro", text="Cadastro")
        
        self.tree_professores.column("id", width=50, anchor="center")
        self.tree_professores.column("nome", width=200)
        self.tree_professores.column("cpf", width=120, anchor="center")
        self.tree_professores.column("telefone", width=120, anchor="center")
        self.tree_professores.column("email", width=180)
        self.tree_professores.column("ativo", width=60, anchor="center")
        self.tree_professores.column("cadastro", width=100, anchor="center")
        
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree_professores.yview)
        self.tree_professores.configure(yscrollcommand=scrollbar.set)
        
        self.tree_professores.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botões de ação
        frame_botoes_acao = ctk.CTkFrame(coluna_direita)
        frame_botoes_acao.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(frame_botoes_acao, text="📚 LANÇAR AULAS", command=self._lancar_aulas,
                     fg_color="#3498db", hover_color="#2980b9", width=140, height=38,
                     font=("Arial", 12, "bold")).pack(side="left", padx=3)
        
        ctk.CTkButton(frame_botoes_acao, text="✏️ EDITAR", command=self._editar_professor,
                     fg_color="#f39c12", hover_color="#d68910", width=100, height=38,
                     font=("Arial", 12)).pack(side="left", padx=3)
        
        ctk.CTkButton(frame_botoes_acao, text="👁️ VISUALIZAR", command=self._visualizar_professor,
                     fg_color="#9b59b6", hover_color="#8e44ad", width=100, height=38,
                     font=("Arial", 12)).pack(side="left", padx=3)
        
        ctk.CTkButton(frame_botoes_acao, text="✅/❌ ATIVAR", command=self._toggle_ativo,
                     fg_color="#e74c3c", hover_color="#c0392b", width=100, height=38,
                     font=("Arial", 12)).pack(side="left", padx=3)
        
        ctk.CTkButton(frame_botoes_acao, text="🗑️ EXCLUIR", command=self._excluir_professor,
                     fg_color="#c0392b", hover_color="#a93226", width=100, height=38,
                     font=("Arial", 12)).pack(side="left", padx=3)
        
        ctk.CTkButton(frame_botoes_acao, text="📊 RELATÓRIO", command=self._gerar_relatorio,
                     fg_color="#27ae60", hover_color="#219955", width=100, height=38,
                     font=("Arial", 12)).pack(side="left", padx=3)
        
        # Configurar eventos
        self.tree_professores.bind("<<TreeviewSelect>>", self._on_selecionar_professor)
        self.tree_professores.bind("<Double-1>", lambda e: self._visualizar_professor())
        
    def _on_selecionar_professor(self, event):
        """Quando um professor é selecionado na lista"""
        selection = self.tree_professores.selection()
        if selection:
            self.professor_selecionado = {
                "id": self.tree_professores.item(selection[0])["values"][0],
                "nome": self.tree_professores.item(selection[0])["values"][1],
                "cpf": self.tree_professores.item(selection[0])["values"][2],
                "telefone": self.tree_professores.item(selection[0])["values"][3],
                "email": self.tree_professores.item(selection[0])["values"][4]
            }
        
    def _carregar_professores(self):
        """Carrega a lista de professores eventuais"""
        for item in self.tree_professores.get_children():
            self.tree_professores.delete(item)
            
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, cpf, telefone, email, ativo, data_cadastro FROM professores_eventuais ORDER BY nome")
        
        for professor in cursor.fetchall():
            ativo_texto = "✅" if professor[5] else "❌"
            data_cadastro = professor[6] if professor[6] else "-"
            self.tree_professores.insert("", "end", values=professor[:5] + (ativo_texto, data_cadastro))
            
        conn.close()
        
    def _validar_cpf(self, cpf):
        """Valida o formato do CPF"""
        cpf = re.sub(r'[^\d]', '', cpf)
        return len(cpf) == 11
        
    def _cadastrar_professor(self):
        """Cadastra um novo professor eventual"""
        nome = self.entry_nome.get().strip().upper()  # Converter para maiúsculas
        cpf = self.entry_cpf.get().strip()
        telefone = self.entry_telefone.get().strip()
        email = self.entry_email.get().strip()
        
        if not nome:
            messagebox.showwarning("Aviso", "Informe o nome do professor!")
            return
            
        if cpf and not self._validar_cpf(cpf):
            messagebox.showwarning("Aviso", "CPF inválido!")
            return
        
        # CPF e email são opcionais, telefone desejável mas não obrigatório
        try:
            conn = conectar()
            cursor = conn.cursor()
            
            # Verificar se CPF já existe (apenas se foi informado)
            if cpf:
                cursor.execute("SELECT id FROM professores_eventuais WHERE cpf = ? AND id != ?", 
                             (cpf, self.professor_selecionado["id"] if self.modo_edicao else 0))
                if cursor.fetchone():
                    messagebox.showwarning("Aviso", "CPF já cadastrado!")
                    conn.close()
                    return
            
            if self.modo_edicao and self.professor_selecionado:
                # MODO EDIÇÃO - Atualizar professor existente
                cursor.execute('''
                    UPDATE professores_eventuais 
                    SET nome = ?, cpf = ?, telefone = ?, email = ?
                    WHERE id = ?
                ''', (nome, cpf or None, telefone or None, email or None, self.professor_selecionado["id"]))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Sucesso", "Professor atualizado com sucesso!")
                self._cancelar_edicao()
                
            else:
                # MODO CADASTRO - Inserir novo professor
                cursor.execute('''
                    INSERT INTO professores_eventuais (nome, cpf, telefone, email)
                    VALUES (?, ?, ?, ?)
                ''', (nome, cpf or None, telefone or None, email or None))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Sucesso", "Professor cadastrado com sucesso!")
                self._limpar_formulario()
            
            self._carregar_professores()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar professor:\n{e}")
            
    def _limpar_formulario(self):
        """Limpa o formulário"""
        self.entry_nome.delete(0, "end")
        self.entry_cpf.delete(0, "end")
        self.entry_telefone.delete(0, "end")
        self.entry_email.delete(0, "end")
        self.professor_selecionado = None
        
    def _preencher_formulario(self, dados):
        """Preenche o formulário com dados para edição"""
        self.entry_nome.delete(0, "end")
        self.entry_nome.insert(0, dados["nome"])
        self.entry_cpf.delete(0, "end")
        self.entry_cpf.insert(0, dados["cpf"] or "")
        self.entry_telefone.delete(0, "end")
        self.entry_telefone.insert(0, dados["telefone"] or "")
        self.entry_email.delete(0, "end")
        self.entry_email.insert(0, dados["email"] or "")
        
    def _entrar_modo_edicao(self):
        """Ativa o modo de edição"""
        self.modo_edicao = True
        self.label_titulo_form.configure(text="✏️ EDITAR PROFESSOR")
        self.btn_cadastrar.configure(text="💾 SALVAR EDIÇÃO")
        self.btn_cancelar_edicao.pack(side="left", padx=5)
        
    def _cancelar_edicao(self):
        """Cancela o modo de edição"""
        self.modo_edicao = False
        self.label_titulo_form.configure(text="📝 CADASTRAR PROFESSOR")
        self.btn_cadastrar.configure(text="✅ CADASTRAR")
        self.btn_cancelar_edicao.pack_forget()
        self._limpar_formulario()
        
    def _lancar_aulas(self):
        """Abre a tela para lançar aulas"""
        if not self.professor_selecionado:
            messagebox.showwarning("Aviso", "Selecione um professor primeiro!")
            return
            
        from views.lancar_aulas_eventuais import GerenciadorAulasEventuais
        gerenciador_aulas = GerenciadorAulasEventuais(self.root, self.professor_selecionado["id"], self.professor_selecionado["nome"])
        gerenciador_aulas.abrir_tela()
        
    def _visualizar_professor(self):
        """Abre tela de visualização detalhada"""
        if not self.professor_selecionado:
            messagebox.showwarning("Aviso", "Selecione um professor primeiro!")
            return
            
        from views.visualizar_professor import VisualizarProfessor
        visualizador = VisualizarProfessor(self.root, self.professor_selecionado["id"])
        visualizador.abrir_tela()
        
    def _editar_professor(self):
        """Edita professor selecionado"""
        if not self.professor_selecionado:
            messagebox.showwarning("Aviso", "Selecione um professor primeiro!")
            return
            
        # Preenche o formulário com os dados do professor selecionado
        self._preencher_formulario(self.professor_selecionado)
        self._entrar_modo_edicao()
        
    def _excluir_professor(self):
        """Exclui professor selecionado"""
        if not self.professor_selecionado:
            messagebox.showwarning("Aviso", "Selecione um professor primeiro!")
            return
            
        professor_id = self.professor_selecionado["id"]
        professor_nome = self.professor_selecionado["nome"]
        
        # Verificar se o professor tem aulas lançadas
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM aulas_eventuais WHERE professor_eventual_id = ?", (professor_id,))
        total_aulas = cursor.fetchone()[0]
        conn.close()
        
        mensagem = f"Tem certeza que deseja EXCLUIR o professor:\n\n"
        mensagem += f"📍 Nome: {professor_nome}\n"
        mensagem += f"📊 Aulas lançadas: {total_aulas}\n\n"
        
        if total_aulas > 0:
            mensagem += f"⚠️  ATENÇÃO: Todas as {total_aulas} aulas lançadas também serão excluídas!\n\n"
        
        mensagem += "Esta ação NÃO pode ser desfeita!"
        
        if messagebox.askyesno("❌ CONFIRMAR EXCLUSÃO", mensagem, icon="warning"):
            try:
                conn = conectar()
                cursor = conn.cursor()
                
                # Primeiro exclui as aulas (devido à chave estrangeira)
                cursor.execute("DELETE FROM aulas_eventuais WHERE professor_eventual_id = ?", (professor_id,))
                
                # Depois exclui o professor
                cursor.execute("DELETE FROM professores_eventuais WHERE id = ?", (professor_id,))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Sucesso", "Professor excluído com sucesso!")
                self._carregar_professores()
                self._limpar_formulario()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir professor:\n{e}")
                
    def _toggle_ativo(self):
        """Ativa/Inativa professor selecionado"""
        if not self.professor_selecionado:
            messagebox.showwarning("Aviso", "Selecione um professor primeiro!")
            return
            
        professor_id = self.professor_selecionado["id"]
        professor_nome = self.professor_selecionado["nome"]
        
        # Descobre o status atual
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT ativo FROM professores_eventuais WHERE id = ?", (professor_id,))
        resultado = cursor.fetchone()
        conn.close()
        
        if not resultado:
            messagebox.showerror("Erro", "Professor não encontrado!")
            return
            
        ativo_atual = resultado[0]
        novo_status = not ativo_atual
        status_texto = "ativar" if novo_status else "inativar"
        
        if messagebox.askyesno("Confirmar", f"Deseja {status_texto} o professor {professor_nome}?"):
            try:
                conn = conectar()
                cursor = conn.cursor()
                cursor.execute("UPDATE professores_eventuais SET ativo = ? WHERE id = ?", (novo_status, professor_id))
                conn.commit()
                conn.close()
                
                acao_texto = "ativado" if novo_status else "inativado"
                messagebox.showinfo("Sucesso", f"Professor {acao_texto} com sucesso!")
                self._carregar_professores()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao alterar status:\n{e}")
                
    def _gerar_relatorio(self):
        """Gera relatório de professores eventuais"""
        from reports.gerar_pdf_eventuais import gerar_relatorio_eventuais
        try:
            # Pega o mês e ano atual
            from datetime import datetime
            hoje = datetime.now()
            resultado = gerar_relatorio_eventuais(hoje.month, hoje.year)
            if resultado:
                messagebox.showinfo("Sucesso", f"Relatório gerado com sucesso!\n\nArquivo: {resultado}")
            else:
                messagebox.showerror("Erro", "Não foi possível gerar o relatório!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório:\n{e}")