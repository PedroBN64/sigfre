# main.py
import customtkinter as ctk
from views.tela_principal import criar_tela_principal

# CORREÇÃO: usar set_appearance_mode e set_default_color_theme
ctk.set_appearance_mode("Dark")     # "Light", "Dark", "System"
ctk.set_default_color_theme("blue")   # tema de cores

app = ctk.CTk()
app.geometry("900x600")
app.title("SIGFRE - Sistema de Folha de Pagamento Escolar")

criar_tela_principal(app)

app.mainloop()
