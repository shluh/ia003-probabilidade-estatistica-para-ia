from base64 import b64encode
from pathlib import Path

import pandas as pd
import streamlit as st

from paineis.escolha_base_de_dados import render as render_escolha_base
from paineis.hipoteses_formuladas import render as render_inferencia
from paineis.painel_descritivo_amostra import (
    preparar_amostra,
    render as render_amostra,
)
from paineis.painel_descritivo_populacao import render_descritivo
from paineis.procedimento_de_selecao import render as render_procedimento


st.set_page_config(
    page_title="Proteção no Ambiente Virtual — versão editorial",
    page_icon="imagens/logodisque100.jpg",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1120px;
        padding-top: 3rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: #302C29;
        font-family: Georgia, serif;
    }

    [data-testid="stSidebar"] {
        background-color: #F3EFEA;
    }

    [data-testid="stSidebar"] h1 {
        font-size: 2.1rem;
    }

    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] label p {
        font-size: 1.1rem;
    }

    .sidebar-logos {
        position: fixed;
        left: 2rem;
        bottom: 1.25rem;
        width: 180px;
        display: flex;
        flex-direction: column;
        gap: 1rem;
        z-index: 1000;
    }

    .sidebar-logos img {
        display: block;
        width: 180px;
        height: auto;
        border-radius: 0.75rem;
    }

    .editorial-copy {
        color: #5D554F;
        font-size: 1.2rem;
        line-height: 1.65;
        margin: 0.35rem 0 1.1rem 0;
    }

    .editorial-number {
        color: #713C2E;
        font-family: Georgia, serif;
        font-size: 3rem;
        font-weight: 700;
        line-height: 1.05;
        white-space: nowrap;
    }

    .editorial-number-small {
        font-size: 1.8rem;
    }

    .editorial-highlight {
        color: #713C2E;
        font-size: 1.8rem;
        font-weight: 700;
    }

    h2 {
        border-bottom: 1px solid #DED6CE;
        padding-bottom: 0.35rem;
        margin-top: 2.2rem;
    }

    div[data-testid="stMetric"] {
        background: transparent;
        border: 0;
        padding: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner="Carregando dados...")
def carregar_dados() -> pd.DataFrame:
    caminho_dados = (
        Path(__file__).parent
        / "dados"
        / "base_analise_disque100.parquet"
    )
    return pd.read_parquet(caminho_dados)


def preparar_populacao(df: pd.DataFrame) -> pd.DataFrame:
    ordem_idades = [
        "RECÉM-NASCIDO (ATÉ 28 DIAS)",
        "MENOS DE 01 ANO",
        "01 ANO",
        "02 ANOS",
        "03 ANOS",
        "04 ANOS",
        "05 ANOS",
        "06 ANOS",
        "07 ANOS",
        "08 ANOS",
        "09 ANOS",
        "10 ANOS",
        "11 ANOS",
        "12 ANOS",
        "13 ANOS",
        "14 ANOS",
        "15 ANOS",
        "16 ANOS",
        "17 ANOS",
    ]
    return df.loc[
        (df["Grupo_vulnerável"]
         == "VIOLÊNCIA CONTRA CRIANÇA OU ADOLESCENTE")
        & (df["Cenário_da_violação"]
           == "AMBIENTE VIRTUAL (NO ÂMBITO DA INTERNET)")
        & (df["País"] == "BR | BRASIL")
        & (df["Faixa_etária_da_vítima"].isin(ordem_idades))
    ].copy()


def imagem_data_uri(nome: str, tipo: str) -> str:
    caminho = Path(__file__).parent / "imagens" / nome
    dados = b64encode(caminho.read_bytes()).decode("ascii")
    return f"data:{tipo};base64,{dados}"


df_filtrado = preparar_populacao(carregar_dados())
df_amostra, metadados_amostra = preparar_amostra(df_filtrado)

st.sidebar.title("Painel editorial")
pagina = st.sidebar.radio(
    "Selecione uma seção",
    [
        "Escolha da base de dados",
        "Procedimento de Seleção",
        "Painel Descritivo",
        "Hipóteses formuladas",
    ],
)
st.sidebar.caption(
    f"{len(df_filtrado):,}".replace(",", ".")
    + " registros na população filtrada"
)
st.sidebar.markdown(
    f"""
    <div class="sidebar-logos">
        <img src="{imagem_data_uri('logodisque100.jpg', 'image/webp')}"
             alt="Disque 100">
        <img src="{imagem_data_uri('logoufrgs.jpg', 'image/jpeg')}"
             alt="UFRGS">
    </div>
    """,
    unsafe_allow_html=True,
)

subpainel_descritivo = None
if pagina == "Painel Descritivo":
    subpainel_descritivo = st.sidebar.radio(
        "Selecione o subpainel",
        ["População", "Amostra"],
    )

if pagina == "Escolha da base de dados":
    render_escolha_base()
elif pagina == "Procedimento de Seleção":
    render_procedimento(df_amostra, metadados_amostra)
elif pagina == "Painel Descritivo" and subpainel_descritivo == "População":
    render_descritivo(
        df_filtrado,
        "O retrato da violência no ambiente virtual",
        "População do Disque 100 | 2º semestre de 2025 e "
        "1º semestre de 2026.",
        (
            "Este painel reúne os registros filtrados do Disque 100 "
            "para descrever como as denúncias de violência contra "
            "crianças e adolescentes aparecem no ambiente virtual."
        ),
    )
elif pagina == "Painel Descritivo" and subpainel_descritivo == "Amostra":
    render_amostra(df_amostra, metadados_amostra, df_filtrado)
elif pagina == "Hipóteses formuladas":
    render_inferencia(df_filtrado, df_amostra)
