"""
Module for Transaction Class
"""


class Transaction:
    """
    transaction_type : str
    date : str
    amount : float
    vendor : str
    category : str
    note : str
    expense_goal: str
    """
    # methods
   
    # ---------------------------------------------------------------------
    # Forces all arguments to be fullfilled
    # Or does it just need set to self without the arguments put in place
    # Need to pull the information from the GUI text boxes initially
    # ---------------------------------------------------------------------
    
    def __init__(self):
        self.transaction_type: str = None
        self.date: str = None
        self.amount: float = None
        self.vendor: str = None
        self.category: str = None
        self.note: str = None
        self.expense_goal: str = None

    def update_from_dict(self, transaction_dict: dict[str, str | float]):
        """
        Method to set attributes from dictionary

        :param transaction_dict: dictionary with attributes and values
        :type transaction_dict: dict[str, str | float]
        :return: None
        """
        self.transaction_type = transaction_dict['transaction_type']
        self.date = transaction_dict['date']
        self.amount = transaction_dict['amount']
        self.vendor = transaction_dict['vendor']
        self.category = transaction_dict['category']
        self.note = transaction_dict['note']
        self.expense_goal = transaction_dict['expense_goal']

    def update_attribute(self, attribute: str, value: str | float):
        """
        Method to update specified attribute with specified value

        :param attribute: name of attribute to update
        :type attribute: str
        :param value: Value to set for attribute
        :type value: str | float
        :return: None
        """
        if hasattr(self, attribute):
            setattr(self, attribute, value)
        else:
            raise AttributeError(f"'Transaction' object has no attribute '{attribute}'")

    def edit(self, transaction_type: str, date: str, amount: float, vendor: str, category: str, note: str,
             expense_goal: str):
        # --------------------------------------------------------------------------------------
        # Go through an text box ties to the variables labled
        # EX. self.amount = amountBox.text (this is how it's done on C# visual studio gui)
        # ^^ (done initially)
        # --------------------------------------------------------------------------------------
        """
        Method to edit transaction

        :param transaction_type: type of transaction (i.e. expense or income)
        :type transaction_type: str
        :param date: date transaction occurred
        :type date:  str
        :param amount: amount of transaction
        :type amount: float
        :param vendor: destination of funds
        :type vendor:  str
        :param category: category for transaction
        :type category:  str
        :param note: note to add to transaction
        :type note:  str
        :param expense_goal: goal to assign transaction to, if any
        :type expense_goal:  str
        :return:
        """
        self.transaction_type = transaction_type
        self.date = date
        self.amount = amount
        self.vendor = vendor
        self.category = category
        self.note = note
        self.expense_goal = expense_goal

    def get(self, attribute: str):
        """
        function to get value of specified attribute of transaction object

        :param attribute: attribute to get value for
        :type attribute: str
        :return: value of specified attribute
        :rtype: float | str
        """
        return self.__getattribute__(attribute)

    def to_dict(self):
        """
        Method to encode transaction as python dictionary

        :return: dictionary with information of goal
        :rtype: dict[str, str|float]
        """
        trans_dict = {'transaction_type': self.transaction_type, 'date': self.date, 'amount': self.amount,
                      'vendor': self.vendor, 'category': self.category, 'note': self.note, 'expense_goal': self.expense_goal}
        return trans_dict
