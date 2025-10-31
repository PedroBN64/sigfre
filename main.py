import customtkinter as ctk
from views.tela_principal import criar_tela_principal
import sys
import traceback

def excecao_global(exctype, value, tb):
    """Captura exceções globais para evitar crashes"""
    if "bad window path name" in str(value):
        print("⚠️  Aviso: Janela já foi fechada, ignorando erro de foco...")
        return
    print("❌ Exceção não tratada:")
    traceback.print_exception(exctype, value, tb)

# Configurar handler global de exceções
sys.excepthook = excecao_global

# Configurar CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

if __name__ == "__main__":
    try:
        root = ctk.CTk()
        root.title("SIGFRE - Sistema de Folha")
        root.geometry("1100x700")
        root.minsize(1000, 600)
        
        # Centralizar na tela
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (1100 // 2)
        y = (root.winfo_screenheight() // 2) - (700 // 2)
        root.geometry(f"1100x700+{x}+{y}")
        
        criar_tela_principal(root)
        root.mainloop()
    except Exception as e:
        print(f"Erro ao iniciar aplicação: {e}")
        traceback.print_exc()