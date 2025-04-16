# pacientes.py
from banco_dados import supabase

def adicionar_paciente(nome, idade, contato, historico):
    dados = {
        "nome": nome,
        "idade": idade,
        "contato": contato,
        "historico": historico
    }
    resposta = supabase.table("pacientes").insert(dados).execute()
    return resposta

def obter_pacientes():
    resposta = supabase.table("pacientes").select("*").execute()
    return resposta.data
