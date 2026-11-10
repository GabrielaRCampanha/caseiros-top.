
from decimal import Decimal, InvalidOperation

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import (
    Produto,
    Pedido,
    ItemPedido,
    Ingrediente,
    MovimentacaoEstoque,
    MovimentacaoFinanceira
)

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("index.html")


@main.route("/produtos", methods=["GET", "POST"])
def produtos():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        categoria = request.form.get("categoria", "").strip()
        preco_texto = request.form.get("preco", "").replace(",", ".")

        if not nome or not categoria or not preco_texto:
            flash("Preencha todos os campos.")
            return redirect(url_for("main.produtos"))

        try:
            preco = Decimal(preco_texto)

            if not preco.is_finite() or preco <= 0:
                raise ValueError

        except (ValueError, InvalidOperation):
            flash("Informe um preço válido e maior que zero.")
            return redirect(url_for("main.produtos"))

        novo_produto = Produto(
            nome=nome,
            categoria=categoria,
            preco=preco
        )

        db.session.add(novo_produto)
        db.session.commit()

        flash("Produto cadastrado com sucesso!")
        return redirect(url_for("main.produtos"))

    lista_produtos = Produto.query.order_by(Produto.nome).all()

    return render_template(
        "produtos.html",
        produtos=lista_produtos
    )


@main.route("/pedidos", methods=["GET", "POST"])
def pedidos():
    if request.method == "POST":
        nome_cliente = request.form.get("nome_cliente", "").strip()
        produto_id = request.form.get("produto_id")
        quantidade_texto = request.form.get("quantidade", "")

        try:
            produto = db.session.get(Produto, int(produto_id))
            quantidade = int(quantidade_texto)

            if produto is None or quantidade <= 0:
                raise ValueError

        except (ValueError, TypeError):
            flash("Selecione um produto e informe uma quantidade válida.")
            return redirect(url_for("main.pedidos"))

        novo_pedido = Pedido(
            nome_cliente=nome_cliente or None
        )

        db.session.add(novo_pedido)
        db.session.flush()

        item = ItemPedido(
            pedido_id=novo_pedido.id,
            produto_id=produto.id,
            quantidade=quantidade,
            preco_unitario=produto.preco
        )

        db.session.add(item)
        db.session.commit()

        flash("Pedido cadastrado com sucesso!")
        return redirect(url_for("main.pedidos"))

    lista_produtos = Produto.query.order_by(Produto.nome).all()

    return render_template(
        "pedidos.html",
        produtos=lista_produtos
    )


@main.route("/consultar-pedidos")
def consultar_pedidos():
    lista_pedidos = Pedido.query.order_by(
        Pedido.data_criacao.desc()
    ).all()

    return render_template(
        "consultar_pedidos.html",
        pedidos=lista_pedidos
    )


@main.route("/atualizar-status/<int:pedido_id>", methods=["POST"])
def atualizar_status(pedido_id):
    pedido = db.session.get(Pedido, pedido_id)

    if pedido is None:
        flash("Pedido não encontrado.")
        return redirect(url_for("main.consultar_pedidos"))

    novo_status = request.form.get("status")

    status_permitidos = [
        "Recebido",
        "Em preparação",
        "Pronto",
        "Entregue"
    ]

    if novo_status not in status_permitidos:
        flash("Status inválido.")
        return redirect(url_for("main.consultar_pedidos"))

    pedido.status = novo_status
    db.session.commit()

    flash("Status do pedido atualizado com sucesso!")

    return redirect(url_for("main.consultar_pedidos"))


@main.route("/estoque")
def estoque():
    lista_ingredientes = Ingrediente.query.order_by(
        Ingrediente.nome
    ).all()

    lista_movimentacoes = MovimentacaoEstoque.query.order_by(
        MovimentacaoEstoque.data_criacao.desc()
    ).all()

    return render_template(
        "estoque.html",
        ingredientes=lista_ingredientes,
        movimentacoes=lista_movimentacoes
    )


@main.route("/cadastrar-ingrediente", methods=["POST"])
def cadastrar_ingrediente():
    nome = request.form.get("nome", "").strip()
    unidade_medida = request.form.get("unidade_medida", "").strip()

    if not nome or not unidade_medida:
        flash("Preencha o nome e a unidade de medida.")
        return redirect(url_for("main.estoque"))

    novo_ingrediente = Ingrediente(
        nome=nome,
        unidade_medida=unidade_medida,
        estoque_atual=Decimal("0")
    )

    db.session.add(novo_ingrediente)
    db.session.commit()

    flash("Ingrediente cadastrado com sucesso!")
    return redirect(url_for("main.estoque"))


@main.route("/movimentar-estoque", methods=["POST"])
def movimentar_estoque():
    ingrediente_id = request.form.get("ingrediente_id")
    tipo = request.form.get("tipo")
    quantidade_texto = request.form.get("quantidade", "").replace(",", ".")
    descricao = request.form.get("descricao", "").strip()

    try:
        ingrediente = db.session.get(
            Ingrediente,
            int(ingrediente_id)
        )

        quantidade = Decimal(quantidade_texto)

        if (
            ingrediente is None
            or not quantidade.is_finite()
            or quantidade <= 0
            or tipo not in ["Entrada", "Saída"]
        ):
            raise ValueError

    except (ValueError, TypeError, InvalidOperation):
        flash("Confira o ingrediente, o tipo e a quantidade informada.")
        return redirect(url_for("main.estoque"))

    if tipo == "Saída" and quantidade > ingrediente.estoque_atual:
        flash("Não há estoque suficiente para essa saída.")
        return redirect(url_for("main.estoque"))

    if tipo == "Entrada":
        ingrediente.estoque_atual += quantidade
    else:
        ingrediente.estoque_atual -= quantidade

    movimentacao = MovimentacaoEstoque(
        ingrediente_id=ingrediente.id,
        tipo=tipo,
        quantidade=quantidade,
        descricao=descricao or None
    )

    db.session.add(movimentacao)
    db.session.commit()

    flash("Movimentação de estoque registrada com sucesso!")
    return redirect(url_for("main.estoque"))


@main.route("/financeiro")
def financeiro():
    movimentacoes = MovimentacaoFinanceira.query.order_by(
        MovimentacaoFinanceira.data_criacao.desc()
    ).all()

    entradas = sum(
        (m.valor for m in movimentacoes if m.tipo == "Entrada"),
        Decimal("0.00")
    )

    saidas = sum(
        (m.valor for m in movimentacoes if m.tipo == "Saída"),
        Decimal("0.00")
    )

    saldo = entradas - saidas

    return render_template(
        "financeiro.html",
        movimentacoes=movimentacoes,
        entradas=entradas,
        saidas=saidas,
        saldo=saldo
    )


@main.route("/cadastrar-movimentacao-financeira", methods=["POST"])
def cadastrar_movimentacao_financeira():
    tipo = request.form.get("tipo")
    descricao = request.form.get("descricao", "").strip()
    valor_texto = request.form.get("valor", "").replace(",", ".")

    if tipo not in ["Entrada", "Saída"] or not descricao or not valor_texto:
        flash("Preencha todos os campos corretamente.")
        return redirect(url_for("main.financeiro"))

    try:
        valor = Decimal(valor_texto)

        if not valor.is_finite() or valor <= 0:
            raise ValueError

    except (ValueError, InvalidOperation):
        flash("Informe um valor válido e maior que zero.")
        return redirect(url_for("main.financeiro"))

    movimentacao = MovimentacaoFinanceira(
        tipo=tipo,
        descricao=descricao,
        valor=valor
    )

    db.session.add(movimentacao)
    db.session.commit()

    flash("Movimentação financeira registrada com sucesso!")
    return redirect(url_for("main.financeiro"))
