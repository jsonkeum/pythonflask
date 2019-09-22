from flask import Flask
from flask_restful import Api
from flask_jwt import JWT

from datetime import timedelta
import os

# security.py we created. We are importing the handlers here for JWT
from security import authenticate, identity
from resources.user import UserRegister
from resources.item import Item, ItemList
from resources.store import Store, StoreList


app = Flask(__name__)
app.secret_key = 'jose'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# by default '/auth'
app.config['JWT_AUTH_URL_RULE'] = '/login'

# by default 5 minutes
app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=1800)

# by default 'username'
app.config['JWT_AUTH_USERNAME_KEY'] = 'username'


api = Api(app)


jwt = JWT(app, authenticate, identity)  # creates new end point /auth

@jwt.auth_response_handler
def customized_response_handler(access_token, identity):
    return {
        'access_token': access_token.decode('utf-8'),
        'user_id': identity.id,
        'username': identity.username
    }

@jwt.jwt_error_handler
def customized_error_handler(error):
    return {
        'message': error.description,
        'code': error.status_code,
    }, error.status_code

api.add_resource(Item, '/item/<string:name>')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(StoreList, '/stores')
api.add_resource(UserRegister, '/register')

# python assings this name if you run it as entry point into the program
if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)