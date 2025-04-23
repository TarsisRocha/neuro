# auth.py – Módulo de autenticação com persistência de sessão

import streamlit as st
from database import supabase
import bcrypt

def verify_password(pwd: str, hashed: str) -> bool:
    return bcrypt.checkpw(pwd.encode("utf-8"), hashed.encode("utf-8"))

def login() -> dict:
    """
    Se já existir st.session_state['auth'], retorna direto.
    Caso contrário, exibe formulário (admin via secrets ou Supabase).
    """
    # Se já logado, retorna os dados
    if "auth" in st.session_state:
        return st.session_state["auth"]

    st.title("Login")
    user_input = st.text_input("Usuário")
    pwd        = st.text_input("Senha", type="password")
    if not st.button("Entrar"):
        st.stop()

    # 1) Admin via secrets
    admin_login    = st.secrets.get("admin_login")
    admin_password = st.secrets.get("admin_password")
    admin_hash     = st.secrets.get("admin_hash")

    if admin_login and user_input == admin_login:
        if (admin_password and pwd == admin_password) or \
           (admin_hash and verify_password(pwd, admin_hash)):
            sess = {"user": admin_login, "name": "Administrador", "role": "admin", "pid": None}
            st.session_state["auth"] = sess
            return sess
        st.error("Senha do admin incorreta.")
        st.stop()

    # 2) Usuário no Supabase
    resp = (
        supabase
        .table("usuarios")
        .select("login, senha_hash, role, paciente_id, nome")
        .eq("login", user_input)
        .execute()
    )
    regs = resp.data or []
    if len(regs) != 1:
        st.error("Usuário não encontrado.")
        st.stop()

    user = regs[0]
    if not verify_password(pwd, user["senha_hash"]):
        st.error("Senha inválida.")
        st.stop()

    sess = {
        "user": user["login"],
        "name": user.get("nome", user["login"]),
        "role": user["role"],
        "pid":  user.get("paciente_id")
    }
    st.session_state["auth"] = sess
    return sess
