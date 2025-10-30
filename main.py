# main.py
import customtkinter as ctk
from views.tela_principal import criar_tela_principal

ctk.set_appearance_theme("blue")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("900x600")
app.title("SIGFRE - Sistema de Folha de Pagamento Escolar")

criar_tela_principal(app)

app.mainloop()
