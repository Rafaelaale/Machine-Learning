# Aula 07 - Criando bucket no S3

## Configuracao estudada

Regiao: Europa, Estocolmo - eu-north-1
Tipo: General Purpose
ACLs: desabilitadas
Acesso publico: bloqueado
Criptografia: SSE-S3
Versionamento: desativado para o exercicio

## Pastas

raw/         - dados originais
processed/   - dados transformados
predictions/ - resultados de modelos

A pasta process/ da aula anterior foi preservada.

## Arquivo

raw/heart.csv - 918 registros

## AWS real vs ambiente local

A configuracao salva em JSON documenta as
opcoes utilizadas no console AWS.

Ela NAO ativa criptografia, IAM ou controles
de acesso reais no sistema de arquivos local.

O caminho s3:// e apenas ilustrativo.

## Custos

Nenhum recurso foi criado na AWS.
Nenhum pagamento necessario.
