# pacientes.py – Módulo de gerenciamento de pacientes
from database import supabase  # Cliente Supabase configurado em database.py
from typing import List, Dict

def obter_pacientes() -> List[Dict]:
    """
    Retorna lista de pacientes com todos os campos necessários,
    incluindo cpf e data_nascimento em ISO.
    """
    resposta = supabase.table("pacientes").select("*").execute()
    data = resposta.data or []
    pacientes = []
    for p in data:
        pacientes.append({
            "id": p.get("id"),
            "nome": p.get("nome", ""),
            "cpf": p.get("cpf", ""),
            "rg": p.get("rg", ""),
            "email": p.get("email", ""),
            "tel": p.get("tel", ""),
            "tel2": p.get("tel2", ""),
            "endereco": p.get("endereco", ""),
            "numero": p.get("numero", ""),
            "complemento": p.get("complemento", ""),
            "bairro": p.get("bairro", ""),
            "cep": p.get("cep", ""),
            "cidade": p.get("cidade", ""),
            "estado": p.get("estado", ""),
            "plano": p.get("plano", ""),
            "historico": p.get("historico", ""),
            "observacoes": p.get("observacoes", ""),
            "data_nascimento": p.get("data_nascimento", ""),
            "idade": p.get("idade", None)
        })
    return pacientes

def adicionar_paciente(
    nome: str,
    data_nascimento: str,
    idade: int,
    cpf: str,
    rg: str,
    email: str,
    tel: str,
    tel2: str,
    endereco: str,
    numero: str,
    complemento: str,
    bairro: str,
    cep: str,
    cidade: str,
    estado: str,
    plano: str,
    historico: str,
    observacoes: str
) -> int:
    """
    Insere novo paciente no banco e retorna o novo ID (ou None se falhar).
    data_nascimento deve vir em formato ISO (YYYY-MM-DD).
    """
    registro = {
        "nome": nome,
        "cpf": cpf,
        "rg": rg,
        "email": email,
        "tel": tel,
        "tel2": tel2,
        "endereco": endereco,
        "numero": numero,
        "complemento": complemento,
        "bairro": bairro,
        "cep": cep,
        "cidade": cidade,
        "estado": estado,
        "plano": plano,
        "historico": historico,
        "observacoes": observacoes,
        "data_nascimento": data_nascimento,
        "idade": idade
    }
    resposta = supabase.table("pacientes").insert(registro).execute()
    if resposta.status_code in (200, 201) and resposta.data:
        return resposta.data[0].get("id")
    return None

def obter_paciente_por_login(login: str) -> Dict:
    """
    Retorna dados de um paciente a partir do login de usuário.
    Assume relacionamento entre tabela 'usuarios' e 'pacientes'.
    """
    # Busca paciente_id em usuários
    resp_u = (
        supabase.table("usuarios")
                .select("paciente_id")
                .eq("login", login)
                .single()
                .execute()
    )
    pid = resp_u.data.get("paciente_id") if resp_u.data else None
    if not pid:
        return {}
    # Busca dados do paciente
    resp_p = (
        supabase.table("pacientes")
                .select("*")
                .eq("id", pid)
                .single()
                .execute()
    )
    p = resp_p.data or {}
    return {
        "id": p.get("id"),
        "nome": p.get("nome", ""),
        "cpf": p.get("cpf", ""),
        "rg": p.get("rg", ""),
        "email": p.get("email", ""),
        "tel": p.get("tel", ""),
        "tel2": p.get("tel2", ""),
        "endereco": p.get("endereco", ""),
        "numero": p.get("numero", ""),
        "complemento": p.get("complemento", ""),
        "bairro": p.get("bairro", ""),
        "cep": p.get("cep", ""),
        "cidade": p.get("cidade", ""),
        "estado": p.get("estado", ""),
        "plano": p.get("plano", ""),
        "historico": p.get("historico", ""),
        "observacoes": p.get("observacoes", ""),
        "data_nascimento": p.get("data_nascimento", ""),
        "idade": p.get("idade", None)
    }
