
from flask import Blueprint

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return """
    <h1>Caseiros Top</h1>
    <p>Sistema de Gestão e Organização da Pastelaria</p>
    <p>Bem-vindo ao sistema!</p>
    """
