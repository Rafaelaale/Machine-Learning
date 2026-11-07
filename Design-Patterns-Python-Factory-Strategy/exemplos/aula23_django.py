"""Exemplo didatico da transcricao - Django.

Em uma aplicacao real, o sender de post_save
deve ser um modelo Django configurado.

Este arquivo documenta o registro do sinal.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver


class User:
    pass


@receiver(post_save, sender=User)
def criar_perfil(sender, instance, created, **kwargs):
    pass
