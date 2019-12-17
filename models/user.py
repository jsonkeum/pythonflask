from typing import Dict, Union

from db import db

UserJSON = Dict[str, Union[int, str]]


class UserModel(db.Model):
    # db.Model is sql alchemy

    # need to declare table and columns
    # of the table that this object is related to
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(80))
    
    # the id field of the model is auto generated as primary key
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
    
    def json(self) -> UserJSON:
        return {
            'id': self.id,
            'username': self.username
        }
    
    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
    
    @classmethod
    def find_by_username(cls, username: str) -> "UserModel":
        # SQLAlchemy converts results into the model object
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def find_by_id(cls, _id: int) -> "UserModel":
        return cls.query.filter_by(id=_id).first()