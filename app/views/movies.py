from flask import request
from flask_restx import Resource, Namespace

from app.models import MovieSchema, Movie
from app.database import db
from sqlalchemy import desc

movies_ns = Namespace('movies')

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


@movies_ns.route('/')
class MoviesView(Resource):
    def get(self):
        page = request.args.get("page")
        status = request.args.get("status")
        if page is not None and status == "new":
            s = db.session.query(Movie).filter().order_by(desc(Movie.year)).limit(12).offset(page)
            return movies_schema.dump(s)
        elif page is None and status == "new":
            s = db.session.query(Movie).filter().order_by(desc(Movie.year))
            return movies_schema.dump(s)
        elif page is not None and status is None:
            s = db.session.query(Movie).filter().limit(12).offset(page)
            return movies_schema.dump(s)
        else:
            s = db.session.query(Movie)
            return movies_schema.dump(s)

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return "", 201


@movies_ns.route('/<int:mid>')
class MovieView(Resource):

    def get(self, mid):
        try:
            movie = db.session.query(Movie).filter(Movie.id == mid).one()
            return movie_schema.dump(movie), 200
        except Exception as e:
            return str(e), 404

    def put(self, mid):
        movie = db.session.query(Movie).get(mid)
        req_json = request.json

        movie.id = req_json.get("id")
        movie.title = req_json.get("title")
        movie.description = req_json.get("description")
        movie.trailer = req_json.get("trailer")
        movie.year = req_json.get("year")
        movie.rating = req_json.get("rating")
        movie.genre_id = req_json.get("genre_id")
        movie.director_id = req_json.get("director_id")

        db.session.add(movie)
        db.session.commit()

        return "", 204

    def delete(self, mid):
        movie = Movie.query.get(mid)
        db.session.delete(movie)
        db.session.commit()
        return "", 204
