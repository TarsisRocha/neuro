import os, streamlit as st
from datetime import datetime
from typing import List, Dict
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Defina SUPABASE_URL e SUPABASE_KEY em env ou Secrets.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
TBL = "agendamentos"

def _tbl():
    return supabase.table(TBL)

def adicionar_agendamento(
    pid: int, data_iso: str, hora: str,
    obs: str, tipo: str
) -> int:
    item = {
        "paciente_id": pid,
        "data_consulta": data_iso,
        "hora_consulta": hora,
        "observacao": obs,
        "tipo_consulta": tipo,
        "criado_em": datetime.utcnow().isoformat()
    }
    res = _tbl().insert(item).execute()
    return res.data[0]["id"]

def obter_agendamentos() -> List[Dict]:
    return _tbl().select("*")\
                 .order("data_consulta")\
                 .order("hora_consulta")\
                 .execute().data or []

def obter_agendamentos_por_paciente(pid: int) -> List[Dict]:
    return _tbl().select("*")\
                 .eq("paciente_id", pid)\
                 .order("data_consulta")\
                 .order("hora_consulta")\
                 .execute().data or []
