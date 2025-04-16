# comunicacao.py
from banco_dados import supabase

def adicionar_comunicacao(paciente_id, mensagem, data):
    dados = {
        "paciente_id": paciente_id,
        "mensagem": mensagem,
        "data": data
    }
    resposta = supabase.table("comunicacoes").insert(dados).execute()
    return resposta

def obter_comunicacoes():
    resposta = supabase.table("comunicacoes").select("*").execute()
    return resposta.data
