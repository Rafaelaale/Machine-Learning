# Séries Temporais com Python — ARIMA, SARIMA e SARIMAX

Projeto desenvolvido no VS Code durante a trilha da Alura.

## Conteúdos estudados

- Preparação e tratamento da série temporal de bicicletas
- Análise exploratória e visualização com Plotly
- Tendência, sazonalidade e decomposição
- Estacionariedade, teste ADF e diferenciação
- Autocorrelação (ACF) e autocorrelação parcial (PACF)
- Parâmetros p, d e q do ARIMA
- Divisão temporal em treino e teste
- Baseline e treinamento ARIMA
- Avaliação com MAE, RMSE e MAPE
- Preparação e treinamento SARIMA
- Variáveis exógenas de clima e calendário
- Treinamento e previsão SARIMAX
- Comparação dos quatro modelos
- Preparação de resultados para Streamlit
- Desenvolvimento e validação do dashboard Streamlit
- Testes automatizados e auditoria dos arquivos

## Resultados da modelagem

| Modelo | MAE | RMSE | MAPE |
|---|---:|---:|---:|
| SARIMAX | 909,00 | 1093,52 | 18,17% |
| Baseline | 1585,18 | 1865,91 | 31,81% |
| ARIMA | 1730,65 | 2031,36 | 34,68% |
| SARIMA | 1775,68 | 2077,50 | 35,53% |

O SARIMAX apresentou o menor MAPE no teste histórico.

Foram utilizadas 396 observações para treino e 60 para teste.

**Limitações:** existem 263 datas ausentes no calendário. A avaliação SARIMAX utilizou clima histórico conhecido, não previsões meteorológicas disponíveis antecipadamente.

## Estrutura

- **src/** — implementação dos modelos e funções
- **aulas/** — executáveis de cada aula
- **notebooks/** — atividades Jupyter
- **tests/** — testes automatizados
- **dados/** — dados de entrada
- **resultados/** — métricas e previsões
- **outputs/tabelas/** — CSVs utilizados pelo aplicativo
- **graficos/** — visualizações Plotly
- **modelos/** — modelos treinados
- **anotacoes/** — documentação dos estudos
- **app.py** — aplicação Streamlit

## Executar a aplicação

Instale as dependências Python necessárias e execute:

``powershell
python -m streamlit run app.py
``

## Auditoria

Na última auditoria informada: 222 testes aprovados, 1 erro de coleta/execução associado ao teste ADF da Aula 05 e 6 avisos de compatibilidade.

O problema pendente não foi ocultado nem apresentado como resolvido.

## Repositório

Projeto publicado dentro de [Machine-Learning](https://github.com/Rafaelaale/Machine-Learning).