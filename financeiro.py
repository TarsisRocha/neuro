# financeiro.py
from banco_dados import obter_conexao

def adicionar_transacao(paciente_id, data, valor, descricao):
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute(
        'INSERT INTO financeiro (paciente_id, data, valor, descricao) VALUES (?, ?, ?, ?)',
        (paciente_id, data, valor, descricao)
    )
    conexao.commit()
    conexao.close()

def obter_transacoes():
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM financeiro')
    transacoes = cursor.fetchall()
    conexao.close()
    return transacoes
