import pandas as pd
import streamlit as st

from calculos.amostragem import (
    MARGEM_ERRO,
    PROPORCAO_CONSERVADORA,
    RANDOM_STATE,
    Z_VALOR,
)


def _numero(valor: int | float, casas: int = 0) -> str:
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace(
        "X", "."
    )


def render(
    df_amostra: pd.DataFrame,
    metadados: dict[str, int | float],
) -> None:
    tamanho_populacao = int(metadados["tamanho_populacao"])
    tamanho_amostra = int(metadados["tamanho_amostra"])
    tamanho_registros = len(df_amostra)
    n0 = float(metadados["n0"])
    percentual_amostrado = float(metadados["percentual_amostrado"])

    st.title("Procedimento de Seleção")
    st.caption(
        "O cálculo do tamanho amostral e o procedimento de seleção da "
        "amostra aleatória simples"
    )

    st.header("O cálculo do tamanho amostral")
    st.markdown(
        """
        <p class="editorial-copy">
        O tamanho da amostra foi calculado considerando a população de
        denúncias distintas, e não o número total de linhas. Isso evita que
        denúncias com várias violações tenham peso maior na seleção.
        </p>
        """,
        unsafe_allow_html=True,
    )

    metricas = st.columns(4)
    metricas[0].markdown(
        f'<p class="editorial-copy">População</p>'
        f'<span class="editorial-number editorial-number-small">'
        f"{_numero(tamanho_populacao)}</span>",
        unsafe_allow_html=True,
    )
    metricas[1].markdown(
        f'<p class="editorial-copy">Confiança</p>'
        f'<span class="editorial-number editorial-number-small">95%</span>',
        unsafe_allow_html=True,
    )
    metricas[2].markdown(
        f'<p class="editorial-copy">Margem de erro</p>'
        f'<span class="editorial-number editorial-number-small">5%</span>',
        unsafe_allow_html=True,
    )
    metricas[3].markdown(
        f'<p class="editorial-copy">Amostra</p>'
        f'<span class="editorial-number editorial-number-small">'
        f"{_numero(tamanho_amostra)}</span>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <p class="editorial-copy" style="margin-top: 2.5rem;">
        Para uma confiança de
        <span class="editorial-number editorial-number-small">95%</span>,
        margem de erro de
        <span class="editorial-number editorial-number-small">5%</span> e
        proporção conservadora de
        <span class="editorial-number editorial-number-small">50%</span>,
        o tamanho inicial calculado foi
        <span class="editorial-number editorial-number-small">
        {_numero(n0, 2)}</span>.
        </p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("**Fórmula do tamanho amostral inicial para proporções**")
    st.latex(
        r"n_0 = \frac{z^2 \cdot p(1-p)}{e^2}"
    )
    st.markdown(
        f"""
        <p class="editorial-copy">
        Como a população é finita, foi aplicada a correção para população
        finita:
        </p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("**Fórmula da correção para população finita**")
    st.latex(
        r"n = \frac{N \cdot n_0}{N - 1 + n_0}"
    )
    st.markdown(
        f"""
        <p class="editorial-copy">
        Com
        <span class="editorial-number editorial-number-small">
        N = {_numero(tamanho_populacao)}</span> e
        <span class="editorial-number editorial-number-small">
        n_0 = {_numero(n0, 2)}</span>, o resultado foi arredondado para cima:
        <span class="editorial-number editorial-number-small">
        n = {_numero(tamanho_amostra)}</span> denúncias.
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.header("Como a amostra foi selecionada")
    st.markdown(
        """
        <ol class="editorial-copy">
        <li>Foram identificados os valores válidos e únicos do campo
        <code>hash</code>.</li>
        <li>Foram sorteadas
        <span class="editorial-number editorial-number-small">
        {tamanho_amostra}</span> denúncias por amostragem aleatória simples,
        sem reposição,
        usando o método <code>sample</code> do Pandas.</li>
        <li>Todos os registros de violação associados aos hashes sorteados
        foram mantidos na amostra.</li>
        </ol>
        """,
        unsafe_allow_html=True,
    )

    resultados = st.columns(3)
    resultados[0].markdown(
        f'<p class="editorial-copy">Denúncias selecionadas</p>'
        f'<span class="editorial-number editorial-number-small">'
        f"{_numero(tamanho_amostra)}</span>",
        unsafe_allow_html=True,
    )
    resultados[1].markdown(
        f'<p class="editorial-copy">Registros preservados</p>'
        f'<span class="editorial-number editorial-number-small">'
        f"{_numero(tamanho_registros)}</span>",
        unsafe_allow_html=True,
    )
    resultados[2].markdown(
        f'<p class="editorial-copy">Percentual da população</p>'
        f'<span class="editorial-number editorial-number-small">'
        f"{_numero(percentual_amostrado, 2)}%</span>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <p class="editorial-copy">
        A seleção é reprodutível porque utiliza a semente aleatória
        <span class="editorial-number editorial-number-small">
        {RANDOM_STATE}</span>. Assim, a mesma população e os mesmos
        parâmetros produzem os mesmos hashes selecionados. O procedimento é
        aleatório, mas cada denúncia válida tem a mesma chance de ser
        escolhida.
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        f"Parâmetros utilizados: z = {Z_VALOR}, p = "
        f"{PROPORCAO_CONSERVADORA:.1f}, e = {MARGEM_ERRO:.0%}."
    )
