# pacientes.py – Módulo de gerenciamento de pacientes
import datetime
from typing import List, Dict
from database import supabase

def obter_pacientes() -> List[Dict]:
    resp = supabase.table("pacientes").select("*").execute()
    data = resp.data or []
    pacientes = []
    for p in data:
        raw = p.get("data_nasc")  # adapte o nome do campo no seu esquema
        data_fmt = ""
        if raw:
            try:
                dt = datetime.date.fromisoformat(raw)
                data_fmt = dt.strftime("%d/%m/%Y")
            except:
                pass
        pacientes.append({
            "id": p.get("id"),
            "nome": p.get("nome", ""),
            "cpf": p.get("cpf", ""),
            # … demais campos …
            "observacao": p.get("observacao", ""),
            "data_nasc": data_fmt,
            "idade": p.get("idade", None)
        })
    return pacientes

def adicionar_paciente(
    nome: str,
    data_nasc: str,
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
    observacao: str
) -> int:
    # converte data de entrada (DD/MM/AAAA ou YYYY-MM-DD) para ISO
    iso_date = None
    if data_nasc:
        try:
            if "/" in data_nasc:
                dt = datetime.datetime.strptime(data_nasc, "%d/%m/%Y").date()
            else:
                dt = datetime.date.fromisoformat(data_nasc)
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
        "observacao": observacao
    }
    if iso_date:
        registro["data_nasc"] = iso_date
    if isinstance(idade, int):
        registro["idade"] = idade

    try:
        resp = supabase.table("pacientes").insert(registro).execute()
    except Exception as e:
        import streamlit as st
        st.error(f"Erro ao inserir paciente: {e}")
        return None

    # supabase-py pode não expor status_code; basta verificar se houve 'data'
    if getattr(resp, "data", None):
        return resp.data[0].get("id")
    return None

def obter_paciente_por_login(login: str) -> Dict:
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
    resp_p = (
        supabase.table("pacientes")
               .select("*")
               .eq("id", pid)
               .single()
               .execute()
    )
    p = resp_p.data or {}
    raw = p.get("data_nasc")
    data_fmt = ""
    if raw:
        try:
            dt = datetime.date.fromisoformat(raw)
            data_fmt = dt.strftime("%d/%m/%Y")
        except:
            pass
    return {
        "id": p.get("id"),
        "nome": p.get("nome", ""),
        "cpf": p.get("cpf", ""),
        # … demais campos …
        "observacao": p.get("observacao", ""),
        "data_nasc": data_fmt,
        "idade": p.get("idade", None)
    }
