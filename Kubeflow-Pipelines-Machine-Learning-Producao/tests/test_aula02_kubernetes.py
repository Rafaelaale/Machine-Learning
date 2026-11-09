import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
K8S = ROOT / 'kubernetes'


def ler(nome):
    return (K8S / nome).read_text(encoding='utf-8-sig')


class TestAula02(unittest.TestCase):

    def test_01_namespace(self):
        self.assertIn('kind: Namespace', ler('01_namespace.yaml'))

    def test_02_nome_namespace(self):
        self.assertIn('name: kubeflow-aula02', ler('01_namespace.yaml'))

    def test_03_pod(self):
        self.assertIn('kind: Pod', ler('02_pod.yaml'))

    def test_04_imagem_pod(self):
        self.assertIn('busybox:1.37', ler('02_pod.yaml'))

    def test_05_deployment(self):
        self.assertIn('kind: Deployment', ler('03_deployment.yaml'))

    def test_06_replicas(self):
        self.assertIn('replicas: 1', ler('03_deployment.yaml'))

    def test_07_selector(self):
        self.assertIn('matchLabels:', ler('03_deployment.yaml'))

    def test_08_job(self):
        self.assertIn('kind: Job', ler('04_job.yaml'))

    def test_09_backoff(self):
        self.assertIn('backoffLimit: 3', ler('04_job.yaml'))

    def test_10_restart(self):
        self.assertIn('restartPolicy: Never', ler('04_job.yaml'))

    def test_11_resources(self):
        for nome in ('02_pod.yaml', '03_deployment.yaml', '04_job.yaml'):
            texto = ler(nome)
            self.assertIn('requests:', texto)
            self.assertIn('limits:', texto)

    def test_12_documentacao(self):
        arquivo = ROOT / 'anotacoes/aula02_conceitos_kubernetes.md'
        self.assertTrue(arquivo.is_file())
        self.assertIn('CRD', arquivo.read_text(encoding='utf-8-sig'))


if __name__ == '__main__':
    unittest.main()
