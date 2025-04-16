# pacientes.py
from banco_dados import obter_conexao

def adicionar_paciente(nome, idade, contato, historico):
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute(
        'INSERT INTO pacientes (nome, idade, contato, historico) VALUES (?, ?, ?, ?)',
        (nome, idade, contato, historico)
    )
    conexao.commit()
    conexao.close()

def obter_pacientes():
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM pacientes')
    pacientes = cursor.fetchall()
    conexao.close()
    return pacientes
