# Projeto CHURN - Estrutura Profissional

## Objetivo

Organizar um projeto de Machine Learning para
analise de abandono de clientes em e-commerce.

Este projeto foi criado para o estudo de
Engenharia de Software para Dados na Alura.

## Origem dos dados

Repositorio oficial:
https://github.com/alura-cursos/projeto-CHURN

Arquivo utilizado:
Churn-antes/dados_corretos2.csv

A amostra contem 10.000 registros.

## Estrutura

- data/raw: dados originais de trabalho
- data/processed: dados preparados
- data/external: fontes externas
- notebooks: analises e experimentos
- tests: testes automatizados do subprojeto
- src/data: carregamento e processamento
- src/features: engenharia de atributos
- src/models: treinamento e avaliacao
- models: modelos treinados
- doc/reports: relatorios e documentacao
- doc/figures: figuras
- requirements.txt: dependencias
- setup.py: configuracao do pacote

## Ambiente

Projeto principal:
Engenharia-de-Software-para-Dados

Interpretador Python:
.venv/Scripts/python.exe

## Principios

- Separacao de responsabilidades
- Codigo limpo
- Reprodutibilidade
- Documentacao
- Reutilizacao
- Testes automatizados

## Status

A estrutura foi criada na Aula 08.

O treinamento de regressao logistica da Aula 07
permanece no projeto principal, separado deste
subprojeto de organizacao profissional.

## Cuidados

Nao carregar arquivos de origem desconhecida
como modelos pickle sem validacao.

Nenhuma implantacao em producao foi realizada.

## Documentacao detalhada - Aula 11

Consulte os documentos disponiveis neste subprojeto:

- [Problema de negocio](doc/PROBLEMA_NEGOCIO.md)
- [Dicionario de dados](doc/DICIONARIO_DADOS.md)
- [Regras de negocio](doc/REGRAS_NEGOCIO.md)
- [Arquitetura](doc/ARQUITETURA.md)
- [Responsabilidades](doc/RESPONSABILIDADES.md)
- [Licenciamento](doc/LICENCIAMENTO.md)
- [Resumo executivo](doc/reports/RESUMO_EXECUTIVO.md)

### Instalacao do pacote de tratamentos

A partir da raiz do projeto principal:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .\projetos\churn_profissional\src\tratamentos
```

### Execucao do laboratorio

```powershell
.\.venv\Scripts\python.exe .\aulas\aula10_pacote_python.py
```

### Testes automatizados

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_aula*.py"
```

### Estado do projeto

Projeto educacional, sem implantacao em producao.

O modelo avaliado na Aula 07 apresentou recall de
0% para churn e precisa de melhorias antes de uso
em qualquer processo de negocio.

A documentacao deve ser revisada sempre que os
dados, as regras ou os componentes forem alterados.
