import calendar
import hashlib
import datetime
import jwt

from flask import request, abort
from flask_restx import Resource, Namespace

from app.database import db, edit_pass, secret, algo, encode_h, encode_hash
from dao.model.user import User

auth_ns = Namespace('auth')


@auth_ns.route('/register')
class AuthView(Resource):
    def post(self):
        data = {
            'email': request.json.get('email'),
            'password': request.json.get('password')
        }
        data_up = edit_pass(data)
        new_user = User(**data_up)
        with db.session.begin():
            db.session.add(new_user)
        return '', 201


@auth_ns.route('/login')
class AutView(Resource):
    def post(self):
        req_json = request.json
        email = req_json.get("email", None)
        password = req_json.get("password", None)
        print(email, password)
        if None in [email, password]:
            abort(400)

        user = db.session.query(User).filter(User.email == email).first()

        if user is None:
            return {"error": "Неверные учётные данные"}, 401

        password_edit = encode_h(password)
        password_hash = encode_hash(password)
        if password_edit != user.password:
            return {"error": "Неверные учётные данные хеша"}, 401


        data = {
            "email": user.email, "password": password_hash
        }
        print(data['password'])
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
