# laudos.py
from banco_dados import supabase

def adicionar_laudo(paciente_id, laudo, data):
    dados = {
        "paciente_id": paciente_id,
        "laudo": laudo,
        "data": data
    }
    resposta = supabase.table("laudos").insert(dados).execute()
    return resposta

def obter_laudos():
    resposta = supabase.table("laudos").select("*").execute()
    return resposta.data
