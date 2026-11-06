# Aula 09 - POO e Programacao Funcional

## Programacao Orientada a Objetos

Organiza entidades em classes com atributos e metodos.

Conceitos:
- Encapsulamento
- Heranca
- Polimorfismo
- Abstracao

No laboratorio:
ClienteChurn representa a entidade cliente.

O objeto e imutavel por meio de dataclass(frozen=True).

## Programacao Funcional

Prioriza funcoes com entradas e saidas claras.

Conceitos:
- Funcoes puras
- Imutabilidade
- Composicao
- Map
- Filter
- Reduce

No laboratorio:
- calcular_dias_inativos
- classificar_risco
- criar_alerta
- preparar_base
- adicionar_risco
- resumir_riscos

## Combinacao dos paradigmas

Os metodos de ClienteChurn reutilizam funcoes.

Isso evita duplicacao de logica e melhora testes.

## Regras do laboratorio

Risco didatico:
- 60 dias ou mais de inatividade
- 2 compras ou menos

Essa regra nao equivale a um modelo de ML.

## Cuidados

Nao modificar o DataFrame original.

Nao misturar treinamento de modelos com
a responsabilidade de representar um cliente.

Nao enviar notificacoes reais no laboratorio.

## Principal aprendizado

POO e PF podem trabalhar juntas para criar
sistemas reutilizaveis, testaveis e organizados.
