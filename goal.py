class Goal:
    
    def __init__(self, name : str, start_date : str, end_date : str, note : str, target_amount : float,
                 date_spent : str, category : str):
        
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
        self.edit(name, start_date, end_date, note, target_amount, date_spent, category)

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
