
from app import db


class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    preco = db.Column(db.Numeric(10, 2), nullable=False)

    def __repr__(self):
        return f"<Produto {self.nome}>"


class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_cliente = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(30), nullable=False, default="Recebido")
    data_criacao = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp()
    )

    itens = db.relationship(
        "ItemPedido",
        backref="pedido",
        cascade="all, delete-orphan"
    )


class ItemPedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(
        db.Integer,
        db.ForeignKey("pedido.id"),
        nullable=False
    )
    produto_id = db.Column(
        db.Integer,
        db.ForeignKey("produto.id"),
        nullable=False
    )
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)

    produto = db.relationship(
        "Produto",
        backref="itens_pedido"
    )


class Ingrediente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    unidade_medida = db.Column(db.String(20), nullable=False)
    estoque_atual = db.Column(
        db.Numeric(10, 3),
        nullable=False,
        default=0
    )

    movimentacoes = db.relationship(
        "MovimentacaoEstoque",
        backref="ingrediente",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Ingrediente {self.nome}>"


class MovimentacaoEstoque(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ingrediente_id = db.Column(
        db.Integer,
        db.ForeignKey("ingrediente.id"),
        nullable=False
    )
    tipo = db.Column(db.String(20), nullable=False)
    quantidade = db.Column(db.Numeric(10, 3), nullable=False)
    descricao = db.Column(db.String(200), nullable=True)
    data_criacao = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp()
    )


class MovimentacaoFinanceira(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    data_criacao = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp()
    )
