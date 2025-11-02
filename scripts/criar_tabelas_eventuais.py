# scripts/criar_tabelas_eventuais.py
import sys
import os

# Adiciona o diretório raiz ao path do Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.criar_tabelas_eventuais import executar_criacao_tabelas

if __name__ == "__main__":
    executar_criacao_tabelas()
    input("Pressione Enter para sair...")