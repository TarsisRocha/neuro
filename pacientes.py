# pacientes.py
from banco_dados import supabase

def adicionar_paciente(nome, data_nascimento, idade, cpf, rg, email, contato, telefone_adicional,
                       endereco, numero, complemento, bairro, cep, cidade, estado, plano_saude, historico, observacoes):
    dados = {
        "nome": nome,
        "data_nascimento": data_nascimento,  # Espera-se formato ISO (string), por exemplo "YYYY-MM-DD"
        "idade": idade,
        "cpf": cpf,
        "rg": rg,
        "email": email,
        "contato": contato,
        "telefone_adicional": telefone_adicional,
        "endereco": endereco,
        "numero": numero,
        "complemento": complemento,
        "bairro": bairro,
        "cep": cep,
        "cidade": cidade,
        "estado": estado,
        "plano_saude": plano_saude,
        "historico": historico,
        "observacoes": observacoes
    }
    resposta = supabase.table("pacientes").insert(dados).execute()
    return resposta

def obter_pacientes():
    resposta = supabase.table("pacientes").select("*").execute()
    return resposta.data
