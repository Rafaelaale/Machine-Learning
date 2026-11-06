# Governança de Dados: Qualidade de Metadados

Projeto desenvolvido durante os estudos da trilha
**Governança de dados: Qualidade de metadados**, da Alura.

## Conteúdos abordados

- Arquitetura de medalhão: Bronze, Silver e Gold
- Artefatos de metadados em JSON
- Programação orientada a objetos com Python
- Classes MetadadosTabela e MetadadosColuna
- Leitura e transformação de artefatos
- Conversão de objetos em DataFrames Pandas
- Consolidação de metadados
- Análise de completude
- Avaliação de regras e validade
- Privacidade e confidencialidade
- Convenções de nomenclatura
- Avaliação de descrições de colunas
- Análise lexical e n-gramas
- Similaridade de cosseno
- Gestão do conhecimento organizacional
- Hierarquia DIKW: dados, informação, conhecimento e sabedoria

## Tecnologias

Python, Pandas, JSON, orientação a objetos, pathlib,
expressões regulares e estatística textual.

## Organização

- `classes/`: classes Python para metadados
- `artefatos/`: arquivos JSON por camada
- `metadados/`: arquivos JSON utilizados nas aulas
- `regras/`: regras de governança
- `resultados/`: relatórios e análises CSV
- `anotacoes/`: conteúdo teórico
- `aula*.py`: implementações práticas

## Execução

Instalar a dependência principal:

```powershell
python -m pip install pandas
```

Executar a consolidação:

```powershell
python aula10_consolidar_dataframes.py
```

Executar as análises:

```powershell
python aula11_analisando_dados.py
python aula12_regras_metadados.py
python aula13_avaliacao_descricoes.py
python aula14_avaliando_descricoes.py
python aula15_qualidade_descricoes.py
python aula16_analise_estatistica_descricoes.py
```

## Observações

Os artefatos apresentados são exemplos didáticos.

A ausência de metadados não implica automaticamente
invalidade de negócio.

A qualidade semântica das descrições requer contexto
e validação das pessoas responsáveis pelos dados.