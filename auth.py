# auth.py – Módulo de autenticação

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
    - user: login
    - name: nome completo (se disponível)
    - role: 'admin' ou 'paciente'
    - pid: id do paciente (se role for 'paciente')
    """
    st.title("Login")
    user_input = st.text_input("Usuário")
    pwd        = st.text_input("Senha", type="password")
    if not st.button("Entrar"):
        st.stop()

    # Busca usuário no Supabase
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
        "pid": user.get("paciente_id")
    }
    st.session_state["auth"] = sessão
    return sessão
