# Aula 04 - Niveis de especializacao da informacao

## 1. Objetivo

Entender a organizacao de novas bases conforme
os niveis de especializacao da informacao.

## 2. Source of Records - SOR

Fonte de registros em sua forma original.

Pode incluir:
- Clientes ativos e inativos.
- Registros duplicados.
- Informacoes incompletas.
- Erros existentes no cadastro.

## 3. Source of Truth - SOT

Fonte tratada segundo regras de qualidade.

Neste laboratorio:
- Remocao de duplicidades.
- Validacao de campos obrigatorios.
- Padronizacao de email e estado.
- Exclusao de registros incompletos.

A SOT conserva clientes validos, independentemente
de estarem ativos ou inativos.

## 4. Specialization - SPEC

Aplicacao de regras especificas de negocio.

Exemplos:
- Clientes ativos.
- Ativos ha mais de seis meses.
- Ativos ha mais de seis meses em SP.

## 5. Reusabilidade

Uma equipe pode reutilizar a fonte tratada ou
uma especializacao existente, sem repetir
todas as transformacoes anteriores.

## 6. Relacao com a linhagem

SOR alimenta SOT.

SOT alimenta SPEC de clientes ativos.

Essa especializacao alimenta outras:
- Mais de seis meses.
- Estado de Sao Paulo.

Documentar essas dependencias permite
rastrear a origem de cada novo ativo.

## 7. Criterios didaticos

Os dados sao ficticios.

A validacao de email e simplificada e nao garante
que o endereco exista ou esteja correto.

Para tornar a analise reproduzivel, adotamos
2026-11-06 como data de referencia.

"Mais de seis meses" significa uma data de inicio
anterior a seis meses da data de referencia.

## 8. Aprendizado principal

A organizacao dos dados em camadas reduz a
repeticao de transformacoes e melhora a
rastreabilidade e a reutilizacao das informacoes.