import streamlit as st


def render() -> None:
    st.title("Escolha da base de dados")

    st.header("A fonte e o link de acesso à base de dados")
    st.markdown(
        """
        | Informação | Resposta |
        |---|---|
        | Instituição ou responsável pelos dados | Ministério dos Direitos Humanos e da Cidadania |
        | Página do conjunto de dados | [https://www.gov.br/mdh/pt-br/acesso-a-informacao/dados-abertos/disque100](https://www.gov.br/mdh/pt-br/acesso-a-informacao/dados-abertos/disque100) ou [https://dados.gov.br/dados/conjuntos-dados/ouvidoria-nacional-de-direitos-humanos--ondh](https://dados.gov.br/dados/conjuntos-dados/ouvidoria-nacional-de-direitos-humanos--ondh) |
        | Formato e arquivos utilizados | CSV |
        | Licença ou condições de uso | Dados Abertos. Creative Commons Attribution |
        | Restrições de acesso ou compartilhamento | Não foi identificada |
        """
    )

    st.header("Uma breve descrição do contexto e do objetivo da base")
    st.markdown(
        """
        - **Tema ou domínio:** Proteção de crianças e adolescentes no ambiente virtual.
        - **Conjunto de dados escolhido:** Disque Direitos Humanos (Disque 100). A base de dados é proveniente dos Dados Abertos do Disque Direitos Humanos (Disque 100), disponibilizados pelo Ministério dos Direitos Humanos e da Cidadania (MDHC). O conjunto de dados reúne registros de denúncias de possíveis violações de direitos humanos recebidas pelo serviço, contendo informações sobre as características das denúncias, das vítimas, dos possíveis suspeitos e das violações relatadas.
        - **Por que o grupo se interessa por esse tema?** Por sua relevância social e pela possibilidade de utilizar dados públicos para compreender as ocorrências e, possivelmente, identificar padrões que possam contribuir para ações de prevenção e proteção.
        - **Que problema ou decisão a visualização poderia apoiar?** Identificação de padrões nas ocorrências.
        - **Recorte inicial:** Segundo semestre de 2025 e primeiro semestre de 2026, considerando apenas registros no Brasil e pessoas de nacionalidade brasileira. O objetivo de analisar registros de violência contra crianças e adolescentes no ambiente virtual no Brasil, buscando identificar padrões e características dessas violações que possam contribuir para a compreensão do fenômeno e subsidiar iniciativas de prevenção e proteção desse público.
        """
    )

    st.header("O número de observações e de variáveis")
    st.markdown(
        """
        <p class="editorial-copy">
        A base original possui
        <span class="editorial-number editorial-number-small">
        5.247.302</span> registros (linhas) e
        <span class="editorial-number editorial-number-small">62</span>
        variáveis (colunas).
        </p>
        <p class="editorial-copy">
        Para delimitar o objeto de estudo, foram aplicados critérios de
        filtragem relacionados ao grupo vulnerável, cenário da violação,
        país e faixa etária da vítima.
        </p>
        <p class="editorial-copy">
        Após essa seleção, foi obtido um subconjunto específico para a
        análise de violência contra crianças e adolescentes (0 a 17 anos)
        no ambiente virtual no Brasil, contendo
        <span class="editorial-number editorial-number-small">
        20.616</span> registros e <span class="editorial-number editorial-number-small">62</span>
        variáveis.
        </p>
        <p class="editorial-copy">
        Cada linha representa um registro de violação associado a uma
        denúncia, sendo possível que uma mesma denúncia esteja relacionada
        a múltiplas violações.
        </p>
        <p class="editorial-copy">
        As dimensões foram identificadas utilizando o atributo
        <code>.shape</code>, da biblioteca Pandas, em Python.
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.header("A definição da população de interesse e da unidade amostral")
    st.markdown(
        """
        <p class="editorial-copy">
        A população de interesse compreende
        <span class="editorial-highlight">
        crianças e adolescentes de 0 a 17 anos</span> expostos a situações
        de violência no <span class="editorial-highlight">
        ambiente virtual</span> no <span class="editorial-highlight">
        Brasil</span>. A população acessível corresponde aos registros de
        denúncias recebidos e disponibilizados pelo Disque 100, referentes
        ao período entre o segundo semestre de 2025 e o primeiro semestre de
        2026, que atendem aos critérios de seleção estabelecidos.
        </p>
        <p class="editorial-copy">
        A unidade amostral é a <span class="editorial-highlight">
        denúncia</span>, identificada pelo campo <code>hash</code>. Como uma
        mesma denúncia pode envolver múltiplas violações, um único
        identificador pode estar associado a diferentes registros na base de
        dados.
        </p>
        <p class="editorial-copy">
        O estudo abrange a totalidade dos registros que atendem aos critérios
        de seleção, caracterizando um levantamento censitário do subconjunto
        analisado.
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.header("A descrição das variáveis selecionadas para as análises")
    st.markdown(
        """
        <p class="editorial-copy">
        Antes de calcular estatísticas, é importante compreender o
        significado dos registros e como os dados foram produzidos.
        </p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        - **O que uma linha representa?** Denúncias recebidas pelo Disque Direitos Humanos (Disque 100).
        - **Como os dados foram produzidos?** Dados Abertos do Ministério dos Direitos Humanos e da Cidadania.
        - **Qual é a cobertura temporal e geográfica?** Brasil, segundo semestre de 2025 a primeiro semestre de 2026.
        - **Quem ou o que pode estar ausente da base?** Estão ausentes, devido ao recorte adotado, denúncias não relacionadas a crianças e adolescentes e aquelas em que o cenário da violação não seja exclusivamente virtual. Também podem estar ausentes casos que não foram denunciados ao Disque 100, além de pessoas ou regiões com menor acesso ou conhecimento sobre o canal. Da mesma forma, podem existir ocorrências registradas exclusivamente por outros canais de denúncia.
        - **Há mais de uma tabela? Como elas se relacionam?** Não se aplica.
        """
    )

    st.subheader("Dicionário dos principais atributos")
    st.markdown(
        """
        Os atributos abaixo são relevantes para a proposta. O tipo
        computacional da coluna não determina sozinho seu significado:
        um código numérico, por exemplo, pode representar uma categoria.

        | Atributo | Significado | Tipo semântico | Unidade ou categorias | Observações |
        |---|---|---|---|---|
        | `violacao` | Tipo de violação registrado na denúncia | Qualitativa nominal | Categorias de violação | Pode apresentar categorias hierárquicas |
        | `Faixa_etária_do_suspeito` | Faixa etária informada do suspeito | Qualitativa ordinal | Faixas etárias | Pode conter valores ausentes ou categorias especiais |
        | `Gênero_do_suspeito` | Gênero informado do suspeito | Qualitativa nominal | Categorias de gênero | Verificar valores ausentes ou não informados |
        | `UF` | Unidade federativa associada ao registro | Qualitativa nominal | Estados brasileiros e Distrito Federal | Verificar valores ausentes ou códigos especiais |
        | `UF_da_vítima` | Unidade federativa informada da vítima | Qualitativa nominal | Estados brasileiros e Distrito Federal | Pode diferir da UF do registro |
        | `Data_de_cadastro` | Data e horário de cadastro do registro | Variável temporal | Data e hora | Formato observado: AAAA-MM-DD HH:MM:SS |
        """
    )
