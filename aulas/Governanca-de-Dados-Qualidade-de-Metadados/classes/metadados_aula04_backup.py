class Metadados:
    """
    Classe inicial criada na Aula 03.
    """
    pass


class MetadadosTabela:
    """
    Representa os metadados de uma tabela
    nas camadas Bronze, Silver ou Gold.
    """

    def __init__(self):
        self.nome: str = None
        self.database: str = None
        self.camada: str = None
        self.descricao: str = None
        self.colunas: list = []

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