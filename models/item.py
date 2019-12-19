from typing import List
from db import db


class ItemModel(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)

    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), nullable=False)
    store = db.relationship("StoreModel")

    @classmethod
    def find_by_name(cls, name: str) -> "ItemModel":
        """
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        
        query = 'SELECT * FROM items WHERE name=?'
        
        result = cursor.execute(query, (name,))
        row = result.fetchone()
        connection.close()
        
        if row:
            # cls instantiates
            return cls(*row)
        """
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_all(cls) -> List["ItemModel"]:
        return cls.query.all()

    # previously insert
    def save_to_db(self) -> None:
        """
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        
        query = 'INSERT INTO items VALUES (?, ?)'
        cursor.execute(query, (self.name, self.price,))
        
        connection.commit()
        connection.close()
        """
        # SQLAlchemy handles both updates and inserts
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
