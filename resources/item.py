from flask_restful import Resource, reqparse
from flask_jwt_extended import fresh_jwt_required, jwt_required

from models.item import ItemModel


class Item(Resource):
    # This is just a useful request body parsing library
    parser = reqparse.RequestParser()
    # only arguments listed below will survive the parsing using reqparse;
    # rest get removed
    parser.add_argument(
        "price", type=float, required=True, help="This field cannot be left blank!"
    )
    parser.add_argument(
        "store_id", type=int, required=True, help="Every item needs a store id."
    )

    # name here is a keyword argument that is tied to the query param
    # described in app.py [ api.add_resource(Item, '/item/<string:name>') ]
    def get(self, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {"message": "Item not found"}, 404

    @fresh_jwt_required
    def post(self, name: str):
        if ItemModel.find_by_name(name):
            return (
                {"message": 'An item with the name "{}" already exists.'.format(name)},
                400,
            )

        request_data = Item.parser.parse_args()
        item = ItemModel(name, **request_data)
        item.save_to_db()

        return item.json(), 201

    @jwt_required
    def delete(self, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": "Item deleted"}, 200
        return {"message": "Item not found"}, 404

    @jwt_required
    def put(self, name: str):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(name, **data)
        else:
            item.price = data["price"]

        item.save_to_db()

        return item.json()


class ItemList(Resource):
    def get(self):
        return {"items": [item.json() for item in ItemModel.find_all()]}, 200
