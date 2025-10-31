import sqlite3
import os

DB_PATH = "database/sigfre.db"

def conectar():
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    criar_tabelas(conn)
    return conn

def criar_tabelas(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS funcionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            rg TEXT UNIQUE NOT NULL,
            cargo TEXT,
            contrato TEXT,
            carga_horaria TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS frequencia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funcionario_id INTEGER,
            data TEXT NOT NULL,
            justificativa TEXT NOT NULL,
            FOREIGN KEY(funcionario_id) REFERENCES funcionarios(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()