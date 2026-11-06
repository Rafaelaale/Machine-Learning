# Arquitetura do projeto

## Projeto principal

Engenharia-de-Software-para-Dados/

- aulas/: programas executaveis das aulas.
- src/: modulos Python criados durante o curso.
- tests/: testes automatizados acumulados.
- anotacoes/: resumos teoricos por aula.
- resultados/: relatorios produzidos nos laboratorios.
- material_alura/: materiais originais da Alura.
- projetos/churn_profissional/: subprojeto estruturado.

## Subprojeto de churn

churn_profissional/

- data/raw/: dados de entrada.
- data/processed/: saidas de pre-processamento.
- data/external/: fontes externas, quando aplicavel.
- notebooks/: experimentos.
- src/data/: modulo de carregamento.
- src/tratamentos/: pacote instalavel.
- models/: artefatos de modelos, quando disponiveis.
- tests/: reservado para testes do subprojeto.
- doc/: documentacao.
- requirements.txt: dependencias declaradas.
- setup.py: configuracao do subprojeto.
- README.md: entrada da documentacao.

## Pacote Python da Aula 10

Instalacao:
python -m pip install -e projetos/churn_profissional/src/tratamentos

Importacao:
from pre_processamento import PreProcessamento

Classe:
PreProcessamento

Etapas:
1. Carregamento do CSV.
2. Conversao de datas.
3. Tratamento de valores ausentes.
4. Codificacao de churn.
5. Criacao de atributos.
6. Codificacao categorica.
7. Exportacao do CSV.

## Limites atuais

O pacote ainda nao aprende parametros de
transformacao somente na etapa de treinamento.

A codificacao categorica pode produzir conjuntos
diferentes de colunas entre bases distintas.

O projeto nao possui implantacao produtiva.
