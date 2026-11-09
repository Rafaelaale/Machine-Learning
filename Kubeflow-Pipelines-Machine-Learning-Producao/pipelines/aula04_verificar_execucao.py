import kfp

RUN_ID = "54213db1-c036-428d-91a6-4b41d517c5fa"

cliente = kfp.Client(host="http://localhost:8080")
execucao = cliente.get_run(run_id=RUN_ID)

print("RUN ID:", RUN_ID)
print("STATUS:", execucao.state)

if execucao.state == "SUCCEEDED":
    print("PIPELINE EXECUTADO COM SUCESSO")
elif execucao.state == "FAILED":
    print("PIPELINE FALHOU")
else:
    print("EXECUCAO PENDENTE OU EM ANDAMENTO")
