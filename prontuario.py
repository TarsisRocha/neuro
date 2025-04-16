# prontuario.py
from banco_dados import supabase

def adicionar_prontuario(paciente_id, descricao, data):
    dados = {
        "paciente_id": paciente_id,
        "descricao": descricao,
        "data": data
    }
    resposta = supabase.table("prontuarios").insert(dados).execute()
    return resposta

def obter_prontuarios_por_paciente(paciente_id):
    resposta = supabase.table("prontuarios").select("*").eq("paciente_id", paciente_id).execute()
    return resposta.data
