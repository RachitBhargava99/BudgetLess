from backend.models import User, Expense, Category
import json
from flask import Blueprint, request
from backend import db, config
import requests
from backend.stats.utils import get_expense_info
from datetime import datetime
import os

stats = Blueprint('stats', __name__)


@stats.route('/expense/create', methods=['GET', 'POST'])
def create_new_expense():
    request_json = request.get_json()
    auth_token = request_json['auth_token']
    user = User.verify_auth_token(auth_token)
    if not user:
        return json.dumps({'status': 0, 'error': "Authentication Failed"})
    else:
        expense_info = request_json['expenses']
        for each in expense_info:
            name = each[1]
            amount = float(each[2])
            user_id = user.id
            cat_id = int(each[3])
            process = bool(int(each[4]))
            new_expense = Expense(name=name, amount=amount, user_id=user_id, cat_id=cat_id, isProcessable=process)
            db.session.add(new_expense)
        user.firstTimeLogin = True
        db.session.commit()
        return json.dumps({'status': 1})


@stats.route('/expense/modify', methods=['GET', 'POST'])
def modify_expense():
    request_json = request.get_json()
    auth_token = request_json['auth_token']
    user = User.verify_auth_token(auth_token)
    if not user:
        return json.dumps({'status': 0, 'error': "Authentication Failed"})
    else:
        id = request_json['id']
        expense = Expense.query.filter_by(id=id).first()
        expense.name = request_json['name']
        expense.amount = request_json['amount']
        expense.cat_id = request_json['cat_id']
        expense.type = request_json['type']
        db.session.commit()
        return json.dumps({'status': 1})


@stats.route('/expense/new', methods=['GET', 'POST'])
def add_new_expense():
    request_json = request.get_json()
    auth_token = request_json['auth_token']
    user = User.verify_auth_token(auth_token)
    if not user:
        return json.dumps({'status': 0, 'error': "Authentication Failed"})
    else:
        name = request_json['name']
        amount = request_json['amount']
        user_id = request_json['user_id']
        cat_id = request_json['cat_id']
        new_expense = Expense(name=name, amount=amount, user_id=user_id, cat_id=cat_id)
        expense_info = get_expense_info(user)
        final = []
        unimp_sum, extra_sum = 0, 0
        for each in expense_info:
            curr_cat = Category.query.filter_by(id=each).first()
            final.append({'id': each,
                          'name': curr_cat.name,
                          'weightage': curr_cat.weightage,
                          'min_val': curr_cat.min_val,
                          'unimp_index': 1 - curr_cat.weightage,
                          'extra': expense_info[each] - curr_cat.min_val\
                              if expense_info[each] >= curr_cat.min_val\
                              else 0})
            unimp_sum += 1 - curr_cat.weightage
            extra_sum += expense_info[each] - curr_cat.min_val
        overall_sum = 0
        i = 0
        for each in final:
            each['unimp_index'] = each['weightage'] / unimp_sum
            each['extra_index'] = each['extra'] / extra_sum
            each['overall_rough'] = each['unimp_index'] * each['extra_index']
            overall_sum += each['overall_rough']
        for each in final:
            each['overall_index'] = (each['overall_rough'] / overall_sum) if overall_sum != 0 else 0
            each['reduce_spendings'] = round((each['overall_index'] * amount), 0)\
                if ((each['overall_index'] * amount) < each['extra'])\
                else each['extra']
        return json.dumps({'status': 1, 'data': final, 'possibility': True if extra_sum >= amount else False,
                          'init': request_json})


@stats.route('/expense/via_deduct', methods=['GET', 'POST'])
def add_expense_via_deduct():
    request_json = request.get_json()
    auth_token = request_json['auth_token']
    user = User.verify_auth_token(auth_token)
    if not user:
        return json.dumps({'status': 0, 'error': "Authentication Failed"})
    else:
        name = request_json['name']
        amount = request_json['amount']
        user_id = request_json['user_id']
        cat_id = request_json['cat_id']
        new_expense = Expense(name=name, amount=amount, user_id=user_id, cat_id=cat_id)
        db.session.add(new_expense)
        expense_info = get_expense_info(user)
        final = []
        unimp_sum, extra_sum = 0, 0
        for each in expense_info:
            curr_cat = Category.query.filter_by(id=each).first()
            final.append({'id': each,
                          'name': curr_cat.name,
                          'weightage': curr_cat.weightage,
                          'min_val': curr_cat.min_val,
                          'unimp_index': 1 - curr_cat.weightage,
                          'extra': expense_info[each] - curr_cat.min_val\
                              if expense_info[each] >= curr_cat.min_val\
                              else 0})
            unimp_sum += 1 - curr_cat.weightage
            extra_sum += expense_info[each] - curr_cat.min_val
        overall_sum = 0
        i = 0
        for each in final:
            each['unimp_index'] = each['weightage'] / unimp_sum
            each['extra_index'] = each['extra'] / extra_sum
            each['overall_rough'] = each['unimp_index'] * each['extra_index']
            overall_sum += each['overall_rough']
        for each in final:
            each['overall_index'] = (each['overall_rough'] / overall_sum) if overall_sum != 0 else 0
            each['reduce_spendings'] = round((each['overall_index'] * amount), 0)\
                if ((each['overall_index'] * amount) < each['extra'])\
                else each['extra']
        for each in final:
            expense = Expense(name="Adjustment", amount=(-1)*each['reduce_spendings'], user_id=user.id,
                              cat_id=each['id'])
            db.session.add(expense)
        db.session.commit()
        return json.dumps({'status': 1})


@stats.route('/expense/via_saving', methods=['GET', 'POST'])
def add_expense_via_saving():
    request_json = request.get_json()
    auth_token = request_json['auth_token']
    user = User.verify_auth_token(auth_token)
    if not user:
        return json.dumps({'status': 0, 'error': "Authentication Failed"})
    else:
        name = request_json['name']
        amount = request_json['amount']
        user_id = request_json['user_id']
        cat_id = request_json['cat_id']
        new_expense = Expense(name=name, amount=amount, user_id=user_id, cat_id=cat_id)
        db.session.add(new_expense)
        db.session.commit()
        return json.dumps({'status': 1})

@stats.route('/expense/view_payable', methods=['GET', 'POST'])
def view_payable_expenses():
    request_json = request.get_json()
    auth_token = request_json['auth_token']
    user = User.verify_auth_token(auth_token)
    if not user:
        return json.dumps({'status': 0, 'error': "Authentication Failed"})
    else:
        payable_expenses = Expense.query.filter_by(user_id=user.id, isProcessable=True)
        final = [{'id': x.id,
                  'name': x.name,
                  'amount': x.amount,
                  'cat': Category.query.filter_by(id=x.cat_id).first().name} for x in payable_expenses]
        final_payment = 0
        for each in final:
            final_payment += each['amount']
        return json.dumps({'status': 1, 'data': final, 'amount': final_payment})


@stats.route('/expense/ocp', methods=['GET', 'POST'])
def one_click_payment():
    request_json = request.get_json()
    auth_token = request_json['auth_token']
    user = User.verify_auth_token(auth_token)
    if not user:
        return json.dumps({'status': 0, 'error': "Authentication Failed"})
    else:
        payable_expenses = Expense.query.filter_by(user_id=user.id, isProcessable=True)
        final = [{'id': x.id,
                  'name': x.name,
                  'amount': x.amount} for x in payable_expenses]
        final_payment = 0
        for each in final:
            final_payment += each['amount']

        payment_data = {
            'amount': str(final_payment),
            'accountID': user.acc_id,
            'customerID': user.cust_id,
            'mode': 'initiate',
            'description': f"Bulk Payment of {final_payment}",
            'requestID': str(user.id),
            'sendOnDate': f"{datetime.now().strftime('%m/%d/%Y')}",
            'speed': "Next Day"
        }

        endpoint_url = 'Payments/OneTimePayment'
        headers = {
            "apiKey": os.environ['FISERV_API_KEY'],
            "businessID": os.environ['BUSINESS_ID']
        }

        request_data = requests.post(
            f"https://certwebservices.ft.cashedge.com/sdk/{endpoint_url}",
            headers=headers,
            json=payment_data
        )

        return json.dumps({'status': 1, 'message': request_data.json()['status']['messageDetail']['message'],
                           'amount': final_payment})


@stats.route('/expense/view', methods=['GET', 'POST'])
def view_all_expenses():
    request_json = request.get_json()
    auth_token = request_json['auth_token']
    user = User.verify_auth_token(auth_token)
    if not user:
        return json.dumps({'status': 0, 'error': "Authentication Failed"})
    else:
        expenses = Expense.query.filter_by(user_id=user.id)
        final = [{'id': x.id,
                  'name': x.name,
                  'amount': x.amount,
                  'cat_id': x.cat_id} for x in expenses]
        exp_sum = 0
        for each in final:
            exp_sum += each['amount']
        savings = user.income - exp_sum
        return json.dumps({'status': 1, 'data': final, 'expenses': exp_sum, 'savings': savings, 'income': user.income})
