import calendar
import hashlib
import datetime
import jwt

from flask import request, abort
from flask_restx import Resource, Namespace

from app.models import UserSchema, User
from app.database import db, secret, algo, admin_required, encode_h, add_user

auth_ns = Namespace('auth')

users_ns = Namespace('users')

user_schema = UserSchema()
users_schema = UserSchema(many=True)


@users_ns.route('/')
class UsersView(Resource):
    def get(self):
        all_users = User.query.all()
        return users_schema.dump(all_users), 200


@users_ns.route('/<int:mid>')
class UsersView(Resource):
    def get(self, mid: int):
        try:
            movie = db.session.query(User).filter(User.id == mid).one()
            return user_schema.dump(movie), 200
        except Exception as e:
            return str(e), 404

    def put(self, mid):
        user = db.session.query(User).get(mid)
        req_json = request.json
        user.email = req_json.get("email")
        user.password = req_json.get("password")

        db.session.add(user)
        db.session.commit()

        return "", 204

    def delete(self, mid):
        user = User.query.get(mid)
        db.session.delete(user)
        db.session.commit()

        return "", 204


@auth_ns.route('/register')
class AuthView(Resource):
    def post(self):
        data = {
            'email': request.json.get('email'),
            'password': request.json.get('password')
        }
        add_user(data)
        new_user = User(**data)
        with db.session.begin():
            db.session.add(new_user)
        return data, 201


@auth_ns.route('/login')
class AuthView(Resource):
    def post(self):
        req_json = request.json
        email = req_json.get("email", None)
        password = req_json.get("password", None)
        if None in [email, password]:
            abort(400)

        user = db.session.query(User).filter(User.email == email).first()

        if user is None:
            return {"error": "Неверные учётные данные"}, 401

        password_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
        print(password_hash)
        print(user.password)
        if password_hash != user.password:
            return {"error": "Неверные учётные данные хеша"}, 401

        data = {
            "email": user.email, "password": user.password
        }
        min30 = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        data["exp"] = calendar.timegm(min30.timetuple())
        access_token = jwt.encode(data, secret, algorithm=algo)
        days130 = datetime.datetime.utcnow() + datetime.timedelta(days=130)
        data["exp"] = calendar.timegm(days130.timetuple())
        refresh_token = jwt.encode(data, secret, algorithm=algo)
        tokens = {"access_token": access_token, "refresh_token": refresh_token}
        return tokens, 201

    def put(self):
        req_json = request.json
        refresh_token = req_json.get("refresh_token")
        if refresh_token is None:
            abort(400)

        try:
            data = jwt.decode(jwt=refresh_token, key=secret, algorithms=[algo])
        except Exception as e:
            abort(400)

        email = data.get("email")

        user = db.session.query(User).filter(User.email == email).first()

        data = {
            "email": user.email,
            "password": user.password
        }
        min30 = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        data["exp"] = calendar.timegm(min30.timetuple())
        access_token = jwt.encode(data, secret, algorithm=algo)
        days130 = datetime.datetime.utcnow() + datetime.timedelta(days=130)
        data["exp"] = calendar.timegm(days130.timetuple())
        refresh_token = jwt.encode(data, secret, algorithm=algo)
        tokens = {"access_token": access_token, "refresh_token": refresh_token}

        return tokens, 201
