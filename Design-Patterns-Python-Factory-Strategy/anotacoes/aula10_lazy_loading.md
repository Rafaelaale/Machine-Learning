# Aula 10 - Lazy Loading

## Objetivo

Aprender a diferenca entre carregamento
imediato e inicializacao tardia.

## 1. Carregamento imediato

Na versao inicial, o modulo possui:

```python
config = Config()
```

Quando o modulo e importado pela primeira
vez, o Python executa seu codigo de nivel
superior e cria esse objeto.

O metodo __init__ carrega o JSON
imediatamente.

Isso acontece mesmo que os dados nunca
sejam utilizados pelo resto do programa.

## 2. Lazy Loading

Na versao tardia, __init__ apenas registra
o caminho e inicializa _data como None.

```python
class Config:
    def __init__(self, arquivo):
        self.arquivo = arquivo
        self._data = None

    @property
    def data(self):
        if self._data is None:
            with open(self.arquivo) as f:
                self._data = json.load(f)

        return self._data
```

O JSON e lido somente no primeiro
acesso a config.data.

## 3. Decorador property

@property permite acessar um metodo
usando sintaxe de atributo.

Exemplo:

config.data

Nao e necessario chamar config.data().

## 4. Cache

Apos a primeira leitura, _data
armazena o dicionario carregado.

Os proximos acessos reutilizam o
mesmo objeto.

O cache deste exemplo pertence
a cada instancia de Config.

## 5. SQLAlchemy

As classes Author e Book possuem
um relacionamento um-para-muitos.

Um autor pode possuir diversos livros.

```python
books = relationship(
    "Book",
    back_populates="author",
    lazy="select"
)
```

## 6. Consulta tardia

Primeiro consultamos Author.

Nesse momento, books ainda nao
foi carregado.

Depois acessamos:

```python
autor.books
```

O SQLAlchemy executa uma consulta
adicional para buscar os livros.

O resultado passa a estar disponivel
na colecao associada ao autor.

## 7. Teste verificavel

O laboratorio registra consultas SELECT
executadas pelo SQLAlchemy.

Antes de acessar books:
o relacionamento esta descarregado.

Depois de acessar books:
ocorre uma consulta SQL adicional.

Segundo acesso:
nenhuma nova consulta e necessaria.

## 8. Limites e cuidados

Lazy Loading pode economizar recursos
quando dados talvez nao sejam usados.

Mas acessos repetidos a relacionamentos
de muitos objetos podem causar o
problema N+1 de consultas SQL.

O relacionamento lazy exige uma sessao
adequada para carregar dados ainda
nao buscados.

A implementacao didatica do JSON
nao inclui sincronizacao para threads.

## 9. Arquivos desta aula

src/aula10_imediato.py

src/aula10_tardio.py

src/aula10_sqlalchemy_lazy.py

dados_aula10/config.json

aulas/aula10_lazy_loading.py

tests/test_aula10_lazy_loading.py

resultados/aula10_lazy_loading.json

## 10. Proxima etapa

Continuar seguindo a proxima
transcricao da Alura.
