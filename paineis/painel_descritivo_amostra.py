import pandas as pd
import streamlit as st

from calculos.amostragem import preparar_amostra, render_painel_amostra
from componentes_visuais.visual_amostra import render

__all__ = ["preparar_amostra", "render", "render_painel_amostra"]


def _render_comparacao(
    df_populacao: pd.DataFrame,
    df_amostra: pd.DataFrame,
) -> None:
    from calculos.inferencia import (
        _evento_proporcoes,
        _registros_por_denuncia,
    )

    eventos_populacao = _evento_proporcoes(df_populacao)
    eventos_amostra = _evento_proporcoes(df_amostra)
    registros_populacao = _registros_por_denuncia(df_populacao)
    registros_amostra = _registros_por_denuncia(df_amostra)

    comparacao = pd.DataFrame({
        "Indicador": [
            "Denúncias distintas",
            "Média de registros por denúncia",
            "Denúncias com adolescentes de 12 a 17 anos",
            "Denúncias com múltiplos registros",
        ],
        "População": [
            len(eventos_populacao),
            registros_populacao.mean(),
            eventos_populacao["adolescente"].mean(),
            eventos_populacao["multiplos_registros"].mean(),
        ],
        "Amostra": [
            len(eventos_amostra),
            registros_amostra.mean(),
            eventos_amostra["adolescente"].mean(),
            eventos_amostra["multiplos_registros"].mean(),
        ],
    })
    comparacao["Diferença (amostra - população)"] = (
        comparacao["Amostra"] - comparacao["População"]
    )

    def formatar_valor(indice: int, valor: float) -> str:
        if indice == 0:
            return f"{valor:,.0f}".replace(",", ".")
        if indice == 1:
            return f"{valor:.2f}".replace(".", ",")
        return f"{valor:.2%}".replace(".", ",")

    colunas_valores = [
        "População",
        "Amostra",
        "Diferença (amostra - população)",
    ]
    comparacao_formatada = comparacao.copy()
    for coluna in colunas_valores:
        comparacao_formatada[coluna] = [
            formatar_valor(indice, valor)
            for indice, valor in comparacao[coluna].items()
        ]

    st.header("Comparação entre população e amostra")
    st.caption(
        "A comparação mostra se o retrato da amostra se aproxima dos "
        "parâmetros observados na população."
    )
    st.dataframe(
        comparacao_formatada,
        hide_index=True,
        use_container_width=True,
    )


def render(
    df_amostra: pd.DataFrame,
    metadados: dict[str, int | float],
    df_populacao: pd.DataFrame,
) -> None:
    from componentes_visuais.visual_amostra import render as render_resumo

    render_resumo(df_amostra, metadados)
    _render_comparacao(df_populacao, df_amostra)
    st.divider()
    render_painel_amostra(df_amostra, metadados)
