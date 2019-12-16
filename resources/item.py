from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    fresh_jwt_required,
    jwt_required,
    jwt_optional,
    get_jwt_claims,
    get_jwt_identity
)

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
    
    
    @jwt_required
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {'message': 'Item not found'}, 404


    @fresh_jwt_required
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': 'An item with the name "{}" already exists.'.format(name)}, 400
        
        request_data = Item.parser.parse_args()
        item = ItemModel(name, **request_data)
        item.save_to_db()

        return item.json(), 201
    
    
    @jwt_required
    def delete(self, name):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
        
        return {'message': 'Item deleted'}, 200
    
    
    @jwt_required
    def put(self, name):
        data = Item.parser.parse_args()
        
        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(name, **data)
        else:
            item.price = data['price']
        
        item.save_to_db()
        
        return item.json()

class ItemList(Resource):
    @jwt_optional
    def get(self):
        # gives whatever we saved in the access token as the identity
        # access_token = create_access_token(identity=user.id, fresh=True)
        user_id = get_jwt_identity()
        if user_id:
            return {'items': [item.json() for item in ItemModel.query.all()]}, 200
        return {
            'items': [item.json()['name'] for item in ItemModel.query.all()],
            'message': 'Login to view more info.'
        }, 200
        