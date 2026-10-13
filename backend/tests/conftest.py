import pytest
from app import create_app
from app.extensions import db
from app.models.user import User
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(
            email="test@example.com",
            name="Alex Runner",
            age=28,
            gender="male",
            height_cm=180.0,
            current_weight_kg=75.0,
            target_weight_kg=72.0,
            activity_level="moderate",
        )
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        # Reload user id
        user_id = user.id
    return user_id

@pytest.fixture
def auth_headers(app, test_user):
    with app.app_context():
        token = create_access_token(identity=str(test_user))
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
