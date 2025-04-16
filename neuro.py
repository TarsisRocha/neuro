import streamlit as st
import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pacientes import adicionar_paciente, obter_pacientes
from agendamentos import adicionar_agendamento, obter_agendamentos
from prontuario import adicionar_prontuario, obter_prontuarios_por_paciente
from financeiro import adicionar_transacao, obter_transacoes
from comunicacao import adicionar_comunicacao
from laudos import adicionar_laudo, obter_laudos
from relatorios import gerar_relatorio, relatorio_por_tipo_agendamento

from streamlit_option_menu import option_menu
from st_aggrid import AgGrid, GridOptionsBuilder

# Configuração da página
st.set_page_config(
    page_title="Consultório de Neuropediatria",
    page_icon="logo.png",
    layout="wide"
)

def mostrar_logo():
    st.image("logo.png", width=200)
    st.markdown("---")

def exibir_tabela(df: pd.DataFrame):
    if not df.empty:
        df.columns = df.columns.map(str)
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_default_column(filter=True, sortable=True)
        gridOptions = gb.build()
        AgGrid(df, gridOptions=gridOptions, update_mode="MODEL_CHANGED")
    else:
        st.info("Nenhum dado para exibir.")

# --- Páginas ---

def pagina_inicial():
    st.title("Início")
    st.write("Bem‑vindo ao sistema de gestão do consultório de neuropediatria.")

def cadastro_pacientes():
    st.title("Cadastro de Pacientes")
    with st.form("form_cadastro"):
        nome = st.text_input("Nome")
        data_nascimento = st.date_input("Data de Nascimento")
        idade = st.number_input("Idade", min_value=0, max_value=150)
        cpf = st.text_input("CPF")
        rg = st.text_input("RG")
        email = st.text_input("E‑mail")
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
            nome,
            data_nascimento.isoformat(),
            idade,
            cpf,
            rg,
            email,
            contato,
            telefone_adicional,
            endereco,
            numero,
            complemento,
            bairro,
            cep,
            cidade,
            estado,
            plano_saude,
            historico,
            observacoes
        )
        st.success("Paciente cadastrado com sucesso!")

def agendamentos_pagina():
    st.title("Agendamento de Consultas")
    pacientes = obter_pacientes()
    if not pacientes:
        st.info("Cadastre um paciente primeiro!")
        return
    opcoes = {f"{p['id']} - {p['nome']}": p['id'] for p in pacientes}
    selecionado = st.selectbox("Selecione o Paciente", list(opcoes.keys()))
    paciente_id = opcoes[selecionado]
    with st.form("form_agendamento"):
        data_consulta = st.date_input("Data da Consulta", datetime.date.today())
        hora_consulta = st.time_input("Hora da Consulta", datetime.time(9, 0))
        observacoes = st.text_area("Observações")
        tipo = st.selectbox("Tipo de Consulta", ["Plano de Saúde", "Particular"])
        enviado = st.form_submit_button("Agendar")
    if enviado:
        adicionar_agendamento(
            paciente_id,
            data_consulta.isoformat(),
            hora_consulta.strftime("%H:%M"),
            observacoes,
            tipo
        )
        st.success("Consulta agendada com sucesso!")

def prontuario_pagina():
    st.title("Prontuário Eletrônico")
    pacientes = obter_pacientes()
    if not pacientes:
        st.info("Cadastre um paciente primeiro!")
        return
    opcoes = {f"{p['id']} - {p['nome']}": p['id'] for p in pacientes}
    sel = st.selectbox("Selecione o Paciente", list(opcoes.keys()))
    paciente_id = opcoes[sel]
    with st.form("form_prontuario"):
        descricao = st.text_area("Descrição de Atendimento")
        enviado = st.form_submit_button("Salvar Registro")
    if enviado:
        adicionar_prontuario(paciente_id, descricao, datetime.date.today().isoformat())
        st.success("Registro salvo com sucesso!")
    st.subheader("Histórico de Atendimentos")
    regs = obter_prontuarios_por_paciente(paciente_id)
    exibir_tabela(pd.DataFrame(regs))

def financeiro_pagina():
    st.title("Gestão Financeira")
    pacientes = obter_pacientes()
    if not pacientes:
        st.info("Cadastre um paciente primeiro!")
        return
    opcoes = {f"{p['id']} - {p['nome']}": p['id'] for p in pacientes}
    sel = st.selectbox("Selecione o Paciente", list(opcoes.keys()))
    paciente_id = opcoes[sel]
    with st.form("form_financeiro"):
        data_tx = st.date_input("Data da Transação", datetime.date.today())
        valor = st.number_input("Valor", min_value=0.0, step=0.1, format="%.2f")
        descricao = st.text_area("Descrição")
        enviado = st.form_submit_button("Registrar")
    if enviado:
        adicionar_transacao(paciente_id, data_tx.isoformat(), valor, descricao)
        st.success("Transação registrada com sucesso!")
    st.subheader("Histórico Financeiro")
    txs = obter_transacoes()
    exibir_tabela(pd.DataFrame(txs))

def comunicacao_pagina():
    st.title("Comunicação com Pacientes")
    pacientes = obter_pacientes()
    if not pacientes:
        st.info("Cadastre um paciente primeiro!")
        return
    opcoes = {f"{p['id']} - {p['nome']}": p['id'] for p in pacientes}
    sel = st.selectbox("Selecione o Paciente", list(opcoes.keys()))
    paciente_id = opcoes[sel]
    with st.form("form_comunicacao"):
        mensagem = st.text_area("Mensagem")
        enviado = st.form_submit_button("Enviar")
    if enviado:
        adicionar_comunicacao(paciente_id, mensagem, datetime.datetime.now().isoformat())
        st.success("Mensagem enviada com sucesso!")

def relatorios_pagina():
    st.title("Relatórios")
    tot_pac, tot_age, tot_fin = gerar_relatorio()
    st.write(f"**Pacientes:** {tot_pac}")
    st.write(f"**Consultas:** {tot_age}")
    st.write(f"**Financeiro:** R$ {tot_fin:.2f}")
    st.subheader("Consultas por Tipo")
    for tipo, qtd in relatorio_por_tipo_agendamento().items():
        st.write(f"{tipo}: {qtd} consulta(s)")

def buscar_paciente_pagina():
    st.title("Buscar Paciente")
    nome_busca = st.text_input("Digite o nome do paciente")
    if nome_busca:
        pacientes = obter_pacientes()
        matches = [p for p in pacientes if nome_busca.lower() in p["nome"].lower()]
        if matches:
            df = pd.DataFrame(matches)
            exibir_tabela(df)
            opção = st.selectbox(
                "Selecione o paciente para ver histórico",
                [f"{p['id']} - {p['nome']}" for p in matches]
            )
            paciente_id = int(opção.split(" - ")[0])
            st.subheader("Histórico de Atendimentos")
            regs = obter_prontuarios_por_paciente(paciente_id)
            exibir_tabela(pd.DataFrame(regs))
        else:
            st.warning("Nenhum paciente encontrado com esse nome.")

def dashboard_pagina():
    st.title("Dashboard Completo")
    tot_pac, tot_age, tot_fin = gerar_relatorio()
    pacs = obter_pacientes()
    media_idade = np.mean([p['idade'] for p in pacs if p.get('idade') is not None]) if pacs else 0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pacientes", tot_pac)
    c2.metric("Consultas", tot_age)
    c3.metric("Financeiro", f"R$ {tot_fin:.2f}")
    c4.metric("Média de Idade", f"{media_idade:.1f}")
    st.markdown("---")

    # Catálogo de Pacientes com múltiplos filtros
    st.subheader("Catálogo de Pacientes")
    if pacs:
        df_p = pd.DataFrame(pacs)
        cidades = df_p['cidade'].dropna().unique().tolist()
        estados = df_p['estado'].dropna().unique().tolist()
        planos = df_p['plano_saude'].dropna().unique().tolist()
        min_id, max_id = int(df_p['idade'].min()), int(df_p['idade'].max())
        idade_range = st.slider("Faixa de Idade", min_id, max_id, (min_id, max_id))
        filtro_cidades = st.multiselect("Filtrar por Cidade", cidades, default=cidades)
        filtro_estados = st.multiselect("Filtrar por Estado", estados, default=estados)
        filtro_planos = st.multiselect("Filtrar por Plano de Saúde", planos, default=planos)
        df_filtrado = df_p[
            df_p['cidade'].isin(filtro_cidades) &
            df_p['estado'].isin(filtro_estados) &
            df_p['plano_saude'].isin(filtro_planos) &
            df_p['idade'].between(*idade_range)
        ]
        exibir_tabela(df_filtrado)

    st.markdown("---")
    st.subheader("Consultas por Mês")
    ags = obter_agendamentos()
    if ags:
        df_ags = pd.DataFrame(ags)
        df_ags['data'] = pd.to_datetime(df_ags['data'])
        df_ags['mes'] = df_ags['data'].dt.to_period('M').astype(str)
        contagem = df_ags.groupby('mes').size().reset_index(name='qtd')
        st.bar_chart(contagem.set_index('mes'))

    st.markdown("---")
    st.subheader("Pacientes por Plano de Saúde")
    if pacs:
        df_p['plano_saude'] = df_p['plano_saude'].fillna('Não informado')
        plano_cnt = df_p['plano_saude'].value_counts().reset_index()
        plano_cnt.columns = ['Plano', 'qtd']
        fig = go.Figure(data=[go.Pie(labels=plano_cnt['Plano'], values=plano_cnt['qtd'])])
        fig.update_layout(title_text="Distribuição de Pacientes por Plano de Saúde")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Distribuição Etária dos Pacientes")
    if pacs:
        idades = [p['idade'] for p in pacs if p.get('idade') is not None]
        bins = np.histogram_bin_edges(idades, bins=10)
        hist, edges = np.histogram(idades, bins=bins)
        df_hist = pd.DataFrame({
            'faixa': [f"{int(edges[i])}-{int(edges[i+1])}" for i in range(len(edges)-1)],
            'qtd': hist
        })
        st.bar_chart(df_hist.set_index('faixa'))

def laudos_pagina():
    st.title("Laudos")
    pacs = obter_pacientes()
    if not pacs:
        st.info("Cadastre um paciente primeiro!")
        return
    op = {f"{p['id']} - {p['nome']}": p['id'] for p in pacs}
    sel = st.selectbox("Selecione o Paciente", list(op.keys()))
    paciente_id = op[sel]
    with st.form("form_laudo"):
        texto = st.text_area("Laudo")
        enviado = st.form_submit_button("Emitir Laudo")
    if enviado:
        adicionar_laudo(paciente_id, texto, datetime.date.today().isoformat())
        st.success("Laudo emitido com sucesso!")
    lds = obter_laudos()
    exibir_tabela(pd.DataFrame(lds))

def main():
    mostrar_logo()
    selected = option_menu(
        menu_title=None,
        options=[
            "Início", "Dashboard", "Buscar Paciente", "Cadastro de Pacientes",
            "Agendamentos", "Prontuário", "Financeiro", "Comunicação",
            "Relatórios", "Laudos"
        ],
        icons=[
            "house","bar-chart","search","person-plus","calendar",
            "file-text","wallet","chat-dots","clipboard-data","file-earmark-text"
        ],
        orientation="horizontal"
    )

    if selected == "Início":
        pagina_inicial()
    elif selected == "Dashboard":
        dashboard_pagina()
    elif selected == "Buscar Paciente":
        buscar_paciente_pagina()
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
