"""Configuracao do pacote de pre-processamento de churn."""

from setuptools import find_packages, setup


setup(
    name="pre-processamento-churn-alura",
    version="0.1.0",
    description="Pre-processamento de clientes para estudo de churn",
    packages=find_packages(),
    install_requires=["pandas>=2.0"],
    python_requires=">=3.10",
)
