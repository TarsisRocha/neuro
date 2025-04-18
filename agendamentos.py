# agendamentos.py — Tabela 'agendamentos' com tratamento de erros
import os
import streamlit as st
from datetime import datetime
from typing import List, Dict
from supabase import create_client, Client

# Conexão Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Defina SUPABASE_URL e SUPABASE_KEY em env ou Secrets.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
TBL = "agendamentos"

def _tbl():
    return supabase.table(TBL)

def adicionar_agendamento(
    paciente_id: int,
    data_consulta: str,      # YYYY-MM-DD
    hora_consulta: str,      # HH:MM
    observacao: str,
    tipo_consulta: str
) -> int:
    """Insere e retorna o ID ou -1 em caso de falha."""
    try:
        dados = {
            "paciente_id": paciente_id,
            "data_consulta": data_consulta,
            "hora_consulta": hora_consulta,
            "observacao": observacao,
            "tipo_consulta": tipo_consulta,
            "criado_em": datetime.utcnow().isoformat()
        }
        res = _tbl().insert(dados).execute()
        return res.data[0]["id"]
    except Exception as e:
        st.error(f"Erro ao agendar consulta: {e}")
        return -1

def obter_agendamentos() -> List[Dict]:
    """Retorna todos os agendamentos ou lista vazia em caso de erro."""
    try:
        res = _tbl().select("*") \
                    .order("data_consulta") \
                    .order("hora_consulta") \
                    .execute()
        return res.data or []
    except Exception as e:
        st.error(f"Não foi possível carregar agendamentos: {e}")
        return []

def obter_agendamentos_por_paciente(paciente_id: int) -> List[Dict]:
    """Retorna agendamentos de um paciente ou lista vazia em caso de erro."""
    try:
        res = _tbl().select("*") \
                    .eq("paciente_id", paciente_id) \
                    .order("data_consulta") \
                    .order("hora_consulta") \
                    .execute()
        return res.data or []
    except Exception as e:
        st.error(f"Não foi possível carregar agendamentos do paciente: {e}")
        return []
