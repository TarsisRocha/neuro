import os, streamlit as st
from typing import Dict
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Defina SUPABASE_URL e SUPABASE_KEY em env ou Secrets.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def gerar_relatorio() -> (int,int,float):
    tot_p = supabase.rpc("count_rows", {"table_name":"pacientes"}).execute().data or 0
    tot_a = supabase.rpc("count_rows", {"table_name":"agendamentos"}).execute().data or 0
    tot_f = supabase.rpc("sum_valor_transacoes").execute().data or 0
    return tot_p, tot_a, tot_f

def relatorio_por_tipo_agendamento() -> Dict[str,int]:
    res = supabase.table("agendamentos")\
                  .select("tipo_consulta, count:tipo_consulta")\
                  .group("tipo_consulta").execute()
    return {r["tipo_consulta"]: r["count"] for r in res.data}
