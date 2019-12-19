from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from marshmallow import ValidationError
import os

from blacklist import BLACKLIST
from resources.user import UserRegister, User, UserLogin, UserLogout, TokenRefresh
from resources.item import Item, ItemList
from resources.store import Store, StoreList

app = Flask(__name__)
app.secret_key = "jose"  # aka app.config['JWT_SECRET_KEY']

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# allow libraries to raise their own exceptions
app.config["PROPAGATE_EXCEPTIONS"] = True

app.config["JWT_BLACKLIST_ENABLED"] = True

app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access", "refresh"]


api = Api(app)


# Flask can set app level error handlers
@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify(err.messages), 400


jwt = JWTManager(app)  # doesn't create /auth endpoint


# if True, throws the revoked token stuff
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token["jti"] in BLACKLIST


api.add_resource(Item, "/item/<string:name>")
api.add_resource(Store, "/store/<string:name>")
api.add_resource(ItemList, "/items")
api.add_resource(StoreList, "/stores")
api.add_resource(UserRegister, "/register")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(TokenRefresh, "/refresh")

# python assigns this name if you run it as entry point into the program
if __name__ == "__main__":
    from configparser import ConfigParser
    from db import db
    from ma import ma

    parser = ConfigParser()
    parser.read("database.ini")

    if parser.has_section("postgresql_settings"):
        params = parser.items("postgresql_settings")
        db_config = {param[0]: param[1] for param in params}
        database_uri = "postgres+psycopg2://{user}:{password}@{host}:{port}/{database}".format(
            **db_config
        )
        app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    else:
        raise Exception("DB Settings not found!!!!")

    db.init_app(app)
    ma.init_app(app)
    app.run(port=5000, debug=True)
