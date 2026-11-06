from pathlib import Path
import sys
import json


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula04_sistemas_ml import (
    carregar_dados,
    previsao_tradicional,
    treinar_modelo,
    prever_ml,
    avaliar,
    detectar_mudanca_esquema,
    detectar_mudanca_media,
)


DADOS = BASE / "dados" / "aula04_churn_rotulado.csv"
RESULTADOS = BASE / "resultados"


def titulo(mensagem):
    print("\n" + "=" * 65)
    print(mensagem)
    print("=" * 65)


def main():
    titulo("ALURA - AULA 04")
    print("SISTEMAS DE ML VS SOFTWARE TRADICIONAL")

    registros = carregar_dados(DADOS)

    treino = [
        item for item in registros
        if item["conjunto"] == "treino"
    ]

    teste = [
        item for item in registros
        if item["conjunto"] == "teste"
    ]

    titulo("1. DADOS E PARTICOES")

    print("Total de registros:", len(registros))
    print("Treinamento:", len(treino))
    print("Teste:", len(teste))
    print("Atributos: dias_sem_compra e reclamacoes_90d")

    titulo("2. SOFTWARE TRADICIONAL")

    avaliacao_regras = avaliar(
        teste, previsao_tradicional
    )

    print("Metodo: regras fixas")
    print("Treinamento necessario: NAO")
    print("Acuracia didatica:", avaliacao_regras["acuracia"])

    titulo("3. SISTEMA DE MACHINE LEARNING")

    modelo = treinar_modelo(treino)

    avaliacao_ml = avaliar(
        teste,
        lambda item: prever_ml(modelo, item),
    )

    print("Algoritmo:", modelo["algoritmo"])
    print("Treinamento necessario: SIM")
    print("Centroides aprendidos:", modelo["centroides"])
    print("Acuracia didatica:", avaliacao_ml["acuracia"])

    titulo("4. VALIDANDO ALTERACAO NO ESQUEMA")

    registro_incompleto = {
        "dias_sem_compra": 30
    }

    verificacao_esquema = detectar_mudanca_esquema(
        registro_incompleto
    )

    print("Esquema valido:", verificacao_esquema["esquema_valido"])
    print(
        "Colunas ausentes:",
        verificacao_esquema["colunas_ausentes"]
    )

    try:
        prever_ml(modelo, registro_incompleto)
    except ValueError as erro:
        print("Falha controlada:", erro)
    else:
        raise AssertionError(
            "O sistema deveria rejeitar o registro incompleto"
        )

    titulo("5. MONITORAMENTO DE MUDANCA NOS DADOS")

    novos_dados = [
        {"dias_sem_compra": 120, "reclamacoes_90d": 0},
        {"dias_sem_compra": 135, "reclamacoes_90d": 1},
        {"dias_sem_compra": 150, "reclamacoes_90d": 2},
    ]

    monitoramento = detectar_mudanca_media(
        treino, novos_dados
    )

    for chave, valor in monitoramento.items():
        print(chave, ":", valor)

    titulo("6. SALVANDO RELATORIO")

    RESULTADOS.mkdir(parents=True, exist_ok=True)

    relatorio = {
        "aula": 4,
        "tema": "ML vs Software tradicional",
        "tipo": "laboratorio didatico",
        "treinamento": len(treino),
        "teste": len(teste),
        "software_tradicional": avaliacao_regras,
        "sistema_ml": {
            "modelo": modelo,
            "avaliacao": avaliacao_ml,
        },
        "verificacao_esquema": verificacao_esquema,
        "monitoramento": monitoramento,
        "etapas_sistema_ml": [
            "definicao_do_problema",
            "carregamento_dos_dados",
            "validacao_do_esquema",
            "separacao_treino_teste",
            "treinamento",
            "previsao",
            "avaliacao",
            "monitoramento_simulado",
        ],
        "limitacoes": [
            "Dados e rotulos de churn ficticios.",
            "Algoritmo simplificado de centroides.",
            "Acuracia deste exemplo nao e evidência de "
            "desempenho em dados reais.",
            "O alerta por media nao comprova drift estatistico.",
            "Nenhum sistema foi colocado em producao.",
        ],
    }

    destino = RESULTADOS / "aula04_ml_vs_tradicional.json"

    destino.write_text(
        json.dumps(
            relatorio, ensure_ascii=False, indent=4
        ),
        encoding="utf-8",
    )

    print("Relatorio:", destino.name)

    titulo("7. VERIFICACOES INTERNAS")

    assert len(registros) == 12
    assert len(treino) == 8
    assert len(teste) == 4
    assert avaliacao_regras["amostras"] == 4
    assert avaliacao_ml["amostras"] == 4
    assert not verificacao_esquema["esquema_valido"]
    assert monitoramento["alerta"]
    assert destino.is_file()

    salvo = json.loads(
        destino.read_text(encoding="utf-8")
    )

    assert salvo["aula"] == 4

    titulo("RESULTADO FINAL")

    print("Registros ficticios: 12")
    print("Amostras de treino: 8")
    print("Amostras de teste: 4")
    print("Sistemas comparados: 2")
    print("Modelo de ML treinado: SIM")
    print("Falha de esquema identificada: SIM")
    print("Alerta de mudanca dos dados: SIM")
    print("Relatorios JSON: 1")
    print("Verificacoes internas: APROVADAS")
    print("Aula 04 executada com sucesso.")


if __name__ == "__main__":
    main()