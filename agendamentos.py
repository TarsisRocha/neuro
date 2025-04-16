# agendamentos.py
from banco_dados import obter_conexao

def adicionar_agendamento(paciente_id, data, hora, observacoes, tipo_consulta):
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute(
        'INSERT INTO agendamentos (paciente_id, data, hora, observacoes, tipo_consulta) VALUES (?, ?, ?, ?, ?)',
        (paciente_id, data, hora, observacoes, tipo_consulta)
    )
    conexao.commit()
    conexao.close()

def obter_agendamentos():
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM agendamentos')
    agendamentos = cursor.fetchall()
    conexao.close()
    return agendamentos
