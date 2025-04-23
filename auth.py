# auth.py – Módulo de autenticação com fallback para usuário padrão nos secrets

import streamlit as st
from banco_dados import supabase
import bcrypt

def hash_password(password: str) -> str:
    """Gera hash para a senha informada."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    """Verifica senha contra o hash armazenado."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

def login() -> dict:
    """
    Exibe formulário de login e retorna dict com:
      user, name, role, pid (se for paciente).
    Primeiro tenta usuário padrão definido em st.secrets;
    caso contrário, consulta a tabela 'usuarios' no Supabase.
    """
    st.title("Login")
    user_input = st.text_input("Usuário")
    pwd        = st.text_input("Senha", type="password")
    if not st.button("Entrar"):
        st.stop()

    # 1) Verifica se é o admin padrão do secrets
    admin_login = st.secrets.get("admin_login")
    admin_pwd   = st.secrets.get("admin_password")
    if admin_login and admin_pwd and user_input == admin_login:
        if pwd == admin_pwd:
            sessão = {"user": admin_login, "name": "Administrador", "role": "admin", "pid": None}
            st.session_state["auth"] = sessão
            return sessão
        else:
            st.error("Senha do admin padrão inválida.")
            st.stop()

    # 2) Busca usuário no Supabase
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

    sessão = {
        "user": user["login"],
        "name": user.get("nome", user["login"]),
        "role": user["role"],
        "pid":  user.get("paciente_id")
    }
    st.session_state["auth"] = sessão
    return sessão
