"""Aplicacao Streamlit - Previsao de demanda de bicicletas.

Lê os CSVs produzidos na Aula 16.
Nao treina modelos durante a visualizacao.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

from src.aula17_app_utils import (
    carregar_dados,
    formatar_data,
    diagnosticar_calendario,
    grafico_historico,
    grafico_metricas,
    grafico_previsoes,
    COLUNAS_PREVISOES,
)


# 1. CONFIGURACAO DA PAGINA

st.set_page_config(
    page_title="Previsao de demanda de bicicletas",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded",
)


# 2. CARREGAMENTO DOS DADOS

@st.cache_data(show_spinner=False)
def carregar_dados_cache():
    return carregar_dados()


try:
    (
        serie_historica,
        metricas,
        previsoes,
        resumo_projeto,
    ) = carregar_dados_cache()

except (
    FileNotFoundError,
    ValueError,
    KeyError,
    pd.errors.EmptyDataError,
    AssertionError,
) as erro:
    st.error(
        "Nao foi possivel carregar os dados do projeto."
    )
    st.exception(erro)
    st.stop()


resumo = resumo_projeto.iloc[0]

modelo_final = str(resumo["modelo_final"])
mape_final = float(resumo["MAPE"])

inicio_historico = formatar_data(
    resumo["inicio_historico"]
)

fim_historico = formatar_data(
    resumo["fim_historico"]
)

inicio_teste = formatar_data(
    previsoes["data_hora"].min()
)

fim_teste = formatar_data(
    previsoes["data_hora"].max()
)

dias_ausentes = diagnosticar_calendario(
    serie_historica
)


# 3. NAVEGACAO E FILTROS

with st.sidebar:
    st.header("Painel de controle")

    st.write(
        "Selecione as curvas que deseja "
        "comparar no periodo de teste."
    )

    modelos_selecionados = st.multiselect(
        "Series exibidas",
        options=list(COLUNAS_PREVISOES),
        default=[
            "Demanda real",
            "Baseline",
            "SARIMAX",
        ],
    )

    st.divider()

    st.caption(
        "Os resultados sao carregados de "
        "arquivos CSV ja preparados."
    )

    st.caption(
        "Nenhum modelo e treinado nesta pagina."
    )


# 4. CABECALHO

st.title("Previsao de demanda de bicicletas")

st.write(
    "Analise historica e comparacao de quatro "
    "abordagens de previsao: Baseline, ARIMA, "
    "SARIMA e SARIMAX."
)

st.caption(
    "Python | pandas | statsmodels | "
    "Plotly | Streamlit"
)


# 5. INDICADORES PRINCIPAIS

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Melhor modelo",
        modelo_final.replace(
            "(1,1,1)x(1,0,1,7)", ""
        ),
    )

with col2:
    st.metric(
        "MAPE do melhor modelo",
        f"{mape_final:.2f}%",
    )

with col3:
    st.metric(
        "Dias observados",
        int(resumo["dias_historico"]),
    )

with col4:
    st.metric(
        "Observacoes de teste",
        int(resumo["dias_teste"]),
    )

st.caption(
    f"Historico: {inicio_historico} a {fim_historico}"
    f" | Teste: {inicio_teste} a {fim_teste}"
)

st.caption(
    f"O historico possui {dias_ausentes} datas "
    "sem observacoes no calendario."
)


# 6. SERIE HISTORICA

st.divider()

st.subheader("Comportamento historico da demanda")

st.write(
    "Quantidade diaria observada de bicicletas "
    "alugadas, incluindo periodos de aumento "
    "e reducao da demanda."
)

st.plotly_chart(
    grafico_historico(serie_historica),
    use_container_width=True,
)


# 7. COMPARACAO DOS MODELOS

st.divider()

st.subheader("Comparacao dos modelos")

st.write(
    "O MAPE representa o erro percentual "
    "absoluto medio. Quanto menor, melhor "
    "foi o desempenho no periodo de teste."
)

metricas_ordenadas = (
    metricas.sort_values("MAPE")
    .reset_index(drop=True)
)

st.plotly_chart(
    grafico_metricas(metricas_ordenadas),
    use_container_width=True,
)

st.dataframe(
    metricas_ordenadas.style.format({
        "MAE": "{:,.2f}",
        "RMSE": "{:,.2f}",
        "MAPE": "{:.2f}%",
    }),
    hide_index=True,
    use_container_width=True,
)


# 8. PREVISOES NO TESTE

st.divider()

st.subheader("Previsoes no periodo de teste")

st.write(
    "Compare a demanda real com as previsoes "
    "dos modelos. Utilize o filtro lateral "
    "para escolher as linhas."
)

if modelos_selecionados:
    st.plotly_chart(
        grafico_previsoes(
            previsoes,
            modelos_selecionados,
        ),
        use_container_width=True,
    )

else:
    st.warning(
        "Selecione ao menos uma serie "
        "no painel lateral."
    )


# 9. DADOS DE PREVISAO

with st.expander("Consultar os dados das previsoes"):
    st.dataframe(
        previsoes,
        hide_index=True,
        use_container_width=True,
    )

    st.download_button(
        "Exportar previsoes em CSV",
        data=previsoes.to_csv(
            index=False
        ).encode("utf-8-sig"),
        file_name="previsoes_bicicletas.csv",
        mime="text/csv",
    )


# 10. LIMITACOES DA ANALISE

st.divider()

st.info(
    "As previsoes apresentadas sao de um teste "
    "historico. O SARIMAX utilizou informacoes "
    "climaticas ja observadas. Previsoes de "
    "periodos futuros exigem valores futuros "
    "das variaveis externas, como temperatura "
    "e umidade."
)

st.warning(
    "A serie possui dias sem observacoes. "
    "Um ciclo de sete registros nem sempre "
    "corresponde a sete dias consecutivos "
    "do calendario."
)


# 11. INFORMACOES COMPLEMENTARES

with st.expander("Como adaptar esta aplicacao"):
    st.markdown(
        """
        Este dashboard utiliza quatro arquivos:

        - `outputs/tabelas/serie_historica.csv`
        - `outputs/tabelas/metricas.csv`
        - `outputs/tabelas/previsoes.csv`
        - `outputs/tabelas/resumo_projeto.csv`

        Possiveis evolucoes:

        - alterar cores e titulos;
        - incluir filtros de datas;
        - acrescentar novas metricas;
        - testar outros modelos de previsao;
        - incorporar previsoes meteorologicas;
        - publicar o projeto em um ambiente web.

        Os graficos sao interativos e podem
        ser ampliados pelo Plotly.
        """
    )
