from backend.models import User, Expense, Category


def get_expense_info(user):
    all_expense = [{'id': x.id,
                    'name': x.name,
                    'cat_id': x.cat_id,
                    'amount': x.amount} for x in Expense.query.filter_by(user_id=user.id)]
    dummy = {}
    for expense in all_expense:
        dummy[expense['cat_id']] = 0 \
            if dummy.get(expense['cat_id']) is None \
            else dummy[expense['cat_id']] + expense['amount']
    return dummy
