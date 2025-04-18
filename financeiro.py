# financeiro.py – Acesso à tabela “transacoes” (ou “financeiro”) no Supabase
# -------------------------------------------------------------------------
# Funções:
#   • adicionar_transacao(paciente_id, data_iso, valor, descricao)
#   • obter_transacoes()                       → todas as transações
#   • obter_transacoes_por_paciente(pid)       → apenas de 1 paciente
# -------------------------------------------------------------------------

import os
from typing import List, Dict
from datetime import datetime

from supabase import create_client, Client
import streamlit as st

# ───────────── Conexão Supabase ─────────────
SUPABASE_URL = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "Defina SUPABASE_URL e SUPABASE_KEY nas variáveis de ambiente "
        "ou nos secrets do Streamlit Cloud."
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
TBL = "transacoes"   # nome da tabela no Supabase


def _table():
    return supabase.table(TBL)


# ---------- CREATE ----------
def adicionar_transacao(
    paciente_id: int,
    data_mov: str,          # "YYYY-MM-DD"
    valor: float,
    descricao: str
) -> int:
    """Insere transação financeira e devolve ID gerado."""
    dados = {
        "paciente_id": paciente_id,
        "data_mov": data_mov,
        "valor": valor,
        "descricao": descricao,
        "criado_em": datetime.utcnow().isoformat()
    }
    res = _table().insert(dados).execute()
    return res.data[0]["id"]


# ---------- READ ----------
def obter_transacoes() -> List[Dict]:
    res = _table().select("*").order("data_mov").execute()
    return res.data or []


def obter_transacoes_por_paciente(paciente_id: int) -> List[Dict]:
    res = (
        _table()
        .select("*")
        .eq("paciente_id", paciente_id)
        .order("data_mov")
        .execute()
    )
    return res.data or []
