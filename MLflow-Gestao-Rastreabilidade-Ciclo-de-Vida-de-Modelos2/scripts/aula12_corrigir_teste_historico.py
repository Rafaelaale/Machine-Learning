from pathlib import Path
import shutil

arquivo = Path(
    "tests/test_aula11_model_registry.py"
)

if not arquivo.is_file():
    raise FileNotFoundError(str(arquivo))

texto = arquivo.read_text(encoding="utf-8")

antigo = '''        self.assertEqual(
            self.versao.tags["lifecycle_status"],
            "candidate",
        )'''

novo = '''        from pathlib import Path
        import json

        registro_aula12 = (
            RESULTADO.parent
            / "aula12_promocao_modelos.json"
        )

        esperado = "candidate"

        if registro_aula12.is_file():
            dados = json.loads(
                registro_aula12.read_text(
                    encoding="utf-8"
                )
            )
            if (
                dados["version"]
                == str(self.versao.version)
            ):
                esperado = "production"

        self.assertEqual(
            self.versao.tags["lifecycle_status"],
            esperado,
        )'''

# RESULTADO e a constante ja importada no teste
# da Aula 11, que precisa ser adicionada no import.
if "RESULTADO," not in texto:
    texto = texto.replace(
        "    ANOTACAO,",
        "    ANOTACAO,\n    RESULTADO,",
    )

if antigo in texto:
    backup = arquivo.with_name(
        arquivo.name + ".backup_aula12"
    )

    if not backup.exists():
        shutil.copy2(arquivo, backup)

    texto = texto.replace(antigo, novo)

    arquivo.write_text(
        texto,
        encoding="utf-8",
    )

    print("TESTE HISTORICO CORRIGIDO")
elif novo in texto:
    print("TESTE HISTORICO JA CORRIGIDO")
else:
    raise RuntimeError(
        "Trecho de lifecycle nao localizado. "
        "Arquivo original preservado."
    )