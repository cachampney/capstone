"""
Module for Transaction Class
"""


class Transaction:
    '''
    transaction_type : str
    date : str
    amount : float
    vendor : str
    category : str
    note : str
    '''
    # methods
   
    # ---------------------------------------------------------------------
    # Forces all arguments to be fullfilled
    # Or does it just need set to self without the arguments put in place
    # Need to pull the information from the GUI text boxes initially
    # ---------------------------------------------------------------------
    
    def __init__(self, transaction_type: str, date: str, amount: float, vendor: str, category: str, note: str):
        self.transaction_type = None
        self.date = None
        self.amount = None
        self.vendor = None
        self.category = None
        self.note = None
        self.edit(transaction_type, date, amount, vendor, category, note)

    def edit(self, transaction_type, date, amount, vendor, category, note):
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

    def get(self, attribute):
        """
        function to get value of specified attribute of transaction object
        :param attribute:
        :return:
        """
        return self.__getattribute__(attribute)
