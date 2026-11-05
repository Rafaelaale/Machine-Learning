# Aula 06 - Amazon S3

## Objetivo
Criar um Data Lake local para o projeto hospitalar.

## Conceitos
Bucket: recipiente de objetos no Amazon S3.
Object: arquivo armazenado com metadados.
Key: identificador do objeto dentro do bucket.
Region: regiao escolhida para armazenar os dados.

## Estrutura do projeto
raw/         - dados originais
process/     - dados tratados
predictions/ - previsoes de Machine Learning

## Seguranca
Na AWS, usar:
- Block Public Access
- Politicas IAM de menor privilegio
- Criptografia e versionamento quando apropriados

## Validacao
O exercicio local compara o SHA-256 do arquivo
original com a copia armazenada em raw/.

## Limites desta simulacao
Pastas locais nao reproduzem automaticamente:
- IAM
- Criptografia gerenciada pela AWS
- Versionamento S3
- Replicacao entre regioes
- Disponibilidade e durabilidade da AWS

Nenhum bucket real foi criado.
Nenhuma cobranca AWS foi gerada.
