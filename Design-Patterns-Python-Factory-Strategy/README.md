# Design Patterns em Python

## Engenharia de Software, Arquitetura e Testes

Projeto educacional desenvolvido durante uma trilha prática
de Design Patterns em Python.

O objetivo é implementar e comparar padrões de projeto,
entender suas aplicações e validar os comportamentos por
meio de testes automatizados.

## Resultados

- **27 aulas com implementações práticas**
- **432 testes automatizados aprovados na última execução local**
- Código Python organizado por aula
- Laboratórios executáveis
- Anotações técnicas
- Relatórios JSON

## Padrões e conceitos implementados

| Tema | Aplicação |
|---|---|
| Singleton | Controle de instância e sincronização |
| Dependency Injection | Redução de acoplamento e composição |
| Lazy Loading | Carregamento sob demanda |
| Proxy | Controle de acesso a objetos |
| Simple Factory | Centralização da criação de objetos |
| Factory Method | Criação através de abstrações |
| Registry | Registro e seleção de implementações |
| Decorator | Composição de funcionalidades |
| Strategy | Algoritmos intercambiáveis |
| Template Method | Estudo de hooks e sequência de execução |

## Organização do projeto

- `src/` — implementações dos conceitos
- `aulas/` — laboratórios executáveis
- `tests/` — testes automatizados
- `anotacoes/` — explicações e materiais de estudo
- `exemplos/` — exemplos adicionais de bibliotecas
- `resultados/` — relatórios gerados

## Exemplos práticos

### Factory Method

Implementação de diferentes formas de pagamento
por meio de classes criadoras e produtos.

### Dependency Injection

Separação entre contratos e implementações concretas,
incluindo exemplos de integração com FastAPI.

### Decorator

Aplicação de logs, repetição de funções,
preservação de metadados e decoradores com classes.

### Strategy

Substituição de uma estrutura extensa de if/else
por estratégias independentes de cálculo de descontos.

Também foi explorada a implementação utilizando
funções de primeira classe e expressões lambda.

### Testes

O projeto utiliza `unittest`.

Para executar os testes, configure um ambiente Python
com as dependências necessárias e, na raiz desta trilha,
execute:

```powershell
python -m unittest discover -s tests -p "test_aula*.py"
```

A execução completa envolve bibliotecas utilizadas
nos laboratórios, como FastAPI e SQLAlchemy.

Os resultados são registros de testes locais;
não constituem certificação externa.

## Aprendizados

- Princípios de programação orientada a objetos
- Separação de responsabilidades
- Polimorfismo
- Composição
- Manutenção e extensibilidade
- Testabilidade
- Identificação de code smells
- Redução de acoplamento
- Aplicação prática de padrões de projeto

## Limitações

Os exemplos foram construídos com finalidade didática.
Não representam sistemas empresariais implantados
ou experiência profissional de produção.

Algumas demonstrações de frameworks são exemplos de código
e não aplicações completas com infraestrutura externa.

## Autor

Rafael Alexandre Oliveira Araujo

[GitHub](https://github.com/Rafaelaale)

[Voltar ao portfólio principal](../README.md)
