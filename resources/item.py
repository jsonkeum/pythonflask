from flask_restful import Resource, reqparse
from flask_jwt_extended import fresh_jwt_required, jwt_required

from models.item import ItemModel

BLANK_ERROR = "'{}' cannot be left blank!"
ITEM_NOT_FOUND = "Item not found."
ITEM_DELETED = "Item deleted."
ITEM_ALREADY_EXISTS = "An item with the name '{}' already exists."


class Item(Resource):
    # This is just a useful request body parsing library
    parser = reqparse.RequestParser()
    # only arguments listed below will survive the parsing using reqparse;
    # rest get removed
    parser.add_argument(
        "price", type=float, required=True, help=BLANK_ERROR.format("price")
    )
    parser.add_argument(
        "store_id", type=int, required=True, help=BLANK_ERROR.format("store_id")
    )

    # name here is a keyword argument that is tied to the query param
    # described in app.py [ api.add_resource(Item, '/item/<string:name>') ]
    @classmethod
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {"message": ITEM_NOT_FOUND}, 404

    @classmethod
    @fresh_jwt_required
    def post(cls, name: str):
        if ItemModel.find_by_name(name):
            return (
                {"message": ITEM_ALREADY_EXISTS.format(name)},
                400,
            )

        request_data = Item.parser.parse_args()
        item = ItemModel(name, **request_data)
        item.save_to_db()

        return item.json(), 201

    @classmethod
    @jwt_required
    def delete(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": ITEM_DELETED}, 200
        return {"message": ITEM_NOT_FOUND}, 404

    @classmethod
    @jwt_required
    def put(cls, name: str):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(name, **data)
        else:
            item.price = data["price"]

        item.save_to_db()

        return item.json()


class ItemList(Resource):
    @classmethod
    def get(cls):
        return {"items": [item.json() for item in ItemModel.find_all()]}, 200
