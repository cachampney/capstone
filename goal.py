class Goal:
    
    def __init__(self, name : str, start_date : str, end_date : str, note : str, target_amount : float, date_spent : str):
        
        """
        Initialize the variables for the class
        
        """
        self.name = None
        self.start_date = None
        self.end_date = None
        self.note = None
        self.target_amount = None
        self.date_spent = None
        self.edit(name, start_date, end_date, note, target_amount, date_spent)

    def edit(self, name, start_date, end_date, note, target_amount, date_spent):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.note = note
        self.target_amount = target_amount
        self.date_spent = date_spent
        
    def get(self, attribute):
        
        """
        function to get value of specified attribute of transaction object
        :param attribute:
        :return:
        """
        return self.__getattribute__(attribute)
