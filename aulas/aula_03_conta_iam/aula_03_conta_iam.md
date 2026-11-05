# Aula 03 - Conta AWS e administrador

## Objetivo
Preparar uma conta AWS segura para estudar ciencia de dados.

## Cadastro
- [ ] Verificar se ja possuo uma conta AWS
- [ ] Consultar elegibilidade ao plano gratuito
- [ ] Concluir cadastro no site oficial, se necessario
- [ ] Proteger o usuario root com MFA
- [ ] Conferir plano, creditos e data de expiracao
- [ ] Configurar alertas de custos e uso

## Administracao de identidades
- [ ] Conhecer o IAM Identity Center
- [ ] Configurar acesso administrativo seguro
- [ ] Nao utilizar root nas atividades cotidianas
- [ ] Preferir credenciais temporarias
- [ ] Aplicar o principio do menor privilegio

## Politicas IAM
AdministratorAccess:
Permite praticamente todas as acoes e recursos.
Nao deve ser atribuido a usuarios comuns de estudo.

politica_s3_exemplo.json:
Demonstra permissao de leitura, envio e exclusao
de objetos em um bucket de exemplo.

## Faturamento
Acesso ao console de cobranca para usuarios e roles IAM
pode exigir ativacao especifica pelo root, alem
das permissoes IAM necessarias.

## Seguranca
Nunca salvar credenciais, tokens, senhas ou dados
de cartao dentro do repositorio do projeto.

## Estado
Esta pratica local nao cria conta AWS,
usuarios IAM, buckets ou recursos pagos.
