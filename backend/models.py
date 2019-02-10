from backend import db
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin
from flask import current_app
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(31), nullable=False)
    lname = db.Column(db.String(31), nullable=False)
    email = db.Column(db.String(63), unique=True, nullable=False)
    password = db.Column(db.String(63), unique=False, nullable=False)
    address_line_1 = db.Column(db.String(61), unique=False, nullable=False)
    city = db.Column(db.String(26), unique=False, nullable=False)
    state = db.Column(db.String(3), unique=False, nullable=False)
    zip_code = db.Column(db.String(12), unique=False, nullable=False)
    phone_num = db.Column(db.String(11), unique=False, nullable=False)
    acc_num = db.Column(db.String(31), unique=False, nullable=False)
    cust_id = db.Column(db.String(123), unique=False, nullable=True)
    acc_id = db.Column(db.String(123), unique=False, nullable=True)
    income = db.Column(db.Integer, unique=False, nullable=True)
    firstTimeLogin = db.Column(db.Boolean, unique=False, default=False)
    isAdmin = db.Column(db.Boolean, nullable=False, default=False)

    def get_auth_token(self, expires_seconds=86400):
        s = Serializer(current_app.config['SECRET_KEY'], expires_seconds)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def get_reset_token(self, expires_seconds=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_seconds)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"{self.id}"


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(127), nullable=False)
    amount = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cat_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    isProcessable = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"{self.id}"


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    weightage = db.Column(db.Float, nullable=False, default=0)
    min_val = db.Column(db.Integer, nullable=False, default=0)
