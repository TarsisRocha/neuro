# pacientes.py – Módulo de gerenciamento de pacientes
import datetime
from typing import List, Dict
from banco_dados import supabase

def obter_pacientes() -> List[Dict]:
    """
    Retorna lista de pacientes com todos os campos necessários,
    formatando data_nascimento como DD/MM/AAAA.
    """
    resp = supabase.table("pacientes").select("*").execute()
    data = resp.data or []
    pacientes = []
    for p in data:
        raw = p.get("data_nascimento")
        data_fmt = ""
        if raw:
            try:
                dt = datetime.date.fromisoformat(raw)
                data_fmt = dt.strftime("%d/%m/%Y")
            except:
                data_fmt = ""
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
            "data_nascimento": data_fmt,
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
    data_nascimento pode vir em DD/MM/AAAA ou ISO (YYYY-MM-DD).
    """
    # converte entrada para ISO
    iso_date = None
    if data_nascimento:
        try:
            if "/" in data_nascimento:
                dt = datetime.datetime.strptime(data_nascimento, "%d/%m/%Y").date()
            else:
                dt = datetime.date.fromisoformat(data_nascimento)
            iso_date = dt.isoformat()
        except ValueError:
            iso_date = None

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
        "observacoes": observacoes
    }
    if iso_date:
        registro["data_nascimento"] = iso_date
    if isinstance(idade, int):
        registro["idade"] = idade

    try:
        resp = supabase.table("pacientes").insert(registro).execute()
    except Exception as e:
        import streamlit as st
        st.error(f"Erro ao inserir paciente: {e}")
        return None

    if resp.status_code in (200, 201) and resp.data:
        return resp.data[0].get("id")
    return None

def obter_paciente_por_login(login: str) -> Dict:
    """
    Retorna dados de um paciente a partir do login de usuário,
    formatando data_nascimento como DD/MM/AAAA.
    """
    # busca id do paciente
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
    # busca dados do paciente
    resp_p = (
        supabase.table("pacientes")
               .select("*")
               .eq("id", pid)
               .single()
               .execute()
    )
    p = resp_p.data or {}
    raw = p.get("data_nascimento")
    data_fmt = ""
    if raw:
        try:
            dt = datetime.date.fromisoformat(raw)
            data_fmt = dt.strftime("%d/%m/%Y")
        except:
            data_fmt = ""
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
        "data_nascimento": data_fmt,
        "idade": p.get("idade", None)
    }
