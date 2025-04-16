# relatorios.py
from pacientes import obter_pacientes
from agendamentos import obter_agendamentos
from financeiro import obter_transacoes

def gerar_relatorio():
    pacientes = obter_pacientes()
    agendamentos = obter_agendamentos()
    transacoes = obter_transacoes()
    
    total_pacientes = len(pacientes)
    total_agendamentos = len(agendamentos)
    total_financeiro = sum(t['valor'] for t in transacoes)
    
    return total_pacientes, total_agendamentos, total_financeiro

def relatorio_por_tipo_agendamento():
    agendamentos = obter_agendamentos()
    relatorio = {}
    for ag in agendamentos:
        tipo = ag['tipo_consulta'] if ag['tipo_consulta'] is not None else "Não informado"
        relatorio[tipo] = relatorio.get(tipo, 0) + 1
    return relatorio
