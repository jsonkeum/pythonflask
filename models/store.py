from db import db

class StoreModel(db.Model):
    __tablename__ = 'stores'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    
    # SQLAlchemy looks at ItemModel to see if there is a relationship
    # in this case stores.id and returns all the item objects in 
    # that relationship
    # lazy='dynamic' means that self.items is not a list of
    # Item objects but a query builder e.g. self.items.all()
    # trade off between load now once or load later multi times
    items = db.relationship('ItemModel', lazy='dynamic')
    
    def __init__(self, name):
        self.name = name

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'items': [item.json() for item in self.items.all()]
        }
    
    
    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    #previously insert
    def save_to_db(self):
        # SQLAlchemy handles both updates and inserts
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()