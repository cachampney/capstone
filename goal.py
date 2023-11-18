class Goal:
    
    def __init__(self, name : str, start_date : str, end_date : str, note : str, target_amount : float,
                 date_spent : str, category : str, amount_left : float, current_amount : float):
        
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
        self.current_amount = None
        self.amount_left = None
        self.current_amount = None
        self.edit(name, start_date, end_date, note, target_amount, date_spent, category, amount_left, current_amount)

    def edit(self, name, start_date, end_date, note, target_amount, date_spent, category, amount_left, current_amount):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.note = note
        self.target_amount = target_amount
        self.date_spent = date_spent
        self.category = category
        self.amount_left = amount_left
        self.current_amount = current_amount
        
        
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
                     'current_amount': self.current_amount}
        return goal_dict
    
    #Sets the current amount left torwards finishing the goal
    def set_startBalance(self, target_amount, amount_left):
            self.amount_left = self.target_amount
            return amount_left  
       
    #Used for when the user goes to change the balance goal amount
    #This way the amount left towards goal will refelct those changes and update
    #If there is anything within the current amount torwards the goal it will also be reflected
    def set_updateBalance(target_amount, amount_left, current_amount):
        if current_amount == 0:
            amount_left = target_amount
            return amount_left
        else:
            amount_left = target_amount - current_amount
            return amount_left
         
    #Calculates the current amount torwards the goal when a transaction is added to it
    #Also updates the amount left torwards the goal
    def calc_currentAmount(trans_amount, amount_left, current_amount):
        current_amount += trans_amount
        amount_left -=trans_amount
        return current_amount, amount_left
   
    #Calculates the current amount torwards a goal when a transaction is removed from it
    #Also updates the amount left torwards the goal
    def remove_currentAmount(trans_amount, amount_left, current_amount):
        current_amount -= trans_amount
        amount_left += trans_amount
        return current_amount, amount_left