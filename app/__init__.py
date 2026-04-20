from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from pathlib import Path

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

from .models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-key-change-this-in-production'  # Change this!
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sleep.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)

    # Import blueprints
    from . import routes, auth
    app.register_blueprint(routes.bp)
    app.register_blueprint(auth.bp)

    with app.app_context():
        db.create_all()

    return app