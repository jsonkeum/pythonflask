import traceback

from flask import request, make_response, render_template
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

from libs.mailgun import MailGunException
from schemas.user import UserSchema
from models.user import UserModel
from blacklist import BLACKLIST

ACTIVATION_SUCCESSFUL = "User successfully activated!"
ERROR_UPDATING_USER = "Error updating user."
LOGGED_OUT = "Successfully logged out."
CHECK_YOUR_EMAIL = "You have not confirmed registration. Please check your email <{}>"
INVALID_CREDENTIALS = "Invalid credentials"
USER_DELETED = "User deleted."
USER_NOT_FOUND = "User not found."
USERNAME_EXISTS = "A user with that username already exists."
EMAIL_EXISTS = "A user with that email already exists."
FAILED_TO_CREATE = "Internal server error. Failed to create user."
SUCCESS_REGISTER_MESSAGE = (
    "Account created successfully, an email with an activation link has been sent to your "
    "email address, please check. "
)

user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        json = request.get_json()
        # user_schema creates a UserModel object with attribute values being request variables
        user = user_schema.load(json)

        if UserModel.find_by_username(user.username):
            return {"message": USERNAME_EXISTS}, 400

        if UserModel.find_by_email(user.email):
            return {"message": EMAIL_EXISTS}, 400

        try:
            user.save_to_db()
            user.send_confirmation_email()
            return {"message": SUCCESS_REGISTER_MESSAGE}, 201
        except MailGunException as e:
            user.delete_from_db()
            return {"message": str(e)}, 500
        except:
            traceback.print_exc()
            return {"message": FAILED_TO_CREATE}


class User(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        return user_schema.dump(user)

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        user.delete_from_db()
        return {"message": USER_DELETED}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        json = request.get_json()
        # partial lets marshmallow ignore email field for logging in
        user_data = user_schema.load(json, partial=("email",))

        # find user in db
        user = UserModel.find_by_username(user_data.username)

        # check password
        if user and safe_str_cmp(user.password, user_data.password):
            if user.activated:
                # create access token
                access_token = create_access_token(identity=user.id, fresh=True)

                # create refresh token
                refresh_token = create_refresh_token(user.id)

                # return
                return (
                    {"access_token": access_token, "refresh_token": refresh_token},
                    200,
                )
            return ({"message": CHECK_YOUR_EMAIL.format(user.username)}, 400)

        return {"message": INVALID_CREDENTIALS}, 401


class UserLogout(Resource):

    # basically blacklisting the old access token so that the user has to
    # login again and get a new token
    @classmethod
    @jwt_required
    def post(cls):
        jti = get_raw_jwt()["jti"]  # jti is a JWT ID, a unique identifier for a JWT
        BLACKLIST.add(jti)
        return {"message": LOGGED_OUT}, 200


class TokenRefresh(Resource):
    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        # accepts refresh token, gets user id based on that token, then generates new
        # access token but one that is not fresh
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200


class UserConfirm(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if user:
            user.activated = True
            try:
                user.save_to_db()
            except:
                return {"message": ERROR_UPDATING_USER}, 500
            # location of the template is assumed to be in the templates folder next to app.py
            headers = {"Content-Type": "text/html"}
            return make_response(
                render_template("confirmation_page.html", email=user.username),
                200,
                headers,
            )
        return {"message": USER_NOT_FOUND}, 404
