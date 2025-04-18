# pacientes.py  –  Acesso à tabela “pacientes” no Supabase
# --------------------------------------------------------
# Funções:
#   • adicionar_paciente(...)
#   • obter_pacientes()
#   • obter_paciente_por_id(id_)
#   • obter_paciente_por_login(login)  -> para autenticação de pacientes
# --------------------------------------------------------

import os
from typing import List, Dict, Optional
from datetime import datetime

from supabase import create_client, Client


# ───────────── Conexão Supabase ─────────────
SUPABASE_URL = os.getenv("SUPABASE_URL")     or st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")     or st.secrets.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "Defina SUPABASE_URL e SUPABASE_KEY como variáveis de ambiente "
        "ou nos secrets do Streamlit Cloud."
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
TBL = "pacientes"        # nome da tabela no Supabase


# ───────────── CRUD helpers ────────────────
def _table():
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
    """Insere paciente e devolve o ID gerado."""
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
        "login": login,           # para acesso do paciente
        "senha_hash": senha_hash, # bcrypt hash, se houver
        "criado_em": datetime.utcnow().isoformat(),
    }
    res = _table().insert(dados).execute()
    return res.data[0]["id"]


def obter_pacientes() -> List[Dict]:
    """Lista todos os pacientes ordenados por nome."""
    res = _table().select("*").order("nome").execute()
    return res.data or []


def obter_paciente_por_id(id_: int) -> Optional[Dict]:
    res = _table().select("*").eq("id", id_).single().execute()
    return res.data


def obter_paciente_por_login(login: str) -> Optional[Dict]:
    """
    Retorna paciente cujo campo `login` (ou email)
    corresponda ao valor informado.
    """
    res = (
        _table()
        .select("*")
        .or_(f"login.eq.{login},email.eq.{login}")
        .single()
        .execute()
    )
    return res.data