import streamlit as st
import datetime
import pandas as pd
import numpy as np
import os
from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

from pacientes import adicionar_paciente, obter_pacientes
from agendamentos import adicionar_agendamento, obter_agendamentos
from prontuario import adicionar_prontuario, obter_prontuarios_por_paciente
from financeiro import adicionar_transacao, obter_transacoes
from comunicacao import adicionar_comunicacao
from relatorios import gerar_relatorio, relatorio_por_tipo_agendamento

from laudo_templates import LAUDOS

from streamlit_option_menu import option_menu
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(page_title="Consultório de Neuropediatria",
                   page_icon="neuro.png", layout="wide")

def mostrar_logo():
    st.image("neuro.png", width=150)
    st.markdown("---")

def exibir_tabela(df: pd.DataFrame):
    if df is None or df.empty:
        st.info("Nenhum dado para exibir.")
        return
    df.columns = df.columns.map(str)
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_default_column(filter=True, sortable=True)
    AgGrid(df, gridOptions=gb.build(), update_mode="MODEL_CHANGED")

def pagina_inicial():
    st.title("Início")
    st.write("Bem‑vindo ao sistema de gestão do consultório de neuropediatria.")

def cadastro_pacientes():
    st.title("Cadastro de Pacientes")
    with st.form("form_cadastro"):
        nome = st.text_input("Nome")
        data_nasc = st.date_input("Data de Nascimento")
        idade = st.number_input("Idade", min_value=0, max_value=150)
        cpf = st.text_input("CPF")
        rg = st.text_input("RG")
        email = st.text_input("E‑mail")
        tel = st.text_input("Telefone")
        tel2 = st.text_input("Telefone Adicional")
        endereco = st.text_input("Endereço")
        numero = st.text_input("Número")
        comp = st.text_input("Complemento")
        bairro = st.text_input("Bairro")
        cep = st.text_input("CEP")
        cidade = st.text_input("Cidade")
        estado = st.text_input("Estado")
        plano = st.text_input("Plano de Saúde")
        historico = st.text_area("Histórico Médico")
        obs = st.text_area("Observações")
        enviar = st.form_submit_button("Salvar")
    if enviar:
        adicionar_paciente(
            nome, data_nasc.isoformat(), idade,
            cpf, rg, email,
            tel, tel2, endereco, numero, comp,
            bairro, cep, cidade, estado,
            plano, historico, obs
        )
        st.success("Paciente cadastrado com sucesso!")

def agendamentos_pagina():
    st.title("Agendamento de Consultas")
    pacientes = obter_pacientes()
    if not pacientes:
        st.info("Cadastre um paciente primeiro!")
        return
    op = {f"{p['id']} - {p['nome']}": p['id'] for p in pacientes}
    sel = st.selectbox("Paciente", list(op.keys()))
    pid = op[sel]
    with st.form("form_agendamento"):
        data_c = st.date_input("Data da Consulta", datetime.date.today())
        hora_c = st.time_input("Hora da Consulta", datetime.time(9, 0))
        obs = st.text_area("Observações")
        tipo = st.selectbox("Tipo de Consulta", ["Plano de Saúde", "Particular"])
        enviar = st.form_submit_button("Agendar")
    if enviar:
        adicionar_agendamento(pid, data_c.isoformat(),
                              hora_c.strftime("%H:%M"), obs, tipo)
        st.success("Consulta agendada!")

def prontuario_pagina():
    st.title("Prontuário Eletrônico")
    pacientes = obter_pacientes()
    if not pacientes:
        st.info("Cadastre um paciente primeiro!")
        return
    op = {f"{p['id']} - {p['nome']}": p['id'] for p in pacientes}
    sel = st.selectbox("Paciente", list(op.keys()))
    pid = op[sel]
    with st.form("form_prontuario"):
        desc = st.text_area("Descrição de Atendimento")
        enviar = st.form_submit_button("Salvar")
    if enviar:
        adicionar_prontuario(pid, desc, datetime.date.today().isoformat())
        st.success("Registro salvo com sucesso!")
    regs = obter_prontuarios_por_paciente(pid)
    exibir_tabela(pd.DataFrame(regs))

def financeiro_pagina():
    st.title("Gestão Financeira")
    pacientes = obter_pacientes()
    if not pacientes:
        st.info("Cadastre um paciente primeiro!")
        return
    op = {f"{p['id']} - {p['nome']}": p['id'] for p in pacientes}
    sel = st.selectbox("Paciente", list(op.keys()))
    pid = op[sel]
    with st.form("form_financeiro"):
        data_f = st.date_input("Data da Transação", datetime.date.today())
        valor = st.number_input("Valor", min_value=0.0, step=0.1)
        desc = st.text_area("Descrição")
        enviar = st.form_submit_button("Registrar")
    if enviar:
        adicionar_transacao(pid, data_f.isoformat(), valor, desc)
        st.success("Transação registrada!")
    txs = obter_transacoes()
    exibir_tabela(pd.DataFrame(txs))

def comunicacao_pagina():
    st.title("Comunicação com Pacientes")
    pacientes = obter_pacientes()
    if not pacientes:
        st.info("Cadastre um paciente primeiro!")
        return
    op = {f"{p['id']} - {p['nome']}": p['id'] for p in pacientes}
    sel = st.selectbox("Paciente", list(op.keys()))
    pid = op[sel]
    with st.form("form_comunicacao"):
        msg = st.text_area("Mensagem")
        enviar = st.form_submit_button("Enviar")
    if enviar:
        adicionar_comunicacao(pid, msg, datetime.datetime.now().isoformat())
        st.success("Mensagem enviada!")

def relatorios_pagina():
    st.title("Relatórios e Estatísticas")
    tot_p, tot_a, tot_f = gerar_relatorio()
    st.write(f"**Pacientes:** {tot_p}")
    st.write(f"**Consultas:** {tot_a}")
    st.write(f"**Financeiro:** R$ {tot_f:.2f}")
    st.subheader("Consultas por Tipo")
    for t, q in relatorio_por_tipo_agendamento().items():
        st.write(f"{t}: {q} consulta(s)")

def dashboard_pagina():
    st.title("Dashboard Completo")
    tot_p, tot_a, tot_f = gerar_relatorio()
    pacs = obter_pacientes()
    media = np.mean([p['idade'] for p in pacs if p.get('idade') is not None]) if pacs else 0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pacientes", tot_p)
    c2.metric("Consultas", tot_a)
    c3.metric("Financeiro", f"R$ {tot_f:.2f}")
    c4.metric("Média de Idade", f"{media:.1f}")
    st.markdown("---")
    st.subheader("Catálogo de Pacientes")
    exibir_tabela(pd.DataFrame(pacs))

def buscar_paciente_pagina():
    st.title("Buscar Paciente")
    nome = st.text_input("Digite parte do nome")
    if nome:
        pacs = obter_pacientes()
        matches = [p for p in pacs if nome.lower() in p["nome"].lower()]
        if matches:
            exibir_tabela(pd.DataFrame(matches))
            op = {f"{p['id']} - {p['nome']}": p['id'] for p in matches}
            sel = st.selectbox("Ver histórico de", list(op.keys()))
            pid = op[sel]
            st.subheader("Histórico de Atendimentos")
            regs = obter_prontuarios_por_paciente(pid)
            exibir_tabela(pd.DataFrame(regs))
        else:
            st.warning("Nenhum paciente encontrado.")

def laudos_pagina():
    st.title("Emissão de Laudo em PDF")
    pacientes = obter_pacientes()
    if not pacientes:
        st.info("Cadastre um paciente primeiro!")
        return

    op_p = {f"{p['id']} - {p['nome']}": p for p in pacientes}
    sel_p = st.selectbox("Paciente", list(op_p.keys()))
    pac = op_p[sel_p]

    modelo_key = st.selectbox("Modelo de Laudo", list(LAUDOS.keys()))
    template_text = LAUDOS[modelo_key]

    st.markdown("**Edite o texto. Use `{nome}` e `{data}` como placeholders.**")
    laudo_txt = st.text_area("Conteúdo do Laudo", value=template_text, height=300)

    if st.button("Gerar PDF"):
        ctx = {
            "nome": pac["nome"],
            "data": datetime.date.today().strftime("%d/%m/%Y")
        }
        rendered = laudo_txt.format(**ctx)

        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        w, h = letter

        logo = "neuro.png"
        if os.path.exists(logo):
            img = ImageReader(logo)
            lw, lh = 150, 50
            c.drawImage(img, (w-lw)/2, h-lh-20, width=lw, height=lh, mask="auto")

        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(w/2, h-lh-40, "Consultório de Neuropediatria")

        text_obj = c.beginText(40, h-lh-80)
        text_obj.setFont("Helvetica", 12)
        text_obj.setLeading(16)
        for line in rendered.split("\n"):
            text_obj.textLine(line)
        c.drawText(text_obj)

        c.showPage()
        c.save()
        buf.seek(0)

        fn = f"laudo_{pac['nome'].replace(' ','_')}_{ctx['data'].replace('/','-')}.pdf"
        st.download_button("Download do Laudo (PDF)", buf, file_name=fn, mime="application/pdf")

def main():
    mostrar_logo()
    choice = option_menu(
        None,
        ["Início","Dashboard","Buscar Paciente","Cadastro de Pacientes","Agendamentos",
         "Prontuário","Financeiro","Comunicação","Relatórios","Laudos"],
        ["house","bar-chart","search","person-plus","calendar","file-text",
         "wallet","chat-dots","clipboard-data","file-earmark-text"],
        default_index=0,
        orientation="horizontal"
    )
    if choice=="Início": pagina_inicial()
    elif choice=="Dashboard": dashboard_pagina()
    elif choice=="Buscar Paciente": buscar_paciente_pagina()
    elif choice=="Cadastro de Pacientes": cadastro_pacientes()
    elif choice=="Agendamentos": agendamentos_pagina()
    elif choice=="Prontuário": prontuario_pagina()
    elif choice=="Financeiro": financeiro_pagina()
    elif choice=="Comunicação": comunicacao_pagina()
    elif choice=="Relatórios": relatorios_pagina()
    elif choice=="Laudos": laudos_pagina()

if __name__=="__main__":
    main()
