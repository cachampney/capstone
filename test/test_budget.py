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
