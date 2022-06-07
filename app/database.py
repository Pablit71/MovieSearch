import hashlib
import sqlite3

import jwt
from flask import request, abort
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
secret = 's3cR$eT'
algo = 'HS256'


def connect(query):
    connection = sqlite3.connect('movies.db')
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    connection.close()
    return result


def admin_required(func):
    def wrapper(*args, **kwargs):
        if 'Authorization' not in request.headers:
            abort(401)

        data = request.headers['Authorization']
        token = data.split("Bearer ")[-1]
        try:
            user = jwt.decode(token, secret, algorithms=[algo])
            role = user.get("role")
        except Exception as e:
            print("JWT Decode Exception", e)
            abort(401)
        if role != "admin":
            abort(403)
        return func(*args, **kwargs)

    return wrapper


def admin_auth(func):
    def wrapper(*args, **kwargs):
        if 'Authorization' not in request.headers:
            abort(401)

        data = request.headers['Authorization']
        token = data.split("Bearer ")[-1]
        try:
            user = jwt.decode(token, secret, algorithms=[algo])
            role = user.get("role")
            print(role)
        except Exception as e:
            print("JWT Decode Exception", e)
            abort(401)
        if role != "admin":
            abort(403)
        return func(*args, **kwargs)

    return wrapper


def encode_h(password):
    password_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
    return password_hash


def add_user(data):
    data['password'] = encode_h(data.get('password'))
