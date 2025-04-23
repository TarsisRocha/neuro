# auth.py – Módulo de autenticação com admin via st.secrets

import streamlit as st
from banco_dados import supabase
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

def login() -> dict:
    """
    1) tenta login de admin definido em st.secrets:
       st.secrets['admin_login'], st.secrets['admin_password']
    2) se não for admin, busca na tabela 'usuarios' do Supabase
    Retorna dict com keys: user, name, role, pid
    """
    st.title("Login")
    user_input = st.text_input("Usuário")
    pwd        = st.text_input("Senha", type="password")
    if not st.button("Entrar"):
        st.stop()

    # --- 1) Admin via secrets ---
    admin_login    = st.secrets.get("admin_login")
    admin_password = st.secrets.get("admin_password")
    if admin_login and admin_password and user_input == admin_login:
        if pwd == admin_password:
            sess = {"user": admin_login, "name": "Administrador", "role": "admin", "pid": None}
            st.session_state["auth"] = sess
            return sess
        else:
            st.error("Senha do admin incorreta.")
            st.stop()

    # --- 2) Usuário comum no Supabase ---
    resp = (
        supabase
        .table("usuarios")
        .select("login, senha_hash, role, paciente_id, nome")
        .eq("login", user_input)
        .execute()
    )
    registros = resp.data or []
    if len(registros) != 1:
        st.error("Usuário não encontrado.")
        st.stop()

    user = registros[0]
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
