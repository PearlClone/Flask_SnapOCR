import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_login import LoginManager

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    app.config['SECRET_KEY'] = 'thisisasecretkeyformyappflask'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
    #postgres://snapocr_postgres_user:Q6Dc6Hi9A1VtxUJajrxsOwHybVMQwYtA@dpg-chlqjre7avj2178s81cg-a.frankfurt-postgres.render.com/snapocr_postgres

    app.config['UPLOADED_PHOTOS_DEST'] = 'uploads'
    photos = UploadSet('photos', IMAGES)
    configure_uploads(app, photos)

    db.init_app(app)

    from . import models

    with app.app_context():
        db.create_all()
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app



