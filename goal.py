from transaction import Transaction


class Goal:
    
    def __init__(self):
        
        """
        Initialize the variables for the class
        
        """
        self.name: str = None
        self.start_date: str = None
        self.end_date: str = None
        self.note: str = None
        self.target_amount: float = None
        self.date_spent: str = None
        self.category: str = None
        self.current_amount: float = 0.00
        self.amount_left: float = 0.00
        self.transactions: list[Transaction] = []

    def edit(self, name: str, start_date: str, end_date: str, note: str, target_amount: float, date_spent: str,
             category: str):
        """
        Method to edit goal

        :param name: name of goal
        :type name: str
        :param start_date: start date of goal
        :type start_date: str
        :param end_date: end date of goal
        :type end_date: str
        :param note: note to include in goal
        :type note: str
        :param target_amount: target amount to reach
        :type target_amount: float
        :param date_spent: date money spent
        :type date_spent: str
        :param category: category for goal
        :type category: str
        :return: None
        """
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.note = note
        self.target_amount = target_amount
        self.date_spent = date_spent
        self.category = category

    def init_goal(self, name: str, start_date: str, end_date: str, note: str, target_amount: float, date_spent: str,
                  category: str):
        """
        Alternative init method

        :param name: name of goal
        :type name: str
        :param start_date: start date of goal
        :type start_date: str
        :param end_date: end date of goal
        :type end_date: str
        :param note: note to include in goal
        :type note: str
        :param target_amount: target amount to reach
        :type target_amount: float
        :param date_spent: date money spent
        :type date_spent: str
        :param category: category for goal
        :type category: str
        :return: None
        :param name:
        :param start_date:
        :param end_date:
        :param note:
        :param target_amount:
        :param date_spent:
        :param category:
        :return:
        """
        self.edit(name, start_date, end_date, note, target_amount, date_spent, category)
        self.amount_left = target_amount

    def get(self, attribute: str):
        """
        Method to get value of specified attribute of transaction object

        :param attribute: attribute to retrieve
        :type: attribute: str
        :return: value of attribute
        """
        return self.__getattribute__(attribute)

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
            raise AttributeError(f"'Goal' object has no attribute '{attribute}'")

    def to_dict(self):
        """
        Method to encode goal as python dictionary

        :return: dictionary with information of goal
        :rtype: dict[str, str|float]
        """
        goal_dict = {'name': self.name, 'start_date': self.start_date, 'end_date': self.end_date, 'note': self.note,
                     'target_amount': self.target_amount, 'date_spent': self.date_spent, 'category': self.category,
                     'current_amount': self.current_amount, 'amount_left': self.amount_left}
        return goal_dict

    def update_from_dict(self, goal_dict: dict[str, float | str]):
        """
        method to update goal using provided dictionary

        :param goal_dict: dictionary with values
        :type goal_dict: dict[str, float | str]
        :return: None
        """
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
        """
        Method to set the current amount left towards finishing the goal

        :return: None
        """
        self.amount_left = self.target_amount
       
    # Used for when the user goes to change the balance goal amount
    # This way the amount left towards goal will refelct those changes and update
    # If there is anything within the current amount torwards the goal it will also be reflected
    def set_updateBalance(self):
        """
        Method to update balance towards goal amount

        :return: None
        """
        self.amount_left = self.target_amount - self.current_amount

    # Calculates the current amount torwards the goal when a transaction is added to it
    # Also updates the amount left torwards the goal
    def calc_currentAmount(self, trans_amount: float):
        """
        Method to calculate the current and adding amount

        :param trans_amount: amount to add to current amount
        :type trans_amount: float
        :return: None
        """
        self.current_amount += trans_amount
        self.set_updateBalance()
   
    # Calculates the current amount torwards a goal when a transaction is removed from it
    # Also updates the amount left torwards the goal
    def remove_currentAmount(self, trans_amount: float):
        """
        Method to calculate current amount after removing amount

        :param trans_amount: amount to remove to current amount
        :type trans_amount: float
        :return:
        """
        self.current_amount -= trans_amount
        self.set_updateBalance()

    def apply_transaction(self, transaction: Transaction):
        """
        Method to apply a transaction to the goal

        :param transaction: transaction to apply
        :type transaction: Transaction
        :return: None
        """
        if transaction.transaction_type.lower() == 'income':
            self.remove_currentAmount(transaction.amount)
        else:
            self.calc_currentAmount(transaction.amount)
        self.transactions.append(transaction)

    def remove_transaction(self, transaction: Transaction):
        """
        Method to remove a transaction from the goal

        :param transaction: transaction to remove
        :type transaction: Transaction
        :return: None
        """
        try:
            idx = self.transactions.index(transaction)
            if transaction.transaction_type.lower() == 'income':
                self.calc_currentAmount(transaction.amount)
            else:
                self.remove_currentAmount(transaction.amount)
            del self.transactions[idx]
        except ValueError:
            pass
