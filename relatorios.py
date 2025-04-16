# relatorios.py
from pacientes import obter_pacientes
from agendamentos import obter_agendamentos
from financeiro import obter_transacoes

def gerar_relatorio():
    pacientes = obter_pacientes()
    agendamentos = obter_agendamentos()
    transacoes = obter_transacoes()
    
    total_pacientes = len(pacientes) if pacientes else 0
    total_agendamentos = len(agendamentos) if agendamentos else 0
    total_financeiro = sum(t["valor"] for t in transacoes) if transacoes else 0
    
    return total_pacientes, total_agendamentos, total_financeiro

def relatorio_por_tipo_agendamento():
    agendamentos = obter_agendamentos()
    relatorio = {}
    for ag in agendamentos:
        tipo = ag.get("tipo_consulta", "Não informado")
        if tipo:
            relatorio[tipo] = relatorio.get(tipo, 0) + 1
    return relatorio
