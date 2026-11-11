"""Demonstracao sintetica da Aula 5.1, sem Spark, rede ou pacotes externos."""

from random import Random
from statistics import mean

randomico = Random(42)
quantidade = 1200


def criar_amostra(media_renda, novo_conceito):
    linhas = []
    for _ in range(quantidade):
        renda = max(0.0, randomico.gauss(media_renda, 0.9))
        # Modelo antigo: mesma regra de predicao nos dois periodos.
        predito = int(renda >= 3.5)
        # Mudanca proposital na relacao renda x compra (somente simulacao).
        prob = (0.50 - 0.08 * (renda - 3.0)) if novo_conceito else (0.20 + 0.16 * (renda - 3.0))
        prob = min(0.95, max(0.05, prob))
        compra = int(randomico.random() < prob)
        linhas.append((renda, predito, compra))
    return linhas


def ks_estatistica(a, b):
    """D = distancia maxima entre distribuicoes acumuladas empiricas."""
    a, b = sorted(a), sorted(b)
    i = j = 0
    maior = 0.0
    while i < len(a) or j < len(b):
        x = min(a[i] if i < len(a) else float("inf"),
                b[j] if j < len(b) else float("inf"))
        while i < len(a) and a[i] <= x:
            i += 1
        while j < len(b) and b[j] <= x:
            j += 1
        maior = max(maior, abs(i / len(a) - j / len(b)))
    return maior


referencia = criar_amostra(3.0, novo_conceito=False)
producao = criar_amostra(4.0, novo_conceito=True)

ks = ks_estatistica([r[0] for r in referencia], [r[0] for r in producao])
taxa_pred_ref = mean(r[1] for r in referencia)
taxa_pred_prod = mean(r[1] for r in producao)

# Compara a taxa real dentro de um MESMO intervalo de renda.
# Isto sugere uma mudanca condicional, nao constitui prova por si so.
faixa_ref = [r[2] for r in referencia if 2.8 <= r[0] <= 3.8]
faixa_prod = [r[2] for r in producao if 2.8 <= r[0] <= 3.8]

assert len(referencia) == len(producao) == quantidade
assert faixa_ref and faixa_prod
assert 0 <= ks <= 1

print("===== DEMONSTRACAO LOCAL - DADOS FICTICIOS =====")
print(f"Registros por periodo: {quantidade}")
print(f"Feature drift - estatistica KS da renda: {ks:.4f}")
print(f"Prediction drift - previsoes positivas: {taxa_pred_ref:.1%} -> {taxa_pred_prod:.1%}")
print(f"Concept drift (indicio) - compras reais na MESMA faixa de renda: {mean(faixa_ref):.1%} -> {mean(faixa_prod):.1%}")
print("ATENCAO: exemplo pedagogico, nao corresponde a metricas do Databricks.")
print("Nenhum modelo treinado, nenhuma tabela escrita, nenhum job criado.")