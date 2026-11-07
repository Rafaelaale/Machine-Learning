# Engenharia de Dados — Arquiteturas Modernas

Projeto educacional com implementacoes praticas
baseadas nas aulas da Alura.

## Estudo de caso: Minishop

Plataforma de dados desenvolvida com Python e SQL.

### Conteudos implementados

- Sistemas OLTP e processamento OLAP
- Modelagem dimensional de Data Warehouse
- Fatos, dimensoes e surrogate keys
- ETL e orquestracao de cargas
- Data Lake e camadas Bronze, Silver e Gold
- Lakehouse com DuckDB e arquivos Parquet
- Consultas SQL sobre dados analiticos
- Camada semantica e metricas de negocio
- Consumo analitico e Business Intelligence
- Catalogo, linhagem e qualidade dos dados

## Organizacao

- `src/`: implementacoes Python
- `aulas/`: executaveis dos laboratorios
- `tests/`: testes automatizados
- `anotacoes/`: documentacao teorica
- `sql/`: scripts SQL, quando disponiveis

## Tecnologias

Python, SQL, SQLite, DuckDB, Parquet e unittest.

## Testes

Ultima execucao local informada:
408 testes aprovados.

O resultado de testes nao substitui a execucao
no ambiente de quem clonar o repositorio.

Para executar, instale as dependencias e utilize:

```powershell
python -m unittest discover -s tests -p "test_aula*.py"
```

## Observacoes

O repositorio publica codigos e documentacao.

Bancos de dados locais, ambientes virtuais,
caches e dados temporarios nao sao incluidos.

Os laboratorios podem gerar seus proprios
arquivos de dados durante a execucao.