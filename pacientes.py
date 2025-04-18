# pacientes.py — CRUD para a tabela ‘pacientes’, com todos os campos

import os, streamlit as st
from datetime import datetime
from typing import List, Dict, Optional
from supabase import create_client, Client

# Conexão Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Defina SUPABASE_URL e SUPABASE_KEY em environment ou Secrets.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
TBL = "pacientes"

def _tbl():
    return supabase.table(TBL)

def adicionar_paciente(
    nome: str,
    data_nasc: str,   # ISO YYYY‑MM‑DD
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
) -> Optional[int]:
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
        "complemento": complemento,
        "bairro": bairro,
        "cep": cep,
        "cidade": cidade,
        "estado": estado,
        "plano": plano,
        "historico": historico,
        "observacao": observacoes,
        "criado_em": datetime.utcnow().isoformat(),
    }
    try:
        res = _tbl().insert(dados).execute()
        return res.data[0]["id"]
    except Exception as e:
        st.error(f"Erro ao criar paciente: {e}")
        return None

def obter_pacientes() -> List[Dict]:
    try:
        res = _tbl()\
            .select("id,nome,data_nasc,idade,cpf,rg,email,tel,tel2,"
                    "endereco,numero,complemento,bairro,cep,cidade,estado,"
                    "plano,historico,observacao")\
            .order("nome")\
            .execute()
        return res.data or []
    except Exception as e:
        st.error(f"Erro ao carregar pacientes: {e}")
        return []

def obter_paciente_por_login(login: str) -> Optional[Dict]:
    try:
        res = _tbl().select("*").eq("login", login).single().execute()
        return res.data
    except Exception as e:
        st.error(f"Erro ao buscar paciente por login: {e}")
        return None
