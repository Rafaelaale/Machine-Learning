# Aula 04 - Singleton Pythonico

## Objetivo

Melhorar o Singleton da Aula 03,
substituindo get_instance() por __new__.

## Conceito

Em Python:

__new__ cria ou retorna o objeto.

__init__ inicializa o objeto retornado.

Nesta aula, usamos __new__ para controlar
a instancia compartilhada.

## Implementacao

```python
class Singleton:
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
        return cls._instancia
```

## Por que super().__new__(cls)?

Porque chamar Singleton() dentro de
Singleton.__new__ executaria o proprio
__new__ novamente, causando recursao.

super().__new__(cls) permite criar o objeto
usando o mecanismo de baixo nivel.

## Experimento

s1 = Singleton()
s2 = Singleton()
s3 = Singleton.__new__(Singleton)

Resultado:

s1 is s2 -> True
s1 is s3 -> True

## Carregamento do JSON

O arquivo config.json e lido na criacao
da primeira instancia.

As proximas chamadas reutilizam
os dados em memoria.

## Diferenca para Aula 03

Aula 03:
Config.get_instance() retorna
a instancia compartilhada.

Config() pode criar outro objeto.

Aula 04:
Singleton() ja retorna a instancia
compartilhada.

## Limites importantes

A implementacao nao e thread-safe.

Duas threads podem verificar
_instancia como None simultaneamente
e tentar criar dois objetos.

O exemplo desta aula nao implementa
locks ou sincronizacao.

A classe tambem nao garante uma
instancia unica em processos Python
diferentes.

## Observacao tecnica

A versao do laboratorio so publica
_instancia depois que o JSON foi
carregado com sucesso.

Isso evita guardar uma instancia
incompleta se ocorrer erro na leitura.

## Proxima aula

Investigar o problema de concorrencia
e implementar a protecao conforme
o conteudo da Alura.
