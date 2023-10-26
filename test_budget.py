from ..budget import Budget
from ..transaction import Transaction


def test_add_transaction_expense():
    b = Budget()
    t = Transaction("expense", "13/10/2023", 23.23, 'target', 'clothes', "new shirt")
    b.add_transaction(t)
    assert t in b.expense_transactions


def test_add_transaction_income():
    b = Budget()
    t = Transaction("income", "13/10/2023", 23.23, 'target', 'clothes', "new shirt")
    b.add_transaction(t)
    assert t in b.income_transactions


def test_delete_transaction_expense():
    b = Budget()
    t = Transaction("expense", "13/10/2023", 23.23, 'target', 'clothes', "new shirt")
    b.add_transaction(t)
    b.delete_transaction(t)
    assert t not in b.expense_transactions


def test_delete_transaction_income():
    b = Budget()
    t = Transaction("income", "13/10/2023", 23.23, 'target', 'clothes', "new shirt")
    b.add_transaction(t)
    b.delete_transaction(t)
    assert t not in b.income_transactions


def test_get_transactions_income():
    b = Budget()
    t = Transaction("income", "13/10/2023", 23.23, 'target', 'clothes', "new shirt")
    b.add_transaction(t)
    ts = b.get_transactions(transaction_type='income')
    assert t in ts


def test_add_category():
    b = Budget()
    b.add_category("pickles")
    assert 'pickles' in b.categories

def test_remove_category():
    b = Budget()
    b.add_category("pickles")
    assert 'pickles' in b.categories
    b.remove_category('pickles')
    assert 'pickles' not in b.categories