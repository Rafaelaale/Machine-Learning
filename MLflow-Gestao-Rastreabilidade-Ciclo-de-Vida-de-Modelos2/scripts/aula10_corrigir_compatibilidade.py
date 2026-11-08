from pathlib import Path
import shutil

raiz = Path.cwd()

arquivo_src = raiz / "src/aula09_organizacao_experimentos.py"
arquivo_teste = raiz / "tests/test_aula09_organizacao_experimentos.py"

for arquivo in (arquivo_src, arquivo_teste):
    if not arquivo.is_file():
        raise FileNotFoundError(str(arquivo))

def atualizar(arquivo, antigo, novo):
    texto = arquivo.read_text(encoding="utf-8")

    if novo in texto and antigo not in texto:
        print("JA CORRIGIDO:", arquivo.name)
        return

    if antigo not in texto:
        raise RuntimeError(
            "Trecho esperado nao encontrado: "
            + str(arquivo)
        )

    backup = arquivo.with_name(
        arquivo.name + ".backup_aula10"
    )

    if not backup.exists():
        shutil.copy2(arquivo, backup)

    texto = texto.replace(antigo, novo)

    arquivo.write_text(
        texto,
        encoding="utf-8",
    )

    print("CORRIGIDO:", arquivo.name)
    print("BACKUP:", backup.name)


# A Aula 09 deve recuperar o historico inteiro,
# inclusive runs que avancaram para outra etapa.
atualizar(
    arquivo_src,
    '"AND tags.selection_status = \'candidate\' "',
    '"AND tags.organization_lesson = \'aula_09\' "',
)

# A substituicao acima pode duplicar a condicao
# organization_lesson; removemos a duplicacao.
texto = arquivo_src.read_text(encoding="utf-8")

duplicado = (
    '"AND tags.organization_lesson = \'aula_09\' "\n'
    '            "AND tags.organization_lesson = \'aula_09\' "'
)

if duplicado in texto:
    arquivo_src.write_text(
        texto.replace(
            duplicado,
            '"AND tags.organization_lesson = \'aula_09\' "'
        ),
        encoding="utf-8",
    )

# Atualiza o teste historico para refletir a
# evolucao dos status na Aula 10.
antigo = '''            for chave, valor in esperado.items():
                self.assertEqual(
                    atualizada.data.tags.get(chave),
                    valor,
                )'''

novo = '''            for chave, valor in esperado.items():
                if chave == "selection_status":
                    arquivo_selecao = (
                        ARQUIVO_JSON.parent
                        / "aula10_escolha_campeao.json"
                    )

                    if arquivo_selecao.is_file():
                        selecao = json.loads(
                            arquivo_selecao.read_text(
                                encoding="utf-8"
                            )
                        )
                        campeao_id = selecao["champion"]["run_id"]
                        valor = (
                            "champion candidate"
                            if run.info.run_id == campeao_id
                            else "challenger"
                        )

                self.assertEqual(
                    atualizada.data.tags.get(chave),
                    valor,
                )'''

atualizar(
    arquivo_teste,
    antigo,
    novo,
)

print("\nCOMPATIBILIDADE AULAS 09/10: CORRIGIDA")