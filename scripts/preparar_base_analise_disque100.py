from pathlib import Path

import pandas as pd


PASTA_PROJETO = Path(__file__).resolve().parents[1]
PASTA_DADOS = PASTA_PROJETO / "dados"
BASE_CONSOLIDADA = PASTA_DADOS / "base_historica_2025_2026.parquet"
BASE_ANALISE = PASTA_DADOS / "base_analise_disque100.parquet"

COLUNAS_ANALISE = [
    "Grupo_vulnerável",
    "Cenário_da_violação",
    "País",
    "Faixa_etária_da_vítima",
    "hash",
    "violacao",
    "Gênero_do_suspeito",
    "Faixa_etária_do_suspeito",
    "Relação_vítima_suspeito",
    "Denunciante",
]

FAIXAS_ETARIAS_ANALISE = [
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


def preparar_base_analise() -> pd.DataFrame:
    """Cria a base mínima usada pelos painéis da aplicação."""
    df = pd.read_parquet(
        BASE_CONSOLIDADA,
        columns=COLUNAS_ANALISE,
    )
    return df.loc[
        (df["Grupo_vulnerável"]
         == "VIOLÊNCIA CONTRA CRIANÇA OU ADOLESCENTE")
        & (df["Cenário_da_violação"]
           == "AMBIENTE VIRTUAL (NO ÂMBITO DA INTERNET)")
        & (df["País"] == "BR | BRASIL")
        & (df["Faixa_etária_da_vítima"].isin(FAIXAS_ETARIAS_ANALISE))
    ].copy()


def main() -> None:
    df = preparar_base_analise()
    df.to_parquet(
        BASE_ANALISE,
        index=False,
        compression="snappy",
    )
    print(f"Linhas: {len(df)}")
    print(f"Colunas: {len(df.columns)}")
    print(f"Arquivo: {BASE_ANALISE}")


if __name__ == "__main__":
    main()
