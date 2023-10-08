"""
Module containing budget class
"""


class Budget:
    """
    Object representing a budget. Holds transactions and other budget related data.
    """

    def __init__(self):
        self.expense_transactions = []
        self.income_transactions = []
        self.total_expenses = 0
        self.total_income = 0
        self.balance = 0

    def add_transaction(self, transaction):
        """
        Method to add transaction to budget

        :param transaction: transaction to add to budget
        :type transaction: Transaction
        :return: bool - True if transaction added successful, False if not
        """
        # validate transaction
        if not transaction or not isinstance(transaction, Transaction):
            raise ValueError("Transaction must not be empty and must be of type Transaction")
        if transaction.transaction_type == 'income':
            self.income_transactions.append(transaction)
            self.total_income += transaction.amount
        if transaction.transaction_type == 'expense':
            self.expense_transactions.append(transaction)
            self.total_expenses += transaction.amount
        self.balance = self.total_income - self.total_expenses  # update balance
        return True

    def delete_transaction(self, transaction):
        """
        Method to delete transaction from budget

        :param transaction: transaction to delete
        :type transaction: Transaction
        :return: bool - True if transaction removed, False if not (likely transaction was not in list)
        """
        if not transaction or not isinstance(transaction, Transaction):
            raise ValueError("Transaction must not be empty and must be of type Transaction")
        if transaction.transaction_type == 'income':
            try:
                self.income_transactions.remove(transaction)
            except ValueError:
                return False
            else:
                self.total_income -= transaction.amount
        if transaction.transaction_type == 'expense':
            try:
                self.expense_transactions.remove(transaction)
            except ValueError:
                return False
            else:
                self.total_expenses -= transaction.amount
        self.balance = self.total_income - self.total_expenses  # update balance
        return True

    def get_transactions(self, **kwargs):
        """
        Method to get list of transactions based on specified attribute values
        Example: budget.get_transactions(transaction_type="income", "amount"=58.25) would return
         list of transactions that are income transactions and have amount of 58.25.

        :param kwargs: keyword arguments (key=value) to get transactions based on
        :return: [Transaction] - list of Transactions, empty if no matching transactions found
        """
        trans_to_return = []  # empty list to hold transactions to return
        valid_keys = ['transaction_type', 'date', 'amount', 'vendor', 'category', 'note']
        # validate passed in keyword arguments
        for key in kwargs.keys():
            if key not in valid_keys:
                raise ValueError(f"Invalid key ({key}) provided. Valid keys are {valid_keys}.")
        for trans in self.expense_transactions:  # search through expense transactions
            for attribute, value in kwargs.items():
                if trans.get(attribute) == value:
                    trans_to_return.append(trans)
        for trans in self.income_transactions:  # search through income transactions
            for attribute, value in kwargs.items():
                if trans.get(attribute) == value:
                    trans_to_return.append(trans)
        return trans_to_return
