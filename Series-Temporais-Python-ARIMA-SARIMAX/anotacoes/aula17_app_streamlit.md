# Aula 17 — Explorando app.py com Streamlit

## Objetivo

Criar uma aplicação para visualizar
os resultados de previsão de demanda.

Não há treinamento durante a execução
do aplicativo.

## Organização

app.py: interface Streamlit.

src/aula17_app_utils.py:
carregamento, validação e gráficos.

outputs/tabelas:
quatro arquivos da Aula 16.

tests:
testes automatizados.

## Configuração

st.set_page_config configura:

- título;
- ícone;
- largura da página.

## Carregamento

Os quatro arquivos CSV são carregados
e suas colunas são validadas.

A aplicação utiliza:

- demanda
- modelo
- MAE
- RMSE
- MAPE
- modelo_final
- inicio_historico
- fim_historico
- dias_historico
- dias_teste

## Indicadores

- melhor modelo;
- MAPE;
- dias observados;
- observações de teste.

## Gráficos

1. Série histórica de demanda.
2. Comparação de MAPE.
3. Previsões dos quatro modelos.

## Interatividade

O painel lateral permite escolher
quais modelos visualizar.

Também é possível consultar e exportar
a tabela de previsões.

## Execução

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Encerramento

Pressione Ctrl+C no terminal
em que o Streamlit estiver rodando.

## Cuidados técnicos

A série histórica possui 263 datas ausentes.

Os 60 registros do teste não correspondem
necessariamente a 60 dias consecutivos.

O SARIMAX foi avaliado com clima histórico
conhecido, não com previsões meteorológicas
geradas antes do período avaliado.

## Próxima aula

Encerramento do curso e possibilidades
de evolução do projeto.
