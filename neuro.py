# app.py
import streamlit as st
import datetime
import pandas as pd
from banco_dados import inicializar_banco
from pacientes import adicionar_paciente, obter_pacientes
from agendamentos import adicionar_agendamento, obter_agendamentos
from prontuario import adicionar_prontuario, obter_prontuarios_por_paciente
from financeiro import adicionar_transacao, obter_transacoes
from comunicacao import adicionar_comunicacao
from laudos import adicionar_laudo, obter_laudos
from relatorios import gerar_relatorio, relatorio_por_tipo_agendamento

# Importa os componentes para menus e tabelas interativas
from streamlit_option_menu import option_menu
from st_aggrid import AgGrid, GridOptionsBuilder

# Inicializa o banco de dados
inicializar_banco()

# --- Funções auxiliares para exibir tabelas com AgGrid ---
def exibir_tabela(df):
    if not df.empty:
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_default_column(filter=True, sortable=True)
        gridOptions = gb.build()
        AgGrid(df, gridOptions=gridOptions, update_mode="MODEL_CHANGED")
    else:
        st.info("Nenhum dado para exibir.")

# --- Páginas do sistema ---

def pagina_inicial():
    st.title("Clinica Gilma Montenegro")
    st.write("Bem-vindo ao sistema de gestão do consultório!")
    st.image("https://via.placeholder.com/800x300.png?text=Dashboard+Consult%C3%B3rio", use_column_width=True)

def cadastro_pacientes():
    st.header("Cadastro de Pacientes")
    with st.form("form_cadastro"):
        nome = st.text_input("Nome")
        idade = st.number_input("Idade", min_value=0, max_value=150, step=1)
        contato = st.text_input("Contato")
        historico = st.text_area("Histórico Médico")
        enviado = st.form_submit_button("Salvar")
    if enviado:
        adicionar_paciente(nome, idade, contato, historico)
        st.success("Paciente cadastrado com sucesso!")
        
def agendamentos_pagina():
    st.header("Agendamento de Consultas")
    pacientes = obter_pacientes()
    if not pacientes:
        st.info("Cadastre um paciente primeiro!")
        return
    opcoes_paciente = { f"{p['id']} - {p['nome']}": p['id'] for p in pacientes }
    selecionado = st.selectbox("Selecione o Paciente", list(opcoes_paciente.keys()))
    paciente_id = opcoes_paciente[selecionado]
    with st.form("form_agendamento"):
        data_consulta = st.date_input("Data da Consulta", datetime.date.today())
        hora_consulta = st.time_input("Hora da Consulta", datetime.time(9, 0))
        observacoes = st.text_area("Observações")
        opcoes_tipo = ["Plano de Saúde", "Particular"]
        tipo_consulta = st.selectbox("Tipo de Consulta", opcoes_tipo)
        enviado = st.form_submit_button("Agendar")
    if enviado:
        adicionar_agendamento(paciente_id, data_consulta.isoformat(), hora_consulta.strftime("%H:%M"), observacoes, tipo_consulta)
        st.success("Consulta agendada com sucesso!")

def prontuario_pagina():
    st.header("Prontuário Eletrônico")
    pacientes = obter_pacientes()
    if not pacientes:
        st.info("Cadastre um paciente primeiro!")
        return
    opcoes_paciente = { f"{p['id']} - {p['nome']}": p['id'] for p in pacientes }
    selecionado = st.selectbox("Selecione o Paciente", list(opcoes_paciente.keys()))
    paciente_id = opcoes_paciente[selecionado]
    with st.form("form_prontuario"):
        descricao = st.text_area("Descrição / Registro de Atendimento")
        enviado = st.form_submit_button("Salvar Registro")
    if enviado:
        adicionar_prontuario(paciente_id, descricao, datetime.date.today().isoformat())
        st.success("Registro salvo com sucesso!")
        
    st.subheader("Histórico de Atendimentos")
    registros = obter_prontuarios_por_paciente(paciente_id)
    if registros:
        df_registros = pd.DataFrame(registros)
        exibir_tabela(df_registros)
    else:
        st.info("Nenhum registro encontrado.")

def financeiro_pagina():
    st.header("Gestão Financeira")
    pacientes = obter_pacientes()
    if not pacientes:
        st.info("Cadastre um paciente primeiro!")
        return
    opcoes_paciente = { f"{p['id']} - {p['nome']}": p['id'] for p in pacientes }
    selecionado = st.selectbox("Selecione o Paciente", list(opcoes_paciente.keys()))
    paciente_id = opcoes_paciente[selecionado]
    with st.form("form_financeiro"):
        data_transacao = st.date_input("Data da Transação", datetime.date.today())
        valor = st.number_input("Valor", min_value=0.0, step=0.1, format="%.2f")
        descricao = st.text_area("Descrição")
        enviado = st.form_submit_button("Registrar Transação")
    if enviado:
        adicionar_transacao(paciente_id, data_transacao.isoformat(), valor, descricao)
        st.success("Transação registrada!")
        
    st.subheader("Histórico Financeiro")
    transacoes = obter_transacoes()
    if transacoes:
        df_transacoes = pd.DataFrame(transacoes)
        exibir_tabela(df_transacoes)
    else:
        st.info("Nenhuma transação registrada.")

def comunicacao_pagina():
    st.header("Comunicação com Pacientes")
    pacientes = obter_pacientes()
    if not pacientes:
        st.info("Cadastre um paciente primeiro!")
        return
    opcoes_paciente = { f"{p['id']} - {p['nome']}": p['id'] for p in pacientes }
    selecionado = st.selectbox("Selecione o Paciente", list(opcoes_paciente.keys()))
    paciente_id = opcoes_paciente[selecionado]
    with st.form("form_comunicacao"):
        mensagem = st.text_area("Digite a mensagem")
        enviado = st.form_submit_button("Enviar")
    if enviado:
        adicionar_comunicacao(paciente_id, mensagem, datetime.datetime.now().isoformat())
        st.success("Mensagem enviada!")

def relatorios_pagina():
    st.header("Relatórios e Estatísticas")
    total_pacientes, total_agendamentos, total_financeiro = gerar_relatorio()
    st.write(f"**Total de Pacientes:** {total_pacientes}")
    st.write(f"**Total de Consultas Agendadas:** {total_agendamentos}")
    st.write(f"**Total Financeiro:** R$ {total_financeiro:.2f}")
    
    st.subheader("Consultas por Tipo")
    rel_tipo = relatorio_por_tipo_agendamento()
    if rel_tipo:
        for tipo, qtde in rel_tipo.items():
            st.write(f"{tipo}: {qtde} consulta(s)")
    else:
        st.info("Nenhuma consulta registrada.")
    
    st.subheader("Agendamentos")
    agendamentos = obter_agendamentos()
    if agendamentos:
        df_agendamentos = pd.DataFrame(agendamentos)
        exibir_tabela(df_agendamentos)
    else:
        st.info("Nenhuma consulta agendada.")

def dashboard_pagina():
    st.header("Dashboard")
    total_pacientes, total_agendamentos, total_financeiro = gerar_relatorio()
    col1, col2, col3 = st.columns(3)
    col1.metric("Pacientes", total_pacientes)
    col2.metric("Consultas", total_agendamentos)
    col3.metric("Financeiro", f"R$ {total_financeiro:.2f}")
    
    st.subheader("Gráfico: Consultas por Tipo")
    agendamentos = obter_agendamentos()
    if agendamentos:
        from collections import Counter
        tipos = [ag['tipo_consulta'] for ag in agendamentos if ag['tipo_consulta']]
        contagem = Counter(tipos)
        df_tipos = pd.DataFrame(list(contagem.items()), columns=["Tipo", "Quantidade"])
        st.bar_chart(df_tipos.set_index("Tipo"))
    else:
        st.info("Sem dados para o gráfico.")

def laudos_pagina():
    st.header("Emissão de Laudos")
    pacientes = obter_pacientes()
    if not pacientes:
        st.info("Cadastre um paciente primeiro!")
        return
    opcoes_paciente = { f"{p['id']} - {p['nome']}": p['id'] for p in pacientes }
    selecionado = st.selectbox("Selecione o Paciente", list(opcoes_paciente.keys()))
    paciente_id = opcoes_paciente[selecionado]
    with st.form("form_laudo"):
        laudo_texto = st.text_area("Digite o laudo")
        enviado = st.form_submit_button("Emitir Laudo")
    if enviado:
        adicionar_laudo(paciente_id, laudo_texto, datetime.date.today().isoformat())
        st.success("Laudo emitido com sucesso!")
        st.subheader("Laudo Emitido:")
        st.write(laudo_texto)
        
    st.subheader("Laudos Emitidos")
    lista_laudos = obter_laudos()
    if lista_laudos:
        df_laudos = pd.DataFrame(lista_laudos)
        exibir_tabela(df_laudos)
    else:
        st.info("Nenhum laudo encontrado.")

# --- Menu interativo usando streamlit-option-menu ---
def main():
    selected = option_menu(
        menu_title="Menu",
        options=["Início", "Dashboard", "Cadastro de Pacientes", "Agendamentos", 
                 "Prontuário", "Financeiro", "Comunicação", "Relatórios", "Laudos"],
        icons=["house", "bar-chart", "person-plus", "calendar", "file-text", "wallet", "chat-dots", "clipboard-data", "file-earmark-text"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal"
    )
    
    if selected == "Início":
        pagina_inicial()
    elif selected == "Dashboard":
        dashboard_pagina()
    elif selected == "Cadastro de Pacientes":
        cadastro_pacientes()
    elif selected == "Agendamentos":
        agendamentos_pagina()
    elif selected == "Prontuário":
        prontuario_pagina()
    elif selected == "Financeiro":
        financeiro_pagina()
    elif selected == "Comunicação":
        comunicacao_pagina()
    elif selected == "Relatórios":
        relatorios_pagina()
    elif selected == "Laudos":
        laudos_pagina()

if __name__ == "__main__":
    main()
