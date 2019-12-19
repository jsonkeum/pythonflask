from flask_restful import Resource
from flask_jwt_extended import jwt_required
from schemas.store import StoreSchema
from models.store import StoreModel

store_schema = StoreSchema()
store_list_schema = StoreSchema(many=True)


class Store(Resource):
    @classmethod
    @jwt_required
    def get(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return store_schema.dump(store)
        return {"message": "Store not found."}, 404

    @classmethod
    @jwt_required
    def post(cls, name: str):
        if StoreModel.find_by_name(name):
            return (
                {"message": 'A store with name "{}" already exists.'.format(name)},
                400,
            )

        store = StoreModel(name=name)
        try:
            store.save_to_db()
        except:
            return {"message": "An error occurred while creating the store."}, 500

        return store_schema.dump(store), 201

    @classmethod
    @jwt_required
    def delete(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()

        return {"message": "Store deleted"}


class StoreList(Resource):
    @classmethod
    @jwt_required
    def get(cls):
        return {"stores": store_list_schema.dump(StoreModel.find_all())}
