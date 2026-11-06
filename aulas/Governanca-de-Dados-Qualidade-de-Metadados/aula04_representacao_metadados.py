from classes.metadados import MetadadosTabela

print("\n===== ALURA - AULA 04 =====")
print("CRIANDO REPRESENTACAO DOS METADADOS")

# Instanciar objeto
m = MetadadosTabela()

print("\nOBJETO CRIADO:")
print(m)

print("\nTIPO DO OBJETO:")
print(type(m))

print("\nATRIBUTOS INICIAIS:")
print("Nome:", m.nome)
print("Database:", m.database)
print("Camada:", m.camada)
print("Descricao:", m.descricao)
print("Colunas:", m.colunas)

# Testar preenchimento dos atributos
m.nome = "previsoes_de_venda_diario"
m.database = "bz_data_science"
m.camada = "bronze"
m.descricao = "Previsoes diarias de vendas"

m.colunas = [
    "data_referencia",
    "produto_id",
    "previsao_vendas"
]

print("\nOBJETO COM ATRIBUTOS PREENCHIDOS:")
print(m)

# Validacoes
assert isinstance(m, MetadadosTabela)
assert m.camada == "bronze"
assert len(m.colunas) == 3

print("\nTESTES CONCLUIDOS COM SUCESSO.")