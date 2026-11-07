# Aula 05 - Singleton Thread Safe

## Problema

Na Aula 04, o Singleton foi criado com __new__.

A verificacao:

if cls._instancia is None:

nao protege contra acesso concorrente.

Duas threads podem verificar None antes de
qualquer uma publicar sua instancia.

O resultado pode ser a criacao de dois objetos.

## Threads

O modulo threading permite concorrencia.

Uma thread executa uma funcao usando
threading.Thread(target=funcao).

O metodo start() inicia a thread.
O metodo join() aguarda seu encerramento.

## Barrier

threading.Barrier(100) permite sincronizar
o inicio de 100 threads.

A barreira deve ser compartilhada,
nao recriada dentro de cada trabalhador.

## Experimento real

Criamos 100 threads que tentam instanciar
o Singleton da Aula 04.

Registramos os IDs e mantemos referencias
aos objetos para evitar confusoes por
reutilizacao de identificadores.

Nao exigimos que aparecam duas instancias,
pois o agendamento das threads varia.

## Experimento controlado

A classe didatica
SingletonComCorridaControlada
faz duas threads aguardarem no ponto
em que ambas ja verificaram None.

Em seguida, as duas criam objetos.

Esse experimento torna o problema
reproduzivel sem alterar a Aula 04.

## Cuidado com os testes

Um teste concorrente que passou uma vez
nao demonstra ausencia de condicoes
de corrida.

A ausencia de uma falha observada
nao significa que ela seja impossivel.

## Limites da aula

Nao implementamos a solucao thread-safe.

Nao adicionamos Lock ao Singleton original.

A implementacao segura sera estudada
na proxima aula apresentada pela Alura.
