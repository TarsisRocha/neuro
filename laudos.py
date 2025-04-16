# laudos.py
from banco_dados import obter_conexao

def adicionar_laudo(paciente_id, laudo, data):
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute(
        'INSERT INTO laudos (paciente_id, laudo, data) VALUES (?, ?, ?)',
        (paciente_id, laudo, data)
    )
    conexao.commit()
    conexao.close()

def obter_laudos():
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM laudos')
    laudos = cursor.fetchall()
    conexao.close()
    return laudos
