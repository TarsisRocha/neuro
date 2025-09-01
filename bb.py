# app.py — Analisador de Extrato (MVP) — versão corrigida

import io
import re
import unicodedata
from typing import List, Tuple, Optional

import pandas as pd
import streamlit as st

# ===== Config =====
APP_TITLE = "Analisador de Extrato (MVP)"
st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)
st.caption("Importe CSV/OFX/PDF, normalize, categorize por regras e veja resumos.")

# ===== Sidebar =====
st.sidebar.header("Importação")
file = st.sidebar.file_uploader("Envie um arquivo CSV/OFX/PDF", type=["csv", "ofx", "txt", "pdf"])
currency_symbol = st.sidebar.text_input("Símbolo da moeda", value="R$")
credit_positive = st.sidebar.selectbox("Crédito como positivo?", ["Sim", "Não"], index=0)
show_debug = st.sidebar.checkbox("Modo debug", value=False)

st.sidebar.header("Regras de categorização (ordem = prioridade)")
DEFAULT_RULES_LIST = [
    (r"\b(CASHBACK|ESTORNO)\b", "Ajustes/Entradas"),
    (r"\bPIX\s*(RECEB|CRED|ENTR)\b", "Entradas"),
    (r"\bSal(á|a)rio\b|Proventos|Rendimento|Dep(ó|o)sito|Receb\.", "Entradas"),
    (r"\bPIX\b", "Transferências"),
    (r"\bTED|DOC|TRANSFER(Ê|E)NCIA\b", "Transferências"),
    (r"IFood|iFood|Rappi|Uber\s*Eats", "Alimentação"),
    (r"Mercado\s*Livre|Carrefour|Assa(í|i)|Atacad(ã|a)o|Supermercado|Hiper", "Mercado"),
    (r"\bPosto\b|Combust(í|i)vel|Shell|Ipiranga|BR\b", "Combustível"),
    (r"Uber(?!\s*Eats)|99\s?Pop|Táxi", "Transporte"),
    (r"Farm(á|a)cia|Drogasil|Pague\s*Menos|Drogaria", "Saúde"),
    (r"Brisanet|Vivo|Claro|TIM|Oi", "Telefonia/Internet"),
    (r"Netflix|Spotify|YouTube|Prime|Disney", "Assinaturas"),
    (r"Aluguel|Imobili(á|a)ria", "Moradia"),
    (r"\b(Anuidade|Tarifa|Pacote\s*Servi(ç|c)os)\b", "Tarifas Bancárias"),
    (r"\bDARF\b|\bGPS\b|\bSEFAZ\b|Imposto", "Impostos/Taxas"),
    (r"\b(CART(Ã|A)O|DEB(IT|IT.)|PAGTO\s*CART|\bCOMPRA\b)", "Cartão/Débito"),
    (r"CEF|CAIXA|BB|Bradesco|Ita(u|ú)|Santander|Nubank|Inter|C6", "Bancário/Taxas"),
    (r".*", "Outros"),
]
_rules_default_text = "\n".join([f"{pat} => {cat}" for pat, cat in DEFAULT_RULES_LIST])
rules_text = st.sidebar.text_area("Regex => Categoria (um por linha)", value=_rules_default_text, height=260)

# ===== Regras helpers =====
def parse_rules(text: str) -> List[Tuple[str, str]]:
    rules: List[Tuple[str, str]] = []
    for line in text.splitlines():
        if "=>" in line:
            pat, cat = line.split("=>", 1)
            rules.append((pat.strip(), cat.strip()))
    return rules or DEFAULT_RULES_LIST

def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def apply_rules(desc: str, rules: List[Tuple[str, str]]) -> str:
    d = strip_accents(desc or "")
    for pattern, cat in rules:
        if re.search(pattern, d, flags=re.IGNORECASE):
            return cat
    return "Outros"

# ===== Normalização corrigida =====
DATE_CANDIDATES = ["data", "date", "Data", "Posting Date", "Transaction Date"]
DESC_CANDIDATES = ["descricao", "description", "Memo", "Details", "Descrição", "Histórico", "Historico", "Texto"]
AMT_CANDIDATES  = ["valor", "amount", "Value", "Amount", "Valor"]

def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=["data", "descricao", "valor"])

    cols = {c: str(c).strip() for c in df.columns}
    df = df.rename(columns=cols)
    colnames = list(df.columns)

    def pick(cands):
        for c in cands:
            if c in colnames:
                return c
        return None

    dcol = pick(DATE_CANDIDATES)
    xcol = pick(DESC_CANDIDATES)
    vcol = pick(AMT_CANDIDATES)

    if dcol is None:
        for c in colnames:
            try:
                if df[c].astype(str).str.contains(r"\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2}", na=False).any():
                    dcol = c; break
            except Exception:
                pass

    if xcol is None:
        for c in colnames:
            cl = c.lower()
            if "desc" in cl or "memo" in cl or "hist" in cl or "texto" in cl:
                xcol = c; break

    if vcol is None:
        numc = []
        for c in colnames:
            try:
                ratio = pd.to_numeric(df[c], errors="coerce").notna().mean()
            except Exception:
                ratio = 0
            if ratio > 0.6:
                numc.append(c)
        if numc:
            vcol = numc[-1]

    if dcol is None or xcol is None or vcol is None:
        return pd.DataFrame(columns=["data", "descricao", "valor"])

    # Trata valor (BRL com . de milhar e , decimal)
    valor_series = (
        df[vcol]
        .astype(str)
        .str.replace("\u00A0", " ", regex=False)       # NBSP
        .str.replace(".", "", regex=False)             # remove milhar
        .str.replace(",", ".", regex=False)            # vírgula -> ponto
    )

    out = pd.DataFrame({
        "data": df[dcol],
        "descricao": df[xcol].astype(str).str.strip(),
        "valor": pd.to_numeric(valor_series, errors="coerce"),
    })

    # ✅ força datetime antes de usar .dt
    out["data"] = pd.to_datetime(out["data"], errors="coerce", dayfirst=True)
    out = out.dropna(subset=["data", "valor"]).reset_index(drop=True)
    out["data"] = out["data"].dt.date  # agora .dt é seguro

    out["dia"] = pd.to_datetime(out["data"]).dt.day
    out["ano_mes"] = pd.to_datetime(out["data"]).dt.to_period("M").astype(str)
    return out

# ===== PDF (pdfplumber + OCR) =====
def _brl_to_float(s: str) -> Optional[float]:
    if s is None:
        return None
    s = str(s).strip()
    if s == "" or s.lower() in ("nan", "none", "-"):
        return None
    s = re.sub(r"[^\d,.-]", "", s)
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None

def parse_santander_pdf(file_bytes: bytes) -> pd.DataFrame:
    try:
        import pdfplumber
    except Exception:
        return pd.DataFrame(columns=["data", "descricao", "valor"])

    rows = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables() or []
            for tbl in tables:
                tbl = [[(c or "").strip() for c in row] for row in tbl if any((c or "").strip() for c in row)]
                if not tbl:
                    continue
                header = [h.strip() for h in tbl[0]]
                body = tbl[1:]
                hlower = [h.lower() for h in header]

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

                for r in body:
                    try:
                        data = r[idx_data] if idx_data is not None and idx_data < len(r) else None
                        desc = r[idx_desc] if idx_desc is not None and idx_desc < len(r) else None
                        valor = None
                        if idx_cred is not None or idx_deb is not None:
                            cred = _brl_to_float(r[idx_cred]) if idx_cred is not None and idx_cred < len(r) else None
                            deb  = _brl_to_float(r[idx_deb])  if idx_deb  is not None and idx_deb  < len(r) else None
                            valor = (cred or 0.0) - (deb or 0.0)
                            if (cred is None and deb is None) and idx_val is not None and idx_val < len(r):
                                valor = _brl_to_float(r[idx_val])
                        else:
                            rawv = r[idx_val] if idx_val is not None and idx_val < len(r) else None
                            valor = _brl_to_float(rawv)
                            if idx_dc is not None and idx_dc < len(r):
                                dc = str(r[idx_dc]).strip().upper()
                                if dc.startswith("D") and valor is not None and valor > 0:
                                    valor = -valor

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
        return pd.DataFrame(columns=["data", "descricao", "valor"])

    df = pd.DataFrame(rows, columns=["data", "descricao", "valor"])
    df = df[df["descricao"].str.lower() != "descrição"]
    return df.reset_index(drop=True)

def parse_pdf_with_ocr(file_bytes: bytes) -> pd.DataFrame:
    try:
        import pdf2image, pytesseract
    except Exception:
        return pd.DataFrame(columns=["data", "descricao", "valor"])

    try:
        images = pdf2image.convert_from_bytes(file_bytes, dpi=200)
    except Exception:
        return pd.DataFrame(columns=["data", "descricao", "valor"])

    lines: List[str] = []
    for img in images:
        text = pytesseract.image_to_string(img, lang="por")
        for ln in text.splitlines():
            ln = ln.strip()
            if ln:
                lines.append(ln)

    row_re = re.compile(r"^(\d{2}/\d{2}/\d{4})\s+(.+?)\s+(-?\d{1,3}(?:\.\d{3})*,\d{2})$", re.UNICODE)
    rows = []
    for ln in lines:
        m = row_re.match(ln)
        if m:
            d, desc, v = m.groups()
            try:
                dt = pd.to_datetime(d, format="%d/%m/%Y").date()
            except Exception:
                dt = None
            vf = v.replace(".", "").replace(",", ".")
            try:
                vf = float(vf)
            except Exception:
                vf = None
            if dt and (vf is not None):
                rows.append((dt, desc, vf))

    return pd.DataFrame(rows, columns=["data", "descricao", "valor"]) if rows else pd.DataFrame(columns=["data", "descricao", "valor"])

# ===== OFX =====
def parse_ofx_basic(file_bytes: bytes) -> pd.DataFrame:
    content = file_bytes.decode(errors="ignore")
    dates = re.findall(r"<DTPOSTED>(\d{8})", content)
    memos = re.findall(r"<MEMO>(.*?)\n", content)
    amts  = re.findall(r"<TRNAMT>(-?\d+[.,]?\d*)", content)
    df_raw = pd.DataFrame({"data": dates, "descricao": memos, "valor": amts})
    try:
        df_raw["data"] = pd.to_datetime(df_raw["data"], format="%Y%m%d").dt.date
    except Exception:
        pass
    try:
        df_raw["valor"] = pd.to_numeric(
            df_raw["valor"].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
            errors="coerce"
        )
    except Exception:
        df_raw["valor"] = pd.to_numeric(df_raw["valor"], errors="coerce")
    return df_raw.dropna(subset=["data", "valor"]).reset_index(drop=True)

def parse_ofx(file_bytes: bytes) -> pd.DataFrame:
    try:
        from ofxparse import OfxParser
    except Exception:
        return parse_ofx_basic(file_bytes)

    text = None
    for enc in ("latin-1", "utf-8", "cp1252"):
        try:
            text = file_bytes.decode(enc)
            break
        except Exception:
            continue
    if text is None:
        text = file_bytes.decode(errors="ignore")

    ofx = OfxParser.parse(io.StringIO(text))
    rows = []
    for acct in getattr(ofx, "accounts", []):
        stt = getattr(acct, "statement", None)
        if not stt or not getattr(stt, "transactions", None):
            continue
        for t in stt.transactions:
            data = pd.to_datetime(t.date).date() if t.date else None
            desc = (t.memo or t.payee or t.checknum or "").strip()
            valor = float(t.amount) if t.amount is not None else None
            if data and valor is not None:
                rows.append((data, desc, valor))
    return pd.DataFrame(rows, columns=["data", "descricao", "valor"])

# ===== Fluxo principal =====
rules = parse_rules(rules_text)

if file is not None:
    try:
        name = file.name.lower()
        df_raw = pd.DataFrame()

        if name.endswith((".csv", ".txt")):
            df_raw = pd.read_csv(file, sep=None, engine="python", encoding="utf-8")

        elif name.endswith(".ofx"):
            df_raw = parse_ofx(file.read())

        elif name.endswith(".pdf"):
            pdf_bytes = file.read()
            df_raw = parse_santander_pdf(pdf_bytes)
            if df_raw is None or df_raw.empty:
                df_raw = parse_pdf_with_ocr(pdf_bytes)

        else:
            st.error("Formato não suportado. Use CSV, OFX ou PDF.")
            st.stop()

    except Exception as e:
        st.exception(e)
        st.stop()

    if show_debug:
        st.info("DEBUG — pré-normalização")
        st.write("Linhas extraídas (PDF/OFX/CSV):", 0 if df_raw is None else len(df_raw))
        st.dataframe(df_raw.head(50) if df_raw is not None else pd.DataFrame())

    df = normalize_df(df_raw if df_raw is not None else pd.DataFrame())

    if df.empty:
        st.warning("Não foi possível reconhecer o extrato. Tente exportar **CSV/OFX** ou ative o *Modo debug*.")
        st.stop()

    if credit_positive == "Não":
        df["valor"] = -df["valor"]

    df["categoria"] = df["descricao"].apply(lambda s: apply_rules(s, rules))

    # KPIs
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Movimentos", len(df))
    with col2:
        entradas = df.loc[df["valor"] > 0, "valor"].sum()
        st.metric("Entradas", f"{currency_symbol} {entradas:,.2f}")
    with col3:
        saidas = df.loc[df["valor"] < 0, "valor"].sum()
        st.metric("Saídas", f"{currency_symbol} {saidas:,.2f}")

    # Resumos
    st.subheader("Resumo por mês")
    resumo_mes = df.groupby("ano_mes")["valor"].sum().reset_index().rename(columns={"valor": "saldo"})
    st.dataframe(resumo_mes)

    st.subheader("Resumo por categoria")
    resumo_cat = df.groupby("categoria")["valor"].sum().reset_index().sort_values("valor")
    st.dataframe(resumo_cat)

    # Tabela
    st.subheader("Extrato normalizado")
    st.dataframe(df)

    # Export
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button("Baixar CSV normalizado", data=csv_bytes, file_name="extrato_normalizado.csv", mime="text/csv")

    with st.expander("Dicas"):
        st.write("""
        - Priorize OFX > CSV > PDF para melhor parsing.
        - Coloque regras mais específicas no topo; genéricas no fim (ex.: `.* => Outros`).
        - PDF imagem requer OCR (pytesseract + pdf2image + pacotes do sistema).
        """)
else:
    st.info("Envie um arquivo de extrato (CSV/OFX/PDF) pela barra lateral.")
    st.write("Dica: priorize OFX > CSV > PDF.")