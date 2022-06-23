from flask import request
from flask_restx import Resource, Namespace

from app.models import GenreSchema, Genre
from app.database import db

genres_ns = Namespace('genres')

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@genres_ns.route('/')
class GenresView(Resource):
    def get(self):
        all_genres = Genre.query.all()
        return genres_schema.dump(all_genres), 200

    def post(self):
        req_json = request.json
        new_genres = Genre(**req_json)
        with db.session.begin():
            db.session.add(new_genres)
        return "", 201


@genres_ns.route('/<int:gid>')
class GenreView(Resource):
    def get(self, gid):
        try:
            genre = db.session.query(Genre).filter(Genre.id == gid).one()
            return genre_schema.dump(genre), 200
        except Exception as e:
            return str(e), 404

    def put(self, gid):
        genre = db.session.query(Genre).get(gid)
        req_json = request.json
        genre.id = req_json.get("id")
        genre.name = req_json.get("name")

        db.session.add(genre)
        db.session.commit()

        return "", 204

    def delete(self, mid):
        user = Genre.query.get(mid)
        db.session.delete(user)
        db.session.commit()

        return "", 204
