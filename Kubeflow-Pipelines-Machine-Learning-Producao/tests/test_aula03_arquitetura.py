import ast
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CODIGO = ROOT / "pipelines/aula03_arquitetura_kfp.py"
NOTAS = ROOT / "anotacoes/aula03_arquitetura_kubeflow.md"
NOTEBOOK = ROOT / "notebooks/03_arquitetura_kubeflow.ipynb"


class TestAula03(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.codigo = CODIGO.read_text(encoding="utf-8-sig")
        cls.arvore = ast.parse(cls.codigo)
        cls.funcoes = {
            item.name: item
            for item in cls.arvore.body
            if isinstance(item, ast.FunctionDef)
        }
        cls.notas = NOTAS.read_text(encoding="utf-8-sig")

    def test_01_codigo_existe(self):
        self.assertTrue(CODIGO.is_file())

    def test_02_python_valido(self):
        compile(self.codigo, str(CODIGO), "exec")

    def test_03_preprocess(self):
        self.assertIn("preprocess", self.funcoes)

    def test_04_train(self):
        self.assertIn("train", self.funcoes)

    def test_05_pipeline(self):
        self.assertIn("pipeline_ml", self.funcoes)

    def test_06_decorador_component_preprocess(self):
        fun = self.funcoes["preprocess"]
        self.assertTrue(any(
            isinstance(d, ast.Call)
            and isinstance(d.func, ast.Attribute)
            and d.func.attr == "component"
            for d in fun.decorator_list
        ))

    def test_07_decorador_component_train(self):
        fun = self.funcoes["train"]
        self.assertTrue(any(
            isinstance(d, ast.Call)
            and isinstance(d.func, ast.Attribute)
            and d.func.attr == "component"
            for d in fun.decorator_list
        ))

    def test_08_decorador_pipeline(self):
        fun = self.funcoes["pipeline_ml"]
        self.assertTrue(any(
            isinstance(d, ast.Call)
            and isinstance(d.func, ast.Attribute)
            and d.func.attr == "pipeline"
            for d in fun.decorator_list
        ))

    def test_09_dependencia_entre_etapas(self):
        self.assertIn(
            "train(dataset=preparacao.output)",
            self.codigo,
        )

    def test_10_compilador(self):
        self.assertIn("compiler.Compiler().compile", self.codigo)

    def test_11_notas_kfp(self):
        self.assertIn("Kubeflow Pipelines", self.notas)

    def test_12_notas_katib(self):
        self.assertIn("Katib", self.notas)

    def test_13_notas_trainer_kserve(self):
        self.assertIn("Trainer", self.notas)
        self.assertIn("KServe", self.notas)

    def test_14_notebook(self):
        self.assertTrue(NOTEBOOK.is_file())
        dados = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
        self.assertEqual(dados["nbformat"], 4)
        self.assertGreaterEqual(len(dados["cells"]), 4)


if __name__ == "__main__":
    unittest.main()
