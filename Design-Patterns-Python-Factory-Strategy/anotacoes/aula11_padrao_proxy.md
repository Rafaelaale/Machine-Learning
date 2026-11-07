# Aula 11 - Padrao Proxy

## Objetivo

Controlar o acesso a um objeto sem
precisar modificar a classe original.

## 1. Objeto real

Config carrega o arquivo JSON
no seu metodo __init__.

Sua responsabilidade nao foi alterada.

## 2. Proxy com Lazy Loading

ConfigProxy recebe o caminho do arquivo.

Ao ser criado, nao instancia Config.

Quando acessamos proxy.data:

1. Verifica se _config e None.
2. Cria Config caso necessario.
3. Retorna o dicionario data.

O objeto real passa a existir apenas
quando a configuracao for solicitada.

## 3. Proxy com logs

ConfigProxyLazyLoading acrescenta
mensagens para observacao.

No primeiro acesso:

Acessando configuração...
Carregando configuração...
Lendo arquivo de configuração...

Nos acessos seguintes, nao ocorre
nova leitura do JSON.

## 4. DataProxy

O DataProxy intercepta acessos ao
dicionario com __getitem__.

Exemplo:

dados = DataProxy(proxy)
tema = dados["theme"]

O metodo registra a chave e
retorna o valor encontrado.

Na implementacao apresentada pela Alura,
chaves ausentes retornam None usando get().

Isso difere do comportamento convencional
de um dict, que gera KeyError.

## 5. Vantagens

- Controle de acesso.
- Lazy Loading.
- Registro de logs.
- Possibilidade de cache.
- Acrescentar funcionalidades ao objeto real.

## 6. Desvantagens

- Complexidade adicional.
- Possivel aumento de latencia.
- Mais uma camada para depurar.
- Confusao entre o Proxy e o objeto real.

## 7. Decorador property

@property oferece acesso a uma funcao
pela sintaxe de atributo.

Exemplo:

objeto.x

No laboratorio, retorna 10.

## 8. functools.partial

partial cria um objeto chamavel
com argumentos previamente definidos.

Exemplo:

plus_10 = partial(soma, 10)
plus_10(5)

Resultado: 15.

Tambem demonstramos:

plus_5 = partial(soma, b=5)
plus_5(10)

Resultado: 15.

Embora seja usado na transcricao como
exemplo de intermediacao de chamadas,
partial nao e necessariamente uma
implementacao integral do padrao GoF Proxy.

## 9. Arquivos criados

dados_aula11/config.json
src/aula11_padrao_proxy.py
aulas/aula11_padrao_proxy.py
tests/test_aula11_padrao_proxy.py
anotacoes/aula11_padrao_proxy.md
resultados/aula11_padrao_proxy.json

## 10. Observacao tecnica

O proxy da aula e didatico e nao possui
sincronizacao para multiplas threads.

O arquivo config.json das aulas anteriores
nao foi alterado.
