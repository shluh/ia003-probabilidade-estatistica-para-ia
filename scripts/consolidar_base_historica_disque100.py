from pathlib import Path

import pandas as pd


PASTA_PROJETO = Path(__file__).resolve().parents[1]
PASTA_DADOS = PASTA_PROJETO / "dados"
PASTA_SEGUNDO_SEMESTRE_2025 = (
    PASTA_DADOS / "segundo_semestre_2025_parquet"
)
PASTA_PRIMEIRO_SEMESTRE_2026 = (
    PASTA_DADOS / "primeiro_semestre_2026_parquet"
)
SAIDA = PASTA_DADOS / "base_historica_2025_2026.parquet"


def consolidar_base() -> pd.DataFrame:
    """Consolida os datasets do Disque 100 em uma base histórica."""
    df_2025 = pd.read_parquet(PASTA_SEGUNDO_SEMESTRE_2025)
    df_2026 = pd.read_parquet(PASTA_PRIMEIRO_SEMESTRE_2026)

    df = pd.concat(
        [df_2025, df_2026],
        ignore_index=True,
    )
    df["Data_de_cadastro"] = pd.to_datetime(df["Data_de_cadastro"])
    return df.sort_values("Data_de_cadastro").reset_index(drop=True)


def main() -> None:
    df = consolidar_base()
    df.to_parquet(
        SAIDA,
        index=False,
        compression="snappy",
    )
    print(f"Linhas: {len(df)}")
    print(f"Arquivo: {SAIDA}")


if __name__ == "__main__":
    main()
