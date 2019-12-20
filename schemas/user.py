from marshmallow import pre_dump

from ma import ma
from models.user import UserModel


class UserSchema(ma.ModelSchema):
    class Meta:

        # gets column definition from UserModel class and creates marshmallow fields based on that.
        model = UserModel
        # need the comma to make these a tuple
        load_only = ("password",)
        dump_only = ("id", "confirmation")

        @pre_dump
        def _pre_dump(self, user: UserModel):
            user.confirmation = [user.most_recent_confirmation]
            return user
