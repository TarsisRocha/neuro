import os, streamlit as st
from datetime import datetime
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Defina SUPABASE_URL e SUPABASE_KEY em env ou Secrets.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
TBL = "mensagens"

def adicionar_comunicacao(pid: int, mensagem: str, timestamp: str):
    supabase.table(TBL).insert({
        "paciente_id": pid,
        "mensagem": mensagem,
        "enviado_em": timestamp
    }).execute()
