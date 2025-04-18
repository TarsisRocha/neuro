# app.py – Gestor de Clínica de Neuropediatria
# -------------------------------------------
# • Autenticação admin/paciente (streamlit‑authenticator)
# • Dashboard, pacientes, agenda, prontuário, financeiro, mensagens
# • Emissão de laudos em PDF
# • Área do paciente para upload de exames
# • Tabelas interativas com AgGrid
# -------------------------------------------

import streamlit as st
import streamlit_authenticator as stauth           # pip install streamlit-authenticator
from streamlit_option_menu import option_menu
from st_aggrid import AgGrid, GridOptionsBuilder

import datetime, os, json, textwrap
from pathlib import Path
from io import BytesIO

import pandas as pd
import numpy as np
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

# ───────────── Caminhos base ─────────────
BASE_DIR   = Path(__file__).resolve().parent
LOGO_FILE  = BASE_DIR / "neuro.png"
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# ──────────── Funções de dados (exemplos) ────────────
# Troque por chamadas reais ao Supabase.
from pacientes import (adicionar_paciente, obter_pacientes,
                       obter_paciente_por_login)
from agendamentos import (adicionar_agendamento, obter_agendamentos,
                          obter_agendamentos_por_paciente)
from prontuario import (adicionar_prontuario,
                        obter_prontuarios_por_paciente)
from financeiro  import (adicionar_transacao, obter_transacoes,
                         obter_transacoes_por_paciente)
from comunicacao import adicionar_comunicacao
from relatorios  import gerar_relatorio, relatorio_por_tipo_agendamento
from laudo_templates import LAUDOS             # dicionário de modelos

# ───────────── Config página ──────────────
st.set_page_config("Clínica de Neuropediatria",
                   page_icon=str(LOGO_FILE), layout="wide")

# ───────────── Autenticação ───────────────
if "users" in st.secrets:
    credentials = st.secrets["users"]
else:
    with (BASE_DIR / "users.json").open() as f:
        credentials = json.load(f)

authenticator = stauth.Authenticate(
    credentials,           # dict no formato do streamlit‑authenticator
    cookie_name="neurocookie",
    key="supersecret",
    cookie_expiry_days=7,
)

user_name, status, user_key = authenticator.login("Login", "main")

if status is False:
    st.error("Usuário ou senha incorretos."); st.stop()
elif status is None:
    st.info("Digite usuário e senha."); st.stop()

role = credentials["usernames"][user_key]["role"]   # "admin" ou "paciente"
st.sidebar.success(f"Logado como {user_name} ({role})")
authenticator.logout("Sair", "sidebar")

# ───────────── Helpers UI ────────────────
def logo_sidebar():
    st.sidebar.image(str(LOGO_FILE), width=120)
    st.sidebar.markdown("---")

def aggrid(df: pd.DataFrame):
    if df.empty:
        st.info("Nenhum dado."); return
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_default_column(filter=True, sortable=True)
    AgGrid(df, gridOptions=gb.build(), update_mode="MODEL_CHANGED")

logo_sidebar()

# ───────────── PDF Laudo ──────────────────
def gerar_pdf(texto: str, paciente: str):
    data_str = datetime.date.today().strftime("%d-%m-%Y")
    buf = BytesIO()
    pdf = pdfcanvas.Canvas(buf, pagesize=letter)
    w,h = letter
    if LOGO_FILE.exists():
        pdf.drawImage(ImageReader(str(LOGO_FILE)), (w-150)/2, h-70, 150, 50, mask="auto")
    pdf.setFont("Helvetica-Bold",16)
    pdf.drawCentredString(w/2, h-90, "Consultório de Neuropediatria")
    pdf.setFont("Helvetica-Bold",14)
    pdf.drawCentredString(w/2, h-110, "LAUDO MÉDICO")
    tx = pdf.beginText(40, h-140)
    tx.setFont("Helvetica",12); tx.setLeading(18)
    for para in texto.split("\n\n"):
        for line in textwrap.wrap(para, 95):
            tx.textLine(line)
        tx.textLine("")
    pdf.drawText(tx)
    pdf.showPage(); pdf.save(); buf.seek(0)
    return buf, f"laudo_{paciente.replace(' ','_')}_{data_str}.pdf"

# ───────────── Páginas ADMIN ──────────────
def page_dashboard():
    st.title("Dashboard")
    tot_p, tot_a, tot_f = gerar_relatorio()
    c1,c2,c3 = st.columns(3)
    c1.metric("Pacientes", tot_p)
    c2.metric("Consultas", tot_a)
    c3.metric("Receita", f"R$ {tot_f:.2f}")

def page_pacientes():
    st.title("Pacientes")
    with st.expander("Novo paciente"):
        with st.form("cad"):
            nome = st.text_input("Nome completo")
            nasc = st.date_input("Nascimento")
            idade = st.number_input("Idade",0,150)
            email = st.text_input("Email")
            ok = st.form_submit_button("Salvar")
        if ok:
            adicionar_paciente(nome, nasc.isoformat(), idade,
                               "", "", email, "", "", "", "", "", "",
                               "", "", "", "", "", "")
            st.success("Cadastrado!")
    aggrid(pd.DataFrame(obter_pacientes()))

def page_agenda(admin=True, pid=None):
    st.title("Agendamentos")
    if admin:
        op = {f"{p['id']} - {p['nome']}": p['id'] for p in obter_pacientes()}
        pid = op[st.selectbox("Paciente", list(op))]
    with st.expander("Novo agendamento"):
        with st.form("ag"):
            data = st.date_input("Data")
            hora = st.time_input("Hora")
            tipo = st.selectbox("Tipo",["Plano de Saúde","Particular"])
            obs = st.text_input("Obs.")
            ok = st.form_submit_button("Salvar")
        if ok:
            adicionar_agendamento(pid, data.isoformat(), hora.strftime("%H:%M"), obs, tipo)
            st.success("Agendado!")
    df = (pd.DataFrame(obter_agendamentos())
          if admin else
          pd.DataFrame(obter_agendamentos_por_paciente(pid)))
    aggrid(df)

def page_prontuario(pid):
    st.title("Prontuário do paciente")
    with st.expander("Novo registro"):
        with st.form("pr"):
            desc = st.text_area("Descrição")
            ok = st.form_submit_button("Salvar")
        if ok:
            adicionar_prontuario(pid, desc, datetime.date.today().isoformat())
            st.success("Salvo!")
    aggrid(pd.DataFrame(obter_prontuarios_por_paciente(pid)))

def page_financeiro(admin=True, pid=None):
    st.title("Financeiro")
    if admin:
        op = {f"{p['id']} - {p['nome']}": p['id'] for p in obter_pacientes()}
        pid = op[st.selectbox("Paciente", list(op))]
    with st.expander("Nova transação"):
        with st.form("fin"):
            data = st.date_input("Data")
            valor = st.number_input("Valor",0.0)
            desc  = st.text_input("Descrição")
            ok = st.form_submit_button("Salvar")
        if ok:
            adicionar_transacao(pid, data.isoformat(), valor, desc)
            st.success("Lançado!")
    df = (pd.DataFrame(obter_transacoes())
          if admin else
          pd.DataFrame(obter_transacoes_por_paciente(pid)))
    aggrid(df)

def page_mensagens():
    st.title("Enviar mensagem")
    op = {f"{p['id']} - {p['nome']}": p['id'] for p in obter_pacientes()}
    pid = op[st.selectbox("Paciente", list(op))]
    msg = st.text_area("Mensagem")
    if st.button("Enviar"):
        adicionar_comunicacao(pid, msg, datetime.datetime.now().isoformat())
        st.success("Enviado!")

def page_laudos():
    st.title("Laudos")
    op = {f"{p['id']} - {p['nome']}": p for p in obter_pacientes()}
    pac = op[st.selectbox("Paciente", list(op))]
    modelo = st.selectbox("Modelo", list(LAUDOS))
    texto = LAUDOS[modelo].format(nome=pac['nome'], data=datetime.date.today().strftime("%d/%m/%Y"))
    texto = st.text_area("Conteúdo", texto, height=300)
    if st.button("Gerar PDF"):
        buf, fname = gerar_pdf(texto, pac['nome'])
        st.download_button("Download", buf, file_name=fname, mime="application/pdf")

def page_relatorios():
    st.title("Relatórios")
    tot_p, tot_a, tot_f = gerar_relatorio()
    c1,c2,c3 = st.columns(3)
    c1.metric("Pacientes", tot_p)
    c2.metric("Consultas", tot_a)
    c3.metric("Receita", f"R$ {tot_f:.2f}")
    st.subheader("Consultas por tipo")
    for k,v in relatorio_por_tipo_agendamento().items():
        st.write(f"{k}: {v}")

# ───────────── Páginas Paciente ───────────
def page_perfil(pac):
    st.title("Meu perfil")
    aggrid(pd.DataFrame([pac]))

def page_exames(pac):
    st.title("Meus exames")
    file = st.file_uploader("Enviar arquivo", ["pdf","png","jpg","jpeg"])
    if file and st.button("Salvar"):
        dest = UPLOAD_DIR / f"{pac['id']}_{file.name}"
        with dest.open("wb") as f: f.write(file.getbuffer())
        st.success("Enviado!")
    st.write("Arquivos:")
    for arq in UPLOAD_DIR.glob(f"{pac['id']}_*"):
        st.write(f"- {arq.name}")

# ───────────── Router ─────────────────────
if role == "admin":
    menu = option_menu(None,
        ["Dashboard","Pacientes","Agendamentos","Prontuários","Financeiro",
         "Mensagens","Laudos","Relatórios"],
        icons=["bar-chart","people","calendar","file-text","wallet",
               "chat-dots","file-earmark-pdf","clipboard-data"],
        orientation="horizontal")
    if menu=="Dashboard": page_dashboard()
    elif menu=="Pacientes": page_pacientes()
    elif menu=="Agendamentos": page_agenda()
    elif menu=="Prontuários":
        pid = st.selectbox("Paciente", [p['id'] for p in obter_pacientes()])
        page_prontuario(pid)
    elif menu=="Financeiro": page_financeiro()
    elif menu=="Mensagens": page_mensagens()
    elif menu=="Laudos": page_laudos()
    elif menu=="Relatórios": page_relatorios()
else:
    pac_self = obter_paciente_por_login(user_key)
    menu = option_menu(None,
        ["Meu Perfil","Meus Exames","Minhas Consultas"],
        icons=["person","file-earmark-arrow-up","calendar"],
        orientation="horizontal")
    if menu=="Meu Perfil": page_perfil(pac_self)
    elif menu=="Meus Exames": page_exames(pac_self)
    elif menu=="Minhas Consultas": page_agenda(admin=False, pid=pac_self['id'])