# banco_dados.py
import sqlite3

NOME_BANCO = 'consultorio.db'

def obter_conexao():
    conexao = sqlite3.connect(NOME_BANCO)
    conexao.row_factory = sqlite3.Row  # Permite acessar as colunas pelo nome
    return conexao

def inicializar_banco():
    conexao = obter_conexao()
    cursor = conexao.cursor()
    # Tabela de Pacientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            idade INTEGER,
            contato TEXT,
            historico TEXT
        )
    ''')
    # Tabela de Agendamentos com campo tipo_consulta
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER,
            data TEXT,
            hora TEXT,
            observacoes TEXT,
            tipo_consulta TEXT,
            FOREIGN KEY(paciente_id) REFERENCES pacientes(id)
        )
    ''')
    # Tabela de Prontuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prontuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER,
            descricao TEXT,
            data TEXT,
            FOREIGN KEY(paciente_id) REFERENCES pacientes(id)
        )
    ''')
    # Tabela Financeira
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS financeiro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER,
            data TEXT,
            valor REAL,
            descricao TEXT,
            FOREIGN KEY(paciente_id) REFERENCES pacientes(id)
        )
    ''')
    # Tabela de Comunicações
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comunicacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER,
            mensagem TEXT,
            data TEXT,
            FOREIGN KEY(paciente_id) REFERENCES pacientes(id)
        )
    ''')
    # Tabela de Laudos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS laudos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER,
            laudo TEXT,
            data TEXT,
            FOREIGN KEY(paciente_id) REFERENCES pacientes(id)
        )
    ''')
    conexao.commit()
    conexao.close()
