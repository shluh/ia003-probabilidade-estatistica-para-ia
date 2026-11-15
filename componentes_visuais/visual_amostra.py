import pandas as pd
import streamlit as st

from componentes_visuais.visual_populacao import render_descritivo


def render(
    df_amostra: pd.DataFrame,
    metadados: dict[str, int | float],
) -> None:
    tamanho_amostra = f"{metadados['tamanho_amostra']:,}".replace(",", ".")
    tamanho_populacao = f"{metadados['tamanho_populacao']:,}".replace(",", ".")
    render_descritivo(
        df_amostra,
        "Uma amostra, um retrato semelhante?",
        "Uma leitura da amostra selecionada aleatoriamente a partir "
        "da população do Disque 100.",
        (
            f"Para observar se o retrato se mantém, analisamos "
            f"{tamanho_amostra} denúncias selecionadas "
            f"entre {tamanho_populacao}. Cada hash "
            "representa uma denúncia, e todos os seus registros de "
            "violações permanecem juntos."
        ),
    )
    st.divider()
    st.caption(
        f"A amostra contém {metadados['tamanho_amostra']:,} denúncias "
        f"de uma população de {metadados['tamanho_populacao']:,}, "
        f"({metadados['percentual_amostrado']:.1f}%). "
        "A seleção foi aleatória simples, sem reposição, por hash."
    )
