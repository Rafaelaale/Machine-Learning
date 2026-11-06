# Aula 03 - Principios 4 ao 7 da Engenharia de Software

## Referencia

Os principios apresentados pela Alura sao
atribuidos a David Hooker.

O curso utiliza como referencia a obra
Engenharia de Software: Uma Abordagem Profissional,
de Roger Pressman e Bruce Maxim.

## Principio 4 - O que um produz, outros consomem

O codigo deve ser compreensivel e utilizavel
por outras pessoas.

Boas praticas:

- Documentar funcoes e processos.
- Usar nomes claros.
- Organizar arquivos.
- Facilitar manutencao.
- Considerar pessoas que utilizarao o sistema.

No projeto de churn, usamos funcoes documentadas
com entradas e resultados bem definidos.

## Principio 5 - Esteja aberto para o futuro

Planejar o software para lidar com mudancas.

Perguntas importantes:

- Novos produtos podem ser adicionados?
- Os dados podem mudar?
- As funcoes sao generalizaveis?
- Podemos substituir componentes?
- As bibliotecas possuem manutencao?

No laboratorio, novos produtos podem ser
incluidos por configuracao de catalogo.

## Principio 6 - Planeje com antecedencia

Pensar em reutilizacao e manutencao futura.

Beneficios:

- Reducao de retrabalho.
- Melhor aproveitamento do codigo.
- Reducao de custo.
- Maior consistencia.
- Menor tempo para novas entregas.

A Alura destaca o equilibrio entre
custo, qualidade e tempo.

O laboratorio reutiliza a validacao da Aula 02.

## Principio 7 - Pense antes de agir

Antes de mudar uma regra ou modelo, formular
e testar hipoteses.

Exemplo:

O que acontece quando alteramos o limite
de inatividade utilizado na classificacao?

No laboratorio, comparamos tres limites
de dias sem compra: 30, 60 e 90.

Nenhuma mudanca e aplicada automaticamente.

## Contexto: sistema de churn

O curso utiliza um sistema de previsao
de abandono de clientes em um e-commerce.

Nosso projeto usa regras ficticias para
demonstrar os principios de engenharia.

Nao foi treinado um modelo de Machine Learning.

## Revisao dos sete principios

1. Razao de existir.
2. KISS - manter simples.
3. Manter a visao.
4. O que um produz, outros consomem.
5. Esteja aberto para o futuro.
6. Planeje com antecedencia.
7. Pense antes de agir.

## Arquitetura do laboratorio

- src: funcoes reutilizaveis.
- dados: clientes ficticios.
- aulas: programa principal.
- tests: testes automatizados.
- resultados: relatorio JSON.
- anotacoes: conteudo da aula.

## Principal aprendizado

Sistemas de dados devem ser compreensiveis,
adaptaveis, reutilizaveis e planejados
antes de serem modificados.

## Proxima aula

Continuar o curso na mesma pasta do VS Code.

Nao usar Git ou GitHub durante a trilha.