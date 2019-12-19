from flask import request
from flask_restful import Resource
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    jwt_refresh_token_required,
    get_raw_jwt,
)
from schemas.user import UserSchema
from models.user import UserModel
from blacklist import BLACKLIST

user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        json = request.get_json()
        # user_schema creates a UserModel object with attribute values being request variables
        user = user_schema.load(json)

        if UserModel.find_by_username(user.username):
            return {"message": "A user with that username already exists."}, 400

        user.save_to_db()

        return {"message": "User created successfully."}, 201


class User(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User not found."}, 404
        return user_schema.dump(user)

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User not found."}, 404
        user.delete_from_db()
        return {"message": "User deleted."}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        json = request.get_json()
        user_data = user_schema.load(json)

        # find user in db
        user = UserModel.find_by_username(user_data.username)

        # check password
        if user and safe_str_cmp(user.password, user_data.password):
            # create access token
            access_token = create_access_token(identity=user.id, fresh=True)

            # create refresh token
            refresh_token = create_refresh_token(user.id)

            # return
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        return {"message": "Invalid credentials"}, 401


class UserLogout(Resource):

    # basically blacklisting the old access token so that the user has to
    # login again and get a new token
    @classmethod
    @jwt_required
    def post(cls):
        jti = get_raw_jwt()["jti"]  # jti is a JWT ID, a unique identifier for a JWT
        BLACKLIST.add(jti)
        return {"message": "Successfully logged out."}, 200


class TokenRefresh(Resource):
    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        # accepts refresh token, gets user id based on that token, then generates new
        # access token but one that is not fresh
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
