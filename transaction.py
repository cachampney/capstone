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
        self.transaction_type = None
        self.date = None
        self.amount = None
        self.vendor = None
        self.category = None
        self.note = None
        self.expense_goal = None

    def update_attribute(self, attribute, value):
        if hasattr(self, attribute):
            setattr(self, attribute, value)
        else:
            raise AttributeError(f"'Transaction' object has no attribute '{attribute}'")

    def edit(self, transaction_type, date, amount, vendor, category, note, expense_goal):
        # --------------------------------------------------------------------------------------
        # Go through an text box ties to the variables labled
        # EX. self.amount = amountBox.text (this is how it's done on C# visual studio gui)
        # ^^ (done initially)
        # --------------------------------------------------------------------------------------
        self.transaction_type = transaction_type
        self.date = date
        self.amount = amount
        self.vendor = vendor
        self.category = category
        self.note = note
        self.expense_goal = expense_goal

    def get(self, attribute):
        """
        function to get value of specified attribute of transaction object
        :param attribute:
        :return:
        """
        return self.__getattribute__(attribute)


    def to_dict(self):
        trans_dict = {'transaction_type': self.transaction_type, 'date': self.date, 'amount': self.amount,
                      'vendor': self.vendor, 'category': self.category, 'note': self.note, 'expense_goal': self.expense_goal}
        return trans_dict
