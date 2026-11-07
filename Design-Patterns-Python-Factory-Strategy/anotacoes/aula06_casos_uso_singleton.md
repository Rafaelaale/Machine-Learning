# Aula 06 - Casos de uso do Singleton

## None

None representa ausencia de valor.

a = None
b = None

a is b retorna True.

## True e False

True e False possuem identidades
unicas dentro do interpretador Python.

## sys.stdin, sys.stdout e sys.stderr

Representam os fluxos atuais de
entrada, saida e erro padrao.

Essas referencias podem ser substituidas
durante redirecionamentos ou testes.

## logging.getLogger

Chamadas com o mesmo nome reutilizam
o logger registrado.

log1 = logging.getLogger("meu_logger")
log2 = logging.getLogger("meu_logger")

log1 is log2 retorna True.

## SQLAlchemy scoped_session

Uma scoped_session reutiliza a mesma
sessao dentro do escopo atual.

Por padrao, o escopo e local a thread.

Session = scoped_session(
    sessionmaker(bind=engine)
)

session1 = Session()
session2 = Session()

session1 is session2 retorna True.

Em outra thread, a sessao normalmente
e diferente.

Session.remove() descarta a sessao
associada ao escopo atual.

## Conclusao

scoped_session nao representa uma unica
sessao global para todas as threads.

Singleton pode ser util, mas o uso
excessivo de estado global pode
dificultar testes e manutencao.

## Ferramentas utilizadas

Python
sys
logging
threading
SQLAlchemy
SQLite em memoria
