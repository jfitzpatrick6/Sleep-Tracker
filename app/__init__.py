from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sleep.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from . import routes
    app.register_blueprint(routes.bp)

    with app.app_context():
        db.create_all()

    return app