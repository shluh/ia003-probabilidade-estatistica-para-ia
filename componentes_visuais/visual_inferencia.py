import altair as alt
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


def _exibir_mapa_de_calor(df_populacao: pd.DataFrame) -> None:
    st.header("Faixa etária e tipos de violação")
    st.caption(
        "Registros por faixa etária da vítima e tipo específico de violação, "
        "agrupado pelo nome final da classificação."
    )

    dados = df_populacao[
        ["Faixa_etária_da_vítima", "violacao"]
    ].copy()
    for coluna in dados.columns:
        dados[coluna] = dados[coluna].astype("string").str.strip()

    dados = dados[
        dados["Faixa_etária_da_vítima"].notna()
        & dados["violacao"].notna()
        & dados["Faixa_etária_da_vítima"].ne("")
        & dados["violacao"].ne("")
        & ~dados["Faixa_etária_da_vítima"].str.upper().isin(
            [
                "CRIANÇA/ADOLESCENTE IDADE NÃO INFORMADA",
                "NÃO INFORMADO",
            ]
        )
    ].copy()

    if dados.empty:
        st.info("Não há dados válidos para construir o mapa de calor.")
        return

    dados["Tipo de violação"] = (
        dados["violacao"].str.split(">").str[-1].str.strip()
    )
    top_violacoes = (
        dados["Tipo de violação"].value_counts().head(10).index.tolist()
    )
    dados = dados[dados["Tipo de violação"].isin(top_violacoes)]

    matriz = (
        dados.groupby(["Faixa_etária_da_vítima", "Tipo de violação"])
        .size()
        .reset_index(name="Registros")
        .rename(columns={"Faixa_etária_da_vítima": "Faixa etária"})
    )

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
    idades_presentes = matriz["Faixa etária"].unique().tolist()
    idades_ordenadas = [
        idade for idade in ordem_idades if idade in idades_presentes
    ]
    idades_ordenadas.extend(
        idade for idade in idades_presentes if idade not in idades_ordenadas
    )

    grade = pd.MultiIndex.from_product(
        [idades_ordenadas, top_violacoes],
        names=["Faixa etária", "Tipo de violação"],
    ).to_frame(index=False)
    matriz = grade.merge(
        matriz,
        on=["Faixa etária", "Tipo de violação"],
        how="left",
    )
    matriz["Registros"] = matriz["Registros"].fillna(0).astype(int)

    grafico = (
        alt.Chart(matriz)
        .mark_rect(cornerRadius=3, stroke="#FAF9F6", strokeWidth=2)
        .encode(
            x=alt.X(
                "Tipo de violação:N",
                title="Tipo de violação (nome final)",
                sort=top_violacoes,
                axis=alt.Axis(
                    labelAngle=-45,
                    labelLimit=300,
                    labelFontSize=13,
                    labelPadding=8,
                    labelOverlap=False,
                ),
            ),
            y=alt.Y(
                "Faixa etária:N",
                title="Faixa etária da vítima",
                sort=idades_ordenadas,
                axis=alt.Axis(
                    labelFontSize=13,
                    domain=False,
                    ticks=False,
                ),
            ),
            color=alt.Color(
                "Registros:Q",
                title="Registros",
                scale=alt.Scale(
                    range=["#F3E7DE", "#D97757", "#843F2B"]
                ),
            ),
            tooltip=[
                alt.Tooltip("Faixa etária:N"),
                alt.Tooltip("Tipo de violação:N"),
                alt.Tooltip("Registros:Q"),
            ],
        )
        .properties(height=700)
        .configure_view(strokeWidth=0)
        .configure_axis(labelColor="#302C29", titleColor="#302C29")
    )
    st.altair_chart(grafico, use_container_width=True)
    st.caption(
        "As classificações são agrupadas pelo nome final; nomes iguais em "
        "caminhos diferentes são somados. Cada célula representa a "
        "quantidade de registros."
    )


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

    _exibir_mapa_de_calor(df_populacao)
    st.divider()

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
