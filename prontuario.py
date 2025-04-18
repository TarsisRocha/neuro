import os, streamlit as st
from datetime import datetime
from typing import List, Dict
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Defina SUPABASE_URL e SUPABASE_KEY em env ou Secrets.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
TBL = "prontuarios"

def _tbl():
    return supabase.table(TBL)

def adicionar_prontuario(
    pid: int, descricao: str, data_iso: str
) -> int:
    item = {
        "paciente_id": pid,
        "descricao": descricao,
        "data_registro": data_iso,
        "criado_em": datetime.utcnow().isoformat()
    }
    res = _tbl().insert(item).execute()
    return res.data[0]["id"]

def obter_prontuarios_por_paciente(pid: int) -> List[Dict]:
    return _tbl().select("*")\
                 .eq("paciente_id", pid)\
                 .order("data_registro")\
                 .execute().data or []
