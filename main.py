import customtkinter as ctk
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

# ========== CONFIGURAÇÕES DE PERFORMANCE ==========
# Configurar CustomTkinter para melhor performance
try:
    ctk.deactivate_automatic_dpi_awareness()  # Melhora performance em monitores HiDPI
except:
    pass  # Ignora se não estiver disponível

ctk.set_widget_scaling(1.0)  # Escala fixa para melhor performance
ctk.set_window_scaling(1.0)

# Configurar aparência
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

if __name__ == "__main__":
    try:
        print("🚀 Iniciando SIGFRE...")
        
        # Criar janela principal
        root = ctk.CTk()
        
        # Configurações básicas da janela
        root.title("SIGFRE - Sistema de Folha")
        root.geometry("1100x700")
        root.minsize(1000, 600) # Tamanho mínimo da janela
        
        # Centralizar na tela
        root.update_idletasks()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = 1100
        window_height = 700
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")    
        
        print("✅ Janela principal criada...")
        
        # Importar e criar tela principal DENTRO do try para capturar erros
        try:
            from views.tela_principal import criar_tela_principal
            print("✅ Módulos carregados...")
            criar_tela_principal(root)
            print("✅ Tela principal criada com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao carregar tela principal: {e}")
            traceback.print_exc()
            # Mostrar mensagem de erro ao usuário
            import tkinter.messagebox as tk_messagebox
            tk_messagebox.showerror("Erro", f"Erro ao carregar interface:\n{str(e)}")
            sys.exit(1)
        
        # Configurar fechamento
        def fechar_aplicacao():
            """Fecha a aplicação de forma otimizada"""
            try:
                print("👋 Encerrando SIGFRE...")
                root.quit()
                root.destroy()
            except Exception as e:
                print(f"⚠️  Aviso ao fechar: {e}")
        
        root.protocol("WM_DELETE_WINDOW", fechar_aplicacao)
        
        print("🎉 SIGFRE carregado com sucesso! Iniciando interface...")
        
        # Iniciar loop principal
        root.mainloop()
        
        print("👋 SIGFRE encerrado.")
        
    except KeyboardInterrupt:
        print("\n🛑 Aplicação interrompida pelo usuário")
        
    except Exception as e:
        print(f"❌ Erro crítico ao iniciar aplicação: {e}")
        traceback.print_exc()
        
        # Tentar mostrar mensagem de erro mesmo com falha na interface
        try:
            import tkinter.messagebox as tk_messagebox
            tk_messagebox.showerror("Erro Crítico", 
                                  f"Erro ao iniciar SIGFRE:\n{str(e)}\n\nVerifique o console para detalhes.")
        except:
            print("Não foi possível mostrar mensagem de erro gráfica.")
            
        sys.exit(1)