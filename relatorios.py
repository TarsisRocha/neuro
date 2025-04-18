# relatorios.py — Funções de relatório sem usar RPC no banco
import os
import streamlit as st
from typing import Dict
import pacientes
import agendamentos
import financeiro

# Conexão Supabase (mantém para outras funções, se precisar)
from supabase import create_client, Client
SUPABASE_URL = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def gerar_relatorio() -> (int, int, float):
    """
    Retorna (total_pacientes, total_consultas, total_receita).
    Faz contagens e somas em memória para evitar RPCs ausentes.
    """
    # Total de pacientes
    pacs = pacientes.obter_pacientes()
    tot_p = len(pacs)

    # Total de consultas
    ags = agendamentos.obter_agendamentos()
    tot_a = len(ags)

    # Soma de valores financeiros
    txs = financeiro.obter_transacoes()
    tot_f = sum(t.get("valor", 0) for t in txs)

    return tot_p, tot_a, tot_f

def relatorio_por_tipo_agendamento() -> Dict[str, int]:
    """
    Retorna um dicionário {tipo_consulta: contador}.
    """
    counts: Dict[str,int] = {}
    for ag in agendamentos.obter_agendamentos():
        tipo = ag.get("tipo_consulta", "Desconhecido")
        counts[tipo] = counts.get(tipo, 0) + 1
    return counts
