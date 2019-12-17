from typing import Dict, List, Union

from db import db

ItemJSON = Dict[str, Union[int, str, float]]


class ItemModel(db.Model):
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    price = db.Column(db.Float(precision=2))
    
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))

    def __init__(self, name: str, price: float, store_id: int):
        self.name = name
        self.price = price
        self.store_id = store_id

    def json(self) -> ItemJSON:
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'store_id': self.store_id
        }

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