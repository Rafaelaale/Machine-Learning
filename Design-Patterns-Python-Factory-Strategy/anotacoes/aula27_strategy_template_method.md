# Aula 27 - Casos de uso do Strategy e Template Method

## 1. Objetivo

Reconhecer aplicacoes de Strategy
e Template Method em Python e frameworks.

## 2. Strategy em list.sort

O metodo sort recebe um parametro key.

Uma funcao passada como key determina
qual criterio sera utilizado na ordenacao.

Exemplo original da aula:

```python
lista_de_frutas = [
    "maçã", "banana", "abacaxi", "laranja", "uva"
]

def por_tamanho(fruta):
    return len(fruta)

def ordem_alfabetica(fruta):
    return fruta

lista_de_frutas.sort(key=por_tamanho)
print(lista_de_frutas)

lista_de_frutas.sort(key=ordem_alfabetica)
print(lista_de_frutas)
```

## 3. Lambda em sort

```python
lista_de_frutas.sort(
    key=lambda fruta: len(fruta)
)
```

A lambda substitui a necessidade
de uma funcao nomeada simples.

sort modifica a propria lista.

A ordenacao do Python e estavel:
elementos com a mesma chave mantem
sua ordem relativa anterior.

## 4. Metodos magicos

Os metodos com dois underscores
tambem sao conhecidos como dunder methods.

__init__ configura a instancia.

__lt__ implementa comparacao menor que.

__eq__ implementa igualdade.

```python
class Pessoa:
    def __init__(self, nome, idade):
        self.nome = nome
        self.idade = idade

    def __lt__(self, other):
        return self.idade < other.idade

    def __eq__(self, other):
        return (
            self.nome == other.nome
            and self.idade == other.idade
        )
```

Alice tem 30 anos e Bob tem 25.

Alice < Bob retorna False.

A igualdade compara nome e idade.

## 5. Strategy no Django

O Django permite definir backends
de autenticacao por configuracao.

```python
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "django.contrib.auth.backends.RemoteUserBackend",
]
```

Os backends sao intercambiaveis,
observadas suas configuracoes
e dependencias reais.

## 6. Strategy no Celery

A transcricao apresenta:

```python
CELERY_TASK_SERIALIZER = "json"
CELERY_TASK_SERIALIZER = "pickle"
```

Essas atribuicoes sucessivas sao
exemplos de configuracoes alternativas.

Se executadas juntas, a segunda
substitui a primeira.

No projeto, mantivemos os exemplos
sem habilitar um worker Celery.

Aviso: pickle e inseguro ao
desserializar conteudo nao confiavel.

## 7. Template Method em Django forms

O Django possui uma sequencia de
validacao executada por full_clean.

A validacao pode invocar hooks,
como clean_email, definidos pelo
desenvolvedor.

```python
from django import forms

class ContatoForm(forms.Form):
    nome = forms.CharField(max_length=100)
    email = forms.EmailField()
    mensagem = forms.CharField(widget=forms.Textarea)

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if not email.endswith("@example.com"):
            raise forms.ValidationError(
                "Email deve ser do domínio example.com"
            )

        return email
```

O exemplo real esta salvo em:

exemplos/aula27_django_forms.py

## 8. Ciclo is_valid e full_clean

A transcricao usa a representacao:

```python
def is_valid(self):
    self.cleaned_data = {}
    self.errors = {}
    self.full_clean()
    return not self.errors
```

Trata-se de uma simplificacao
didatica do ciclo de validacao.

O arquivo Django do projeto utiliza
a implementacao real do framework
e nao sobrescreve is_valid.

O arquivo src da Aula 27 inclui
FormularioContatoDidatico, uma
simulacao independente da biblioteca.

Ela demonstra a sequencia fixa
de validacao e o hook clean_email.

## 9. Template Method em unittest

Em unittest.TestCase, setUp e
executado antes de cada teste.

```python
import unittest

class TestMinhaFuncionalidade(unittest.TestCase):
    def setUp(self):
        self.dados_teste = self.criar_dados_teste()

    def criar_dados_teste(self):
        return {"nome": "Teste", "idade": 30}

    def test_algo(self):
        self.assertEqual(
            self.dados_teste["nome"],
            "Teste"
        )
```

Arquivo independente:

exemplos/aula27_unittest_setup.py

O proprio unittest coordena
o ciclo de execucao dos testes.

O desenvolvedor personaliza
o preparo de cada teste com setUp.

## 10. Strategy versus Template Method

Strategy:
Substitui um algoritmo completo
por outro algoritmo com interface
ou assinatura compativel.

Template Method:
Mantem a estrutura geral do
algoritmo e permite personalizar
etapas ou hooks especificos.

## 11. Relacao com aulas anteriores

Aula 24:
Problema dos if/else.

Aula 25:
Strategy com classes.

Aula 26:
Strategy com funcoes e lambdas.

Aula 27:
Casos de uso reais e apresentacao
do Template Method.

## 12. Arquivos desta aula

src/aula27_strategy_template_method.py
aulas/aula27_strategy_template_method.py
tests/test_aula27_strategy_template_method.py
anotacoes/aula27_strategy_template_method.md

exemplos/aula27_django_forms.py
exemplos/aula27_configuracoes_frameworks.py
exemplos/aula27_unittest_setup.py

resultados/aula27_strategy_template_method.json

## 13. Validacao

16 testes novos.
Meta acumulada: 432 testes.

Os arquivos anteriores permanecem
preservados, sem substituicao.
