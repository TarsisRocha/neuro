import os, streamlit as st
from datetime import datetime
from typing import List, Dict
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Defina SUPABASE_URL e SUPABASE_KEY em env ou Secrets.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
TBL = "transacoes"

def _tbl():
    return supabase.table(TBL)

def adicionar_transacao(
    pid: int, data_iso: str, valor: float, desc: str
) -> int:
    item = {
        "paciente_id": pid,
        "data_mov": data_iso,
        "valor": valor,
        "descricao": desc,
        "criado_em": datetime.utcnow().isoformat()
    }
    res = _tbl().insert(item).execute()
    return res.data[0]["id"]

def obter_transacoes() -> List[Dict]:
    return _tbl().select("*").order("data_mov").execute().data or []

def obter_transacoes_por_paciente(pid: int) -> List[Dict]:
    return _tbl().select("*")\
                 .eq("paciente_id", pid)\
                 .order("data_mov")\
                 .execute().data or []
