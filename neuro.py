# neuro.py – App principal para Clínica de Neuropediatria

import streamlit as st
from pathlib import Path
import datetime, os, textwrap, json
from io import BytesIO

import pandas as pd
import numpy as np
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from streamlit_option_menu import option_menu
from st_aggrid import AgGrid, GridOptionsBuilder

# ---- Diretórios e arquivos base ----
BASE_DIR   = Path(__file__).resolve().parent
LOGO_FILE  = BASE_DIR / "neuro.png"
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# ---- Configuração da página ----
st.set_page_config(
    page_title="Clínica de Neuropediatria",
    page_icon=str(LOGO_FILE),
    layout="wide"
)

# ---- Autenticação ----
import auth  # deve existir auth.py conforme instruído

auth_data   = auth.login()
user_key    = auth_data["user"]
user_name   = auth_data["name"]
role        = auth_data["role"]            # 'admin' ou 'paciente'
paciente_id = auth_data.get("pid")         # para pacientes

st.sidebar.success(f"Logado como {user_name} ({role})")
if st.sidebar.button("Sair"):
    st.session_state.pop("auth")
    st.experimental_rerun()

# ---- Logo na barra lateral ----
def sidebar_logo():
    if LOGO_FILE.exists():
        st.sidebar.image(str(LOGO_FILE), width=120)
    st.sidebar.markdown("---")

sidebar_logo()

# ---- Helper para tabelas ----
def aggrid_table(df: pd.DataFrame):
    if df is None or df.empty:
        st.info("Nenhum dado.")
        return
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_default_column(filter=True, sortable=True)
    AgGrid(df, gridOptions=gb.build(), update_mode="MODEL_CHANGED")

# ---- Geração de PDF para laudos ----
def gerar_pdf_laudo(texto: str, nome_pac: str):
    data_str = datetime.date.today().strftime("%d-%m-%Y")
    buf = BytesIO()
    pdf = pdfcanvas.Canvas(buf, pagesize=letter)
    w, h = letter
    if LOGO_FILE.exists():
        pdf.drawImage(
            ImageReader(str(LOGO_FILE)),
            (w-150)/2, h-70, width=150, height=50, mask="auto"
        )
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(w/2, h-90, "Consultório de Neuropediatria")
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawCentredString(w/2, h-110, "LAUDO MÉDICO")
    text_obj = pdf.beginText(40, h-140)
    text_obj.setFont("Helvetica", 12)
    text_obj.setLeading(18)
    for para in texto.split("\n\n"):
        for line in textwrap.wrap(para, 95):
            text_obj.textLine(line)
        text_obj.textLine("")
    pdf.drawText(text_obj)
    pdf.showPage()
    pdf.save()
    buf.seek(0)
    fname = f"laudo_{nome_pac.replace(' ','_')}_{data_str}.pdf"
    return buf, fname

# ---- Importa módulos de dados ----
import users, pacientes, agendamentos, prontuario, financeiro, comunicacao, relatorios
from laudo_templates import LAUDOS

# ---- Páginas do app ----

def page_dashboard():
    st.title("Dashboard")
    tot_p, tot_a, tot_f = relatorios.gerar_relatorio()
    c1, c2, c3 = st.columns(3)
    c1.metric("Pacientes", tot_p)
    c2.metric("Consultas", tot_a)
    c3.metric("Receita", f"R$ {tot_f:.2f}")

def page_pacientes():
    st.title("Pacientes")
    with st.expander("Novo paciente"):
        with st.form("cadpac"):
            nome = st.text_input("Nome completo")
            data_nasc_str = st.text_input("Data de nascimento (DD/MM/AAAA)")
            data_nasc = None
            idade = None
            if data_nasc_str:
                try:
                    data_nasc = datetime.datetime.strptime(
                        data_nasc_str, "%d/%m/%Y"
                    ).date()
                    hoje = datetime.date.today()
                    idade = hoje.year - data_nasc.year - (
                        (hoje.month, hoje.day) < (data_nasc.month, data_nasc.day)
                    )
                    st.write(f"Idade calculada: {idade} anos")
                except ValueError:
                    st.error("Formato inválido! Use DD/MM/AAAA")
            email = st.text_input("E‑mail")
            plano = st.text_input("Plano de Saúde")
            ok = st.form_submit_button("Salvar")
        if ok:
            if not nome or not data_nasc:
                st.error("Preencha nome e data corretamente.")
            else:
                pacientes.adicionar_paciente(
                    nome,
                    data_nasc.isoformat(),
                    idade,
                    "", "", email,
                    "", "",
                    "", "", "", "", "", "", "",
                    plano,
                    "", ""
                )
                st.success("Paciente cadastrado!")
    df = pd.DataFrame(pacientes.obter_pacientes())
    aggrid_table(df)

def page_agendamentos(admin=True, pid=None):
    st.title("Agendamentos")
    if admin:
        opc = {f"{p['id']} - {p['nome']}": p['id']
               for p in pacientes.obter_pacientes()}
        pid = opc[st.selectbox("Paciente", list(opc))]
    with st.expander("Novo agendamento"):
        with st.form("formag"):
            data_c = st.date_input("Data")
            hora_c = st.time_input("Hora")
            tipo = st.selectbox("Tipo", ["Plano de Saúde", "Particular"])
            obs = st.text_input("Observação")
            ok = st.form_submit_button("Agendar")
        if ok:
            agendamentos.adicionar_agendamento(
                pid, data_c.isoformat(),
                hora_c.strftime("%H:%M"), obs, tipo
            )
            st.success("Consulta agendada!")
    df = (pd.DataFrame(agendamentos.obter_agendamentos())
          if admin else
          pd.DataFrame(agendamentos.obter_agendamentos_por_paciente(pid)))
    aggrid_table(df)

def page_prontuarios(pid):
    st.title("Prontuário")
    with st.expander("Novo registro"):
        with st.form("formpr"):
            desc = st.text_area("Descrição")
            ok = st.form_submit_button("Salvar")
        if ok:
            prontuario.adicionar_prontuario(
                pid, desc, datetime.date.today().isoformat()
            )
            st.success("Registro salvo!")
    df = pd.DataFrame(prontuario.obter_prontuarios_por_paciente(pid))
    aggrid_table(df)

def page_financeiro(admin=True, pid=None):
    st.title("Financeiro")
    if admin:
        opc = {f"{p['id']} - {p['nome']}": p['id']
               for p in pacientes.obter_pacientes()}
        pid = opc[st.selectbox("Paciente", list(opc))]
    with st.expander("Nova transação"):
        with st.form("formfin"):
            data_m = st.date_input("Data")
            val = st.number_input("Valor", 0.0)
            desc = st.text_input("Descrição")
            ok = st.form_submit_button("Registrar")
        if ok:
            financeiro.adicionar_transacao(
                pid, data_m.isoformat(), val, desc
            )
            st.success("Transação registrada!")
    df = (pd.DataFrame(financeiro.obter_transacoes())
          if admin else
          pd.DataFrame(financeiro.obter_transacoes_por_paciente(pid)))
    aggrid_table(df)

def page_comunicacao():
    st.title("Enviar Mensagem")
    opc = {f"{p['id']} - {p['nome']}": p['id']
           for p in pacientes.obter_pacientes()}
    pid = opc[st.selectbox("Paciente", list(opc))]
    msg = st.text_area("Mensagem")
    if st.button("Enviar"):
        comunicacao.adicionar_comunicacao(
            pid, msg, datetime.datetime.now().isoformat()
        )
        st.success("Mensagem enviada!")

def page_laudos():
    st.title("Laudos")
    opc = {f"{p['id']} - {p['nome']}": p
           for p in pacientes.obter_pacientes()}
    pac = opc[st.selectbox("Paciente", list(opc))]
    modelo = st.selectbox("Modelo de Laudo", list(LAUDOS.keys()))
    texto = LAUDOS[modelo].format(
        nome=pac['nome'],
        data=datetime.date.today().strftime("%d/%m/%Y")
    )
    texto = st.text_area("Conteúdo", texto, height=300)
    if st.button("Gerar PDF"):
        buf, fname = gerar_pdf_laudo(texto, pac['nome'])
        st.download_button("Download PDF", buf, file_name=fname, mime="application/pdf")

def page_usuarios():
    st.title("Gerenciar Usuários")
    with st.expander("Criar Novo Usuário"):
        with st.form("formusr"):
            lg = st.text_input("Login")
            nm = st.text_input("Nome")
            pw = st.text_input("Senha", type="password")
            rl = st.selectbox("Perfil", ["paciente", "admin"])
            ok = st.form_submit_button("Criar")
        if ok:
            users.criar_usuario(lg, nm, pw, rl)
            st.success("Usuário criado!")
    df = pd.DataFrame(users.listar_usuarios())
    aggrid_table(df)

def page_relatorios():
    st.title("Relatórios")
    tot_p, tot_a, tot_f = relatorios.gerar_relatorio()
    c1, c2, c3 = st.columns(3)
    c1.metric("Pacientes", tot_p)
    c2.metric("Consultas", tot_a)
    c3.metric("Receita", f"R$ {tot_f:.2f}")
    st.subheader("Consultas por Tipo")
    for tp, qt in relatorios.relatorio_por_tipo_agendamento().items():
        st.write(f"{tp}: {qt}")

def page_minhas_consultas(pid):
    st.title("Minhas Consultas")
    df = pd.DataFrame(
        agendamentos.obter_agendamentos_por_paciente(pid)
    )
    aggrid_table(df)

def page_exames(pid):
    st.title("Meus Exames")
    file = st.file_uploader("Enviar exame (PDF/imagem)",
                             type=["pdf","png","jpg","jpeg"])
    if file and st.button("Enviar Exame"):
        dest = UPLOAD_DIR / f"{pid}_{file.name}"
        with dest.open("wb") as f:
            f.write(file.getbuffer())
        st.success("Exame enviado!")
    st.subheader("Arquivos enviados")
    for arq in UPLOAD_DIR.glob(f"{pid}_*"):
        st.write(f"- {arq.name}")

# ---- Roteador principal ----
if role == "admin":
    escolha = option_menu(None,
        ["Dashboard","Pacientes","Agendamentos","Prontuários",
         "Financeiro","Mensagens","Laudos","Usuários","Relatórios"],
        icons=["bar-chart","people","calendar","file-text","wallet",
               "chat-dots","file-earmark-pdf","person-check","clipboard-data"],
        orientation="horizontal"
    )
    if escolha == "Dashboard":      page_dashboard()
    elif escolha == "Pacientes":    page_pacientes()
    elif escolha == "Agendamentos": page_agendamentos(admin=True)
    elif escolha == "Prontuários":
        pid_sel = st.selectbox("Paciente ID",
                    [p['id'] for p in pacientes.obter_pacientes()])
        page_prontuarios(pid_sel)
    elif escolha == "Financeiro":   page_financeiro(admin=True)
    elif escolha == "Mensagens":    page_comunicacao()
    elif escolha == "Laudos":       page_laudos()
    elif escolha == "Usuários":     page_usuarios()
    elif escolha == "Relatórios":   page_relatorios()
else:
    escolha = option_menu(None,
        ["Meu Perfil","Meus Exames","Minhas Consultas"],
        icons=["person","file-earmark-arrow-up","calendar"],
        orientation="horizontal"
    )
    if escolha == "Meu Perfil":
        st.title("Meu Perfil")
        df = pd.DataFrame([pacientes.obter_paciente_por_login(user_key)])
        aggrid_table(df)
    elif escolha == "Meus Exames":
        page_exames(paciente_id)
    elif escolha == "Minhas Consultas":
        page_minhas_consultas(paciente_id)
