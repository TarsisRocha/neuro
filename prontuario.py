# prontuario.py
from banco_dados import obter_conexao

def adicionar_prontuario(paciente_id, descricao, data):
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute(
        'INSERT INTO prontuarios (paciente_id, descricao, data) VALUES (?, ?, ?)',
        (paciente_id, descricao, data)
    )
    conexao.commit()
    conexao.close()

def obter_prontuarios_por_paciente(paciente_id):
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM prontuarios WHERE paciente_id = ?', (paciente_id,))
    prontuarios = cursor.fetchall()
    conexao.close()
    return prontuarios
