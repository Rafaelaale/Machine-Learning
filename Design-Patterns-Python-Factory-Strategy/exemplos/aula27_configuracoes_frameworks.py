"""Exemplos de configuracao citados na Aula 27.

Nao inicializa Django nem Celery.
"""

# settings.py de um projeto Django:
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "django.contrib.auth.backends.RemoteUserBackend",
]

# Exemplo ilustrativo: Celery pode configurar JSON:
CELERY_TASK_SERIALIZER = "json"

# A aula tambem demonstra a alternativa:
# CELERY_TASK_SERIALIZER = "pickle"
#
# Nao habilitamos pickle: a desserializacao de
# dados nao confiaveis pode executar codigo.
# Em sistemas reais, prefira JSON quando possivel.
