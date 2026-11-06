class Metadados:
    """
    Classe inicial da Aula 03.
    """
    pass


class MetadadosTabela:
    """
    Representa os metadados de uma tabela.

    A leitura do arquivo JSON ocorre fora desta classe.
    """

    def __init__(self):
        self.nome: str = None
        self.database: str = None
        self.camada: str = None
        self.descricao: str = None
        self.colunas: list = []

    def load_from_artefato(self, info: dict):
        """
        Transfere os metadados de um dicionario
        para os atributos da instancia.
        """

        if not isinstance(info, dict):
            raise TypeError(
                "O artefato deve ser um dicionario."
            )

        self.nome = info.get("name")
        self.database = info.get("database")
        self.descricao = info.get("descricao")
        self.colunas = info.get("schema", [])

        return self

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"nome={self.nome!r}, "
            f"database={self.database!r}, "
            f"camada={self.camada!r}, "
            f"descricao={self.descricao!r}, "
            f"colunas={self.colunas!r}"
            f")"
        )