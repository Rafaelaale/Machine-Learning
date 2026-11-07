# Aula 25 - Padrão Strategy

## Objetivo

Refatorar o exemplo de descontos da
Aula 24 para eliminar as condições
de dentro da função calcular_preco.

## 1. Problema anterior

A função calcular_preco utilizava
vários if/elif/else para decidir
qual desconto deveria aplicar.

Isso provocava complexidade crescente,
alto acoplamento e dificuldade
de manutenção e reutilização.

## 2. Classe abstrata

RegraDeDesconto é a abstração
compartilhada pelas estratégias.

```python id="7ps3dv"
from abc import ABC, abstractmethod

class RegraDeDesconto(ABC):
    @abstractmethod
    def calcular(self, total):
        pass
```

Uma estratégia concreta precisa
implementar o método calcular.

## 3. Estratégias concretas

DescontoVip:
total * 0.8

DescontoNovo:
total * 0.9

DescontoFuncionario:
total * 0.7

SemDesconto:
total

Cada estratégia possui
uma única responsabilidade.

## 4. Composição no Cliente

```python id="jfkav1"
class Cliente:
    def __init__(self, nome, estrategia: RegraDeDesconto):
        self.nome = nome
        self.regra_de_desconto = estrategia
```

O cliente armazena a estratégia
que será utilizada.

## 5. Polimorfismo

```python id="d8jvtf"
def calcular_preco(cliente: Cliente, total):
    return cliente.regra_de_desconto.calcular(total)
```

A função não precisa conhecer
as classes concretas de desconto.

Cada objeto resolve o cálculo
por meio do seu próprio método.

## 6. Exemplos da aula

```python id="8mf8xa"
maria = Cliente("Maria", DescontoVip())
joao = Cliente("João", DescontoNovo())
ana = Cliente("Ana", SemDesconto())

print(calcular_preco(maria, 200))  # 160
print(calcular_preco(joao, 200))   # 180
print(calcular_preco(ana, 200))    # 200
```

## 7. Estratégias intercambiáveis

A estratégia da Maria pode ser
substituída depois da criação.

```python id="fbogkz"
maria.regra_de_desconto = DescontoNovo()
```

Agora o preço final para R$ 200
passa de R$ 160 para R$ 180.

## 8. Aberto/fechado

Uma nova regra pode ser criada
por meio de uma classe adicional.

Não é necessário modificar
calcular_preco para adicionar
essa nova estratégia.

## 9. Benefícios

- Extensibilidade.
- Manutenção mais simples.
- Maior coesão.
- Melhor testabilidade.
- Reutilização.
- Baixo acoplamento.
- Código mais claro.

## 10. Relação com a Aula 24

A Aula 24 demonstrou o problema.

A Aula 25 aplica Strategy usando
classes concretas e uma classe abstrata.

As regras de parceria e Black Friday
da aula anterior não foram migradas
nesta etapa, pois a transcrição
apresenta somente quatro estratégias.

## 11. Próxima aula

A transcrição anuncia a implementação
do Strategy utilizando funções,
aproveitando que funções também
são objetos em Python.

Não antecipamos essa implementação.

## 12. Arquivos

src/aula25_padrao_strategy.py
aulas/aula25_padrao_strategy.py
tests/test_aula25_padrao_strategy.py
anotacoes/aula25_padrao_strategy.md
resultados/aula25_padrao_strategy.json

## 13. Validação

16 testes novos.
Meta acumulada: 400 testes.
