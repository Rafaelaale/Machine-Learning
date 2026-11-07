"""Executavel da Aula 06."""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.aula06_diferenciacao import executar_aula


if __name__ == "__main__":
    executar_aula()
