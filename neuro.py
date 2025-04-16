# app.py
import streamlit as st
import datetime
import pandas as pd
import numpy as np
from pacientes import adicionar_paciente, obter_pacientes
from agendamentos import adicionar_agendamento, obter_agendamentos
from prontuario import adicionar_prontuario, obter_prontuarios_por_paciente
from financeiro import adicionar_transacao, obter_transacoes
from comunicacao import adicionar_comunicacao
from laudos import adicionar_laudo, obter_laudos
from relatorios import gerar_relatorio, relatorio_por_tipo_agendamento

# Importando os componentes para menus interativos e tabelas
from streamlit_option_menu import option_menu
from st_aggrid import AgGrid, GridOptionsBuilder

# Função auxiliar para exibir DataFrames com AgGrid
def exibir_tabela(df):
    if not df.empty:
        # Garante que os nomes das colunas sejam strings
        df.columns = df.columns.map(str)
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_default_column(filter=True, sortable=True)
        gridOptions = gb.build()
        AgGrid(df, gridOptions=gridOptions, update_mode="MODEL_CHANGED")
    else:
        st.info("Nenhum dado para exibir.")

# --- Páginas do Sistema ---

def pagina_inicial():
    st.title("Consultório de Neuropediatria")
    st.write("Bem-vindo ao sistema de gestão do consultório!")
    st.image("https://via.placeholder.com/800x300.png?text=Dashboard+Consult%C3%B3rio", use_container_width=True)

def cadastro_pacientes():
    st.header("Cadastro de Pacientes")
    with st.form("form_cadastro"):
        nome = st.text_input("Nome")
        data_nascimento = st.date_input("Data de Nascimento")
        idade = st.number_input("Idade", min_value=0, max_value=150, step=1)
        cpf = st.text_input("CPF")
        rg = st.text_input("RG")
        email = st.text_input("E-mail")
        contato = st.text_input("Telefone")
        telefone_adicional = st.text_input("Telefone Adicional")
        endereco = st.text_input("Endereço")
        numero = st.text_input("Número")
        complemento = st.text_input("Complemento")
        bairro = st.text_input("Bairro")
        cep = st.text_input("CEP")
        cidade = st.text_input("Cidade")
        estado = st.text_input("Estado")
        plano_saude = st.text_input("Plano de Saúde")
        historico = st.text_area("Histórico Médico")
        observacoes = st.text_area("Observações")
        enviado = st.form_submit_button("Salvar")
    if enviado:
        adicionar_paciente(
            nome, data_nascimento.isoformat(), idade, cpf, rg, email,
            contato, telefone_adicional, endereco, numero, complemento,
            bairro, cep, cidade, estado, plano_saude, historico, observacoes
        )
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
        adicionar_agendamento(
            paciente_id, data_consulta.isoformat(), hora_consulta.strftime("%H:%M"),
            observacoes, tipo_consulta
        )
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
    st.markdown(f"### Indicadores Gerais")
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

# --- Dashboard Completo ---
def dashboard_pagina():
    st.header("Dashboard Completo")
    # Indicadores gerais
    total_pacientes, total_agendamentos, total_financeiro = gerar_relatorio()
    pacientes = obter_pacientes()
    if pacientes:
        media_idade = np.mean([p["idade"] for p in pacientes if p.get("idade") is not None])
    else:
        media_idade = 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Pacientes", total_pacientes)
    col2.metric("Consultas", total_agendamentos)
    col3.metric("Financeiro", f"R$ {total_financeiro:.2f}")
    col4.metric("Média de Idade", f"{media_idade:.1f}")

    st.markdown("---")
    # Catálogo de Pacientes interativo
    st.subheader("Catálogo de Pacientes")
    if pacientes:
        df_pacientes = pd.DataFrame(pacientes)
        # Filtro simples: por cidade, por exemplo
        cidades = df_pacientes["cidade"].unique()
        filtro_cidade = st.multiselect("Filtrar por Cidade", cidades, default=cidades)
        df_filtrado = df_pacientes[df_pacientes["cidade"].isin(filtro_cidade)]
        exibir_tabela(df_filtrado)
    else:
        st.info("Nenhum paciente cadastrado.")

    st.markdown("---")
    # Gráfico de Consultas por Mês
    st.subheader("Consultas por Mês")
    agendamentos = obter_agendamentos()
    if agendamentos:
        df_agendamentos = pd.DataFrame(agendamentos)
        # Converte a coluna 'data' para datetime e extrai o mês
        df_agendamentos["data_dt"] = pd.to_datetime(df_agendamentos["data"])
        df_agendamentos["mes"] = df_agendamentos["data_dt"].dt.to_period("M").astype(str)
        consultas_por_mes = df_agendamentos.groupby("mes").size().reset_index(name="consultas")
        st.bar_chart(consultas_por_mes.set_index("mes"))
    else:
        st.info("Nenhuma consulta registrada.")

    st.markdown("---")
    # Gráfico de Distribuição de Pacientes por Plano de Saúde
    st.subheader("Pacientes por Plano de Saúde")
    if pacientes:
        df_pacientes = pd.DataFrame(pacientes)
        plano_contagem = df_pacientes["plano_saude"].value_counts().reset_index()
        plano_contagem.columns = ["Plano", "Quantidade"]
        st.plotly_chart(
            {
                "data": [{
                    "labels": plano_contagem["Plano"],
                    "values": plano_contagem["Quantidade"],
                    "type": "pie"
                }],
                "layout": {"title": "Distribuição de Pacientes por Plano de Saúde"}
            },
            use_container_width=True
        )
    else:
        st.info("Nenhum paciente cadastrado.")

    st.markdown("---")
    # Histograma de Idades
    st.subheader("Distribuição Etária dos Pacientes")
    if pacientes:
        df_pacientes = pd.DataFrame(pacientes)
        st.histogram(df_pacientes["idade"].dropna(), bins=10)
    else:
        st.info("Nenhum paciente cadastrado.")

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
