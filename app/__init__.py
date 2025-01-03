from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session

# Inisialisasi database dan migrasi
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Konfigurasi aplikasi
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:8889/flask_user_hub'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SESSION_TYPE'] = 'filesystem'

    # Inisialisasi database dan session
    db.init_app(app)
    migrate.init_app(app, db)
    Session(app)

    # Registrasi blueprint
    from app.routes import main
    app.register_blueprint(main)

    return app
