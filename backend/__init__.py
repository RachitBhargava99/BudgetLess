from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_bcrypt import Bcrypt
##from flask_login import LoginManager
from flask_mail import Mail
from backend.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
##login_manager = LoginManager()
##login_manager.login_view = 'login'
##login_manager.login_message_category = 'info'
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
##    login_manager.init_app(app)
    mail.init_app(app)

    from backend.payments.routes import payments
    from backend.users.routes import users
    from backend.stats.routes import stats
    app.register_blueprint(payments)
    app.register_blueprint(users)
    app.register_blueprint(stats)

    db.create_all(app=app)

    return app
