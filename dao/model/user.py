from marshmallow import Schema, fields

from app.database import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    password = db.Column(db.String)


class UserSchema(Schema):
    id = fields.Int()
    email = fields.Str()
    password = fields.Str()
