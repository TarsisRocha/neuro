# agendamentos.py
from banco_dados import supabase

def adicionar_agendamento(paciente_id, data, hora, observacoes, tipo_consulta):
    dados = {
        "paciente_id": paciente_id,
        "data": data,
        "hora": hora,
        "observacoes": observacoes,
        "tipo_consulta": tipo_consulta
    }
    resposta = supabase.table("agendamentos").insert(dados).execute()
    return resposta

def obter_agendamentos():
    resposta = supabase.table("agendamentos").select("*").execute()
    return resposta.data
