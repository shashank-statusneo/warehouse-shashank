import settings

from datetime import timedelta
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS


# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
app = Flask(__name__)
jwt = JWTManager()


@app.route('/', methods=['GET'])
def server_status():
    return jsonify({"message": "server is up"}), 200


def get_app(config):
    app.config.update(config)
    app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=settings.TOKEN_EXPIRE_IN)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(minutes=settings.TOKEN_EXPIRE_IN)
    CORS(app)
    db.init_app(app)
    jwt.init_app(app)

    # blueprint for warehouse routes
    from project.routers.warehouse import warehouse
    app.register_blueprint(warehouse)

    # blueprint for warehouse routes
    from project.routers.auth import auth_router
    app.register_blueprint(auth_router)

    return app
