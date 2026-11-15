import math

import pandas as pd
import streamlit as st
from scipy.stats import norm, t


ALFA = 0.05
Z_95 = norm.ppf(0.975)
TERRACOTA = "#D97757"

IDADES_12_17 = {
    "12 ANOS",
    "13 ANOS",
    "14 ANOS",
    "15 ANOS",
    "16 ANOS",
    "17 ANOS",
}


def _normalizar(serie: pd.Series) -> pd.Series:
    return (
        serie.astype("string")
        .str.strip()
        .replace("", pd.NA)
    )


def _hashes_validos(df: pd.DataFrame) -> pd.Series:
    return _normalizar(df["hash"]).dropna().drop_duplicates()


def _fpc(n: int, n_populacao: int) -> float:
    if n_populacao <= 1 or n >= n_populacao:
        return 0.0
    return math.sqrt((n_populacao - n) / (n_populacao - 1))


def _p_valor_bilateral(z: float) -> float:
    return 2 * norm.sf(abs(z))


def _p_valor_unilateral_direita(z: float) -> float:
    return norm.sf(z)


def _intervalo_proporcao(
    proporcao: float,
    n: int,
    n_populacao: int,
) -> tuple[float, float]:
    erro_padrao = math.sqrt(
        proporcao * (1 - proporcao) / n
    ) * _fpc(n, n_populacao)
    margem = Z_95 * erro_padrao
    return max(0.0, proporcao - margem), min(1.0, proporcao + margem)


def _teste_proporcao(
    sucessos: int,
    n: int,
    n_populacao: int,
    alternativa: str,
) -> dict[str, float | str]:
    proporcao = sucessos / n
    erro_padrao_nulo = math.sqrt(0.5 * 0.5 / n) * _fpc(
        n,
        n_populacao,
    )
    estatistica = (proporcao - 0.5) / erro_padrao_nulo
    if alternativa == "maior":
        valor_p = _p_valor_unilateral_direita(estatistica)
        rejeita = valor_p < ALFA
    else:
        valor_p = _p_valor_bilateral(estatistica)
        rejeita = valor_p < ALFA
    return {
        "proporcao": proporcao,
        "limite_inferior": _intervalo_proporcao(
            proporcao,
            n,
            n_populacao,
        )[0],
        "limite_superior": _intervalo_proporcao(
            proporcao,
            n,
            n_populacao,
        )[1],
        "estatistica": estatistica,
        "valor_p": valor_p,
        "conclusao": (
            "Rejeita-se H₀ ao nível de 5%."
            if rejeita
            else "Não se rejeita H₀ ao nível de 5%."
        ),
    }


def _teste_media(
    valores: pd.Series,
    valor_nulo: float,
    n_populacao: int,
) -> dict[str, float | str]:
    valores = valores.astype(float)
    n = len(valores)
    media = float(valores.mean())
    desvio = float(valores.std())
    erro_padrao = desvio / math.sqrt(n) * _fpc(n, n_populacao)
    estatistica = (media - valor_nulo) / erro_padrao
    graus_liberdade = n - 1
    valor_p = 2 * t.sf(abs(estatistica), graus_liberdade)
    margem = t.ppf(0.975, graus_liberdade) * erro_padrao
    return {
        "media": media,
        "desvio": desvio,
        "limite_inferior": media - margem,
        "limite_superior": media + margem,
        "estatistica": estatistica,
        "valor_p": valor_p,
        "conclusao": (
            "Rejeita-se H₀ ao nível de 5%."
            if valor_p < ALFA
            else "Não se rejeita H₀ ao nível de 5%."
        ),
    }


def _base_denuncias(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series]:
    hashes = _normalizar(df["hash"])
    base = pd.DataFrame({"hash": hashes}).dropna()
    base = base.drop_duplicates()
    return base, base["hash"]


def _evento_proporcoes(df: pd.DataFrame) -> pd.DataFrame:
    base, hashes = _base_denuncias(df)
    idades = _normalizar(df["Faixa_etária_da_vítima"])
    violacoes = _normalizar(df["violacao"])

    eventos_idade = (
        pd.DataFrame({
            "hash": _normalizar(df["hash"]),
            "adolescente": idades.isin(IDADES_12_17),
        })
        .dropna(subset=["hash"])
        .groupby("hash")["adolescente"]
        .any()
    )

    contagem_registros = (
        pd.DataFrame({
            "hash": _normalizar(df["hash"]),
            "violacao": violacoes,
        })
        .dropna(subset=["hash", "violacao"])
        .groupby("hash")
        .size()
    )

    base["adolescente"] = (
        hashes.map(eventos_idade).fillna(False).astype(bool).to_numpy()
    )
    base["registros"] = (
        hashes.map(contagem_registros).fillna(0).astype(int).to_numpy()
    )
    base["multiplos_registros"] = base["registros"] >= 2
    return base


def _idades_por_denuncia(
    df: pd.DataFrame,
) -> tuple[pd.Series, int, int]:
    idades = _normalizar(df["Faixa_etária_da_vítima"])
    mapa_idades = {
        f"{idade:02d} ANO" if idade == 1 else f"{idade:02d} ANOS": idade
        for idade in range(1, 18)
    }
    idade_numerica = idades.map(mapa_idades)
    registros_excluidos = int(idade_numerica.isna().sum())

    base = pd.DataFrame({
        "hash": _normalizar(df["hash"]),
        "idade": idade_numerica,
    }).dropna()
    idades_por_hash = base.groupby("hash")["idade"]
    hashes_multiplas_idades = int(
        (idades_por_hash.nunique() > 1).sum()
    )
    medias_por_hash = idades_por_hash.mean()
    return medias_por_hash, registros_excluidos, hashes_multiplas_idades


def _registros_por_denuncia(df: pd.DataFrame) -> pd.Series:
    base, hashes = _base_denuncias(df)
    contagem = (
        pd.DataFrame({
            "hash": _normalizar(df["hash"]),
            "violacao": _normalizar(df["violacao"]),
        })
        .dropna(subset=["hash", "violacao"])
        .groupby("hash")
        .size()
    )
    base["registros"] = (
        hashes.map(contagem).fillna(0).astype(int).to_numpy()
    )
    return base.set_index("hash")["registros"]


def _indicador(valor: float, percentual: bool = False) -> str:
    if percentual:
        return f"{valor * 100:.2f}%".replace(".", ",")
    return f"{valor:.4f}".replace(".", ",")


def _formatar_p_valor(valor: float) -> str:
    if valor < 0.00005:
        return "<0,0001"
    return f"{valor:.4f}".replace(".", ",")


def _bloco_proporcao(
    titulo: str,
    pergunta: str,
    parametro_populacional: float,
    resultado: dict[str, float | str],
    nome_evento: str,
    tamanho_populacao: int,
    tamanho_amostra: int,
) -> None:
    st.subheader(titulo)
    st.caption(pergunta)
    colunas = st.columns(4)
    colunas[0].metric(
        "Proporção na população",
        _indicador(parametro_populacional, percentual=True),
    )
    colunas[1].metric(
        "Estimativa na amostra",
        _indicador(float(resultado["proporcao"]), percentual=True),
    )
    colunas[2].metric(
        "Limite inferior (95%)",
        _indicador(float(resultado["limite_inferior"]), percentual=True),
    )
    colunas[3].metric(
        "Limite superior (95%)",
        _indicador(float(resultado["limite_superior"]), percentual=True),
    )
    st.write(
        f"**Evento:** {nome_evento}. **α = {ALFA:.0%}** | "
        f"estatística z = {float(resultado['estatistica']):.3f} | "
        f"valor-p = {_formatar_p_valor(float(resultado['valor_p']))}"
    )
    st.write(f"**Conclusão:** {resultado['conclusao']}")
    st.caption(
        f"Comparação baseada em {tamanho_populacao:,} denúncias na "
        f"população e {tamanho_amostra:,} na amostra. "
        "O intervalo e o teste usam correção para população finita."
    )


def _bloco_media(
    titulo: str,
    pergunta: str,
    parametro_populacional: float,
    resultado: dict[str, float | str],
    nome_variavel: str,
    tamanho_populacao: int,
    tamanho_amostra: int,
) -> None:
    st.subheader(titulo)
    st.caption(pergunta)
    colunas = st.columns(4)
    colunas[0].metric(
        "Média na população",
        _indicador(parametro_populacional),
    )
    colunas[1].metric(
        "Estimativa na amostra",
        _indicador(float(resultado["media"])),
    )
    colunas[2].metric(
        "Limite inferior (95%)",
        _indicador(float(resultado["limite_inferior"])),
    )
    colunas[3].metric(
        "Limite superior (95%)",
        _indicador(float(resultado["limite_superior"])),
    )
    st.write(
        f"**Variável:** {nome_variavel}. **α = {ALFA:.0%}** | "
        f"estatística t = {float(resultado['estatistica']):.3f} | "
        f"valor-p = {_formatar_p_valor(float(resultado['valor_p']))}"
    )
    st.write(f"**Conclusão:** {resultado['conclusao']}")
    st.caption(
        f"Comparação baseada em {tamanho_populacao:,} denúncias na "
        f"população e {tamanho_amostra:,} na amostra. "
        "Cada denúncia contribui com uma observação independente."
    )


def render_painel_inferencia(
    df_populacao: pd.DataFrame,
    df_amostra: pd.DataFrame,
    metadados_amostra: dict[str, int | float],
) -> None:
    """Renderiza inferências usando a população como referência."""
    st.title("Inferência estatística")
    st.caption(
        "A população fornece os parâmetros de referência; os testes e "
        "intervalos são calculados a partir da amostra por hash."
    )

    eventos_pop = _evento_proporcoes(df_populacao)
    eventos_amostra = _evento_proporcoes(df_amostra)
    n_pop = len(eventos_pop)
    n_amostra = len(eventos_amostra)

    st.header("Inferência para proporções")

    resultado_adolescentes = _teste_proporcao(
        int(eventos_amostra["adolescente"].sum()),
        n_amostra,
        n_pop,
        "maior",
    )
    parametro_adolescentes = eventos_pop["adolescente"].mean()
    _bloco_proporcao(
        "Hipótese 1 — Denúncias envolvendo adolescentes",
        "H₀: p = 0,50 | H₁: p > 0,50. Mais de 50% das denúncias "
        "envolvem vítimas de 12 a 17 anos?",
        parametro_adolescentes,
        resultado_adolescentes,
        "denúncia com ao menos um registro de vítima de 12 a 17 anos",
        n_pop,
        n_amostra,
    )

    resultado_multiplos = _teste_proporcao(
        int(eventos_amostra["multiplos_registros"].sum()),
        n_amostra,
        n_pop,
        "maior",
    )
    parametro_multiplos = eventos_pop["multiplos_registros"].mean()
    _bloco_proporcao(
        "Hipótese 2 — Denúncias com múltiplos registros",
        "H₀: p = 0,50 | H₁: p > 0,50. Mais de 50% das denúncias "
        "apresentam dois ou mais registros de violações?",
        parametro_multiplos,
        resultado_multiplos,
        "denúncia com pelo menos dois registros de violações",
        n_pop,
        n_amostra,
    )

    st.divider()
    st.header("Inferência para médias")

    idades_pop, excluidos_pop, multiplas_pop = _idades_por_denuncia(
        df_populacao
    )
    idades_amostra, excluidos_amostra, multiplas_amostra = (
        _idades_por_denuncia(df_amostra)
    )
    resultado_idade = _teste_media(
        idades_amostra,
        12,
        len(idades_pop),
    )
    _bloco_media(
        "Hipótese 3 — Idade média das vítimas",
        "H₀: μ = 12 | H₁: μ ≠ 12. A idade média das vítimas "
        "é diferente de 12 anos?",
        float(idades_pop.mean()),
        resultado_idade,
        "média das idades numéricas de 1 a 17 anos por denúncia",
        len(idades_pop),
        len(idades_amostra),
    )
    st.caption(
        f"Foram excluídos {excluidos_pop:,} registros da população e "
        f"{excluidos_amostra:,} da amostra por não atenderem ao critério "
        "de idade numérica entre 1 e 17 anos. Não foram atribuídas idades "
        "aproximadas. Hashes com mais de uma idade distinta: "
        f"{multiplas_pop:,} na população e {multiplas_amostra:,} na amostra. "
        "Nesses casos, foi utilizada a média das idades válidas dentro "
        "de cada hash, mantendo uma observação por denúncia."
    )

    registros_pop = _registros_por_denuncia(df_populacao)
    registros_amostra = _registros_por_denuncia(df_amostra)
    resultado_registros = _teste_media(
        registros_amostra,
        4,
        len(registros_pop),
    )
    _bloco_media(
        "Hipótese 4 — Média de registros por denúncia",
        "H₀: μ = 4 | H₁: μ ≠ 4. A quantidade média de registros "
        "de violações por denúncia é diferente de 4?",
        float(registros_pop.mean()),
        resultado_registros,
        "quantidade de registros de violações por hash",
        len(registros_pop),
        len(registros_amostra),
    )

    st.divider()
    st.caption(
        "Limitações: a seleção foi feita por denúncia, sem reposição, "
        "e todos os registros de cada hash foram preservados. Os erros "
        "padrão usam correção para população finita; proporções usam "
        "aproximação normal e médias usam teste t de uma amostra. As "
        "condições de tamanho e contagem da amostra são adequadas aos "
        "procedimentos aplicados. As conclusões não comprovam hipóteses; "
        "indicam apenas se há evidência estatística suficiente para rejeitar "
        "H₀ ao nível de 5%. A variabilidade entre amostras pode alterar "
        "estimativas, intervalos e valores-p."
    )
