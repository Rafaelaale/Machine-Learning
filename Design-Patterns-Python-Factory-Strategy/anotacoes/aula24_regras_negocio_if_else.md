# Aula 24 - Regras de negocio if/else ao resgate de novo

## Objetivo

Demonstrar os problemas de design que
surgem quando muitas regras comerciais
ficam concentradas em um unico metodo.

A aula prepara o estudo de Strategy.

## 1. Modelo Cliente

```python
from dataclasses import dataclass

@dataclass
class Cliente:
    nome: str
    tipo: str
    parceiro: str = None
```

No projeto foi utilizada a anotacao
Optional[str], equivalente para esse
uso com valor padrao None.

## 2. Regras iniciais

vip: total * 0.8
novo: total * 0.9
funcionario: total * 0.7
outros: total sem alteracao

## 3. Regras expandidas

parceria: total * 0.85

Se parceiro == empresa_x:
    preco -= 10

Se parceiro == empresa_y:
    preco -= 5

black_friday:
    preco = total * 0.5

Se total > 500:
    preco *= 0.9

Importante: a verificacao usa o total
original, nao o preco com desconto.

No limite exato de R$ 500, o desconto
extra nao se aplica.

## 4. Problemas apresentados na aula

1. Complexidade crescente.
2. Dificil manutencao.
3. Dificil testabilidade.
4. Violacao do principio aberto/fechado.
5. Baixa coesao.
6. Alto acoplamento.
7. Dificil reutilizacao.

Um code smell indica possivel
problema de design, nao necessariamente bug.

## 5. Principio aberto/fechado

Novos tipos de cliente obrigam
a modificar calcular_preco.

Essa situacao motiva separar regras
em implementacoes independentes.

## 6. Solucao proposta pela transcricao

Separar as estrategias de calculo
de preco em funcoes ou objetos diferentes.

A implementacao de Strategy
fica para a proxima aula.

## 7. Observacoes tecnicas

Os exemplos reproduzem as formulas
da aula, usando float.

Para sistemas financeiros de producao,
a precisao decimal e arredondamentos
exigem tratamento especifico.

A transcricao nao apresenta validacao
de valores negativos nem piso de preco.

Esses comportamentos nao foram
modificados nesta implementacao.

## 8. Arquivos da aula

src/aula24_regras_negocio_if_else.py
aulas/aula24_regras_negocio_if_else.py
tests/test_aula24_regras_negocio_if_else.py
anotacoes/aula24_regras_negocio_if_else.md
resultados/aula24_regras_negocio_if_else.json

## 9. Testes

16 testes novos.
Meta acumulada: 384 testes.
