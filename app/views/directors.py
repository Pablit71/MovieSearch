from flask import request
from flask_restx import Resource, Namespace

from app.models import DirectorSchema, Director
from app.database import db, admin_required, admin_auth

directors_ns = Namespace('directors')

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)


@directors_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        all_directors = Director.query.all()
        return directors_schema.dump(all_directors), 200


@directors_ns.route('/<int:did>')
class DirectorView(Resource):
    def get(self, did):
        try:
            director = db.session.query(Director).filter(Director.id == did).one()
            return director_schema.dump(director), 200
        except Exception as e:
            return str(e), 404

    def post(self):
        req_json = request.json
        new_directors = Director(**req_json)
        with db.session.begin():
            db.session.add(new_directors)
        return "", 201

    def put(self, did):
        director = db.session.query(Director).get(did)
        req_json = request.json
        director.id = req_json.get("id")
        director.name = req_json.get("name")

        db.session.add(director)
        db.session.commit()

        return "", 204

    def delete(self, mid):
        user = Director.query.get(mid)
        db.session.delete(user)
        db.session.commit()

        return "", 204
