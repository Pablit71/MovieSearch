import base64
import hashlib
import sqlite3

import jwt
from flask import request, abort
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
PWD_HASH_SALT = base64.b64decode("salt")
PWD_HASH_ITERATIONS = 100
algo = 'HS256'
secret = 's3cR$eT'


def connect(query):
    connection = sqlite3.connect('movies.db')
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    connection.close()
    return result


def auth_required(func):
    def wrapper(*args, **kwargs):
        if 'Authorization' not in request.headers:
            abort(401)
        data = request.headers['Authorization']
        token = data.split("Bearer ")[-1]
        try:
            jwt.decode(token, secret, algorithms=[algo])
        except Exception as e:
            print(f"Traceback: {e}")
            abort(401)
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
    hash_digest = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        PWD_HASH_SALT,
        PWD_HASH_ITERATIONS
    )

    return base64.b64encode(hash_digest)


def edit_pass(data):
    data['password'] = encode_h(data.get('password'))
    return data


def edit_pass_put(data_1, uid, class_input, data_2):
    request_pass_1 = edit_pass(data_1)
    query = f"""
        select password
        from user 
        where id = '{uid}'
        """
    response = connect(query)[0][0]
    if response == data_1['password']:
        print(f'response - {response}')
        password_edit = edit_pass(data_2)
        print(f'password_edit - {password_edit}')
        user = class_input.query.get(uid)
        print(f'user - {user.password}')
        user.password = password_edit['password']
        print(f'user.password - {user.password}')
        db.session.add(user)
        db.session.commit()
        print("Пароли равны")
    else:
        print(f"Данного пароля ({data_1['password']}), не подходит в базе")


def encode_hash(password):
    hash_digest = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        PWD_HASH_SALT,
        PWD_HASH_ITERATIONS
    )
    return str(base64.b64encode(hash_digest))
