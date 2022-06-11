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


def edit_pass(data):
    data['password'] = encode_h(data.get('password'))
    return data['password']


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
        user.password = password_edit
        print(f'user.password - {user.password}')
        db.session.add(user)
        db.session.commit()
        print("Пароли равны")
    else:
        print(f"Данного пароля ({data_1['password']}), не подходит в базе")
