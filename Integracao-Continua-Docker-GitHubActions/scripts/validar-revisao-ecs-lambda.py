from pathlib import Path
import ast
import zipfile

root = Path(r"F:\Projetos\Docker-GitHubActions-CI-CD")

app_file = root / "docker-automation/burguer-app/auth-service/app.py"
model_file = root / "docker-automation/burguer-app/auth-service/models/user_model.py"
lambda_file = root / "docker-automation/lambda-estudo/auth-service-lambda/lambda_function.py"
zip_file = root / "aulas/aws-lambda/auth-service-lambda-demo.zip"


def analisar_python(path):
    codigo = path.read_text(encoding="utf-8-sig")
    arvore = ast.parse(codigo, filename=str(path))
    return codigo, arvore


print("\n===== VALIDANDO AUTH-SERVICE =====")

codigo_app, arvore_app = analisar_python(app_file)

obrigatorios = [
    "load_dotenv()",
    "Flask(__name__)",
    "app.secret_key",
    "register_blueprint",
    "auth_bp",
    "auth.login_page",
]

for termo in obrigatorios:
    if termo not in codigo_app:
        raise RuntimeError(f"Componente ausente: {termo}")
    print(f"VALIDADO: {termo}")

funcoes_app = {
    node.name
    for node in ast.walk(arvore_app)
    if isinstance(node, ast.FunctionDef)
}

if "index" not in funcoes_app:
    raise RuntimeError("Rota index nao encontrada")

portas = [
    keyword.value.value
    for node in ast.walk(arvore_app)
    if isinstance(node, ast.Call)
    for keyword in node.keywords
    if keyword.arg == "port"
    and isinstance(keyword.value, ast.Constant)
]

if 5000 not in portas:
    raise RuntimeError("Porta 5000 nao encontrada")

print("VALIDADO: rota index")
print("VALIDADO: porta 5000")

if 'SECRET_KEY carregada' in codigo_app:
    print("ATENCAO: codigo original registra a SECRET_KEY")
    print("Corrigir antes de publicar ou usar em producao")

if "debug=True" in codigo_app:
    print("ATENCAO: debug=True no codigo original")
    print("Desabilitar em producao")


print("\n===== VALIDANDO SERIALIZACAO =====")

_, arvore_modelo = analisar_python(model_file)

funcoes = [
    node
    for node in arvore_modelo.body
    if isinstance(node, ast.FunctionDef)
    and node.name == "serialize_user"
]

if len(funcoes) != 1:
    raise RuntimeError("serialize_user nao encontrada")

retornos = [
    node.value
    for node in ast.walk(funcoes[0])
    if isinstance(node, ast.Return)
    and isinstance(node.value, ast.Dict)
]

if len(retornos) != 1:
    raise RuntimeError("Retorno de serializacao inesperado")

campos = {
    chave.value
    for chave in retornos[0].keys
    if isinstance(chave, ast.Constant)
}

esperados = {"email", "name", "address", "role"}

if campos != esperados:
    raise RuntimeError("Campos de usuario diferentes do esperado")

for campo in sorted(esperados):
    print(f"CAMPO IDENTIFICADO: {campo}")


print("\n===== VALIDANDO LAMBDA =====")

_, arvore_lambda = analisar_python(lambda_file)

funcoes_lambda = {
    node.name
    for node in arvore_lambda.body
    if isinstance(node, ast.FunctionDef)
}

if "lambda_handler" not in funcoes_lambda:
    raise RuntimeError("Lambda handler nao encontrado")

print("VALIDADO: lambda_handler")

if not zip_file.is_file():
    raise RuntimeError("Pacote ZIP da aula anterior nao encontrado")

with zipfile.ZipFile(zip_file) as pacote:
    if pacote.testzip() is not None:
        raise RuntimeError("Pacote ZIP corrompido")

    if "lambda_function.py" not in pacote.namelist():
        raise RuntimeError("Handler ausente do ZIP")

print("VALIDADO: ZIP com lambda_function.py")
print("\nREVISAO ESTATICA PYTHON APROVADA")
