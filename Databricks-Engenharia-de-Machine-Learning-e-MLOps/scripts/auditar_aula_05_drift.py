from pathlib import Path
import json
import sys

projeto = Path(__file__).resolve().parents[1]
origem = projeto / "material-alura" / "6123-alura-ml-databricks" / "aula_5"
relatorio = projeto / "relatorios" / "auditoria_aula_05_01_drift.txt"

esperados = [
    "aula_5_2_gerando_dados.ipynb",
    "aula_5_2_job_dados_prod.ipynb",
    "aula_5_2_job_monitoramento_drift.ipynb",
    "verificar_drift.ipynb",
    "aula_5_5_re_treino.ipynb",
    "aula_5_5_promp_genie.ipynb",
]

fontes = {}
linhas = ["AUDITORIA AULA 5.1 - MONITORAMENTO E DRIFT", ""]

print("===== NOTEBOOKS ORIGINAIS DA ALURA =====")

for arquivo in esperados:
    caminho = origem / arquivo
    if not caminho.is_file():
        raise FileNotFoundError(f"Notebook original ausente: {caminho}")

    documento = json.loads(caminho.read_text(encoding="utf-8-sig"))
    celulas = documento.get("cells", [])
    codigo = "\n".join(
        "".join(c.get("source", []))
        for c in celulas if c.get("cell_type") == "code"
    )
    n_codigo = sum(c.get("cell_type") == "code" for c in celulas)
    fontes[arquivo] = codigo

    mensagem = f"VALIDADO: {arquivo} | celulas={len(celulas)} | codigo={n_codigo}"
    print(mensagem)
    linhas.append(mensagem)

yaml = origem / "carga_produtiva_monitoramento.yaml"
if not yaml.is_file():
    raise FileNotFoundError(f"YAML original ausente: {yaml}")
texto_yaml = yaml.read_text(encoding="utf-8-sig")
print("VALIDADO: carga_produtiva_monitoramento.yaml")
linhas.append("VALIDADO: carga_produtiva_monitoramento.yaml")

monitoramento = fontes["aula_5_2_job_monitoramento_drift.ipynb"]
verificar = fontes["verificar_drift.ipynb"]
producao = fontes["aula_5_2_job_dados_prod.ipynb"]
retreino = fontes["aula_5_5_re_treino.ipynb"]

avisos = [
    ("KS sobre distribuicoes numericas; p-value sozinho nao mede impacto",
     "ks_2samp" in monitoramento),
    ("Mudanca na taxa do target tratada como concept drift; classificacao precisa revisao",
     "var_relativa" in monitoramento and "media_t" in monitoramento),
    ("Contagem de alertas antigos sem filtro de periodo",
     "WHERE drift_detectado = true" in verificar and "periodo_inicio" not in verificar),
    ("Append produtivo pode duplicar dados ao reexecutar periodos",
     '.mode("append")' in producao),
    ("Retreinamento promove Champion automaticamente",
     "set_registered_model_alias" in retreino),
    ("Retreinamento original realiza divisao aleatoria",
     "train_test_split" in retreino),
    ("YAML possui caminho de usuario ainda nao configurado",
     "<SEU_EMAIL>" in texto_yaml),
]

print("\n===== PONTOS DE ATENCAO =====")
linhas.extend(["", "PONTOS DE ATENCAO:"])

for descricao, encontrado in avisos:
    if encontrado:
        print("ATENCAO:", descricao)
        linhas.append("ATENCAO: " + descricao)

linhas.extend([
    "", "RESULTADO: 6 NOTEBOOKS + 1 YAML INSPECIONADOS",
    "Auditoria apenas estatica; codigo da Alura nao executado.",
    "Nenhum job criado, nenhuma tabela alterada, nenhum alias promovido.",
])

relatorio.parent.mkdir(parents=True, exist_ok=True)
relatorio.write_text("\n".join(linhas) + "\n", encoding="utf-8")
print("\nRELATORIO:", relatorio)