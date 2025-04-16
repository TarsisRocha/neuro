# financeiro.py
from banco_dados import supabase

def adicionar_transacao(paciente_id, data, valor, descricao):
    dados = {
        "paciente_id": paciente_id,
        "data": data,
        "valor": valor,
        "descricao": descricao
    }
    resposta = supabase.table("financeiro").insert(dados).execute()
    return resposta

def obter_transacoes():
    resposta = supabase.table("financeiro").select("*").execute()
    return resposta.data
