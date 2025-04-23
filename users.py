# users.py – Módulo de gerenciamento de usuários

import bcrypt
from typing import List, Dict
from database import supabase

def criar_usuario(
    login: str,
    nome: str,
    senha: str,
    role: str,
    paciente_id: int
) -> bool:
    """
    Cria um usuário no Supabase, garantindo que cada campo vá para a coluna certa.

    Parâmetros:
      - login: texto único do usuário
      - nome: nome completo do usuário
      - senha: texto em claro (será transformado em hash)
      - role: 'paciente' ou 'admin'
      - paciente_id: id do paciente vinculado (pode ser None para admin)

    Retorna True se criado com sucesso.
    """
    # Gera hash da senha
    senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # Monta registro com chaves idênticas ao schema do Supabase
    registro = {
        "login":       login,
        "nome":        nome,
        "senha_hash":  senha_hash,
        "role":        role,
        "paciente_id": paciente_id
    }

    resp = supabase.table("usuarios").insert(registro).execute()
    return bool(getattr(resp, "data", None))


def listar_usuarios() -> List[Dict]:
    """
    Retorna lista de usuários com campos:
      id, login, nome, senha_hash, role, paciente_id, criado_em, atualizado_em, created_at
    """
    resp = supabase.table("usuarios").select("*").execute()
    data = resp.data or []
    usuarios = []
    for u in data:
        usuarios.append({
            "id":             u.get("id"),
            "login":          u.get("login", ""),
            "nome":           u.get("nome", ""),
            "senha_hash":     u.get("senha_hash", ""),
            "role":           u.get("role", ""),
            "paciente_id":    u.get("paciente_id"),
            "criado_em":      u.get("criado_em"),
            "atualizado_em":  u.get("atualizado_em"),
            "created_at":     u.get("created_at")
        })
    return usuarios
