class Goal:
    
    def __init__(self):
        
        """
        Initialize the variables for the class
        
        """
        self.name = None
        self.start_date = None
        self.end_date = None
        self.note = None
        self.target_amount = None
        self.date_spent = None
        self.category = None
        self.current_amount = 0.00
        self.amount_left = 0.00
        self.transactions = []

    def edit(self, name, start_date, end_date, note, target_amount, date_spent, category):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.note = note
        self.target_amount = target_amount
        self.date_spent = date_spent
        self.category = category
        
    def get(self, attribute):

        """
        function to get value of specified attribute of transaction object
        :param attribute:
        :return:
        """
        return self.__getattribute__(attribute)

    def update_attribute(self, attribute, value):
        if hasattr(self, attribute):
            setattr(self, attribute, value)
        else:
            raise AttributeError(f"'Goal' object has no attribute '{attribute}'")

    def to_dict(self):
        goal_dict = {'name': self.name, 'start_date': self.start_date, 'end_date': self.end_date, 'note': self.note,
                     'target_amount': self.target_amount, 'date_spent': self.date_spent, 'category': self.category,
                     'current_amount': self.current_amount, 'amount_left': self.amount_left}
        return goal_dict

    def update_from_dict(self, goal_dict):
        self.name = goal_dict['name']
        self.start_date = goal_dict['start_date']
        self.end_date = goal_dict['end_date']
        self.note = goal_dict['note']
        self.target_amount = goal_dict['target_amount']
        self.date_spent = goal_dict['date_spent']
        self.category = goal_dict['category']
        self.current_amount = goal_dict['current_amount']
        self.amount_left = goal_dict['amount_left']

    # Sets the current amount left torwards finishing the goal
    def set_startBalance(self):
        self.amount_left = self.target_amount
       
    # Used for when the user goes to change the balance goal amount
    # This way the amount left towards goal will refelct those changes and update
    # If there is anything within the current amount torwards the goal it will also be reflected
    def set_updateBalance(self):
        self.amount_left = self.target_amount - self.current_amount

    # Calculates the current amount torwards the goal when a transaction is added to it
    # Also updates the amount left torwards the goal
    def calc_currentAmount(self, trans_amount):
        self.current_amount += trans_amount
        self.amount_left -= self.current_amount
        self.set_updateBalance()
   
    # Calculates the current amount torwards a goal when a transaction is removed from it
    # Also updates the amount left torwards the goal
    def remove_currentAmount(self, trans_amount):
        self.current_amount -= trans_amount
        self.amount_left -= self.current_amount
        self.set_updateBalance()

    def apply_transaction(self, transaction):
        """
        Method to apply a transaction to the goal

        :param transaction: transaction to apply
        :type transaction: transactions.Transaction
        :return: None
        """
        self.calc_currentAmount(transaction.amount)
        self.transactions.append(transaction)

    def remove_transaction(self, transaction):
        """
        Method to remove a transaction from the goal

        :param transaction: transaction to remove
        :type transaction: transactions.Transaction
        :return: None
        """
        try:
            idx = self.transactions.index(transaction)
            self.remove_currentAmount(transaction.amount)
            del self.transactions[idx]
        except ValueError:
            pass
