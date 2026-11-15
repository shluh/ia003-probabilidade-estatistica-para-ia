import pandas as pd
import streamlit as st

from calculos.inferencia import (
    _evento_proporcoes,
    _idades_por_denuncia,
    _registros_por_denuncia,
    _teste_media,
    _teste_proporcao,
)


def _percentual(valor: float) -> str:
    return f"{valor:.2%}".replace(".", ",")


def _decimal(valor: float) -> str:
    return f"{valor:.3f}".replace(".", ",")


def _p_valor(valor: float) -> str:
    return "<0,0001" if valor < 0.00005 else f"{valor:.4f}".replace(".", ",")


def _hipotese(
    titulo: str,
    pergunta: str,
    h0: str,
    h1: str,
    populacao: str,
    amostra: str,
    intervalo: str,
    teste: str,
    conclusao: str,
) -> None:
    st.subheader(titulo)
    st.markdown(
        f'<p class="editorial-copy" style="font-size: 1.3rem;">'
        f"<strong>Pergunta:</strong> {pergunta}</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p class="editorial-copy" style="font-size: 1.3rem;">'
        f"<strong>H₀:</strong> {h0}<br>"
        f"<strong>H₁:</strong> {h1}</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p class="editorial-copy">População: '
        f'<span class="editorial-number editorial-number-small">'
        f"{populacao}</span> &nbsp;|&nbsp; Amostra: "
        f'<span class="editorial-number editorial-number-small">'
        f"{amostra}</span></p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p class="editorial-copy" style="font-size: 1.3rem;">'
        f"<strong>Intervalo de confiança de 95%:</strong> "
        f"{intervalo}</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p class="editorial-copy" style="font-size: 1.3rem;">'
        f"<strong>Teste:</strong> {teste}</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p class="editorial-copy" style="font-size: 1.3rem;">'
        f"<strong>Conclusão:</strong> {conclusao}</p>",
        unsafe_allow_html=True,
    )


def render(df_populacao: pd.DataFrame, df_amostra: pd.DataFrame) -> None:
    st.title("Hipóteses formuladas")
    st.caption(
        "Inferência estatística a partir da amostra de denúncias do "
        "Disque 100 | nível de significância de 5%."
    )
    st.markdown(
        '<p class="editorial-copy">Aqui, a população fornece os '
        "parâmetros de referência e a amostra fornece as estimativas. "
        "Os testes avaliam se as diferenças observadas são compatíveis "
        "com as hipóteses formuladas; eles não transformam evidência "
        "estatística em prova absoluta.</p>",
        unsafe_allow_html=True,
    )

    eventos_pop = _evento_proporcoes(df_populacao)
    eventos_amostra = _evento_proporcoes(df_amostra)
    n_pop = len(eventos_pop)
    n_amostra = len(eventos_amostra)

    st.markdown(
        '<h2 style="font-size: 1.9rem;">Inferência para proporções</h2>',
        unsafe_allow_html=True,
    )

    r = _teste_proporcao(
        int(eventos_amostra["adolescente"].sum()),
        n_amostra,
        n_pop,
        "maior",
    )
    _hipotese(
        "Hipótese 1 — Adolescentes de 12 a 17 anos",
        "Mais de 50% das denúncias envolvem adolescentes?",
        "p = 0,50",
        "p > 0,50",
        _percentual(eventos_pop["adolescente"].mean()),
        _percentual(float(r["proporcao"])),
        f"{_percentual(float(r['limite_inferior']))} a "
        f"{_percentual(float(r['limite_superior']))}",
        f"z = {_decimal(float(r['estatistica']))}; "
        f"valor-p = {_p_valor(float(r['valor_p']))}; α = 5%",
        str(r["conclusao"]),
    )

    r = _teste_proporcao(
        int(eventos_amostra["multiplos_registros"].sum()),
        n_amostra,
        n_pop,
        "maior",
    )
    _hipotese(
        "Hipótese 2 — Dois ou mais registros",
        "Mais de 50% das denúncias apresentam múltiplos registros?",
        "p = 0,50",
        "p > 0,50",
        _percentual(eventos_pop["multiplos_registros"].mean()),
        _percentual(float(r["proporcao"])),
        f"{_percentual(float(r['limite_inferior']))} a "
        f"{_percentual(float(r['limite_superior']))}",
        f"z = {_decimal(float(r['estatistica']))}; "
        f"valor-p = {_p_valor(float(r['valor_p']))}; α = 5%",
        str(r["conclusao"]),
    )

    st.divider()
    st.header("Inferência para médias")

    idades_pop, excluidos_pop, multiplas_pop = _idades_por_denuncia(
        df_populacao
    )
    idades_amostra, excluidos_amostra, multiplas_amostra = (
        _idades_por_denuncia(df_amostra)
    )
    r = _teste_media(idades_amostra, 12, len(idades_pop))
    _hipotese(
        "Hipótese 3 — Idade média das vítimas",
        "A idade média das vítimas é diferente de 12 anos?",
        "μ = 12",
        "μ ≠ 12",
        _decimal(float(idades_pop.mean())),
        _decimal(float(r["media"])),
        f"{_decimal(float(r['limite_inferior']))} a "
        f"{_decimal(float(r['limite_superior']))}",
        f"t = {_decimal(float(r['estatistica']))}; "
        f"valor-p = {_p_valor(float(r['valor_p']))}; α = 5%",
        str(r["conclusao"]),
    )
    st.caption(
        f"Excluídos: {excluidos_pop:,} registros na população e "
        f"{excluidos_amostra:,} na amostra. Foram mantidos uma observação "
        f"por hash; hashes com múltiplas idades: {multiplas_pop:,} na "
        f"população e {multiplas_amostra:,} na amostra."
    )

    registros_pop = _registros_por_denuncia(df_populacao)
    registros_amostra = _registros_por_denuncia(df_amostra)
    r = _teste_media(registros_amostra, 4, len(registros_pop))
    _hipotese(
        "Hipótese 4 — Registros por denúncia",
        "A quantidade média de registros é diferente de 4?",
        "μ = 4",
        "μ ≠ 4",
        _decimal(float(registros_pop.mean())),
        _decimal(float(r["media"])),
        f"{_decimal(float(r['limite_inferior']))} a "
        f"{_decimal(float(r['limite_superior']))}",
        f"t = {_decimal(float(r['estatistica']))}; "
        f"valor-p = {_p_valor(float(r['valor_p']))}; α = 5%",
        str(r["conclusao"]),
    )

    st.caption(
        "Os números são consumidos dos mesmos cálculos estatísticos dos "
        "painéis atuais. Esta versão altera apenas a apresentação visual."
    )
