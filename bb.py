import os
import io
import re
import base64
from datetime import datetime

import pandas as pd
import streamlit as st

APP_TITLE = "Analisador de Extrato (MVP)"

st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)
st.caption("Importe um CSV/OFX, categorize automaticamente e veja o resumo por mês/categoria.")

# ---------- Helpers ----------
import pdfplumber

def _brl_to_float(s: str):
    if s is None:
        return None
    s = str(s).strip()
    if s == "" or s.lower() in ("nan", "none", "-"):
        return None
    # Remove currency symbols and spaces
    s = re.sub(r"[^\d,.-]", "", s)
    # Handle cases like "1.234,56" -> "1234.56"
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None

def parse_santander_pdf(file_bytes: bytes) -> pd.DataFrame:
    
    
    rows = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            # Tenta extrair todas as tabelas da página
            tables = page.extract_tables() or []
            for tbl in tables:
                # Limpa linhas vazias
                tbl = [ [ (c or "").strip() for c in row ] for row in tbl if any((c or "").strip() for c in row) ]
                if not tbl:
                    continue
                # Detecta header (primeira linha)
                header = [h.strip() for h in tbl[0]]
                body = tbl[1:]

                # Heurísticas comuns do Santander
                # 1) Header contendo Data | Descrição | Valor | (D/C) ou colunas Crédito/Débito
                hlower = [h.lower() for h in header]

                # Mapas por nome aproximado
                def find_col(names):
                    for cand in names:
                        for idx, h in enumerate(hlower):
                            if cand in h:
                                return idx
                    return None

                idx_data = find_col(["data", "lançamento", "dt"])
                idx_desc = find_col(["descri", "hist", "texto", "lançamento"])
                idx_val  = find_col(["valor", "r$", "vlr"])
                idx_cred = find_col(["crédito", "credito"])
                idx_deb  = find_col(["débito", "debito"])
                idx_dc   = find_col(["d/c", "dc", "tipo", "natureza"])

                # Se tiver Crédito/Débito separados, calcula sinal
                for r in body:
                    try:
                        data = r[idx_data] if idx_data is not None and idx_data < len(r) else None
                        desc = r[idx_desc] if idx_desc is not None and idx_desc < len(r) else None

                        # Monta valor
                        valor = None
                        if idx_cred is not None or idx_deb is not None:
                            cred = _brl_to_float(r[idx_cred]) if idx_cred is not None and idx_cred < len(r) else None
                            deb  = _brl_to_float(r[idx_deb])  if idx_deb  is not None and idx_deb  < len(r) else None
                            valor = (cred or 0.0) - (deb or 0.0)
                            # se ambos None, tenta coluna 'valor'
                            if (cred is None and deb is None) and idx_val is not None and idx_val < len(r):
                                valor = _brl_to_float(r[idx_val])
                        else:
                            # única coluna de valor, usa D/C para sinal se existir
                            rawv = r[idx_val] if idx_val is not None and idx_val < len(r) else None
                            valor = _brl_to_float(rawv)
                            if idx_dc is not None and idx_dc < len(r):
                                dc = str(r[idx_dc]).strip().upper()
                                if dc.startswith("D") and valor is not None and valor > 0:
                                    valor = -valor

                        # Normaliza data brasileira
                        d = None
                        if data:
                            for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"):
                                try:
                                    d = pd.to_datetime(data, format=fmt).date()
                                    break
                                except Exception:
                                    pass

                        if d and desc and (valor is not None):
                            rows.append((d, desc, valor))
                    except Exception:
                        continue

    if not rows:
        return pd.DataFrame(columns=["data","descricao","valor"])

    df = pd.DataFrame(rows, columns=["data","descricao","valor"])
    # Remove possíveis cabeçalhos repetidos como linhas
    df = df[df["descricao"].str.lower() != "descrição"]
    return df.reset_index(drop=True)

DATE_COLS = ["data", "date", "Data", "Posting Date", "Transaction Date"]
DESC_COLS = ["descricao", "description", "Memo", "Details", "Descrição"]
AMT_COLS  = ["valor", "amount", "Value", "Amount", "Valor"]

def _try_parse_date(s):
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(str(s)[:10], fmt).date()
        except Exception:
            continue
    return None

def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    cols = {c:str(c).strip() for c in df.columns}
    df = df.rename(columns=cols)

    # Map column names to canonical
    def pick(colnames, candidates):
        for c in candidates:
            if c in colnames:
                return c
        return None

    colnames = list(df.columns)
    dcol = pick(colnames, DATE_COLS)
    xcol = pick(colnames, DESC_COLS)
    vcol = pick(colnames, AMT_COLS)

    # Heurísticas extras
    if dcol is None:
        # tenta detectar por dtype/valores com '/'
        for c in colnames:
            if df[c].astype(str).str.contains(r"\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2}", na=False).any():
                dcol = c; break
    if xcol is None:
        for c in colnames:
            if "desc" in c.lower() or "memo" in c.lower() or "hist" in c.lower():
                xcol = c; break
    if vcol is None:
        # tenta col numérica com sinais
        numeric_cols = [c for c in colnames if pd.to_numeric(df[c], errors="coerce").notna().mean() > 0.7]
        if numeric_cols:
            vcol = numeric_cols[-1]

    if dcol is None or xcol is None or vcol is None:
        st.error(f"Não encontrei colunas padrão. Data:{dcol} | Descrição:{xcol} | Valor:{vcol}")
        st.stop()

    out = pd.DataFrame({
        "data": df[dcol].apply(_try_parse_date),
        "descricao": df[xcol].astype(str).str.strip(),
        "valor": pd.to_numeric(df[vcol], errors="coerce")
    })
    out = out.dropna(subset=["data","valor"]).reset_index(drop=True)
    out["dia"] = pd.to_datetime(out["data"]).dt.day
    out["ano_mes"] = pd.to_datetime(out["data"]).dt.to_period("M").astype(str)
    return out

# ---------- Regras de categorização ----------
DEFAULT_RULES = {
    r"PIX|Chave|Transfer(ê|e)ncia|TED|DOC": "Transferências",
    r"IFood|Rappi|Uber Eats|iFood": "Alimentação",
    r"Supermercado|Hiper|Atacad(ã|a)o|Carrefour|Assa(í|i)|Mercado": "Mercado",
    r"Uber|99\s?Pop|Táxi": "Transporte",
    r"Farm(á|a)cia|Drogasil|Pague\s*Menos|Drogaria": "Saúde",
    r"Vivo|Claro|TIM|Oi|Brisanet": "Telefonia/Internet",
    r"Netflix|Spotify|YouTube|Prime|Disney": "Assinaturas",
    r"CEF|CAIXA|BB|Bradesco|Ita(u|ú)|Santander|Nubank": "Bancário/Taxas",
    r"Aluguel|Imobili(á|a)ria": "Moradia",
    r"Posto|Combust(í|i)vel|Shell|Ipiranga|BR": "Combustível",
    r"(Anuidade|Tarifa|Pacote\s*Servi(ç|c)os)": "Tarifas Bancárias",
    r"Sal(á|a)rio|Pagamento|Proventos|Rendimento|Dep(ó|o)sito": "Entradas"
}

def apply_rules(desc: str, rules: dict) -> str:
    for pattern, cat in rules.items():
        if re.search(pattern, desc, flags=re.IGNORECASE):
            return cat
    # fallback heurística
    if "-" in desc and any(k in desc.lower() for k in ["deb", "pag", "comp", "cart"]):
        return "Cartão/Débito"
    return "Outros"

# ---------- Upload ----------
st.sidebar.header("Importação")
file = st.sidebar.file_uploader("Envie um arquivo CSV/OFX/PDF", type=["csv","ofx","txt","pdf"])
currency_symbol = st.sidebar.text_input("Símbolo da moeda (ex.: R$)", value="R$")
credit_positive = st.sidebar.selectbox("Crédito como positivo?", ["Sim","Não"], index=0)

# Regras editáveis
st.sidebar.header("Regras de categorização")
rules_text = st.sidebar.text_area("Regex => Categoria (um por linha)",
    value="\n".join([f"{k} => {v}" for k,v in DEFAULT_RULES.items()]), height=200)

def parse_rules(text):
    rules = {}
    for line in text.splitlines():
        if "=>" in line:
            k,v = line.split("=>", 1)
            rules[k.strip()] = v.strip()
    return rules or DEFAULT_RULES

rules = parse_rules(rules_text)

if file is not None:
    # Leitura básica
    try:
        if file.name.lower().endswith(".csv") or file.name.lower().endswith(".txt"):
            df_raw = pd.read_csv(file, sep=None, engine="python", encoding="utf-8")
        elif file.name.lower().endswith(".ofx"):
            # parse bem simples de OFX (Memo e Value)
            content = file.read().decode(errors="ignore")
            import re
            dates = re.findall(r"<DTPOSTED>(\d{8})", content)
            memos = re.findall(r"<MEMO>(.*?)\n", content)
            amts  = re.findall(r"<TRNAMT>(-?\d+[.,]?\d*)", content)
            df_raw = pd.DataFrame({"data": dates, "descricao": memos, "valor": amts})
            df_raw["data"] = pd.to_datetime(df_raw["data"], format="%Y%m%d").dt.date
        elif file.name.lower().endswith(".pdf"):
            pdf_bytes = file.read()
            df_raw = parse_santander_pdf(pdf_bytes)
        else:
            st.error("Formato não suportado.")
            st.stop()
    except Exception as e:
        st.exception(e)
        st.stop()

    df = normalize_df(df_raw)
    if credit_positive == "Não":
        df["valor"] = -df["valor"]

    # Categorias
    df["categoria"] = df["descricao"].apply(lambda s: apply_rules(s, rules))

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Movimentos", len(df))
    with col2:
        st.metric("Entradas", f"{currency_symbol} {df.loc[df['valor']>0,'valor'].sum():,.2f}")
    with col3:
        st.metric("Saídas", f"{currency_symbol} {df.loc[df['valor']<0,'valor'].sum():,.2f}")

    st.subheader("Resumo por mês")
    resumo_mes = df.groupby("ano_mes")["valor"].sum().reset_index().rename(columns={"valor":"saldo"})
    st.dataframe(resumo_mes)

    st.subheader("Resumo por categoria")
    resumo_cat = df.groupby("categoria")["valor"].sum().reset_index().sort_values("valor")
    st.dataframe(resumo_cat)

    st.subheader("Extrato normalizado")
    st.dataframe(df)

    # Export
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Baixar CSV normalizado", data=csv, file_name="extrato_normalizado.csv", mime="text/csv")

    # Dicas
    with st.expander("Dicas de uso"):
        st.write("""
        - Ajuste as *regras* na barra lateral para melhorar a categorização automática.
        - Se o banco exporta CSV com outros nomes de colunas, a detecção tenta mapear automaticamente.
        - Para saldo inicial, some manualmente ou importe um arquivo de mês anterior.
        """)
else:
    st.info("Envie um arquivo de extrato (CSV/OFX) pela barra lateral.")
    st.write("Bancos comuns: Nubank, Itaú, Caixa, Bradesco, Santander, Inter, C6 etc.")

st.caption("MVP local. Integrações (Supabase, dashboards detalhados, múltiplas contas) podem ser adicionadas.")