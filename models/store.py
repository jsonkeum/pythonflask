from typing import List
from db import db


class StoreModel(db.Model):
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    # SQLAlchemy looks at ItemModel to see if there is a relationship
    # in this case stores.id and returns all the item objects in
    # that relationship
    # lazy='dynamic' means that self.items is not a list of
    # Item objects but a query builder e.g. self.items.all()
    # trade off between load now once or load later multi times
    items = db.relationship("ItemModel", lazy="dynamic")

    @classmethod
    def find_by_name(cls, name: str) -> "StoreModel":
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_all(cls) -> List["StoreModel"]:
        return cls.query.all()

    # previously insert
    def save_to_db(self) -> None:
        # SQLAlchemy handles both updates and inserts
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
