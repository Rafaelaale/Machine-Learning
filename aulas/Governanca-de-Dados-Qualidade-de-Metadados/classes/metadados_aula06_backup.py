class Metadados:
    """
    Classe inicial da Aula 03.
    """
    pass


class MetadadosTabela:
    """
    Representa os metadados de uma tabela.
    """

    def __init__(self):
        self.nome: str = None
        self.database: str = None
        self.camada: str = None
        self.descricao: str = None
        self.colunas: list = []

    def load_from_artefato(self, info: dict):

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


class MetadadosColuna:
    """
    Representa os metadados de uma coluna.
    """

    def __init__(self) -> None:

        self.nome: str = None
        self.datatype: str = None
        self.descricao: str = None
        self.privacidade: str = None
        self.confidencialidade: str = None

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"nome={self.nome!r}, "
            f"datatype={self.datatype!r}, "
            f"descricao={self.descricao!r}, "
            f"privacidade={self.privacidade!r}, "
            f"confidencialidade={self.confidencialidade!r}"
            f")"
        )

    def load_from_tabela(self, item: dict):

        if not isinstance(item, dict):
            raise TypeError(
                "A coluna deve ser um dicionario."
            )

        self.nome = item.get("name")
        self.datatype = item.get("datatype")
        self.descricao = item.get("descricao")
        self.privacidade = item.get("privacidade")
        self.confidencialidade = item.get(
            "confidencialidade"
        )

        return self