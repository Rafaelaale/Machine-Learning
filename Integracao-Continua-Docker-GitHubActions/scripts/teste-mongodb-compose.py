import os
import sys
from pymongo import MongoClient

uri = os.environ.get('MONGO_URI')

if not uri:
    sys.exit('ERRO: MONGO_URI ausente')

if 'mongo:27017' not in uri:
    sys.exit('ERRO: MONGO_URI nao aponta para o Compose')

cliente = MongoClient(uri, serverSelectionTimeoutMS=8000)
banco = cliente['burguer_app_db']
colecoes = banco.list_collection_names()

print('MONGODB AUTENTICADO COM SUCESSO')
print('BANCO:', banco.name)
print('COLECOES:', len(colecoes))
cliente.close()
