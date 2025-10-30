# database/db.py
import sqlite3
import os

DB_NAME = "sigfre.db"

def conectar():
    return sqlite3.connect(DB_NAME)

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS funcionarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        rg TEXT UNIQUE,
        cargo TEXT,
        contrato TEXT,
        carga_horaria TEXT
    )
    """)
    
    conn.commit()
    conn.close()

# Criar tabela ao importar
criar_tabelas()
