"""Exemplo da transcricao - Click.

Requer Click somente quando este arquivo for executado.
"""

import click


@click.group()
def cli():
    pass


@cli.command()
def build():
    print("Build iniciado")


if __name__ == "__main__":
    cli()
