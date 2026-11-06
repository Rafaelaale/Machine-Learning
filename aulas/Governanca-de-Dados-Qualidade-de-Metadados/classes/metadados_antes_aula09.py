class Metadados:
    pass


class MetadadosColuna:
    def __init__(self):
        self.nome = None
        self.datatype = None
        self.descricao = None
        self.privacidade = None
        self.confidencialidade = None

    def __repr__(self):
        return (
            f"MetadadosColuna("
            f"nome={self.nome!r}, "
            f"datatype={self.datatype!r}, "
            f"descricao={self.descricao!r}, "
            f"privacidade={self.privacidade!r}, "
            f"confidencialidade={self.confidencialidade!r})"
        )

    def load_from_item_tabela(self, item):
        if not isinstance(item, dict):
            raise TypeError("A coluna deve ser um dicionario.")

        self.nome = item.get("name")
        self.datatype = item.get("datatype")
        self.descricao = item.get("descricao")
        self.privacidade = item.get("privacidade")
        self.confidencialidade = item.get("confidencialidade")
        return self

    def load_from_tabela(self, item):
        return self.load_from_item_tabela(item)


class MetadadosTabela:
    def __init__(self):
        self.nome = None
        self.database = None
        self.camada = None
        self.descricao = None
        self.colunas = []

    def __repr__(self):
        return (
            f"MetadadosTabela("
            f"nome={self.nome!r}, "
            f"database={self.database!r}, "
            f"camada={self.camada!r}, "
            f"descricao={self.descricao!r}, "
            f"colunas={self.colunas!r})"
        )

    def load_from_artefato(self, info):
        if not isinstance(info, dict):
            raise TypeError("O artefato deve ser um dicionario.")

        self.nome = info.get("name")
        self.database = info.get("database")
        self.camada = None
        self.descricao = info.get("descricao")
        self.colunas = info.get("schema") or []

        if not isinstance(self.colunas, list):
            raise TypeError("O schema deve ser uma lista.")

        return self

    def converte_colunas_em_objetos(self):
        lista_colunas_objetos = []

        for item in self.colunas:
            if isinstance(item, MetadadosColuna):
                meta_col = item
            else:
                meta_col = MetadadosColuna()
                meta_col.load_from_item_tabela(item)

            lista_colunas_objetos.append(meta_col)

        self.colunas = lista_colunas_objetos
        return self