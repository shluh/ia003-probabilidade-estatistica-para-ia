import math

import altair as alt
import pandas as pd
import streamlit as st


TERRACOTA = "#D97757"
TEXTO = "#262624"
GRADE = "#E5E1D8"

Z_VALOR = 1.96
MARGEM_ERRO = 0.05
PROPORCAO_CONSERVADORA = 0.5
RANDOM_STATE = 2026


def preparar_amostra(
    df_populacao: pd.DataFrame,
    random_state: int = RANDOM_STATE,
) -> tuple[pd.DataFrame, dict[str, int | float]]:
    """Seleciona denúncias por amostragem aleatória simples sem reposição."""
    hashes = (
        df_populacao["hash"]
        .astype("string")
        .str.strip()
        .replace("", pd.NA)
    )

    hashes_validos = hashes.dropna().drop_duplicates()
    tamanho_populacao = len(hashes_validos)
    hashes_ausentes = int(hashes.isna().sum())

    if tamanho_populacao == 0:
        return (
            df_populacao.iloc[0:0].copy(),
            {
                "tamanho_populacao": 0,
                "tamanho_amostra": 0,
                "hashes_ausentes": hashes_ausentes,
                "percentual_amostrado": 0.0,
                "n0": 0.0,
            },
        )

    n0 = (
        Z_VALOR**2
        * PROPORCAO_CONSERVADORA
        * (1 - PROPORCAO_CONSERVADORA)
        / MARGEM_ERRO**2
    )
    tamanho_amostra = min(
        tamanho_populacao,
        math.ceil(
            (tamanho_populacao * n0)
            / (tamanho_populacao - 1 + n0)
        ),
    )

    hashes_selecionados = hashes_validos.sample(
        n=tamanho_amostra,
        random_state=random_state,
    )
    df_amostra = df_populacao.loc[
        hashes.isin(hashes_selecionados)
    ].copy()

    return (
        df_amostra,
        {
            "tamanho_populacao": tamanho_populacao,
            "tamanho_amostra": tamanho_amostra,
            "hashes_ausentes": hashes_ausentes,
            "percentual_amostrado": (
                tamanho_amostra / tamanho_populacao * 100
            ),
            "n0": n0,
        },
    )


def _normalizar_coluna(serie: pd.Series) -> pd.Series:
    return (
        serie.astype("string")
        .str.strip()
        .replace("", pd.NA)
    )


def _exibir_estatisticas(df_amostra: pd.DataFrame) -> None:
    hashes = _normalizar_coluna(df_amostra["hash"])
    violacoes = _normalizar_coluna(df_amostra["violacao"])

    base = pd.DataFrame({
        "hash": hashes,
        "violacao": violacoes,
    }).dropna(subset=["hash", "violacao"])
    base = base[base["violacao"].ne("")]

    tipos_por_hash = base.groupby("hash")["violacao"].nunique()
    registros_por_denuncia = base.groupby("hash").size()

    total_registros = len(df_amostra)
    total_denuncias = hashes.nunique()
    total_violacoes = violacoes.dropna().nunique()
    media_violacoes = tipos_por_hash.mean()

    media_registros = registros_por_denuncia.mean()
    mediana_registros = registros_por_denuncia.median()
    desvio_registros = registros_por_denuncia.std()
    minimo_registros = (
        int(registros_por_denuncia.min())
        if not registros_por_denuncia.empty
        else None
    )
    maximo_registros = (
        int(registros_por_denuncia.max())
        if not registros_por_denuncia.empty
        else None
    )
    amplitude_registros = (
        maximo_registros - minimo_registros
        if minimo_registros is not None
        and maximo_registros is not None
        else None
    )
    variancia_registros = (
        registros_por_denuncia.var()
        if not registros_por_denuncia.empty
        else None
    )
    cv_registros = (
        desvio_registros / media_registros * 100
        if pd.notna(media_registros)
        and media_registros != 0
        and pd.notna(desvio_registros)
        else None
    )

    colunas = st.columns(4)
    colunas[0].metric(
        "Registros",
        f"{total_registros:,}".replace(",", "."),
    )
    colunas[1].metric(
        "Denúncias",
        f"{total_denuncias:,}".replace(",", "."),
    )
    colunas[2].metric(
        "Violações",
        f"{total_violacoes:,}".replace(",", "."),
    )
    colunas[3].metric(
        "Violações por denúncia",
        f"{media_violacoes:.1f}".replace(".", ",")
        if pd.notna(media_violacoes)
        else "N/D",
    )

    st.markdown("**Registros de violações por denúncia distinta**")
    estatisticas = st.columns(5)
    valores = [
        ("Média", media_registros, "{:.2f}"),
        ("Mediana", mediana_registros, "{:.1f}"),
        ("Desvio-padrão", desvio_registros, "{:.2f}"),
    ]
    for coluna, (titulo, valor, formato) in zip(
        estatisticas,
        valores,
    ):
        coluna.metric(
            titulo,
            formato.format(valor).replace(".", ",")
            if pd.notna(valor)
            else "N/D",
        )
    estatisticas[3].metric(
        "Mínimo",
        f"{minimo_registros:,}".replace(",", ".")
        if minimo_registros is not None
        else "N/D",
    )
    estatisticas[4].metric(
        "Máximo",
        f"{maximo_registros:,}".replace(",", ".")
        if maximo_registros is not None
        else "N/D",
    )

    quartis = st.columns(3)
    for coluna, titulo, quantil in zip(
        quartis,
        ["Q1 (25%)", "Q2 (50%)", "Q3 (75%)"],
        [0.25, 0.5, 0.75],
    ):
        valor = (
            registros_por_denuncia.quantile(quantil)
            if not registros_por_denuncia.empty
            else None
        )
        coluna.metric(
            titulo,
            f"{valor:.2f}".replace(".", ",")
            if valor is not None
            else "N/D",
        )

    st.markdown("**Medidas de dispersão**")
    dispersao = st.columns(3)
    dispersao[0].metric(
        "Amplitude",
        f"{amplitude_registros:,.0f}".replace(",", ".")
        if amplitude_registros is not None
        else "N/D",
    )
    dispersao[1].metric(
        "Variância",
        f"{variancia_registros:,.2f}".replace(",", ".")
        if pd.notna(variancia_registros)
        else "N/D",
    )
    dispersao[2].metric(
        "Coeficiente de variação",
        f"{cv_registros:.1f}%".replace(".", ",")
        if pd.notna(cv_registros)
        else "N/D",
    )

    if registros_por_denuncia.empty:
        st.info("Não há denúncias válidas para exibir a distribuição.")
        return

    dados_distribuicao = pd.DataFrame({
        "Registros por denúncia": registros_por_denuncia.astype(int),
    })
    col_histograma, col_boxplot = st.columns(2, gap="large")

    with col_histograma:
        histograma = (
            alt.Chart(dados_distribuicao)
            .mark_bar(color=TERRACOTA, opacity=0.85)
            .encode(
                x=alt.X(
                    "Registros por denúncia:Q",
                    bin=alt.Bin(step=1),
                    title="Número de registros por denúncia",
                ),
                y=alt.Y(
                    "count():Q",
                    title="Quantidade de denúncias",
                ),
                tooltip=[
                    alt.Tooltip(
                        "Registros por denúncia:Q",
                        bin=alt.Bin(step=1),
                        title="Registros por denúncia",
                    ),
                    alt.Tooltip("count():Q", title="Denúncias"),
                ],
            )
            .properties(height=320)
            .configure_view(strokeWidth=0)
            .configure_axis(
                labelColor=TEXTO,
                titleColor=TEXTO,
                gridColor=GRADE,
            )
        )
        st.altair_chart(histograma, use_container_width=True)
        st.caption(
            "Distribui as denúncias segundo o número de registros "
            "associados a cada hash."
        )

    with col_boxplot:
        boxplot = (
            alt.Chart(dados_distribuicao)
            .mark_boxplot(extent=1.5, size=70, color=TERRACOTA)
            .encode(
                y=alt.Y(
                    "Registros por denúncia:Q",
                    title="Número de registros por denúncia",
                ),
                tooltip=[
                    alt.Tooltip(
                        "Registros por denúncia:Q",
                        title="Registros por denúncia",
                    ),
                ],
            )
            .properties(height=320)
            .configure_view(strokeWidth=0)
            .configure_axis(
                labelColor=TEXTO,
                titleColor=TEXTO,
                gridColor=GRADE,
            )
        )
        st.altair_chart(boxplot, use_container_width=True)
        st.caption(
            "Resume mediana, quartis, dispersão e possíveis valores "
            "extremos, sem classificá-los automaticamente como erros."
        )


def _exibir_violacoes(df_amostra: pd.DataFrame) -> None:
    dados = df_amostra[["violacao"]].copy()
    dados["violacao"] = _normalizar_coluna(dados["violacao"])
    dados = dados[dados["violacao"].notna() & dados["violacao"].ne("")]

    st.subheader("Distribuição dos tipos de violação")
    if dados.empty:
        st.info("Não existem classificações válidas de violações.")
        return

    distribuicao = (
        dados["violacao"]
        .value_counts()
        .rename_axis("Tipo de violação")
        .reset_index(name="Registros")
    )
    total_validos = distribuicao["Registros"].sum()
    distribuicao["Percentual"] = (
        distribuicao["Registros"] / total_validos * 100
    )
    top10 = distribuicao.head(10)
    maior_valor = top10["Registros"].max()

    grafico = (
        alt.Chart(top10)
        .mark_bar(cornerRadiusEnd=4, size=22)
        .encode(
            x=alt.X(
                "Registros:Q",
                title="Quantidade de registros",
                axis=alt.Axis(gridColor=GRADE),
            ),
            y=alt.Y(
                "Tipo de violação:N",
                sort="-x",
                title=None,
                axis=alt.Axis(
                    labelLimit=450,
                    labelFontSize=11,
                    domain=False,
                    ticks=False,
                ),
            ),
            color=alt.condition(
                alt.datum.Registros == maior_valor,
                alt.value("#843F2B"),
                alt.value("#D8C8BC"),
            ),
            tooltip=[
                alt.Tooltip(
                    "Tipo de violação:N",
                    title="Classificação completa",
                ),
                alt.Tooltip("Registros:Q", title="Registros", format=","),
                alt.Tooltip(
                    "Percentual:Q",
                    title="% dos registros válidos",
                    format=".2f",
                ),
            ],
        )
        .properties(height=360)
        .configure_view(strokeWidth=0)
        .configure_axis(labelColor=TEXTO, titleColor=TEXTO)
    )
    st.altair_chart(grafico, use_container_width=True)
    st.caption(
        f"Top 10 entre {total_validos:,} registros com classificação "
        "informada. A contagem é por registro, não por denúncia distinta."
    )


def _exibir_perfil(df_amostra: pd.DataFrame) -> None:
    st.header("Perfil dos envolvidos nas denúncias")
    st.caption(
        "Top 3 das categorias mais frequentes. Percentuais usam hashes "
        "distintos com informação disponível para cada característica."
    )

    colunas = [
        "Gênero_do_suspeito",
        "Faixa_etária_do_suspeito",
        "Relação_vítima_suspeito",
        "Denunciante",
    ]
    resultados = {}
    for coluna in colunas:
        base = df_amostra[["hash", coluna]].copy()
        base["hash"] = _normalizar_coluna(base["hash"])
        base[coluna] = _normalizar_coluna(base[coluna])
        base = base.dropna(subset=["hash"])
        base[coluna] = base[coluna].fillna("Não informado")
        base.loc[base[coluna].eq(""), coluna] = "Não informado"
        base = base.drop_duplicates(["hash", coluna])
        informados = base[base[coluna] != "Não informado"]
        resultados[coluna] = (
            informados.groupby(coluna)["hash"].nunique()
            .sort_values(ascending=False)
        ), informados["hash"].nunique()

    def mostrar(coluna: str, titulo: str) -> None:
        resumo, total = resultados[coluna]
        st.markdown(f"**{titulo}**")
        if resumo.empty or total == 0:
            st.info("Não há dados disponíveis para esta característica.")
            return
        maior = int(resumo.head(3).max())
        for posicao, (categoria, quantidade) in enumerate(
            resumo.head(3).items()
        ):
            quantidade = int(quantidade)
            st.markdown(
                f"**{posicao + 1}º — {categoria}** "
                f"({quantidade:,} hashes)".replace(",", ".")
            )
            st.progress(
                min(quantidade / maior, 1.0),
                text=(
                    f"{quantidade / total * 100:.1f}% dos hashes "
                    "com informação"
                ).replace(".", ","),
            )

    esquerda, direita = st.columns(2, gap="large")
    with esquerda:
        mostrar("Gênero_do_suspeito", "Gênero do suspeito")
        st.divider()
        mostrar(
            "Relação_vítima_suspeito",
            "Vínculo do suspeito com a vítima",
        )
    with direita:
        mostrar(
            "Faixa_etária_do_suspeito",
            "Faixa etária do suspeito",
        )
        st.divider()
        mostrar("Denunciante", "Quem realiza a denúncia?")


def render_painel_amostra(
    df_amostra: pd.DataFrame,
    metadados: dict[str, int | float],
) -> None:
    """Renderiza o Painel 2 com dados exclusivamente da amostra."""
    st.title("Análise descritiva da amostra")
    st.caption(
        "Amostragem aleatória simples sem reposição, com cada hash "
        "distinto como unidade de seleção."
    )

    info = st.columns(4)
    info[0].metric(
        "População (denúncias)",
        f"{metadados['tamanho_populacao']:,}".replace(",", "."),
    )
    info[1].metric(
        "Amostra (denúncias)",
        f"{metadados['tamanho_amostra']:,}".replace(",", "."),
    )
    info[2].metric(
        "Percentual amostrado",
        f"{metadados['percentual_amostrado']:.1f}%".replace(".", ","),
    )
    info[3].metric(
        "Hashes ausentes",
        f"{metadados['hashes_ausentes']:,}".replace(",", "."),
    )

    st.info(
        "Hashes ausentes não foram tratados como denúncias distintas e "
        "não puderam ser selecionados pela amostragem por denúncia. "
        "Os registros associados a hashes selecionados foram mantidos "
        "integralmente na amostra."
    )

    st.markdown("**Critério de dimensionamento da amostra**")
    st.latex(
        r"n_0 = \frac{z^2 p(1-p)}{e^2};\quad "
        r"n = \frac{N n_0}{N - 1 + n_0}"
    )
    st.caption(
        "Foi utilizado nível de confiança de 95% (z = 1,96), margem "
        "de erro de 5% (e = 0,05), p = 0,5 como hipótese conservadora "
        f"e correção para população finita. O n₀ calculado foi "
        f"{metadados['n0']:.2f}; a seleção usa random_state={RANDOM_STATE}."
    )

    st.divider()
    _exibir_estatisticas(df_amostra)
    st.divider()
    _exibir_violacoes(df_amostra)
    st.divider()
    _exibir_perfil(df_amostra)

    st.caption(
        "A amostra permite descrever as denúncias selecionadas, mas "
        "estimativas podem variar entre amostras. A seleção por hash "
        "preserva todas as violações associadas a cada denúncia."
    )
