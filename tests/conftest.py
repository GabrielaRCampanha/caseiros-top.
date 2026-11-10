
import pytest

from app import create_app, db


@pytest.fixture
def app(tmp_path):
    test_database = tmp_path / "test_caseiros_top.db"

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{test_database}"
    })

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
