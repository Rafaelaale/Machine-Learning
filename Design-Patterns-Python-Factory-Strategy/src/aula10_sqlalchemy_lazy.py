"""Aula 10 - Lazy Loading de relacionamentos SQLAlchemy."""

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    create_engine,
    event,
    inspect,
    select,
)
from sqlalchemy.orm import (
    Session,
    declarative_base,
    relationship,
)


Base = declarative_base()


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    books = relationship(
        "Book",
        back_populates="author",
        lazy="select",
    )

    def __repr__(self):
        return (
            f"Author(id={self.id}, name={self.name})"
        )


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    author_id = Column(
        ForeignKey("authors.id")
    )

    author = relationship(
        "Author",
        back_populates="books",
    )

    def __repr__(self):
        return (
            f"Book(id={self.id}, title={self.title})"
        )


def demonstrar_sqlalchemy():
    """Comprova o carregamento por consulta SQL.

    Cria um banco SQLite temporario em memoria.
    Captura os SELECTs executados na consulta.
    """

    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
    )

    consultas = []

    try:
        Base.metadata.create_all(engine)

        with Session(engine) as session:
            autor = Author(name="Machado de Assis")

            autor.books = [
                Book(title="Dom Casmurro"),
                Book(title="Memórias Póstumas"),
            ]

            session.add(autor)
            session.commit()

        def registrar_sql(
            conn,
            cursor,
            statement,
            parameters,
            context,
            executemany,
        ):
            if statement.lstrip().upper().startswith("SELECT"):
                consultas.append(statement)

        event.listen(
            engine,
            "before_cursor_execute",
            registrar_sql,
        )

        with Session(engine) as session:
            autor = session.scalars(
                select(Author)
            ).first()

            if autor is None:
                raise RuntimeError(
                    "Autor nao encontrado"
                )

            # Estado antes do acesso ao relacionamento.
            livros_nao_carregados = (
                "books" in inspect(autor).unloaded
            )

            books_no_dict_antes = (
                "books" in autor.__dict__
            )

            consultas_antes = len(consultas)

            # Aqui o relacionamento e acessado.
            livros = autor.books

            titulos = sorted(
                livro.title for livro in livros
            )

            consultas_depois = len(consultas)

            livros_carregados = (
                "books" not in inspect(autor).unloaded
            )

            books_no_dict_depois = (
                "books" in autor.__dict__
            )

            # Acesso repetido reutiliza a colecao carregada.
            livros_novamente = autor.books
            consultas_apos_repeticao = len(consultas)

            return {
                "autor": autor.name,
                "livros": titulos,
                "quantidade_livros": len(livros),
                "books_nao_carregados_antes":
                    livros_nao_carregados,
                "books_no_dict_antes":
                    books_no_dict_antes,
                "books_carregados_depois":
                    livros_carregados,
                "books_no_dict_depois":
                    books_no_dict_depois,
                "consultas_antes_acesso":
                    consultas_antes,
                "consultas_depois_acesso":
                    consultas_depois,
                "consultas_apos_repeticao":
                    consultas_apos_repeticao,
                "consulta_extra_ao_acessar_books":
                    consultas_depois - consultas_antes,
                "mesma_colecao_reutilizada":
                    livros is livros_novamente,
                "sql_executado": list(consultas),
                "banco": "SQLite em memoria",
            }

    finally:
        engine.dispose()
