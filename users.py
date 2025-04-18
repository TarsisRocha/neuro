# users.py — CRUD para tabela 'usuarios'
# --------------------------------------
import os, streamlit as st, bcrypt
from typing import Dict, List, Optional
from datetime import datetime
from supabase import create_client, Client

URL = os.getenv("SUPABASE_URL") or st.secrets["SUPABASE_URL"]
KEY = os.getenv("SUPABASE_KEY") or st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(URL, KEY)
TBL = "usuarios"

def _tbl():
    return supabase.table(TBL)

def hash_pwd(pwd: str) -> str:
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def check_pwd(pwd: str, hashed: str) -> bool:
    return bcrypt.checkpw(pwd.encode(), hashed.encode())

def criar_usuario(login: str, nome: str, senha: str, role: str = "paciente") -> int:
    item = {
        "login": login.lower(),
        "nome": nome,
        "senha_hash": hash_pwd(senha),
        "role": role,
        "criado_em": datetime.utcnow().isoformat()
    }
    res = _tbl().insert(item).execute()
    return res.data[0]["id"]

def get_user(login: str) -> Optional[Dict]:
    res = _tbl().select("*").eq("login", login.lower()).single().execute()
    return res.data

def listar_usuarios() -> List[Dict]:
    res = _tbl().select("id,login,nome,role,criado_em").order("login").execute()
    return res.data or []
