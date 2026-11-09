"""Gera CSV fictício de vendas da Vende+ para uso no projeto."""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


PRODUTOS = {
    "Eletrônicos": [
        ("Fone Bluetooth", 199.90, 299.90),
        ("Carregador USB-C", 49.90, 89.90),
        ("Cabo HDMI 2m", 29.90, 59.90),
        ("Mouse sem fio", 89.90, 159.90),
        ("Teclado mecânico", 299.90, 599.90),
    ],
    "Casa e Decoração": [
        ("Vela aromática", 24.90, 49.90),
        ("Almofada decorativa", 59.90, 119.90),
        ("Quadro decorativo", 89.90, 249.90),
        ("Tapete sala", 199.90, 599.90),
        ("Luminária mesa", 79.90, 189.90),
    ],
    "Vestuário": [
        ("Camiseta básica", 39.90, 79.90),
        ("Calça jeans", 119.90, 249.90),
        ("Tênis casual", 199.90, 399.90),
        ("Jaqueta corta-vento", 159.90, 299.90),
        ("Meia esportiva", 19.90, 39.90),
    ],
    "Esporte e Lazer": [
        ("Bola de futebol", 79.90, 149.90),
        ("Garrafa térmica 1L", 49.90, 99.90),
        ("Corda de pular", 29.90, 59.90),
        ("Bicicleta ergométrica", 899.90, 1599.90),
        ("Halter 5kg par", 119.90, 199.90),
    ],
    "Beleza": [
        ("Hidratante facial", 49.90, 99.90),
        ("Shampoo 400ml", 29.90, 59.90),
        ("Perfume importado", 199.90, 499.90),
        ("Batom matte", 39.90, 69.90),
        ("Protetor solar FPS50", 69.90, 129.90),
    ],
}


def gerar_csv_vendas(data: datetime, caminho_destino: Path, n_linhas: int = 80) -> Path:
    """Gera um CSV de vendas fictícias para a data informada."""
    caminho_destino.mkdir(parents=True, exist_ok=True)
    nome_arquivo = caminho_destino / f"vendas_{data.strftime('%Y-%m-%d')}.csv"

    random.seed(int(data.strftime("%Y%m%d")))

    with open(nome_arquivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "data", "pedido_id", "produto", "categoria",
            "quantidade", "valor_unitario"
        ])

        for i in range(1, n_linhas + 1):
            categoria = random.choice(list(PRODUTOS.keys()))
            produto, preco_min, preco_max = random.choice(PRODUTOS[categoria])
            quantidade = random.choices([1, 2, 3, 4, 5], weights=[50, 25, 15, 7, 3])[0]
            valor_unitario = round(random.uniform(preco_min, preco_max), 2)
            pedido_id = f"PED-{data.strftime('%Y%m%d')}-{i:04d}"

            writer.writerow([
                data.strftime("%Y-%m-%d"),
                pedido_id,
                produto,
                categoria,
                quantidade,
                valor_unitario,
            ])

    return nome_arquivo


if __name__ == "__main__":
    pasta = Path(__file__).parent.parent / "data"
    hoje = datetime.now().date()

    for i in range(3):
        data = hoje - timedelta(days=i)
        arquivo = gerar_csv_vendas(datetime.combine(data, datetime.min.time()), pasta)
        print(f"Gerado: {arquivo}")
