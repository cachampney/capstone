import pytest

from budget import Budget
from goal import Goal
from transaction import Transaction


def test_add_transaction_expense():
    b = Budget()
    t = Transaction("expense", "13/10/2023", 23.23, 'target', 'clothes', "new shirt")
    b.add_transaction(t)
    print(b.expense_transactions)
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


def test_add_expense_goal():
    b = Budget()
    g = Goal("Test", "30/11/2023", "01/12/2023", "note", 50.00, "30/11/2023")
    b.add_expense_goal(g)
    for goal_name, goal in b.expense_goals.items():
        if goal_name == g.name.lower():
            assert True
            assert goal.name == g.name
            return
    assert False


def test_add_expense_goal_duplicate_name():
    b = Budget()
    g = Goal("Test", "30/11/2023", "01/12/2023", "note", 50.00, "30/11/2023")
    b.add_expense_goal(g)
    with pytest.raises(ValueError):
        g1 = Goal("Test", "30/12/2023", "01/01/2024", "note", 50.00, "30/12/2023")
        b.add_expense_goal(g1)


def test_add_expense_goal_dup_name_diff_case():
    b = Budget()
    g = Goal("Test", "30/11/2023", "01/12/2023", "note", 50.00, "30/11/2023")
    b.add_expense_goal(g)
    with pytest.raises(ValueError):
        g1 = Goal("test", "30/12/2023", "01/01/2024", "note", 50.00, "30/12/2023")
        b.add_expense_goal(g1)


def test_add_expense_goal_wrong_type():
    b = Budget()
    g = {"blah": "blah"}
    with pytest.raises(ValueError):
        b.add_expense_goal(g)


def test_get_expense_goal():
    b = Budget()
    g = Goal("Test", "30/11/2023", "01/12/2023", "note", 50.00, "30/11/2023")
    b.add_expense_goal(g)
    assert b.get_expense_goal(g.name) == g


def test_get_expense_goal_diff_case():
    b = Budget()
    g = Goal("Test", "30/11/2023", "01/12/2023", "note", 50.00, "30/11/2023")
    b.add_expense_goal(g)
    assert b.get_expense_goal("TEST") == g


def test_get_expense_goal_not_found():
    b = Budget()
    with pytest.raises(ValueError):
        b.get_expense_goal("test")


def test_delete_expense_goal():
    b = Budget()
    g = Goal("Test", "30/11/2023", "01/12/2023", "note", 50.00, "30/11/2023")
    b.add_expense_goal(g)
    b.delete_expense_goal("Test")
    with pytest.raises(ValueError):
        b.get_expense_goal(g.name)


def test_delete_expense_goal_diff_case():
    b = Budget()
    g = Goal("Test", "30/11/2023", "01/12/2023", "note", 50.00, "30/11/2023")
    b.add_expense_goal(g)
    b.delete_expense_goal("test")
    with pytest.raises(ValueError):
        b.get_expense_goal(g.name)


def test_delete_expense_goal_not_found():
    b = Budget()
    with pytest.raises(ValueError):
        b.delete_expense_goal("test")
