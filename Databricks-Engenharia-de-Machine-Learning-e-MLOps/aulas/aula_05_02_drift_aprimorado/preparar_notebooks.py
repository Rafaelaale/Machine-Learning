import json
import ast
from pathlib import Path

projeto = Path(r"F:\Projetos\Databricks-Engenharia-de-Machine-Learning-e-MLOps")
origem = projeto / "material-alura" / "aula_5"
destino = projeto / "aulas" / "aula_05_02_drift_aprimorado"

nomes = [
    "aula_5_2_gerando_dados",
    "aula_5_2_job_dados_prod",
    "aula_5_2_job_monitoramento_drift"
]

relatorio = []

for nome in nomes:
    arquivo = origem / (nome + ".ipynb")
    notebook = json.loads(arquivo.read_text(encoding="utf-8-sig"))

    codigo = "\n".join(
        "".join(c["source"])
        for c in notebook["cells"]
        if c["cell_type"] == "code"
    )

    ast.parse(codigo)
    codigo = codigo.replace(
        "workspace.default.base_treinamento_modelo",
        "workspace.default.base_treinamento_modelo_aprimorado"
    ).replace(
        "workspace.default.base_tabela_prod",
        "workspace.default.base_tabela_prod_aprimorada"
    ).replace(
        "workspace.default.log_monitoramento_drift",
        "workspace.default.log_monitoramento_drift_aprimorado"
    )

    parametros = '''
dbutils.widgets.text("gravar", "false")
gravar = dbutils.widgets.get("gravar").strip().lower() == "true"
'''

    if nome != nomes[0]:
        parametros += '''
dbutils.widgets.text("data_inicio", "20260101")
dbutils.widgets.text("data_fim", "20260110")
'''

    if nome == nomes[2]:
        parametros += '''
dbutils.widgets.text(
    "features", "renda_mensal_k,tempo_medio_clique_segundos"
)
dbutils.widgets.text("target", "comprou_eletronico")
'''
        codigo = codigo.replace(
            'F.col("dia_prtc").between(p_inicio, p_fim)',
            '(F.col("dia_prtc") >= p_inicio) & (F.col("dia_prtc") < p_fim)'
        ).replace(
            '.sample(fraction=0.1, seed=42).toPandas()',
            '.sample(fraction=0.1, seed=42).limit(5000).toPandas()'
        )

        escrita = 'df_logs.write.format("delta").mode("append").saveAsTable(nome_tabela_auditoria)'
        assert escrita in codigo
        codigo = codigo.replace(
            escrita,
            'if gravar:\n    ' + escrita +
            '\nelse:\n    print("PREVIA: log nao gravado")'
        )

    elif nome == nomes[0]:
        escrita = 'df_treino.write.format("delta").mode("overwrite").saveAsTable(nome_tabela_treino)'
        assert escrita in codigo
        codigo = codigo.replace(
            escrita,
            'if gravar:\n    ' + escrita +
            '\nelse:\n    print("PREVIA: treino nao gravado")'
        )

    else:
        codigo = codigo.replace(
            "    n_total = n_por_dia * dias_delta",
            '    if not 1 <= dias_delta <= 366:\n'
            '        raise ValueError("Periodo invalido")\n'
            '    n_total = n_por_dia * dias_delta'
        )

        inicio = codigo.index("df_prod.write")
        fim = codigo.index("\nprint(", inicio)

        substituto = '''
if gravar:
    if spark.catalog.tableExists(nome_tabela_prod):
        df_prod.write.format("delta").mode("overwrite").option(
            "replaceWhere",
            f"dia_prtc >= '{p_inicio}' AND dia_prtc < '{p_fim}'"
        ).saveAsTable(nome_tabela_prod)
    else:
        df_prod.write.format("delta").mode("overwrite").partitionBy(
            "dia_prtc"
        ).saveAsTable(nome_tabela_prod)
else:
    print("PREVIA: producao nao gravada")
'''
        codigo = codigo[:inicio] + substituto + codigo[fim:]

    codigo = parametros + "\n" + codigo
    ast.parse(codigo)

    novo = destino / (nome + "_aprimorado.ipynb")
    if novo.exists():
        relatorio.append("PRESERVADO: " + novo.name)
        continue

    notebook["cells"] = [
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": codigo.splitlines(keepends=True)
        }
    ]

    novo.write_text(
        json.dumps(notebook, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    relatorio.append("CRIADO: " + novo.name)

for nome in nomes:
    novo = destino / (nome + "_aprimorado.ipynb")
    dados = json.loads(novo.read_text(encoding="utf-8"))
    for celula in dados["cells"]:
        if celula["cell_type"] == "code":
            ast.parse("".join(celula["source"]))
    relatorio.append("VALIDADO: " + novo.name)

(destino / "VALIDACAO_AULA_05_02.txt").write_text(
    "\n".join(relatorio) +
    "\nSintaxe local verificada.\n"
    "Execucao Databricks ainda pendente.\n",
    encoding="utf-8"
)

print("\n".join(relatorio))
print("AUDITORIA LOCAL CONCLUIDA")