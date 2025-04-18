# agendamentos.py – Acesso à tabela “agendamentos” no Supabase
# ------------------------------------------------------------
# Funções expostas:
#   • adicionar_agendamento(...)
#   • obter_agendamentos()
#   • obter_agendamentos_por_paciente(paciente_id)
# ------------------------------------------------------------

import os
from typing import List, Dict
from supabase import create_client, Client
import streamlit as st
from datetime import datetime

# ───────────── Conexão Supabase ─────────────
SUPABASE_URL = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "Defina SUPABASE_URL e SUPABASE_KEY nas variáveis de ambiente "
        "ou em st.secrets."
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
TBL = "agendamentos"


def _table():
    return supabase.table(TBL)


# ---------- CREATE ----------
def adicionar_agendamento(
    paciente_id: int,
    data_consulta: str,              # "YYYY-MM-DD"
    hora_consulta: str,              # "HH:MM"
    observacao: str,
    tipo_consulta: str               # "Plano de Saúde" / "Particular"
) -> int:
    """Insere agendamento e devolve o ID gerado."""
    dados = {
        "paciente_id": paciente_id,
        "data_consulta": data_consulta,
        "hora_consulta": hora_consulta,
        "observacao": observacao,
        "tipo_consulta": tipo_consulta,
        "criado_em": datetime.utcnow().isoformat()
    }
    res = _table().insert(dados).execute()
    return res.data[0]["id"]


# ---------- READ ----------
def obter_agendamentos() -> List[Dict]:
    """Lista todos os agendamentos ordenados por data/hora."""
    res = (
        _table()
        .select("*")
        .order("data_consulta")
        .order("hora_consulta")
        .execute()
    )
    return res.data or []


def obter_agendamentos_por_paciente(paciente_id: int) -> List[Dict]:
    """Lista agendamentos de um paciente específico."""
    res = (
        _table()
        .select("*")
        .eq("paciente_id", paciente_id)
        .order("data_consulta")
        .order("hora_consulta")
        .execute()
    )
    return res.data or []