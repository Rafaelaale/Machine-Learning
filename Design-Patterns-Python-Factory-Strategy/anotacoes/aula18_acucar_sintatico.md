# Aula 18 - Uma pitada de acucar sintatico

## Objetivo

Entender a sintaxe @decorator e sua equivalencia
com a aplicacao explicita de uma funcao decoradora.

## 1. Decorator explicito

```python
somar = adicionar_log(somar)
```

A funcao original e substituida por
uma nova funcao retornada pelo decorator.

## 2. Acucar sintatico

```python
@adicionar_log
def somar(a, b):
    return a + b
```

Esta sintaxe equivale a aplicar:

somar = adicionar_log(somar)

apos a definicao da funcao.

## 3. Aplicacao em mais de uma funcao

```python
@adicionar_log
def somar(a, b):
    return a + b

@adicionar_log
def dividir(a, b):
    return a / b
```

Os dois calculos continuam funcionando,
agora com logs adicionais.

## 4. Reutilizando o decorator da Aula 17

Esta aula importa adicionar_log
do modulo da Aula 17.

Nenhum arquivo da Aula 17 e alterado.

## 5. Proxy versus Decorator

Proxy:
controla acesso, pode esconder o objeto,
adiar carregamentos ou acrescentar verificacoes.

Decorator:
acrescenta comportamentos a objetos ou funcoes.

Os dois podem envolver objetos, mas
seus propositos principais sao diferentes.

## 6. Comportamento do wrapper

O wrapper executa a funcao original,
imprime o log e devolve o resultado.

No exemplo inicial, o wrapper se chama
"wrapper" e nao usa functools.wraps.

## 7. Limites desta aula

Nao implementamos ainda:
- functools.wraps;
- *args e **kwargs;
- decorators com parametros;
- encadeamento de decorators.

Seguiremos a ordem das transcricoes da Alura.

## 8. Arquivos

src/aula18_acucar_sintatico.py
aulas/aula18_acucar_sintatico.py
tests/test_aula18_acucar_sintatico.py
anotacoes/aula18_acucar_sintatico.md
resultados/aula18_acucar_sintatico.json

## 9. Testes

16 testes novos.
Meta acumulada: 288.
