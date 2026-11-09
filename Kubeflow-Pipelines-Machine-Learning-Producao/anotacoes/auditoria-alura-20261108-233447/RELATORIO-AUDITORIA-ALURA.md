# AUDITORIA ALURA - KUBEFLOW MLOPS
Data: 11/08/2026 23:34:47
Projeto: C:\Users\rafal\Desktop\Kubeflow-Pipelines-Machine-Learning-Producao
PASTA OK | src | 16 arquivos
PASTA OK | docker | 1 arquivos
PASTA OK | trainer | 7 arquivos
PASTA OK | serving | 9 arquivos
PASTA OK | tests | 2 arquivos
ARQUIVO OK | EDA | src\eda_fraudes.py
ARQUIVO OK | Feature Engineering | src\features.py
ARQUIVO OK | Machine Learning | src\model.py
ARQUIVO OK | Treinamento XGBoost | src\train.py
ARQUIVO OK | Kubeflow Pipelines | src\pipeline.py
ARQUIVO OK | Execucao de Pipelines | src\pipeline_runner.py
ARQUIVO OK | Katib - Treinamento | src\train_katib.py
ARQUIVO OK | Katib - Otimizacao | src\executar_pipeline_katib_otimizada.py
ARQUIVO OK | Trainer Python | src\train_node.py
ARQUIVO OK | ClusterTrainingRuntime | trainer\runtime-fraude.yaml
ARQUIVO OK | TrainJob | trainer\trainjob.yaml
ARQUIVO OK | Job Kubernetes | trainer\job-fraude-compat.yaml
ARQUIVO OK | Pipeline com Trainer | src\pipeline_kfp_aula27.py
ARQUIVO AUSENTE | Pipeline Compilada Aula 27 | trainer\pipeline-aula27.yaml
ARQUIVO OK | InferenceService | serving\inference-service-fraude.yaml
ARQUIVO OK | Servidor de API | src\server_inferencia_aula31.py
ARQUIVO OK | Deployment de Inferencia | serving\deployment-aula31-corrigido.yaml
ARQUIVO OK | Pipeline End-to-End | src\pipeline_e2e_aula32.py
ARQUIVO OK | Pipeline E2E Compilada | trainer\pipeline-e2e-aula32.yaml
ARQUIVO OK | RBAC E2E | serving\rbac-kfp-deploy-aula32.yaml
ARQUIVOS_PYTHON: 17
ERROS_SINTAXE: 0
SINTAXE PYTHON: VALIDADA
CONSULTA OK | nodes
CONSULTA OK | pvcs
CONSULTA OK | deployments
CONSULTA OK | jobs
CONSULTA OK | katib
CONSULTA OK | crds
CRD AUSENTE | trainjobs.trainer.kubeflow.org
CRD AUSENTE | clustertrainingruntimes.trainer.kubeflow.org
CRD AUSENTE | inferenceservices.serving.kserve.io
CRD AUSENTE | clusterservingruntimes.serving.kserve.io
CONSULTA OK | workflow-aula32
WORKFLOW AULA 32: Succeeded
CONSULTA OK | predictor-json
PREDICTOR READY: 1
IMAGEM: fraude-trainer:2.3
MODELO: /models/serving/releases/ad2cf8271ba14934bf5d04e724ec9bc2/model.ubj
RUN_ID: d711b766-d647-4f8e-8115-b59200cd90fc
BACKUP DE ARQUIVOS: LOCALIZADO
