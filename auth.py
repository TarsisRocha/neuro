import streamlit as st
from banco_dados import supabase
import bcrypt
import datetime

def hash_password(password: str) -> str:
    """Gera hash para a senha informada."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    """Verifica senha contra o hash armazenado."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

def login() -> dict:
    """
    Exibe formulário de login e retorna dict com
    user (login), name, role e pid (se paciente).
    """
    st.title("Login")
    login = st.text_input("Usuário")
    pwd   = st.text_input("Senha", type="password")
    if not st.button("Entrar"):
        st.stop()

    # Busca registro do usuário
    resp = (
        supabase
        .table("usuarios")
        .select("login, senha_hash, role, paciente_id, nome")
        .eq("login", login)
        .single()
        .execute()
    )
    user = resp.data
    if not user or not verify_password(pwd, user["senha_hash"]):
        st.error("Usuário ou senha inválidos.")
        st.stop()

    # Define sessão
    st.session_state["auth"] = {
        "user":      user["login"],
        "name":      user.get("nome", user["login"]),
        "role":      user["role"],
        "pid":       user.get("paciente_id")
    }
    return st.session_state["auth"]
