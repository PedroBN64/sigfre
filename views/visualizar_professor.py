# views/visualizar_professor.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from tkinter import ttk
from database.db import conectar

class VisualizarProfessor:
    def __init__(self, root, professor_id):
        self.root = root
        self.professor_id = professor_id
        self.janela = None
        
    def abrir_tela(self):
        """Abre a tela de visualização detalhada"""
        self.janela = ctk.CTkToplevel(self.root)
        self.janela.title("Detalhes do Professor")
        self.janela.geometry("800x600")
        self.janela.transient(self.root)
        self.janela.grab_set()
        
        self._carregar_dados()
        self._criar_interface()
        
    def _carregar_dados(self):
        """Carrega os dados do professor"""
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT nome, cpf, telefone, email, ativo, data_cadastro
            FROM professores_eventuais WHERE id = ?
        ''', (self.professor_id,))
        
        self.dados_professor = cursor.fetchone()
        conn.close()
        
    def _criar_interface(self):
        """Cria a interface de visualização"""
        if not self.dados_professor:
            ctk.CTkLabel(self.janela, text="Professor não encontrado!").pack(pady=50)
            return
            
        main_frame = ctk.CTkFrame(self.janela)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(main_frame, text="👨‍🏫 DETALHES DO PROFESSOR", 
                     font=("Arial", 18, "bold")).pack(pady=20)
        
        # Container de informações
        frame_info = ctk.CTkFrame(main_frame)
        frame_info.pack(fill="x", pady=15, padx=10)
        
        # Grid de informações
        info_grid = ctk.CTkFrame(frame_info)
        info_grid.pack(fill="x", pady=15, padx=15)
        
        # Nome
        ctk.CTkLabel(info_grid, text="Nome:", font=("Arial", 12, "bold"), width=120).grid(row=0, column=0, sticky="w", pady=8)
        ctk.CTkLabel(info_grid, text=self.dados_professor[0], font=("Arial", 12)).grid(row=0, column=1, sticky="w", pady=8)
        
        # CPF
        ctk.CTkLabel(info_grid, text="CPF:", font=("Arial", 12, "bold"), width=120).grid(row=1, column=0, sticky="w", pady=8)
        ctk.CTkLabel(info_grid, text=self.dados_professor[1] or "Não informado", font=("Arial", 12)).grid(row=1, column=1, sticky="w", pady=8)
        
        # Telefone
        ctk.CTkLabel(info_grid, text="Telefone:", font=("Arial", 12, "bold"), width=120).grid(row=2, column=0, sticky="w", pady=8)
        ctk.CTkLabel(info_grid, text=self.dados_professor[2] or "Não informado", font=("Arial", 12)).grid(row=2, column=1, sticky="w", pady=8)
        
        # Email
        ctk.CTkLabel(info_grid, text="Email:", font=("Arial", 12, "bold"), width=120).grid(row=3, column=0, sticky="w", pady=8)
        ctk.CTkLabel(info_grid, text=self.dados_professor[3] or "Não informado", font=("Arial", 12)).grid(row=3, column=1, sticky="w", pady=8)
        
        # Status
        ctk.CTkLabel(info_grid, text="Status:", font=("Arial", 12, "bold"), width=120).grid(row=4, column=0, sticky="w", pady=8)
        status_texto = "Ativo ✅" if self.dados_professor[4] else "Inativo ❌"
        status_cor = "#27ae60" if self.dados_professor[4] else "#e74c3c"
        ctk.CTkLabel(info_grid, text=status_texto, font=("Arial", 12, "bold"), text_color=status_cor).grid(row=4, column=1, sticky="w", pady=8)
        
        # Data de Cadastro
        ctk.CTkLabel(info_grid, text="Data de Cadastro:", font=("Arial", 12, "bold"), width=120).grid(row=5, column=0, sticky="w", pady=8)
        ctk.CTkLabel(info_grid, text=self.dados_professor[5] or "Não informada", font=("Arial", 12)).grid(row=5, column=1, sticky="w", pady=8)