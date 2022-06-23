import calendar
import hashlib
import datetime
import jwt

from flask import request
from flask_restx import Resource, Namespace

from app.database import db, edit_pass_put, auth_required
from dao.model.user import UserSchema, User

users_ns = Namespace('users')

user_schema = UserSchema()
users_schema = UserSchema(many=True)


@users_ns.route('/')
class UsersView(Resource):
    def get(self):
        all_users = User.query.all()
        return users_schema.dump(all_users), 200


@users_ns.route('/password/')
class UsersView(Resource):
    @auth_required
    def put(self):
        email = request.json.get('email')
        data_old = {
            'password': request.json.get('password_1')
        }
        data_new = {
            'password': request.json.get('password_2')
        }
        edit_pass_put(data_1=data_old, email=email, class_input=User, data_2=data_new)

        return "", 204


@users_ns.route('/<int:mid>')
class UsersView(Resource):
    def get(self, mid: int):
        try:
            movie = db.session.query(User).filter(User.id == mid).one()
            return user_schema.dump(movie), 200
        except Exception as e:
            return str(e), 404

    def delete(self, mid):
        user = User.query.get(mid)
        db.session.delete(user)
        db.session.commit()

        return "", 204
