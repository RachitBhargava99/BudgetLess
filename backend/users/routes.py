from flask import Blueprint, request, current_app
from backend.models import User, Expense, Category
from backend import db, bcrypt, mail
import json
from backend.users.utils import send_reset_email
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from flask_mail import Message
import random
import string
import requests
import os

users = Blueprint('users', __name__)


@users.route('/login', methods=['GET', 'POST'])
def login():
    request_json = request.get_json()
    email = request_json['email']
    password = request_json['password']
    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        final_dict = {
            'id': user.id,
            'auth_token': user.get_auth_token(),
            'fname': user.fname,
            'lname': user.lname,
            'email': user.email,
            'firstTimeLogin': user.firstTimeLogin,
            'isAdmin': user.isAdmin,
            'status': 1
        }
        return json.dumps(final_dict)
    else:
        final_dict = {
            'status': 0,
            'error': "The provided combination of email and password is incorrect."
        }
        return json.dumps(final_dict)


@users.route('/register', methods=['GET', 'POST'])
def normal_register():
    request_json = request.get_json()
    if User.query.filter_by(email=request_json['email']).first():
        return json.dumps({'status': 0, 'output': User.query.filter_by(email=request_json['email']).first().email,
                          'error': "User Already Exists"})
    email = request_json['email']
    hashed_pwd = bcrypt.generate_password_hash(request_json['password']).decode('utf-8')
    fname = request_json['fname']
    lname = request_json['lname']
    address_line_1 = request_json['address_line_1']
    city = request_json['city']
    state = request_json['state']
    zip_code = request_json['zip_code']
    phone_num = request_json['phone_num']
    acc_num = request_json['acc_num']
    # noinspection PyArgumentList
    user = User(email=email, password=hashed_pwd, fname=fname, lname=lname, address_line_1=address_line_1, city=city,
                state=state, zip_code=zip_code, phone_num=phone_num, acc_num=acc_num, isAdmin=False)
    db.session.add(user)
    db.session.commit()

    cust_data = {
        "address": {
            "city": user.city,
            "line1": user.address_line_1,
            "state": user.state,
            "zip": user.zip_code
        },
        "fundingAccount": {
            "ddaAccount": {
                "accountNumber": user.acc_num,
                "accountType": "Checking",
                "rtn": "044000037"
            },
            "nickName": f"{user.fname} {user.lname}"
        },
        "email": user.email,
        "externalCustomerIdentifier": user.id,
        "mode": "initiate",
        "personName": {
            "firstName": user.fname,
            "lastName": user.lname
        },
        "phone1": user.phone_num,
        "requestID": user.id
    }

    endpoint_url = 'Payments/Customers'
    headers = {
        "apiKey": os.environ['FISERV_API_KEY'],
        "businessID": os.environ['BUSINESS_ID']
    }

    request_data = requests.post(
        f"https://certwebservices.ft.cashedge.com/sdk/{endpoint_url}",
        headers=headers,
        json=cust_data
    )

    try:
        user.cust_id = request_data.json()['customerID']
    except Exception:
        raise Exception(f"{request_data.json()}")
    user.acc_id = request_data.json()['fundingAccount']['accountID']

    db.session.commit()

    return json.dumps({'id': user.id, 'status': 1})


@users.route('/admin/add', methods=['GET', 'POST'])
def master_add():
    request_json = request.get_json()
    user = User.query.filter_by(email=request_json['email']).first()
    user.isAdmin = True
    db.session.commit()
    return json.dumps({'status': 1})


@users.route('/password/request_reset', methods=['GET', 'POST'])
def request_reset_password():
    request_json = request.get_json()
    user = User.query.filter_by(email=request_json['email']).first()
    if user:
        send_reset_email(user)
        return json.dumps({'status': 1})
    else:
        return json.dumps({'status': 0, 'error': "User Not Found"})


@users.route('/backend/password/verify_token', methods=['GET', 'POST'])
def verify_reset_token():
    request_json = request.get_json()
    user = User.verify_reset_token(request_json['token'])
    if user is None:
        return json.dumps({'status': 0, 'error': "Sorry, the link is invalid or has expired. Please submit password reset request again."})
    else:
        return json.dumps({'status': 1})


@users.route('/backend/password/reset', methods=['GET', 'POST'])
def reset_password():
    request_json = request.get_json()
    user = User.verify_reset_token(request_json['auth_token'])
    if user is None:
        return json.dumps({'status': 0,
                           'error': "Sorry, the link is invalid or has expired. Please submit password reset request again."})
    else:
        hashed_pwd = bcrypt.generate_password_hash(request_json['password']).decode('utf-8')
        user.password = hashed_pwd
        db.session.commit()
        return json.dumps({'status': 1})


@users.route('/users/data', methods=['GET', 'POST'])
def get_user_data():
    request_json = request.get_json()
    auth_token = request_json['auth_token']
    user = User.verify_auth_token(auth_token)
    if not user:
        return json.dumps({'status': 0, 'error': "Authentication Failed"})
    else:
        all_expense = [{'id': x.id,
                        'name': x.name,
                        'cat_id': x.cat_id,
                        'amount': x.amount} for x in Expense.query.filter_by(user_id=user.id)]
        dummy, final = {}, []
        for expense in all_expense:
            dummy[expense['cat_id']] = 0\
                if dummy.get(expense['cat_id']) is None\
                else dummy[expense['cat_id']] + expense['amount']
        for id in dummy:
            curr_cat = Category.query.filter_by(id=id).first()
            final.append({
                'id': curr_cat.id,
                'name': curr_cat.name,
                'amount': dummy[id]
            })
        return json.dumps({'status': 1,
                           'data': final,
                           'expense_info': all_expense})


@users.route('/users/income', methods=['GET', 'POST'])
def add_user_income():
    request_json = request.get_json()
    auth_token = request_json['auth_token']
    user = User.verify_auth_token(auth_token)
    if not user:
        return json.dumps({'status': 0, 'error': "Authentication Failed"})
    else:
        user_income = request_json['income']
        user.income = user_income
        db.session.commit()
        return json.dumps({'status': 1})


@users.route('/test', methods=['GET'])
def test():
    return "Hello World"
