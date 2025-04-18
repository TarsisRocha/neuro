# pacientes.py — Atualizado com login e senha_hash
# ------------------------------------------------
import os, streamlit as st
from datetime import datetime
from typing import List, Dict, Optional
from supabase import create_client, Client

URL = os.getenv("SUPABASE_URL") or st.secrets["SUPABASE_URL"]
KEY = os.getenv("SUPABASE_KEY") or st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(URL, KEY)
TBL = "pacientes"

def _tbl():
    return supabase.table(TBL)

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
    comp: str,
    bairro: str,
    cep: str,
    cidade: str,
    estado: str,
    plano: str,
    historico: str,
    obs: str,
    login: str = "",
    senha_hash: str = "",
) -> int:
    dados = {
        "nome": nome,
        "data_nasc": data_nasc,
        "idade": idade,
        "cpf": cpf,
        "rg": rg,
        "email": email,
        "tel": tel,
        "tel2": tel2,
        "endereco": endereco,
        "numero": numero,
        "complemento": comp,
        "bairro": bairro,
        "cep": cep,
        "cidade": cidade,
        "estado": estado,
        "plano": plano,
        "historico": historico,
        "observacao": obs,
        "login": login,
        "senha_hash": senha_hash,
        "criado_em": datetime.utcnow().isoformat(),
    }
    res = _tbl().insert(dados).execute()
    return res.data[0]["id"]

def obter_pacientes() -> List[Dict]:
    res = _tbl().select("*").order("nome").execute()
    return res.data or []

def obter_paciente_por_login(login: str) -> Optional[Dict]:
    res = _tbl().select("*").eq("login", login).single().execute()
    return res.data
