# comunicacao.py
from banco_dados import obter_conexao

def adicionar_comunicacao(paciente_id, mensagem, data):
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute(
        'INSERT INTO comunicacoes (paciente_id, mensagem, data) VALUES (?, ?, ?)',
        (paciente_id, mensagem, data)
    )
    conexao.commit()
    conexao.close()

def obter_comunicacoes():
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM comunicacoes')
    comunicacoes = cursor.fetchall()
    conexao.close()
    return comunicacoes
