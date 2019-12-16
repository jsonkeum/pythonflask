from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
import psycopg2

from datetime import timedelta
# from configparser import ConfigParser
import os

from blacklist import BLACKLIST
from resources.user import (
    UserRegister,
    User,
    UserLogin,
    UserLogout,
    TokenRefresh
)
from resources.item import Item, ItemList
from resources.store import Store, StoreList

app = Flask(__name__)
app.secret_key = 'jose' # aka app.config['JWT_SECRET_KEY']
"""
parser = ConfigParser()
parser.read('database.ini')

if parser.has_section('postgresql_settings'):
    params = parser.items('postgresql_settings')
    db_config = {param[0]: param[1] for param in params}
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres+psycopg2://{user}:{password}@{host}:{port}/{database}'.format(**db_config)
else:
    raise Exception('DB Settings not found!!!!')
"""
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# allow libraries to raise their own exceptions
app.config['PROPAGATE_EXCEPTIONS'] = True

app.config['JWT_BLACKLIST_ENABLED'] = True

app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']


api = Api(app)


jwt = JWTManager(app)  # doesn't create /auth endpoint

# claims is like setting some extra data about the user based on id
@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1: # 1 is just a magic number here
        return {'is_admin': True}
    return {'is_admin': False}

# if True, throws the revoked token stuff
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token['jti'] in BLACKLIST


# customize what message to send back to user when token's expired
@jwt.expired_token_loader
def expired_token_callback():
    return {
        'description': 'The token has expired.',
        'error': 'token_expired'
    }, 401

# customize what message to send back to user when token's invalid
@jwt.invalid_token_loader
def invalid_token_callback(error):
    return {
        'description': 'Signature verification failed.',
        'error': 'invalid_token'
    }, 401

# customize what message to send back to user when token's unauthorized
@jwt.unauthorized_loader
def unauthorized_token_callback():
    return {
        'description': 'Unauthorized signature.',
        'error': 'unauthorized_token'
    }, 401

# customize what message to send back to user when token's stale
@jwt.needs_fresh_token_loader
def needs_fresh_token_callback():
    return {
        'description': 'Operation requires a sign in.',
        'error': 'fresh_token'
    }, 401

# customize what message to send back to user when token's revoked
@jwt.revoked_token_loader
def revoked_token_callback():
    return {
        'description': 'The token has been revoked.',
        'error': 'token_revoked'
    }, 401

api.add_resource(Item, '/item/<string:name>')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(StoreList, '/stores')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(TokenRefresh, '/refresh')

# python assings this name if you run it as entry point into the program
if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)