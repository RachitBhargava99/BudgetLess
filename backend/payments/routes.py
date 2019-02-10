from backend.models import User, Expense, Category
import json
from flask import Blueprint, request
from backend import db, config
import requests
from backend.stats.utils import get_expense_info
import os

payments = Blueprint('payments', __name__)


@payments.route('/payment/overall', methods=['GET', 'POST'])
def create_new_expense():
    request_json = request.get_json()
    auth_token = request_json['auth_token']
    user = User.verify_auth_token(auth_token)
    if not user:
        return json.dumps({'status': 0, 'error': "Authentication Failed"})
    else:
        payment_data = {
            "amount": request_json['amount'],
            "customerID": user.cust_id,
            "mode": "initiate",
            "requestID": user.id,
            "address": {
                "city": user.city,
                "line1": user.address_line_1,
                "state": user.state,
                "zip": user.zip_code
            }
        }

        endpoint_url = "Payments/OneTimePayment"
        headers = {
            "apiKey": os.environ['FISERV_API_KEY'],
            "businessID": os.environ['BUSINESS_ID']
        }

        payment_request = requests.post(
            f"https://certwebservices.ft.cashedge.com/sdk/{endpoint_url}",
            headers=headers,
            json=payment_data
        )

        return json.dumps({'status': 1})
