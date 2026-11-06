# Regras de negocio e limitacoes

## Regra demonstrativa da Aula 09

Um cliente e marcado como risco didatico quando:

- days_since_last_purchase >= 60
- num_orders <= 2

As duas condicoes devem ocorrer.

Resultado observado na aula:
894 clientes de 10.000 classificados em risco (8,94%).

Essa regra nao representa uma previsao de ML.

## Modelo estatistico da Aula 07

Algoritmo: LogisticRegression.

Atributos:
- total_spent
- num_orders
- days_since_last_purchase

Divisao utilizada:
75% treinamento e 25% teste.

Metricas observadas:
- Accuracy: 0.698
- Precision da classe 1: 0.0
- Recall da classe 1: 0.0
- F1 da classe 1: 0.0

Conclusao:
O modelo nao identificou corretamente nenhum caso
positivo de churn no conjunto de teste.

## Comunicacoes com clientes

A aula menciona exemplos de acoes por tempo de
inatividade, como SMS e e-mail.

Esses exemplos nao foram implementados como
regras operacionais neste projeto.

Nenhuma notificacao real e enviada.

## Pendencias

- Definir metricas minimas aceitaveis.
- Avaliar falsos negativos e falsos positivos.
- Investigar desbalanceamento e qualidade do alvo.
- Estabelecer uma politica de decisao com o negocio.
- Validar privacidade e autorizacao de uso dos dados.
