# auth.py — Autenticação sem dependências externas
# ------------------------------------------------
import streamlit as st
import bcrypt
import json
from pathlib import Path
import users  # CRUD Supabase da tabela 'usuarios'

BASE_DIR    = Path(__file__).resolve().parent
LOCAL_CRED  = BASE_DIR / "users.json"  # opcional para testes locais

# Carrega credenciais do admin
if "admin_login" in st.secrets:
    ADMIN_LOGIN = st.secrets["admin_login"]
    ADMIN_HASH  = st.secrets["admin_hash"]
else:
    if not LOCAL_CRED.exists():
        raise RuntimeError("Defina admin_login/admin_hash em Secrets ou users.json")
    data = json.loads(LOCAL_CRED.read_text())
    ADMIN_LOGIN = data["admin"]["login"]
    ADMIN_HASH  = data["admin"]["hash"]

def _success(user, name, role, **extra):
    st.session_state.auth = {"user":user, "name":name, "role":role, **extra}
    st.experimental_rerun()

def login():
    if "auth" in st.session_state:
        return st.session_state.auth

    with st.form("login"):
        lg = st.text_input("Login")
        pw = st.text_input("Senha", type="password")
        ok = st.form_submit_button("Entrar")
    if not ok:
        st.stop()

    # Admin
    if lg == ADMIN_LOGIN and bcrypt.checkpw(pw.encode(), ADMIN_HASH.encode()):
        return _success(lg, "Administrador", "admin")

    # Usuário comum
    u = users.get_user(lg)
    if u and bcrypt.checkpw(pw.encode(), u["senha_hash"].encode()):
        return _success(u["login"], u["nome"], u["role"], pid=u.get("paciente_id"))

    st.error("Credenciais inválidas.")
    st.stop()
