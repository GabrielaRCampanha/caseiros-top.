
def test_pagina_inicial(client):
    resposta = client.get("/")
    assert resposta.status_code == 200


def test_pagina_produtos(client):
    resposta = client.get("/produtos")
    assert resposta.status_code == 200


def test_pagina_pedidos(client):
    resposta = client.get("/pedidos")
    assert resposta.status_code == 200


def test_consultar_pedidos(client):
    resposta = client.get("/consultar-pedidos")
    assert resposta.status_code == 200


def test_pagina_estoque(client):
    resposta = client.get("/estoque")
    assert resposta.status_code == 200


def test_pagina_financeiro(client):
    resposta = client.get("/financeiro")
    assert resposta.status_code == 200
