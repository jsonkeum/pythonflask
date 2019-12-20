import traceback
from time import time

from flask import make_response, render_template
from flask_restful import Resource

from libs.mailgun import MailGunException
from models.confirmation import ConfirmationModel
from models.user import UserModel
from schemas.confirmation import ConfirmationSchema

RESEND_FAILED_ = "Resend failed."

RESEND_SUCCESSFUL = "Resend successful"

ALREADY_CONFIRMED_ = "Already confirmed."

USER_NOT_FOUND_ = "User not found."

CONFIRMED = "Registration has already been confirmed."
EXPIRED = "The link has expired."
NOT_FOUND = "Confirmation reference not found."

confirmation_schema = ConfirmationSchema()


class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        # Return confirmation HTML page
        confirmation = ConfirmationModel.find_by_id(confirmation_id)

        if not confirmation:
            return {"message": NOT_FOUND}, 404

        if confirmation.expired:
            return {"message": EXPIRED}, 400

        if confirmation.confirmed:
            return {"message": CONFIRMED}, 400

        confirmation.confirmed = True
        confirmation.save_to_db()

        headers = {"Content-Type": "text/html"}
        return make_response(
            render_template("confirmation_page.html", email=confirmation.user.email),
            200,
            headers,
        )


class ConfirmationByUser(Resource):
    @classmethod
    def get(self, user_id: int):
        # Returns confirmation for a given user. User for testing.
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND_}, 404

        return (
            {
                "current_time": int(time()),
                "confirmation": [
                    confirmation_schema.dump(each)
                    for each in user.confirmation.order_by(ConfirmationModel.expire_at)
                ],
            },
            200,
        )

    @classmethod
    def post(self, user_id: int):
        # Resend confirmation email
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND_}, 404

        try:
            confirmation = user.most_recent_confirmation
            if confirmation:
                if confirmation.confirmed:
                    return {"message": ALREADY_CONFIRMED_}, 400
                confirmation.force_to_expire()

            # create new confirmation object and send email
            new_confirmation = ConfirmationModel(user_id)
            new_confirmation.save_to_db()

            user.send_confirmation_email()
            return {"message": RESEND_SUCCESSFUL}, 201
        except MailGunException as e:
            return {"message": str(e)}, 500
        except:
            traceback.print_exc()
            return {"message": RESEND_FAILED_}, 500
