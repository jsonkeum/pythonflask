from flask_restful import Resource, reqparse
from flask_jwt import jwt_required, current_identity

from models.item import ItemModel

class Item(Resource):
    # This is just a useful request body parsing library
    parser = reqparse.RequestParser()
    # only arguments listed below will survive the parsing using reqparse;
    # rest get removed
    parser.add_argument(
        'price',
        type=float,
        required=True,
        help='This field cannot be left blank!'
    )
    parser.add_argument(
        'store_id',
        type=int,
        required=True,
        help='Every item needs a store id.'
    )
    
    
    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {'message': 'Item not found'}, 404


    @jwt_required()
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': 'An item with the name "{}" already exists.'.format(name)}, 400
        
        request_data = Item.parser.parse_args()
        item = ItemModel(name, request_data['price'], request_data['store_id'])
        item.save_to_db()

        return item.json(), 201
    
    
    @jwt_required()
    def delete(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
        
        return {'message': 'Item deleted'}, 200
    
    
    @jwt_required()
    def put(self, name):
        data = Item.parser.parse_args()
        
        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(name, data['price'], data['store_id'])
        else:
            item.price = data['price']
        
        item.save_to_db()
        
        return item.json()

class ItemList(Resource):
    @jwt_required()
    def get(self):
        """
        print(current_identity.username)
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        
        query = 'SELECT * FROM items'
        result = cursor.execute(query).fetchall()
        
        items = [{ 'name': row[0], 'price': row[1]} for row in result]
        
        connection.close()
        
        return items
        """
        return {'items': [item.json() for item in ItemModel.query.all()]}
        