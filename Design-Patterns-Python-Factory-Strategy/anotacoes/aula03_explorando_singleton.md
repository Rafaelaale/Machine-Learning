# Aula 03 - Explorando o Singleton

## Problema

Precisamos carregar uma configuracao JSON
uma vez e compartilhar o mesmo objeto.

## Solucao apresentada pela Alura

Uma classe Config com:

- NOME_DO_ARQUIVO
- _instancia = None
- __init__()
- get_instance() usando @classmethod

## Primeira chamada

Config.get_instance()

Quando _instancia e None:
- Cria o objeto.
- Le o JSON.
- Guarda a instancia na classe.

## Chamadas posteriores

Retornam o objeto existente.

## Identidade

s1 = Config.get_instance()
s2 = Config.get_instance()

s1 is s2 -> True

## Limitacao demonstrada

s3 = Config()

s1 is s3 -> False

A classe ainda permite a criacao direta
de outras instancias.

## __new__ e __init__

__new__ participa da criacao do objeto.

__init__ inicializa o objeto criado.

## Observacao sobre o projeto

Esta aula reutiliza o config.json da Aula 01.

Nao e necessario inserir senhas reais,
usuarios reais nem dados de banco de producao.

O laboratorio mostra apenas as chaves do
arquivo para evitar exibir valores sensiveis.

## Outras limitacoes

- Nao ha bloqueio de instanciacao direta.
- A implementacao nao e thread-safe.
- O controle vale para a classe no processo.
- Reiniciar Python reinicia o estado da classe.

## Proxima etapa

Aprimorar o Singleton conforme os proximos
exemplos do curso.
