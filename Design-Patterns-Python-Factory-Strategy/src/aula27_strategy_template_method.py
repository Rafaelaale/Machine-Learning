"""Aula 27 - Casos de uso de Strategy e Template Method.

Conteudos da transcricao:
- list.sort(key=...) com funcoes e lambda;
- __lt__ e __eq__ em Pessoa;
- backends de autenticacao do Django;
- serializers do Celery;
- ciclo de validacao de formularios;
- unittest.setUp.

O formulario didatico abaixo ilustra o mecanismo
de hooks sem depender da instalacao do Django.
O exemplo real de Django esta na pasta exemplos.
"""


# 1. STRATEGY: ORDENACAO

lista_de_frutas = [
    "maçã",
    "banana",
    "abacaxi",
    "laranja",
    "uva",
]


def por_tamanho(fruta):
    return len(fruta)


def ordem_alfabetica(fruta):
    return fruta


def demonstrar_ordenacao():
    frutas = lista_de_frutas.copy()

    frutas.sort(key=por_tamanho)
    por_comprimento = frutas.copy()

    frutas.sort(key=ordem_alfabetica)
    alfabetica = frutas.copy()

    frutas.sort(key=lambda fruta: len(fruta))
    por_lambda = frutas.copy()

    return {
        "original": lista_de_frutas.copy(),
        "por_tamanho": por_comprimento,
        "alfabetica": alfabetica,
        "por_lambda": por_lambda,
    }


# 2. DUNDER METHODS

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


def demonstrar_comparacoes():
    p1 = Pessoa("Alice", 30)
    p2 = Pessoa("Bob", 25)
    p3 = Pessoa("Alice", 30)

    return {
        "alice_menor_que_bob": p1 < p2,
        "bob_menor_que_alice": p2 < p1,
        "alice_igual_outra_alice": p1 == p3,
        "alice_igual_bob": p1 == p2,
    }


# 3. EXEMPLO DE CONFIGURACAO DO DJANGO

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "django.contrib.auth.backends.RemoteUserBackend",
]


# 4. EXEMPLOS DE CONFIGURACAO DO CELERY
# Estas strings ilustram opcoes de configuracao.
# Nenhum serializer e ativado em um worker.

SERIALIZADORES_CELERY = {
    "json": "json",
    "pickle": "pickle",
}


def selecionar_serializador(nome):
    return SERIALIZADORES_CELERY[nome]


# 5. TEMPLATE METHOD: SIMULACAO DIDATICA DE FORMS

class FormularioContatoDidatico:
    """Simulacao simplificada, nao um formulario Django."""

    def __init__(self, dados):
        self.dados = dados
        self.cleaned_data = {}
        self.errors = {}

    def clean_email(self):
        email = self.cleaned_data.get("email", "")

        if not email.endswith("@example.com"):
            raise ValueError(
                "Email deve ser do domínio example.com"
            )

        return email

    def full_clean(self):
        """Etapas fixas com um hook personalizavel."""

        self.cleaned_data = {}
        self.errors = {}

        nome = self.dados.get("nome", "")
        email = self.dados.get("email", "")
        mensagem = self.dados.get("mensagem", "")

        if not nome or len(nome) > 100:
            self.errors["nome"] = "Nome inválido"
        else:
            self.cleaned_data["nome"] = nome

        if not email:
            self.errors["email"] = "Email obrigatório"
        elif "@" not in email:
            self.errors["email"] = "Email inválido"
        else:
            self.cleaned_data["email"] = email

            try:
                self.cleaned_data["email"] = (
                    self.clean_email()
                )
            except ValueError as erro:
                self.errors["email"] = str(erro)
                self.cleaned_data.pop("email", None)

        if not mensagem:
            self.errors["mensagem"] = "Mensagem obrigatória"
        else:
            self.cleaned_data["mensagem"] = mensagem

    def is_valid(self):
        self.full_clean()
        return not self.errors


def demonstrar_formularios():
    valido = FormularioContatoDidatico({
        "nome": "Maria",
        "email": "maria@example.com",
        "mensagem": "Olá!",
    })

    invalido = FormularioContatoDidatico({
        "nome": "Maria",
        "email": "maria@outro.com",
        "mensagem": "Olá!",
    })

    return {
        "valido": valido.is_valid(),
        "dados_validos": valido.cleaned_data.copy(),
        "invalido": invalido.is_valid(),
        "erros_invalidos": invalido.errors.copy(),
    }


def analisar_aula27():
    return {
        "aula": 27,
        "titulo": "Casos de uso do Strategy e Template Method",
        "strategy": [
            "sort com key",
            "funcoes",
            "lambda",
            "comparacao de objetos",
            "backends Django",
            "serializadores Celery",
        ],
        "template_method": [
            "Django full_clean e clean_email",
            "unittest setUp",
        ],
        "django_exemplo_real_separado": True,
        "formulario_local_e_simulacao": True,
        "unittest_exemplo_separado": True,
        "pickle_habilitado": False,
    }
