# database/criar_tabelas_eventuais.py
# CORREÇÃO: Mudar de 'db' para 'database.db'
from database.db import conectar

def criar_tabela_professores_eventuais():
    """Cria a tabela de professores eventuais"""
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS professores_eventuais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE,
            telefone TEXT,
            email TEXT,
            ativo BOOLEAN DEFAULT 1,
            data_cadastro DATE DEFAULT CURRENT_DATE
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Tabela 'professores_eventuais' criada/verificada!")

def criar_tabela_aulas_eventuais():
    """Cria a tabela de aulas de professores eventuais"""
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aulas_eventuais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            professor_eventual_id INTEGER NOT NULL,
            professor_substituido TEXT NOT NULL,
            data_aula DATE NOT NULL,
            turmas TEXT NOT NULL,
            quantidade_aulas INTEGER NOT NULL,
            observacoes TEXT,
            data_registro DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY (professor_eventual_id) REFERENCES professores_eventuais (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Tabela 'aulas_eventuais' criada/verificada!")

def executar_criacao_tabelas():
    """Executa a criação de todas as tabelas necessárias"""
    print("🔄 Criando tabelas para professores eventuais...")
    criar_tabela_professores_eventuais()
    criar_tabela_aulas_eventuais()
    print("🎉 Todas as tabelas foram criadas/verificadas com sucesso!")

if __name__ == "__main__":
    executar_criacao_tabelas()