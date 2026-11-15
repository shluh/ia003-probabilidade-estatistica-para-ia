import altair as alt
import pandas as pd
import streamlit as st

from calculos.inferencia import (
    _evento_proporcoes,
    _idades_por_denuncia,
    _registros_por_denuncia,
)


TERRACOTA = "#B45F45"
TERRACOTA_ESCURO = "#713C2E"
NEUTRO = "#E8E1D9"
TEXTO = "#302C29"
GRADE = "#DED6CE"


def _normalizar(serie: pd.Series) -> pd.Series:
    return (
        serie.astype("string")
        .str.strip()
        .replace("", pd.NA)
    )


def _numero(valor: float, casas: int = 2) -> str:
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace(
        "X", "."
    )


def _distribuicao_violacoes(df: pd.DataFrame) -> pd.DataFrame:
    dados = df[["violacao"]].copy()
    dados["violacao"] = _normalizar(dados["violacao"])
    dados = dados[dados["violacao"].notna() & dados["violacao"].ne("")]
    distribuicao = (
        dados["violacao"]
        .value_counts()
        .rename_axis("Tipo de violação")
        .reset_index(name="Registros")
    )
    if not distribuicao.empty:
        distribuicao["Percentual"] = (
            distribuicao["Registros"]
            / distribuicao["Registros"].sum()
            * 100
        )
    return distribuicao


def render_descritivo(
    df: pd.DataFrame,
    titulo: str,
    subtitulo: str,
    introducao: str = "",
) -> None:
    st.title(titulo)
    st.caption(subtitulo)
    if introducao:
        st.markdown(
            f'<p class="editorial-copy">{introducao}</p>',
            unsafe_allow_html=True,
        )

    registros = _registros_por_denuncia(df)
    eventos = _evento_proporcoes(df)
    idades, excluidos, hashes_multiplas_idades = _idades_por_denuncia(df)
    media = registros.mean()
    mediana = registros.median()
    desvio = registros.std()
    q1 = registros.quantile(0.25)
    q3 = registros.quantile(0.75)
    total_denuncias = f"{len(registros):,}".replace(",", ".")

    st.markdown("## A população analisada")
    st.markdown(
        f'<p class="editorial-copy">A análise reúne '
        f'<span class="editorial-number">{total_denuncias}'
        f'</span> denúncias distintas, identificadas por hash, '
        "preservando todos os registros de violações associados a cada "
        "denúncia.</p>",
        unsafe_allow_html=True,
    )

    st.markdown("## Como as denúncias se distribuem")
    st.markdown(
        f'<p class="editorial-copy">Em média, cada denúncia apresenta '
        f'<span class="editorial-number">{_numero(media)}</span> '
        "registros de violações. A mediana é de "
        f'<span class="editorial-number editorial-number-small">'
        f'{_numero(mediana, 0)}</span> registros, indicando que metade '
        "das denúncias possui até esse número de registros e a outra "
        "metade possui pelo menos esse número. Metade central das "
        "denúncias concentra-se entre "
        f'<span class="editorial-number editorial-number-small">'
        f'{_numero(q1, 0)} e {_numero(q3, 0)}</span> registros. O '
        "desvio-padrão é de "
        f'<span class="editorial-number editorial-number-small">'
        f'{_numero(desvio)}</span> registros, indicando variação na '
        "quantidade de violações registradas entre as denúncias.</p>",
        unsafe_allow_html=True,
    )

    st.caption(
        "As medidas são calculadas depois do agrupamento por hash. "
        "Não representam médias de variáveis categóricas."
    )

    dados_distribuicao = pd.DataFrame({
        "Registros por denúncia": registros.astype(int),
    })
    histograma = (
        alt.Chart(dados_distribuicao)
        .mark_bar(color=TERRACOTA)
        .encode(
            x=alt.X(
                "Registros por denúncia:Q",
                bin=alt.Bin(step=1),
                title="Registros por denúncia",
            ),
            y=alt.Y("count():Q", title="Denúncias"),
            tooltip=[
                alt.Tooltip(
                    "Registros por denúncia:Q",
                    bin=alt.Bin(step=1),
                    title="Registros por denúncia",
                ),
                alt.Tooltip("count():Q", title="Denúncias"),
            ],
        )
        .properties(height=280)
        .configure_view(strokeWidth=0)
        .configure_axis(
            labelColor=TEXTO,
            titleColor=TEXTO,
            grid=False,
        )
    )
    st.altair_chart(histograma, use_container_width=True)
    st.caption(
        "O histograma mostra como as denúncias se distribuem conforme "
        "a quantidade de registros associados."
    )

    st.markdown("## Quais tipos aparecem com mais frequência?")
    distribuicao = _distribuicao_violacoes(df)
    if not distribuicao.empty:
        top10 = distribuicao.head(10)
        grafico = (
            alt.Chart(top10)
            .mark_bar(cornerRadiusEnd=4, color=TERRACOTA)
            .encode(
                x=alt.X("Registros:Q", title="Registros"),
                y=alt.Y(
                    "Tipo de violação:N",
                    sort="-x",
                    title=None,
                    axis=alt.Axis(labelLimit=450, domain=False, ticks=False),
                ),
                tooltip=[
                    alt.Tooltip(
                        "Tipo de violação:N",
                        title="Classificação completa",
                    ),
                    alt.Tooltip("Registros:Q", title="Registros"),
                    alt.Tooltip(
                        "Percentual:Q",
                        title="% dos registros válidos",
                        format=".2f",
                    ),
                ],
            )
            .properties(height=360)
            .configure_view(strokeWidth=0)
            .configure_axis(
                labelColor=TEXTO,
                titleColor=TEXTO,
                grid=False,
            )
        )
        st.altair_chart(grafico, use_container_width=True)
        st.caption(
            f"As 10 classificações mais frequentes entre "
            f"{int(distribuicao['Registros'].sum()):,} registros válidos."
        )

    st.markdown("## Alguns sinais desse retrato")
    adolescentes = eventos["adolescente"].mean()
    multiplos = eventos["multiplos_registros"].mean()
    percentual_adolescentes = f"{adolescentes:.1%}".replace(".", ",")
    percentual_multiplos = f"{multiplos:.1%}".replace(".", ",")
    st.markdown(
        '<p class="editorial-copy">Entre as denúncias analisadas, '
        "a proporção com ao menos uma vítima de 12 a 17 anos é "
        f'<span class="editorial-number editorial-number-small">'
        f"{percentual_adolescentes}"
        f'</span>, enquanto a proporção com dois ou mais registros '
        "é "
        f'<span class="editorial-number editorial-number-small">'
        f"{percentual_multiplos}"
        f"</span>.</p>",
        unsafe_allow_html=True,
    )
    st.caption(
        f"{excluidos:,} registros não possuem idade numérica entre 1 e 17 anos "
        f"e {hashes_multiplas_idades:,} hashes apresentam mais de uma idade "
        "distinta; esses casos são tratados no Painel 3."
    )
