# views/relatorio_professores.py
import customtkinter as ctk
from tkinter import messagebox

class RelatorioProfessoresEventuais:
    def __init__(self, root):
        self.root = root
        self.janela = None
        
    def abrir_tela(self):
        """Abre a tela de relatórios"""
        messagebox.showinfo("Relatórios", "Sistema de relatórios em desenvolvimento!\n\nEm breve: Relatórios completos de aulas, frequência e pagamentos.")