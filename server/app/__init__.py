# from flask import Flask 
# from flask_sqlalchemy import SQLAlchemy
# from flask_marshmallow import Marshmallow
# from .config import Config
# from flask_migrate import Migrate 

# db = SQLAlchemy()
# ma = Marshmallow()
# migrate = Migrate()

# def create_app(config_class=Config):
#     app = Flask(__name__)
#     app.config.from_object(config_class)

#     db.init_app(app)
#     ma.init_app(app)
#     migrate.init_app(app, db)

#     from .routes import api_bp
#     app.register_blueprint(api_bp, url_prefix='/api')

#     # with app.app_context():
#     #     from app.services.sms_service import reminder
#     #     reminder()
    

#     from .tasks import start_reminder_service
#     start_reminder_service()

#     return app




import threading
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate

db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()

# 🔒 Verrou global pour éviter plusieurs exécutions
reminder_lock = threading.Lock()
reminder_thread = None  # Stocke le thread globalement

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)

    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    # 🔄 Vérifie et lance un seul thread pour `reminder()`
    global reminder_thread  # Permet d’accéder à la variable globale
    with reminder_lock:
        if reminder_thread is None or not reminder_thread.is_alive():
            from app.services.sms_service import reminder
            reminder_thread = threading.Thread(target=reminder, daemon=True)
            reminder_thread.start()
            print("✅ Thread reminder démarré.")

    return app
