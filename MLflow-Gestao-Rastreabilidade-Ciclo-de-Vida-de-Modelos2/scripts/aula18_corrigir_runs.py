from pathlib import Path

arquivo = Path("src/aula18_run_pipeline.py")
codigo = arquivo.read_text(encoding="utf-8-sig")

inicio = "            run_id = submitted.run_id"
fim = "            return run_id"

novo = '''            project_run_id = submitted.run_id
            project_run = client.get_run(project_run_id)

            if project_run.info.status != "FINISHED":
                raise RuntimeError(
                    f"MLflow Project {entry_point} falhou: "
                    f"{project_run.info.status}"
                )

            arquivos = {
                "prepare": destino / "prepare.json",
                "train": destino / "train.json",
                "evaluate": destino / "evaluation.json",
            }

            arquivo_etapa = arquivos[entry_point]

            if not arquivo_etapa.is_file():
                raise RuntimeError(
                    f"Resultado da etapa ausente: {arquivo_etapa}"
                )

            dados_etapa = json.loads(
                arquivo_etapa.read_text(encoding="utf-8")
            )

            run_id = dados_etapa["run_id"]
            run = client.get_run(run_id)

            if run.info.status != "FINISHED":
                raise RuntimeError(
                    f"Run efetivo {entry_point} falhou: "
                    f"{run.info.status}"
                )

            if dados_etapa["pipeline_id"] != pipeline_id:
                raise RuntimeError(
                    "Run pertence a outro pipeline."
                )

            client.set_tag(
                run_id, "mlflow.parentRunId", parent_id
            )
            client.set_tag(
                run_id, "pipeline_id", pipeline_id
            )
            client.set_tag(
                run_id, "pipeline_step", entry_point
            )
            client.set_tag(
                run_id, "mlflow_project_run_id", project_run_id
            )

            print(
                "ETAPA VALIDADA:",
                entry_point,
                "PROJECT_RUN:",
                project_run_id,
                "MODEL_STEP_RUN:",
                run_id,
                flush=True,
            )

            return run_id'''

if "project_run_id = submitted.run_id" in codigo:
    print("ORQUESTRADOR JA CORRIGIDO")

else:
    pos_inicio = codigo.find(inicio)
    pos_fim = codigo.find(fim, pos_inicio)

    if pos_inicio < 0 or pos_fim < 0:
        raise RuntimeError(
            "Trecho esperado nao encontrado. "
            "Arquivo original preservado."
        )

    pos_fim += len(fim)

    codigo = (
        codigo[:pos_inicio]
        + novo
        + codigo[pos_fim:]
    )

    arquivo.write_text(codigo, encoding="utf-8")
    print("RASTREABILIDADE CORRIGIDA")

print("ARQUIVO:", arquivo)