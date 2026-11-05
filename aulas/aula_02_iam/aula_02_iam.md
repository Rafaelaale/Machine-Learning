# Aula 02 - AWS IAM

## IAM
Gerencia identidades e permissoes na AWS.

## Usuario
Identidade individual com permissoes.

## Grupo
Conjunto de usuarios que compartilham permissoes.

## Role
Identidade assumida temporariamente por usuarios,
aplicacoes ou servicos, como o SageMaker.

## Policy
Documento JSON que define:
- Effect: Allow ou Deny
- Action: operacao autorizada
- Resource: recurso ao qual a regra se aplica

## Privilegio minimo
Permitir somente as operacoes necessarias.

## Exercicio pratico
A politica politica_s3_upload.json permite:
- Enviar arquivos usando s3:PutObject
- Apenas para o prefixo uploads/ do bucket de exemplo

A politica nao concede, por si so:
- s3:GetObject
- s3:DeleteObject
- s3:ListBucket

## Seguranca
- Proteger o root com MFA.
- Nao usar o root nas atividades diarias.
- Preferir IAM Identity Center e credenciais temporarias.
- Nunca colocar senhas ou chaves AWS no codigo.

## Observacao
O bucket usado no JSON e apenas ilustrativo.
Nenhum recurso AWS foi criado.
