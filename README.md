# Análise e visualização de dados do Disque 100

Aplicação interativa desenvolvida com Streamlit para explorar registros
públicos do Disque 100 e analisar denúncias de violência contra crianças e
adolescentes no ambiente virtual.

## Requisitos

- Python 3.10 ou superior
- `pip`

## Configuração do ambiente

### macOS e Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências no ambiente virtual:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Dados

A fonte oficial é a [página de dados abertos do Ministério dos Direitos
Humanos e da Cidadania](https://www.gov.br/mdh/pt-br/acesso-a-informacao/dados-abertos/disque100).

Os datasets utilizados são:

- **Segundo semestre de 2025**
- **Primeiro semestre de 2026**

Os arquivos originais não são versionados neste repositório. Após baixá-los
na página oficial, organize-os em `dados/` com os seguintes nomes de pastas:

```text
dados/
├── segundo_semestre_2025_parquet/
└── primeiro_semestre_2026_parquet/
```

Gere a base consolidada executando:

```bash
python scripts/consolidar_base_historica_disque100.py
```

O script cria `dados/base_historica_2025_2026.parquet`, arquivo utilizado pela
aplicação. As pastas de origem e o arquivo consolidado são ignorados pelo
Git por serem dados gerados ou baixados.

## Estrutura do projeto

```text
.
├── app.py                         # Entrada da aplicação Streamlit
├── scripts/                       # Preparação e consolidação dos dados
│   └── consolidar_base_historica_disque100.py
├── paineis/                       # Seções exibidas no menu lateral
│   ├── escolha_base_de_dados.py
│   ├── procedimento_de_selecao.py
│   ├── painel_descritivo_populacao.py
│   ├── painel_descritivo_amostra.py
│   └── hipoteses_formuladas.py
├── calculos/                      # Amostragem e cálculos estatísticos
│   ├── amostragem.py
│   └── inferencia.py
├── componentes_visuais/           # Gráficos e renderização Streamlit
│   ├── visual_amostra.py
│   ├── visual_populacao.py
│   ├── visual_procedimento.py
│   └── visual_inferencia.py
├── dados/                         # Bases utilizadas pela aplicação
└── imagens/                       # Logos e imagens da interface
```

Os arquivos dentro de `paineis/` correspondem às seções exibidas no menu
lateral. A pasta `calculos/` contém as regras estatísticas, enquanto
`componentes_visuais/` contém a apresentação dos dados. Essa separação mantém
o ponto de entrada pequeno e facilita a manutenção sem misturar lógica e
interface.

## Executar a aplicação

Com o ambiente virtual ativado e as dependências instaladas, execute:

```bash
streamlit run app.py
```

O Streamlit abrirá a aplicação no navegador. Para interromper o servidor,
pressione `Ctrl+C` no terminal.
