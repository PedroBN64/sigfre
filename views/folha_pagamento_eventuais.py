# views/folha_pagamento_eventuais.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from tkinter import ttk, messagebox
from database.db import conectar
from datetime import datetime
from reports.gerar_pdf_eventuais import gerar_relatorio_eventuais

class FolhaPagamentoEventuais:
    def __init__(self, root, mes, ano):
        self.root = root
        self.mes = mes
        self.ano = ano
        self.janela = None
        
    def abrir_tela(self):
        """Abre a tela de folha de pagamento"""
        self.janela = ctk.CTkToplevel(self.root)
        self.janela.title(f"Folha de Pagamento - {self.mes:02d}/{self.ano}")
        self.janela.geometry("1200x700")
        self.janela.transient(self.root)
        self.janela.grab_set()
        
        self._criar_interface()
        self._carregar_dados()
        
    def _criar_interface(self):
        """Cria a interface da folha de pagamento"""
        main_frame = ctk.CTkFrame(self.janela)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Título
        mes_nome = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                   "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"][self.mes - 1]
        
        ctk.CTkLabel(main_frame, text=f"💰 RELATÓRIO DE AULAS - {mes_nome.upper()} {self.ano}", 
                     font=("Arial", 18, "bold")).pack(pady=15)
        
        # Resumo
        frame_resumo = ctk.CTkFrame(main_frame)
        frame_resumo.pack(fill="x", padx=10, pady=10)
        
        self.label_resumo = ctk.CTkLabel(frame_resumo, text="Carregando...", 
                                       font=("Arial", 12, "bold"))
        self.label_resumo.pack(pady=10)
        
        # Container principal com duas colunas
        container_principal = ctk.CTkFrame(main_frame)
        container_principal.pack(fill="both", expand=True, pady=10)
        
        # ========== COLUNA ESQUERDA - LISTA DE PROFESSORES ==========
        coluna_esquerda = ctk.CTkFrame(container_principal)
        coluna_esquerda.pack(side="left", fill="both", padx=(0, 10))
        
        frame_professores = ctk.CTkFrame(coluna_esquerda)
        frame_professores.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(frame_professores, text="👥 PROFESSORES EVENTUAIS", 
                    font=("Arial", 14, "bold")).pack(pady=10)
        
        # Treeview de professores
        self.tree_professores = ttk.Treeview(frame_professores, 
                                           columns=("id", "professor", "total_aulas"),
                                           show="headings", height=15)
        
        self.tree_professores.heading("id", text="ID")
        self.tree_professores.heading("professor", text="Professor Eventual")
        self.tree_professores.heading("total_aulas", text="Total Aulas")
        
        self.tree_professores.column("id", width=50, anchor="center")
        self.tree_professores.column("professor", width=250)
        self.tree_professores.column("total_aulas", width=100, anchor="center")
        
        scrollbar_prof = ttk.Scrollbar(frame_professores, orient="vertical", command=self.tree_professores.yview)
        self.tree_professores.configure(yscrollcommand=scrollbar_prof.set)
        
        self.tree_professores.pack(side="left", fill="both", expand=True)
        scrollbar_prof.pack(side="right", fill="y")
        
        # ========== COLUNA DIREITA - DETALHES DAS AULAS ==========
        coluna_direita = ctk.CTkFrame(container_principal)
        coluna_direita.pack(side="right", fill="both", expand=True)
        
        frame_detalhes = ctk.CTkFrame(coluna_direita)
        frame_detalhes.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(frame_detalhes, text="📋 DETALHES DAS AULAS", 
                    font=("Arial", 14, "bold")).pack(pady=10)
        
        # Treeview de detalhes das aulas
        self.tree_detalhes = ttk.Treeview(frame_detalhes, 
                                        columns=("data", "prof_substituido", "turmas", "aulas", "observacoes"),
                                        show="headings", height=15)
        
        self.tree_detalhes.heading("data", text="Data")
        self.tree_detalhes.heading("prof_substituido", text="Professor Substituído")
        self.tree_detalhes.heading("turmas", text="Turmas")
        self.tree_detalhes.heading("aulas", text="Aulas")
        self.tree_detalhes.heading("observacoes", text="Observações")
        
        self.tree_detalhes.column("data", width=100, anchor="center")
        self.tree_detalhes.column("prof_substituido", width=200)
        self.tree_detalhes.column("turmas", width=150)
        self.tree_detalhes.column("aulas", width=80, anchor="center")
        self.tree_detalhes.column("observacoes", width=200)
        
        scrollbar_det = ttk.Scrollbar(frame_detalhes, orient="vertical", command=self.tree_detalhes.yview)
        self.tree_detalhes.configure(yscrollcommand=scrollbar_det.set)
        
        self.tree_detalhes.pack(side="left", fill="both", expand=True)
        scrollbar_det.pack(side="right", fill="y")
        
        # Botões
        frame_botoes = ctk.CTkFrame(main_frame)
        frame_botoes.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(frame_botoes, text="📄 GERAR RELATÓRIO", command=self._gerar_relatorio,
                     fg_color="#27ae60", hover_color="#219955", width=140, height=38,
                     font=("Arial", 12)).pack(side="left", padx=5)
        
        ctk.CTkButton(frame_botoes, text="🔄 ATUALIZAR", command=self._carregar_dados,
                     fg_color="#3498db", hover_color="#2980b9", width=120, height=38,
                     font=("Arial", 12)).pack(side="left", padx=5)
        
        # Eventos
        self.tree_professores.bind("<<TreeviewSelect>>", self._on_selecionar_professor)
        
    def _on_selecionar_professor(self, event):
        """Quando um professor é selecionado, carrega seus detalhes"""
        selection = self.tree_professores.selection()
        if selection:
            professor_id = self.tree_professores.item(selection[0])["values"][0]
            self._carregar_detalhes_professor(professor_id)
        
    def _carregar_dados(self):
        """Carrega os dados da folha de pagamento"""
        for item in self.tree_professores.get_children():
            self.tree_professores.delete(item)
            
        for item in self.tree_detalhes.get_children():
            self.tree_detalhes.delete(item)
            
        conn = conectar()
        cursor = conn.cursor()
        
        # Busca todos os professores eventuais com aulas no mês
        cursor.execute('''
            SELECT 
                pe.id,
                pe.nome,
                SUM(ae.quantidade_aulas) as total_aulas
            FROM professores_eventuais pe
            INNER JOIN aulas_eventuais ae ON pe.id = ae.professor_eventual_id
            WHERE substr(ae.data_aula, 4, 2) = ? AND substr(ae.data_aula, 7, 4) = ?
            GROUP BY pe.id, pe.nome
            HAVING total_aulas > 0
            ORDER BY pe.nome
        ''', (f"{self.mes:02d}", str(self.ano)))
        
        total_geral_aulas = 0
        total_professores = 0
        
        for professor in cursor.fetchall():
            professor_id, nome, total_aulas = professor
            
            self.tree_professores.insert("", "end", values=(
                professor_id,
                nome, 
                f"{total_aulas}"
            ))
            
            total_geral_aulas += total_aulas
            total_professores += 1
            
        conn.close()
        
        # Atualizar resumo
        mes_nome = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                   "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"][self.mes - 1]
        
        resumo_text = f"📊 RESUMO {mes_nome} {self.ano}: {total_professores} professores | "
        resumo_text += f"{total_geral_aulas} aulas totais"
        
        self.label_resumo.configure(text=resumo_text)
        
    def _carregar_detalhes_professor(self, professor_id):
        """Carrega os detalhes das aulas de um professor específico"""
        for item in self.tree_detalhes.get_children():
            self.tree_detalhes.delete(item)
            
        conn = conectar()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                professor_substituido,
                data_aula,
                turmas,
                quantidade_aulas,
                observacoes
            FROM aulas_eventuais 
            WHERE professor_eventual_id = ?
            AND substr(data_aula, 4, 2) = ? AND substr(data_aula, 7, 4) = ?
            ORDER BY data_aula
        ''', (professor_id, f"{self.mes:02d}", str(self.ano)))
        
        for aula in cursor.fetchall():
            prof_substituido, data, turmas, qtd_aulas, observacoes = aula
            
            self.tree_detalhes.insert("", "end", values=(
                data,
                prof_substituido,
                turmas,
                qtd_aulas,
                observacoes or "-"
            ))
            
        conn.close()
        
    def _gerar_relatorio(self):
        """Gera relatório detalhado em PDF"""
        try:
            # Usar o mês e ano atual da folha de pagamento
            resultado = gerar_relatorio_eventuais(self.mes, self.ano)
            if resultado:
                messagebox.showinfo("Sucesso", f"Relatório gerado com sucesso!\n\nArquivo: {resultado}")
            else:
                messagebox.showerror("Erro", "Não foi possível gerar o relatório!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório:\n{e}")