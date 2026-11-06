from pathlib import Path
import csv
import json
import sqlite3


BASE = Path(__file__).resolve().parent.parent
DADOS = BASE / "dados"
RESULTADOS = BASE / "resultados"

DADOS.mkdir(exist_ok=True)
RESULTADOS.mkdir(exist_ok=True)

BANCO = DADOS / "aula04_especializacao.sqlite3"
DATA_REFERENCIA = "2026-11-06"


def titulo(texto):
    print("\n" + "=" * 65)
    print(texto)
    print("=" * 65)


def criar_origem(conexao):
    """SOR: conserva registros brutos, incluindo erros."""

    conexao.executescript("""
        DROP VIEW IF EXISTS spec_clientes_sp;
        DROP VIEW IF EXISTS spec_ativos_mais_6_meses;
        DROP VIEW IF EXISTS spec_clientes_ativos;
        DROP VIEW IF EXISTS sot_clientes_tratados;
        DROP TABLE IF EXISTS sor_assinantes;

        CREATE TABLE sor_assinantes (
            registro_id INTEGER PRIMARY KEY,
            cliente_id TEXT,
            nome TEXT,
            email TEXT,
            estado TEXT,
            data_inicio TEXT,
            status TEXT
        );
    """)

    registros = [
        ("C001", "Ana", "ana@exemplo.com", "SP", "2025-01-10", "ativo"),
        ("C002", "Bruno", "bruno@exemplo.com", "BA", "2026-01-15", "ativo"),
        ("C003", "Carla", "carla@exemplo.com", "SP", "2026-08-01", "ativo"),
        ("C004", "Daniel", "daniel@exemplo.com", "RJ", "2025-02-10", "inativo"),
        ("C005", "Eva", "eva@exemplo.com", "SP", "2026-03-01", "ativo"),
        ("C006", "Fabio", "fabio@exemplo.com", "SP", "2025-04-15", "inativo"),
        ("C007", "Gabi", "gabi@exemplo.com", "SP", "2026-05-06", "ativo"),

        # Registro duplicado
        ("C002", "Bruno", "bruno@exemplo.com", "BA", "2026-01-15", "ativo"),

        # Registro com email ausente
        ("C008", "Helena", None, "SP", "2026-01-01", "ativo"),

        # Registro com nome ausente
        ("C009", None, "igor@exemplo.com", "SP", "2026-01-01", "ativo"),
    ]

    conexao.executemany(
        """
        INSERT INTO sor_assinantes
        (cliente_id, nome, email, estado, data_inicio, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        registros,
    )

    conexao.commit()


def criar_camadas(conexao):
    """SOT para qualidade; SPEC para regras de negocio."""

    conexao.executescript("""
        CREATE VIEW sot_clientes_tratados AS
        WITH registros_validos AS (
            SELECT
                cliente_id,
                TRIM(nome) AS nome,
                LOWER(TRIM(email)) AS email,
                UPPER(TRIM(estado)) AS estado,
                data_inicio,
                status,
                ROW_NUMBER() OVER (
                    PARTITION BY cliente_id
                    ORDER BY registro_id
                ) AS numero_registro
            FROM sor_assinantes
            WHERE cliente_id IS NOT NULL
              AND TRIM(cliente_id) <> ''
              AND nome IS NOT NULL
              AND TRIM(nome) <> ''
              AND email IS NOT NULL
              AND TRIM(email) LIKE '%@%.%'
              AND estado IS NOT NULL
              AND TRIM(estado) <> ''
              AND date(data_inicio) IS NOT NULL
              AND status IN ('ativo', 'inativo')
        )
        SELECT
            cliente_id,
            nome,
            email,
            estado,
            data_inicio,
            status
        FROM registros_validos
        WHERE numero_registro = 1;

        CREATE VIEW spec_clientes_ativos AS
        SELECT *
        FROM sot_clientes_tratados
        WHERE status = 'ativo';

        CREATE VIEW spec_ativos_mais_6_meses AS
        SELECT *
        FROM spec_clientes_ativos
        WHERE date(data_inicio) <
              date('2026-11-06', '-6 months');

        CREATE VIEW spec_clientes_sp AS
        SELECT *
        FROM spec_ativos_mais_6_meses
        WHERE estado = 'SP';
    """)

    conexao.commit()


def consultar(conexao, tabela):
    permitidos = {
        "sor_assinantes",
        "sot_clientes_tratados",
        "spec_clientes_ativos",
        "spec_ativos_mais_6_meses",
        "spec_clientes_sp",
    }

    if tabela not in permitidos:
        raise ValueError("Tabela nao autorizada")

    cursor = conexao.execute(
        f"SELECT * FROM {tabela} ORDER BY cliente_id, registro_id"
        if tabela == "sor_assinantes"
        else f"SELECT * FROM {tabela} ORDER BY cliente_id"
    )

    return [dict(linha) for linha in cursor.fetchall()]


def salvar_csv(caminho, registros, colunas):
    with caminho.open(
        "w", newline="", encoding="utf-8-sig"
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=colunas,
        )
        escritor.writeheader()
        escritor.writerows(registros)


def main():
    titulo("ALURA - AULA 04")
    print("NIVEIS DE ESPECIALIZACAO DA INFORMACAO")

    titulo("1. SOURCE OF RECORDS - SOR")

    with sqlite3.connect(BANCO) as conexao:
        conexao.row_factory = sqlite3.Row

        criar_origem(conexao)
        criar_camadas(conexao)

        sor = consultar(conexao, "sor_assinantes")
        sot = consultar(conexao, "sot_clientes_tratados")
        ativos = consultar(conexao, "spec_clientes_ativos")
        seis_meses = consultar(
            conexao, "spec_ativos_mais_6_meses"
        )
        sp = consultar(conexao, "spec_clientes_sp")

    print("Registros originais:", len(sor))
    print("Inclui duplicidades e registros incompletos.")

    titulo("2. SOURCE OF TRUTH - SOT")

    print("Registros apos regras de qualidade:", len(sot))
    print("Registros descartados:", len(sor) - len(sot))
    print("Regras:")
    print("- Remover duplicidades por cliente_id")
    print("- Exigir nome e identificador")
    print("- Verificar presenca e formato simples do email")
    print("- Exigir estado, data e status validos")

    titulo("3. SPECIALIZATION - SPEC")

    print("Clientes ativos:", len(ativos))
    print("Ativos ha mais de 6 meses:", len(seis_meses))
    print("Ativos ha mais de 6 meses em SP:", len(sp))
    print("Data de referencia:", DATA_REFERENCIA)

    titulo("4. RESULTADO DA ESPECIALIZACAO")

    for cliente in sp:
        print(cliente)

    titulo("5. DOCUMENTANDO LINHAGEM")

    linhagem = {
        "aula": 4,
        "tema": "Niveis de especializacao",
        "data_referencia": DATA_REFERENCIA,
        "camadas": [
            {
                "nivel": "SOR",
                "ativo": "sor_assinantes",
                "origem": None,
                "transformacao": "Ingestao dos registros brutos",
            },
            {
                "nivel": "SOT",
                "ativo": "sot_clientes_tratados",
                "origem": "sor_assinantes",
                "transformacao": (
                    "Validacao de campos e remocao "
                    "de registros invalidos ou duplicados"
                ),
            },
            {
                "nivel": "SPEC",
                "ativo": "spec_clientes_ativos",
                "origem": "sot_clientes_tratados",
                "transformacao": "Filtrar status ativo",
            },
            {
                "nivel": "SPEC",
                "ativo": "spec_ativos_mais_6_meses",
                "origem": "spec_clientes_ativos",
                "transformacao": (
                    "Filtrar inicio anterior a seis "
                    "meses da data de referencia"
                ),
            },
            {
                "nivel": "SPEC",
                "ativo": "spec_clientes_sp",
                "origem": "spec_ativos_mais_6_meses",
                "transformacao": "Filtrar estado SP",
            },
        ],
        "observacao": (
            "Dados ficticios. Validacao de email simplificada. "
            "SOT preserva clientes validos de ambos os status; "
            "SPEC representa filtros de negocio."
        ),
    }

    arquivo_json = (
        RESULTADOS / "aula04_linhagem_especializacao.json"
    )

    arquivo_json.write_text(
        json.dumps(linhagem, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )

    # CSVs de cada estagio
    bases = {
        "sor": sor,
        "sot": sot,
        "spec_ativos": ativos,
        "spec_mais_6_meses": seis_meses,
        "spec_sp": sp,
    }

    arquivos = []

    for nome, registros in bases.items():
        caminho = RESULTADOS / f"aula04_{nome}.csv"
        colunas = list(registros[0].keys())

        salvar_csv(caminho, registros, colunas)
        arquivos.append(caminho)

        print(f"Gerado: {caminho.name}")

    print("Gerado:", arquivo_json.name)

    titulo("6. TESTES AUTOMATIZADOS")

    assert len(sor) == 10
    assert len(sot) == 7
    assert len(ativos) == 5
    assert len(seis_meses) == 3
    assert len(sp) == 2

    assert {item["cliente_id"] for item in sp} == {
        "C001", "C005"
    }

    assert {item["cliente_id"] for item in seis_meses} == {
        "C001", "C002", "C005"
    }

    assert len({
        item["cliente_id"] for item in sot
    }) == len(sot)

    assert all(item["estado"] == "SP" for item in sp)
    assert all(item["status"] == "ativo" for item in sp)

    assert len(linhagem["camadas"]) == 5
    assert len(arquivos) == 5
    assert all(item.exists() for item in arquivos)
    assert arquivo_json.exists()
    assert BANCO.exists()

    # Verificar ligacoes entre ativos
    for anterior, atual in zip(
        linhagem["camadas"],
        linhagem["camadas"][1:],
    ):
        assert atual["origem"] == anterior["ativo"]

    titulo("RESULTADO FINAL")

    print("Niveis conceituais: 3 (SOR, SOT, SPEC)")
    print("Base original SOR:", len(sor))
    print("Base tratada SOT:", len(sot))
    print("Clientes ativos SPEC:", len(ativos))
    print("Ativos ha mais de 6 meses:", len(seis_meses))
    print("Ativos ha mais de 6 meses em SP:", len(sp))
    print("Arquivos CSV: 5")
    print("Arquivo JSON: 1")
    print("Banco SQLite: 1")
    print("Todos os testes passaram.")
    print("Aula 04 executada com sucesso.")


if __name__ == "__main__":
    main()