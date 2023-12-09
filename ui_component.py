import os
import re
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QMessageBox, QFileDialog, QComboBox, QTableWidget, QTableWidgetItem, QTabWidget,
                             QDialog, QAbstractItemView, QAction, QMainWindow)
import transaction
from transaction import Transaction
from budget import Budget
from goal import Goal


def insert_layout(update_cell_dialog: QDialog, new_input_line: QLineEdit, save_changes_button: QPushButton,
                  layout: QVBoxLayout, prompt: QLabel):
    """
    Inserts a custom layout into a QDialog for updating cell information.

    :param update_cell_dialog: The QDialog instance to which the custom layout will be added.
    :type update_cell_dialog: QDialog
    :param new_input_line: The QLineEdit instance to be included in the layout.
    :type new_input_line: QLineEdit
    :param save_changes_button: The QPushButton instance for saving changes in the layout.
    :type save_changes_button: QPushButton
    :param layout: The target QVBoxLayout instance to which the custom layout will be added.
    :type layout: QVBoxLayout
    :param prompt: The QLabel instance for a prompt to be included in the layout.
    :type prompt: QLabel
    """
    save_layout_first_row = QHBoxLayout()  # Create a QHBoxLayout instance
    save_layout_first_row.addWidget(new_input_line)
    save_layout_second_row = QHBoxLayout()  # Create a QHBoxLayout instance
    save_layout_second_row.addWidget(save_changes_button)
    layout.addWidget(prompt)
    layout.addLayout(save_layout_first_row)
    layout.addLayout(save_layout_second_row)
    update_cell_dialog.setLayout(layout)


#
#  Open Application (Requirement 1.1.1)
#
class BudgetTrackerApp(QMainWindow):
    # Import global row, transaction, and budget variable. This will make manipulating these in the methods much easier
    row: int = 0
    budget: Budget = Budget()
    sort_order: None = None

    #
    #  Open Application (Requirement 1.1.1)
    #
    def __init__(self):
        super().__init__()
        '''
        This section is meant to assign the values to the initial windows and tabs. 
        '''
        self.last_clicked_column: None = None

        # Create the two tabs
        self.budget_tracker_tab: QWidget = QWidget()
        self.expense_goal_tab: QWidget = QWidget()  # Second tab for goals (Requirement 1.2.4)

        # Set up the layout
        budget_tracker_tab_layout = QVBoxLayout()
        self.budget_tracker_tab.setLayout(budget_tracker_tab_layout)

        #
        # Second tab for goals (Requirement 1.2.4)
        #
        expense_goal_tab_layout = QVBoxLayout()
        self.expense_goal_tab.setLayout(expense_goal_tab_layout)

        # Create a QTabWidget and add the tabs
        self.tabs: QTabWidget = QTabWidget(self)
        self.tabs.addTab(self.budget_tracker_tab, "Transaction Tracker")
        self.tabs.addTab(self.expense_goal_tab, "Expense Goals")  # Second tab for goals (Requirement 1.2.4)

        self.setCentralWidget(self.tabs)  # Set the QTabWidget as the central widget

        self.setWindowTitle("Budget Tracker")
        self.setGeometry(900, 200, 800, 600)

        # Create a menu bar
        menubar = self.menuBar()  # File Menu (Requirement 1.3.2)

        # Create a File menu
        file_menu = menubar.addMenu('File')  # File Menu (Requirement 1.3.2)

        # create actions to add to the File menu
        #
        # save budget (Requirement 1.3.6)
        #
        save_action = QAction('Save', self)
        save_action.triggered.connect(self.save_budget_dialog)

        #
        # load budget (Requirement 1.3.7)
        #
        load_action = QAction('Load', self)
        load_action.triggered.connect(self.load_budget_dialog)

        #
        # delete budget (Requirement 1.3.8)
        #
        delete_action = QAction('Delete', self)
        delete_action.triggered.connect(self.delete_budget_dialog)

        #
        # export transactions (Requirement 1.3.5)
        #
        export_action = QAction('Export to Excel', self)
        export_action.triggered.connect(self.export_budget_dialog)

        # Add actions to the File menu
        file_menu.addAction(save_action)  # save budget (Requirement 1.3.6)
        file_menu.addAction(load_action)  # load budget (Requirement 1.3.7)
        file_menu.addAction(delete_action)  # delete budget (Requirement 1.3.8)
        file_menu.addAction(export_action)  # export transactions (Requirement 1.3.5)

        '''
        Begin block of code for the Transaction tracker. 
        '''
        # UI Widgets
        self.transaction_type = QComboBox()  # Select a transaction type (Requirement 1.1.2)

        self.date = QLineEdit()  # Input a date (Requirement 1.1.3)
        self.vendor = QLineEdit()  # Input a Vendor (Requirement 1.1.4)
        self.transaction_amount = QLineEdit()  # Input a float amount (Requirement 1.1.5)
        #
        # Input a note (Requirement 1.1.6)
        #
        self.transaction_note = QLineEdit()
        self.transaction_note.setMaxLength(150)

        self.transaction_category = QComboBox()  # Select a category (Requirement 1.1.7)

        #
        # add goal to transaction (Requirement 1.3.1, 1.3.9)
        #
        self.expense_goals = QComboBox()
        self.expense_goals.setFixedWidth(100)

        self.transaction_table = QTableWidget()
        self.transaction_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        #
        # Total Expense below table (requirement 1.1.10)
        #
        self.total_expenses_label = QLabel(f"Total Expenses: {self.budget.total_expenses}")
        self.total_income_label = QLabel(f"Total Income: {self.budget.total_income}")
        self.balance_label = QLabel(f"Balance: {self.budget.balance}")

        # Adding pre-determined strings for Transaction Type and Category drop down boxes
        #
        #  Select a transaction type (Requirement 1.1.2)
        #
        self.transaction_type.addItem("Expense")
        self. transaction_type.addItem("Income")

        #
        # add goal to transaction (Requirement 1.3.1)
        #
        for transaction_index, transaction_category in enumerate(self.budget.categories):
            self.transaction_category.addItem(transaction_category)
            transaction_index += 1

        #
        # select category for goal (Requirement 1.1.7)
        #
        for expense_goal_index, expense_goal_name in enumerate(self.budget.expense_goals):
            self.expense_goals.addItem(expense_goal_name)
        self.expense_goals.addItem("N/A")

        # Create buttons
        self.add_transaction_button = QPushButton("Add Transaction")  # add transaction (requirement 1.1.8)
        self.remove_transaction_button = QPushButton("Remove Transaction")  # remove transaction (requirement 1.1.9)

        self.update_transaction_cells = QPushButton("Update Cell")  # update transaction (requirement 1.3.3)

        # Connect buttons to their respective functions
        self.add_transaction_button.clicked.connect(self.add_transaction)  # add transaction (requirement 1.1.8)

        #
        # remove transaction (requirement 1.1.9, 1.2.2)
        #
        self.remove_transaction_button.clicked.connect(lambda: self.remove_from_table(self.transaction_table))

        #
        # update transaction (requirement 1.3.3)
        #
        self.update_transaction_cells.clicked.connect(lambda: self.update_transaction_cell_method(
            self.transaction_table))

        # Verify transaction amount and date format
        #
        #  Input a date (Requirement 1.1.3)
        #
        self.date.editingFinished.connect(lambda: self.validate_date(self.date))

        #
        # Input a float amount (Requirement 1.1.5)
        #
        self.transaction_amount.editingFinished.connect(lambda: self.validate_amount(self.transaction_amount))

        # Add Transaction Type and date on the first row
        budget_first_row_layout = QHBoxLayout()

        #
        #  Select a transaction type (Requirement 1.1.2)
        #
        budget_first_row_layout.addWidget(QLabel("Transaction Type:"))
        budget_first_row_layout.addWidget(self.transaction_type)

        #
        #  Input a date (Requirement 1.1.3)
        #
        budget_first_row_layout.addWidget(QLabel("Date:"))
        budget_first_row_layout.addWidget(self.date)

        budget_tracker_tab_layout.addLayout(budget_first_row_layout)

        # Add Vendor and Transaction Amount to the second row
        budget_second_row_layout = QHBoxLayout()

        #
        # Input a Vendor (Requirement 1.1.4)
        #
        budget_second_row_layout.addWidget(QLabel("Vendor:"))
        budget_second_row_layout.addWidget(self.vendor)

        #
        # Input a float amount (Requirement 1.1.5)
        #
        budget_second_row_layout.addWidget(QLabel("Transaction Amount:"))
        budget_second_row_layout.addWidget(self.transaction_amount)
        budget_tracker_tab_layout.addLayout(budget_second_row_layout)

        # Add Transaction Note and Category drop down box onto the third row
        budget_third_row_layout = QHBoxLayout()

        #
        # add goal to transaction (Requirement 1.3.1)
        #
        budget_third_row_layout.addWidget(QLabel("Expense Goal:"))
        budget_third_row_layout.addWidget(self.expense_goals)

        #
        # Select a category (Requirement 1.1.7)
        #
        budget_third_row_layout.addWidget(QLabel("Category:"))
        budget_third_row_layout.addWidget(self.transaction_category)

        #
        # Input a note (Requirement 1.1.6)
        #
        budget_third_row_layout.addWidget(QLabel("Note:"))
        budget_third_row_layout.addWidget(self.transaction_note)

        budget_tracker_tab_layout.addLayout(budget_third_row_layout)

        # Add "add/remove transaction buttons" onto the fourth row
        budget_fifth_row_layout = QHBoxLayout()
        budget_fifth_row_layout.addWidget(self.add_transaction_button)  # add transaction (requirement 1.1.8)
        budget_fifth_row_layout.addWidget(self.remove_transaction_button)  # remove transaction (requirement 1.1.9)
        budget_tracker_tab_layout.addLayout(budget_fifth_row_layout)

        # Set the number of columns to match the expected input and name them.
        self.transaction_table.setColumnCount(7)
        self.transaction_table_headers = ["Date", "Type", "Amount", "Vendor", "Category", "Note",  "Expense Goal"]
        self.transaction_table.setHorizontalHeaderLabels(self.transaction_table_headers)

        # Add display to show list of transactions and set default sortingEnabled to true
        budget_tracker_tab_layout.addWidget(self.transaction_table)  # add transaction (requirement 1.1.8)
        self.transaction_table.setSortingEnabled(True)  # transaction sorting (requirement 1.1.12)

        budget_tracker_tab_layout.addWidget(self.update_transaction_cells)  # update transaction (requirement 1.3.3)

        # Add the labels to the layout
        #
        # total expenses under table (Requirement 1.1.10)
        #
        budget_tracker_tab_layout.addWidget(self.total_expenses_label)

        #
        # total income under table (Requirement 1.2.3)
        #
        budget_tracker_tab_layout.addWidget(self.total_income_label)

        budget_tracker_tab_layout.addWidget(self.balance_label)

        # allow editing of the transaction table

        '''
        end block of code for the transition tracker and begin code for expense goal.
        '''
        #
        # Second tab for goals (Requirement 1.2.4)
        #
        # UI Widgets
        self.name_of_goal = QLineEdit()  # input goal name (Requirement 1.2.8)
        self.begin_date = QLineEdit()  # input begin date (Requirement 1.2.5)
        self.end_date = QLineEdit()  # input end date (Requirement 1.2.6)
        # self.date_spent = QLineEdit()
        self.goal_amount = QLineEdit()  # input goal amount (Requirement 1.2.7)
        self.expense_goal_category = QComboBox()  # select goal category (Requirement 1.2.9)

        #
        # input goal notes (Requirement 1.2.10)
        #
        self.expense_goal_notes = QLineEdit()
        self.expense_goal_notes.setMaxLength(150)

        self.expense_goal_table = QTableWidget()
        self.expense_goal_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Adding pre-determined strings for Category drop down boxes
        #
        # select goal category (Requirement 1.2.9)
        #
        for expense_index, goal_category in enumerate(self.budget.categories):
            self.expense_goal_category.addItem(goal_category)
            expense_index += 1

        # Create buttons
        self.add_goal_button = QPushButton("Add Goal")  # add expense goal (Requirement 1.2.11)
        self.update_cell_button = QPushButton("Update Cell")  # update expense goal (Requirement 1.2.13)
        self.remove_goal_button = QPushButton("Remove Goal")

        # Connect buttons to their respective functions
        self.add_goal_button.clicked.connect(self.add_goal)  # add expense goal (Requirement 1.2.11)

        #
        # update expense goal (Requirement 1.2.13)
        #
        self.update_cell_button.clicked.connect(lambda: self.update_goal_cell(self.expense_goal_table))

        self.remove_goal_button.clicked.connect(lambda: self.remove_from_table(self.expense_goal_table))

        # Verify goal amounts and goal date format
        #
        # input begin date (Requirement 1.2.5)
        #
        self.begin_date.editingFinished.connect(lambda: self.validate_date(self.begin_date))

        #
        # input end date (Requirement 1.2.6)
        #
        self.end_date.editingFinished.connect(lambda: self.validate_date(self.end_date))

        # self.date_spent.editingFinished.connect(lambda: self.validate_date(self.date_spent))
        #
        # input goal amount (Requirement 1.2.7)
        #
        self.goal_amount.editingFinished.connect(lambda: self.validate_amount(self.goal_amount))

        # Add Name of goal to the first row
        expense_first_row_layout = QHBoxLayout()

        #
        # input goal name (Requirement 1.2.8)
        #
        expense_first_row_layout.addWidget(QLabel("Name of Goal: "))
        expense_first_row_layout.addWidget(self.name_of_goal)

        #
        # input goal amount (Requirement 1.2.7)
        #
        expense_first_row_layout.addWidget(QLabel("Goal Amount: "))
        expense_first_row_layout.addWidget(self.goal_amount)
        expense_goal_tab_layout.addLayout(expense_first_row_layout)

        # Add Begin date and End date to the second row
        expense_second_row_layout = QHBoxLayout()

        #
        # input begin date (Requirement 1.2.5)
        #
        expense_second_row_layout.addWidget(QLabel("Begin Date: "))
        expense_second_row_layout.addWidget(self.begin_date)

        #
        # input end date (Requirement 1.2.6)
        #
        expense_second_row_layout.addWidget(QLabel("End Date: "))
        expense_second_row_layout.addWidget(self.end_date)

        expense_goal_tab_layout.addLayout(expense_second_row_layout)

        # Add Amount spent, Date spent, and amount goal to the third row
        expense_third_row_layout = QHBoxLayout()
        # expense_third_row_layout.addWidget(QLabel("Date Spent: "))
        # expense_third_row_layout.addWidget(self.date_spent)

        #
        # select goal category (Requirement 1.2.9)
        #
        expense_third_row_layout.addWidget(QLabel("Category: "))
        expense_third_row_layout.addWidget(self.expense_goal_category)

        #
        # input goal notes (Requirement 1.2.10)
        #
        expense_third_row_layout.addWidget(QLabel("Expense Goal Note: "))
        expense_third_row_layout.addWidget(self.expense_goal_notes)

        expense_goal_tab_layout.addLayout(expense_third_row_layout)

        # Add buttons to add a goal, edit, remove, or save a goal
        expense_goal_tab_layout.addWidget(self.add_goal_button)
        expense_goal_tab_layout.addWidget(self.remove_goal_button)

        # Set the number of columns to match the expected input and name them.
        self.expense_goal_table.setColumnCount(8)
        self.expense_header_labels = ["Goal Name", "Category", "Begin Date", "End Date", "Current \n Amount",
                                      "Goal Amount", " Remaining \n Balance", "Note"]
        self.expense_goal_table.setHorizontalHeaderLabels(self.expense_header_labels)

        # Add display to show list of transactions and allow for default sorting
        expense_goal_tab_layout.addWidget(self.expense_goal_table)
        self.expense_goal_table.setSortingEnabled(True)  # sort goals (Requirement 1.2.12)

        # Add update cell button to bottom of window
        expense_goal_tab_layout.addWidget(self.update_cell_button)  # update expense goal (Requirement 1.2.13)

        self.show()
        '''
        This ends the goal tab section
        '''

    '''
    This section adds and removes and edits from the different tables
    '''

    # this looks to make sure certain items in the transaction are not empty, then adds them to the budget class
    #
    # add transaction (requirement 1.1.8)
    #
    def add_transaction(self):
        """
        Adds a new transaction to the budget and updates relevant components.

        :return: None
        """
        if not self.line_empty(self.transaction_amount.text(), "Transaction Amount"):
            return

        if not self.line_empty(self.date.text(), "Transaction Date"):
            return

        # Create a new Transaction object.
        transaction = Transaction()

        # Update transaction object.
        transaction.edit(self.transaction_type.currentText(), self.date.text(), float(self.transaction_amount.text()),
                         self.vendor.text(), self.transaction_category.currentText(), self.transaction_note.text(),
                         self.expense_goals.currentText())

        # Update budget class. This will allow us to save and load budgets easier as well as update the table.
        self.budget.add_transaction(transaction)

        # if it's a new goal, and it's an actual goal, then we need to manipulate the goal
        if transaction.get("expense_goal") != "N/A":
            # handling updating goal amounts within goal object when transaction is added to budget
            # goal = self.budget.new_transaction_update_goal_amount(transaction)
            goal = self.budget.get_expense_goal(transaction.expense_goal)
            self.add_expense_goal_list_to_table(goal)

        # Pull the attributes out from both expense and income lists and insert them into the table.
        self.add_transaction_lists_to_table(transaction)

        # Update table
        self.transaction_table.update()
        self.expense_goal_table.update()

        # Clear fields for end user
        self.clear_transaction_ui()

        # Update total expenses, income and balance
        self.update_under_table_hud()

    # Removes rows from the table first, and then removes them from the budget class list/dict
    #
    # remove transaction (requirement 1.1.9)
    #
    def remove_from_table(self, table: QTableWidget):
        """
        Removes the selected row from the provided QTableWidget and updates the associated budget data.

        :param table: The QTableWidget from which to remove the selected row.
        :type table: QTableWidget
        :return: None
        """

        # Set selected item to the currently clicked item
        selected_item = table.selectedItems()

        if selected_item:
            # gives us the row int, which is important for removing income/expense objects
            selected_row = selected_item[0].row()

            remove_from_table = table.item(selected_row, 0)
            budget_obj = remove_from_table.data(Qt.UserRole)

            # Remove the row from the table itself
            table.removeRow(selected_row)

            # Check to see if its a transaction or a goal. Perform actions as neccessary
            if isinstance(budget_obj, transaction.Transaction):
                # Remove the transaction object from its respective list
                #
                # remove transaction (requirement 1.1.9)
                #
                if budget_obj.expense_goal != "N/A":
                    goal = self.budget.get_expense_goal(budget_obj.expense_goal)
                    self.budget.update_transaction_expense_goal_cell(budget_obj)
                    self.add_expense_goal_list_to_table(goal)
                self.budget.delete_transaction(budget_obj)
                self.update_under_table_hud()
            else:
                # Remove the goal object from its respective list
                self.budget.delete_expense_goal(budget_obj.name)

                # set all transactions that have this goal in the last column to "N/A"
                set_na_transactions = self.transaction_table.findItems(budget_obj.name, Qt.MatchContains)

                for transaction_item in set_na_transactions:
                    row = transaction_item.row()
                    column = transaction_item.column()
                    change_in_table = self.transaction_table.item(row, 0)
                    trans_obj = change_in_table.data(Qt.UserRole)

                    if column == 6:
                        self.transaction_table.setItem(row, column, QTableWidgetItem("N/A"))
                        trans_obj.update_attribute("expense_goal", "N/A")

                # update the goal Q Combo Box
                self.expense_goals.clear()
                self.expense_goals.addItem("N/A")
                for expense_goal_index, expense_goal_name in enumerate(self.budget.expense_goals):
                    self.expense_goals.addItem(expense_goal_name)

        else:
            QMessageBox.warning(self, "Remove from table", "No row was selected.")
            return

    # adds en expense goal to the table and dictionary in the budget class
    #
    # add expense goal (Requirement 1.2.11)
    #
    def add_goal(self):
        """
        Adds a new expense goal to the budget and updates relevant components.

        :return: None
        """

        # Make sure no lines are empty as all need to be filled out to add a goal
        if not self.line_empty(self.name_of_goal.text(), "Name of Goal"):
            return
        if not self.line_empty(self.goal_amount.text(), "Goal Amount"):
            return
        if not self.line_empty(self.begin_date.text(), "Begin Date"):
            return
        if not self.line_empty(self.end_date.text(), "End Date"):
            return
        # if not self.line_empty(self.date_spent.text(), "Date Spent"):
        #   return

        # create the goal object, then add it to the dictionary
        goal = Goal()
        goal.init_goal(self.name_of_goal.text(), self.begin_date.text(), self.end_date.text(),
                       self.expense_goal_notes.text(), (float(self.goal_amount.text())), "12/12/12",
                       self.expense_goal_category.currentText())

        # Update budget class. This will allow us to save and load budgets easier as well as update the table
        try:
            self.budget.add_expense_goal(goal)
        except:
            QMessageBox.warning(self, "Non-unique Name of Goal",
                                f"Name of Goal: {self.name_of_goal.text()} is not unique. "
                                f"Enter unique name.")
            self.name_of_goal.clear()
            self.name_of_goal.setFocus()
            return

        # Pull the attributes out of the goal list and insert them into the table
        self.add_expense_goal_list_to_table(goal)

        # Update table
        self.expense_goal_table.update()

        # Clear fields for end user
        self.clear_expense_goal_ui()
        self.expense_goals.clear()
        self.expense_goals.addItem("N/A")
        for expense_goal_index, expense_goal_name in enumerate(self.budget.expense_goals):
            self.expense_goals.addItem(expense_goal_name)

    # adds the transaction list from the budget class to the transaction table in the GUI
    #
    # add transaction (requirement 1.1.8)
    #
    def add_transaction_lists_to_table(self, transaction_object: Transaction):
        """
        Adds a transaction object to the expense transaction table and updates the table.

        :param transaction_object: The Transaction object to be added to the table.
        :type transaction_object: Transaction
        :return: None
        """

        # turn off sorting so we don't add blank cells
        self.transaction_table.setSortingEnabled(False)

        # Create a variable so we can store the object into the QTableWidget.
        # This will allow us to pull this exact object back out when we delete it from the table.
        transaction_object_date = QTableWidgetItem(transaction_object.date)
        transaction_object_date.setData(Qt.UserRole, transaction_object)

        # Add expense transaction to the table
        row_position = self.transaction_table.rowCount()
        self.transaction_table.insertRow(row_position)

        # Use row_position as the row index for setting items
        self.transaction_table.setItem(row_position, 0, transaction_object_date)
        self.transaction_table.setItem(row_position, 1, QTableWidgetItem(transaction_object.transaction_type))
        self.transaction_table.setItem(row_position, 2, QTableWidgetItem(str(transaction_object.amount)))
        self.transaction_table.setItem(row_position, 3, QTableWidgetItem(transaction_object.vendor))
        self.transaction_table.setItem(row_position, 4, QTableWidgetItem(transaction_object.category))
        self.transaction_table.setItem(row_position, 5, QTableWidgetItem(transaction_object.note))
        self.transaction_table.setItem(row_position, 6, QTableWidgetItem(transaction_object.expense_goal))

        self.transaction_table.setSortingEnabled(True)

    # Add the expense goal dictionary to the expense goal table in the GUI
    #
    # add expense goal (Requirement 1.2.11)
    #
    def add_expense_goal_list_to_table(self, goal_object: Goal):
        """
        Adds an expense goal object to the expense goal table and updates the table.

        :param goal_object: The Goal object to be added to the table.
        :type goal_object: Goal
        :return: None
        """

        # turn of sorting so we don't add blank cells
        self.expense_goal_table.setSortingEnabled(False)

        # get the original name out of the goal object if there is one. We need it for updating a goal that already
        # exists
        goal_name = goal_object.name
        goal_amount_update = self.expense_goal_table.findItems(goal_name, Qt.MatchContains)

        # Add expense goal to table. If == already existing else == new expense goal
        if goal_amount_update:
            for item in goal_amount_update:
                row = item.row()
                column = item.column()
                if column == 0:
                    row_position = row
            expense_goal_object_name = QTableWidgetItem(goal_name)
            expense_goal_object_name.setData(Qt.UserRole, goal_object)
        else:
            row_position = self.expense_goal_table.rowCount()
            # Create a variable, so we can store the object into the QTableWidget. This will allow us to pull this
            # exact object back out when we delete it from the table.
            expense_goal_object_name = QTableWidgetItem(goal_object.name)
            expense_goal_object_name.setData(Qt.UserRole, goal_object)
            # start balance is now set in init_goal() method of goal object
            # goal_object.set_startBalance()
            self.expense_goal_table.insertRow(row_position)

        # Use row-position as the row index for setting items
        self.expense_goal_table.setItem(row_position, 0, expense_goal_object_name)
        self.expense_goal_table.setItem(row_position, 1, QTableWidgetItem(goal_object.category))
        self.expense_goal_table.setItem(row_position, 2, QTableWidgetItem(goal_object.start_date))
        self.expense_goal_table.setItem(row_position, 3, QTableWidgetItem(goal_object.end_date))
        self.expense_goal_table.setItem(row_position, 4, QTableWidgetItem(str(goal_object.current_amount)))
        self.expense_goal_table.setItem(row_position, 5, QTableWidgetItem(str(goal_object.target_amount)))
        self.expense_goal_table.setItem(row_position, 6, QTableWidgetItem(str(goal_object.amount_left)))
        self.expense_goal_table.setItem(row_position, 7, QTableWidgetItem(goal_object.note))

        # turn the sorting back on
        self.expense_goal_table.setSortingEnabled(True)

    # updates a cell on the transaction table. Checks for appropriate data validation through method calls
    #
    # update transaction (requirement 1.3.3)
    #
    def update_transaction_cell_method(self, table: QTableWidget):
        """
        Opens a dialog box to update the content of a selected cell in the provided QTableWidget.

        :param table: The QTableWidget containing the cell to be updated.
        :type table: QTableWidget
        :return: None
        """

        # Set selected item to the currently clicked item
        selected_item = table.currentItem()

        # get row and column from the selected item, otherwise no cell was selected
        if selected_item:
            current_row = table.row(selected_item)
            current_column = table.column(selected_item)
        else:
            QMessageBox.warning(self, "Update Cell", "No Cell was selected")
            return

        # create a dialog box to update the cells
        update_cell_dialog = QDialog()
        update_cell_dialog.setWindowTitle(f"{self.expense_header_labels[current_column]} Cell Update")
        update_cell_dialog.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)
        update_cell_dialog.resize(200, 75)

        # update lists and validate information being input
        #
        # save transaction updates (requirement 1.3.3)
        #
        self.save_transaction_changes(update_cell_dialog, current_row, current_column)

    # called from the method above
    #
    # save transaction updates (requirement 1.3.3)
    #
    def save_transaction_changes(self, update_cell_dialog: QDialog, row: int, column: int):
        """
        Opens a dialog box for updating the content of a selected cell in the transaction table.

        :param update_cell_dialog: The QDialog instance for updating the cell content.
        :type update_cell_dialog: QDialog
        :param row: The row index of the selected cell.
        :type row: int
        :param column: The column index of the selected cell.
        :type column: int
        :return: None
        """

        # create save button for update_cell_dialog
        save_changes_button = QPushButton("Save")

        # get the goal object out of the table. Stored in the first column
        cell_to_update_obj = self.transaction_table.item(row, 0)
        transaction_obj = cell_to_update_obj.data(Qt.UserRole)

        # Create the layout for the contents of the dialog box
        layout = QVBoxLayout()
        prompt = QLabel("Correct Cell Information Below")

        # check to see if the new line, for current column, matches data restrictions
        if column in (0, 2, 3, 5):
            new_input_line = QLineEdit()
            new_input_line.setText(self.transaction_table.item(row, column).text())
            insert_layout(update_cell_dialog, new_input_line, save_changes_button, layout, prompt)

            # validate that the updates hold the same restrictions as initial input
            save_changes_button.clicked.connect(lambda: self.validate_transaction_updates(column, new_input_line,
                                                                                          update_cell_dialog))

        elif column == 4:
            new_input_line = QComboBox()
            for index, category in enumerate(self.budget.categories):
                new_input_line.addItem(category)
                index += 1
            insert_layout(update_cell_dialog, new_input_line, save_changes_button, layout, prompt)

            save_changes_button.clicked.connect(lambda: update_cell_dialog.accept())
        elif column == 1:
            new_input_line = QComboBox()
            new_input_line.addItems(["Expense", "Income"])
            insert_layout(update_cell_dialog, new_input_line, save_changes_button, layout, prompt)

            save_changes_button.clicked.connect(lambda: update_cell_dialog.accept())
        elif column == 6:
            new_input_line = QComboBox()
            new_input_line.addItem("N/A")
            for expense_goal_index, expense_goal_name in enumerate(self.budget.expense_goals):
                new_input_line.addItem(expense_goal_name)
            insert_layout(update_cell_dialog, new_input_line, save_changes_button, layout, prompt)

            save_changes_button.clicked.connect(lambda: update_cell_dialog.accept())

        result = update_cell_dialog.exec()

        # edit the correct transaction object attribute
        if result == QDialog.Accepted:
            if column == 0:
                transaction_obj.update_attribute("date", new_input_line.text())
                self.transaction_table.setItem(row, column, QTableWidgetItem(new_input_line.text()))
            elif column == 1:
                self.budget.delete_transaction(transaction_obj)
                # delete_transaction auto updates goal amounts
                # if transaction_obj.expense_goal != "N/A":
                #    self.budget.update_transaction_expense_goal_cell(transaction_obj)
                transaction_obj.update_attribute("transaction_type", new_input_line.currentText())
                self.transaction_table.setItem(row, column, QTableWidgetItem(new_input_line.currentText()))
                self.budget.add_transaction(transaction_obj)
                self.update_under_table_hud()
                if transaction_obj.expense_goal != "N/A":
                    # add_transaction auto updates goal amounts
                    # self.budget.new_transaction_update_goal_amount(transaction_obj)
                    goal = self.budget.get_expense_goal(transaction_obj.expense_goal)
                    self.add_expense_goal_list_to_table(goal)
                    self.update_under_table_hud()
            elif column == 2:
                self.budget.update_transaction_expense_goal_cell(transaction_obj)
                transaction_obj.update_attribute("amount", float(new_input_line.text()))
                self.transaction_table.setItem(row, column, QTableWidgetItem(new_input_line.text()))
                self.add_expense_goal_list_to_table(self.budget.new_transaction_update_goal_amount(transaction_obj))
            elif column == 3:
                transaction_obj.update_attribute("vendor", new_input_line.text())
                self.transaction_table.setItem(row, column, QTableWidgetItem(new_input_line.text()))
            elif column == 4:
                transaction_obj.update_attribute("category", new_input_line.currentText())
                self.transaction_table.setItem(row, column, QTableWidgetItem(new_input_line.currentText()))
            elif column == 5:
                transaction_obj.update_attribute("note", new_input_line.text())
                self.transaction_table.setItem(row, column, QTableWidgetItem(new_input_line.text()))
            else:
                # updating the expense goal column, and making sure the goal on the back end is updated correctly.
                # Checks to see if leaving from N/A (default) to actual goal, from goal to goal, or from goal to N/A
                # Each one will require different updates to the goal.
                original_trans_string = transaction_obj.expense_goal
                new_trans_string = new_input_line.currentText()
                if new_trans_string != original_trans_string:
                    if new_trans_string != "N/A" and original_trans_string == "N/A":
                        self.budget.delete_transaction(transaction_obj)
                        transaction_obj.update_attribute("expense_goal", new_input_line.currentText())
                        self.budget.add_transaction(transaction_obj)
                        self.transaction_table.setItem(row, column, QTableWidgetItem(new_input_line.currentText()))
                        self.add_expense_goal_list_to_table(self.budget.get_expense_goal(new_trans_string))
                    elif new_trans_string != "N/A" and original_trans_string != "N/A":
                        goal = self.budget.get_expense_goal(transaction_obj.expense_goal)
                        self.budget.update_transaction_expense_goal_cell(transaction_obj)
                        self.add_expense_goal_list_to_table(goal)
                        self.budget.delete_transaction(transaction_obj)
                        transaction_obj.update_attribute("expense_goal", new_input_line.currentText())
                        self.budget.add_transaction(transaction_obj)
                        self.transaction_table.setItem(row, column, QTableWidgetItem(new_input_line.currentText()))
                        self.add_expense_goal_list_to_table(self.budget.new_transaction_update_goal_amount(transaction_obj))
                    elif new_trans_string == "N/A":
                        goal = self.budget.get_expense_goal(transaction_obj.expense_goal)
                        self.budget.update_transaction_expense_goal_cell(transaction_obj)
                        self.add_expense_goal_list_to_table(goal)
                        transaction_obj.update_attribute("expense_goal", new_input_line.currentText())
                        self.transaction_table.setItem(row, column, QTableWidgetItem(new_input_line.currentText()))
                        print("N/A")

    # calls methods below to verify actual data validation
    #
    # update transaction (requirement 1.3.3)
    #
    def validate_transaction_updates(self, column: int, new_input_line: QLineEdit, update_cell_dialog: QDialog):
        """
        Validates data updates for a selected cell in the transaction table.

        :param column: The column index of the selected cell.
        :type column: int
        :param new_input_line: The QLineEdit containing the new input data.
        :type new_input_line: QLineEdit
        :param update_cell_dialog: The QDialog instance for updating the cell content.
        :type update_cell_dialog: QDialog
        :return: None
        """

        # validate the data from the transaction table
        if column == 0:
            if self.validate_date(new_input_line):
                update_cell_dialog.accept()
                return
            return
        elif column == 2:
            if self.validate_amount(new_input_line):
                update_cell_dialog.accept()
                return

        # no other columns require data validation
        update_cell_dialog.accept()

    # updates a cell on the expense goals table. Checks for appropriate data validation through method calls
    #
    # update expense goal (Requirement 1.2.13)
    #
    def update_goal_cell(self, table: QTableWidget):
        """
        Opens a dialog box to update the content of a selected cell in the provided QTableWidget for expense goals.

        :param table: The QTableWidget containing the cell to be updated.
        :type table: QTableWidget
        :return: None
        """

        # Set selected item to the currently clicked item
        selected_item = table.currentItem()

        # get the current row and column for the selected cell
        if selected_item:
            current_row = table.row(selected_item)
            current_column = table.column(selected_item)
        else:
            QMessageBox.warning(self, "Update Cell", "No Cell was selected")
            return

        # Current amount and balance are not able to be updated directly by the end user.
        #
        # current amount and balance un-editable (Requirement 1.2.16)
        #
        if current_column in (4, 6):
            QMessageBox.warning(self, "None Editable Cell", f"{self.expense_header_labels[current_column]} "
                                f"is not an editable cell")
            return

        # create a dialog box to update the cells
        update_cell_dialog = QDialog()
        update_cell_dialog.setWindowTitle(f"{self.expense_header_labels[current_column]} Cell Update")

        #
        # cancel goal cell changes (Requirement 1.2.14)
        #
        update_cell_dialog.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)

        update_cell_dialog.resize(200, 75)

        # update lists and validate information being input
        #
        # save goal changes (Requirement 1.2.14)
        #
        self.save_goal_changes(update_cell_dialog, current_row, current_column, table)

    # called from the method above
    #
    # save goal changes (Requirement 1.2.14)
    #
    def save_goal_changes(self, update_cell_dialog: QDialog, row: int, column: int, table: QTableWidget):
        """
        Saves changes made in the expense goal cell update dialog and updates the expense goal table.

        :param update_cell_dialog: The QDialog instance for updating the cell content.
        :type update_cell_dialog: QDialog
        :param row: The row index of the selected cell.
        :type row: int
        :param column: The column index of the selected cell.
        :type column: int
        :param table: The QTableWidget containing the cell to be updated.
        :type table: QTableWidget
        :return: None
        """

        # create save button for update_cell_dialog
        save_changes_button = QPushButton("Save")

        # get the goal object out of the table. Stored in the first column
        cell_to_update_obj = self.budget.get_expense_goal(self.expense_goal_table.item(row, 0).text())

        # Create the layout for the contents of the dialog box
        layout = QVBoxLayout()
        prompt = QLabel("Correct Cell Information Below")

        # treat these columns differently from the note column. Need to enforce character limit on the note
        if column in (0, 2, 3, 5):
            new_input_line = QLineEdit()
            new_input_line.setText(table.item(row, column).text())
            insert_layout(update_cell_dialog, new_input_line, save_changes_button, layout, prompt)

            # validate that the updates hold the same restrictions as initial input
            save_changes_button.clicked.connect(lambda: self.validate_goal_updates(column, new_input_line,
                                                                                   update_cell_dialog))
        elif column == 7:
            new_input_line = QLineEdit()
            new_input_line.setText(table.item(row, column).text())
            new_input_line.setMaxLength(150)

            insert_layout(update_cell_dialog, new_input_line, save_changes_button, layout, prompt)

            save_changes_button.clicked.connect(lambda: update_cell_dialog.accept())
        else:
            new_input_line = QComboBox()
            for index, category in enumerate(self.budget.categories):
                new_input_line.addItem(category)
                index += 1
            insert_layout(update_cell_dialog, new_input_line, save_changes_button, layout, prompt)

            save_changes_button.clicked.connect(lambda: update_cell_dialog.accept())

        result = update_cell_dialog.exec()

        # edit the correct goal object attribute
        if result == QDialog.Accepted:
            if column == 0:

                # create new object with previous cells attributes
                new_obj = Goal()
                new_obj.init_goal(new_input_line.text(), cell_to_update_obj.get("start_date"),
                                  cell_to_update_obj.get("end_date"), cell_to_update_obj.get("note"),
                                  cell_to_update_obj.get("target_amount"), cell_to_update_obj.get("date_spent"),
                                  cell_to_update_obj.get("category"))
                new_obj.transactions = cell_to_update_obj.transactions

                # remove the previous object from the table. This will also delete it from the dictionary
                self.remove_from_table(self.expense_goal_table)

                # add "new" goal to the table
                self.add_expense_goal_list_to_table(new_obj)

                # add the goal to the dictionary
                self.budget.add_expense_goal(new_obj)
            elif column == 1:
                cell_to_update_obj.update_attribute("category", new_input_line.currentText())
                self.expense_goal_table.setItem(row, column, QTableWidgetItem(new_input_line.currentText()))
            elif column == 2:
                cell_to_update_obj.update_attribute("start_date", new_input_line.text())
                self.expense_goal_table.setItem(row, column, QTableWidgetItem(new_input_line.text()))
            elif column == 3:
                cell_to_update_obj.update_attribute("end_date", new_input_line.text())
                self.expense_goal_table.setItem(row, column, QTableWidgetItem(new_input_line.text()))
            elif column == 5:
                cell_to_update_obj.update_attribute("target_amount", new_input_line.text())
                self.expense_goal_table.setItem(row, column, QTableWidgetItem(new_input_line.text()))
                self.expense_goal_table.setItem(row, 6, QTableWidgetItem(str(cell_to_update_obj.get("amount_left"))))
            elif column == 7:
                cell_to_update_obj.update_attribute("note", new_input_line.text())
                self.expense_goal_table.setItem(row, column, QTableWidgetItem(new_input_line.text()))

        # update the goal Q Combo Box
        self.expense_goals.clear()
        self.expense_goals.addItem("N/A")
        for expense_goal_index, expense_goal_name in enumerate(self.budget.expense_goals):
            self.expense_goals.addItem(expense_goal_name)

    # calls methods below to verify actual data validation
    #
    # update expense goal (Requirement 1.2.13)
    #
    def validate_goal_updates(self, column: int, new_input: QLineEdit, update_cell_dialog: QDialog):
        """
        Validates data updates for a selected cell in the expense goal table.

        :param column: The column index of the selected cell.
        :type column: int
        :param new_input: The QLineEdit containing the new input data.
        :type new_input: QLineEdit
        :param update_cell_dialog: The QDialog instance for updating the cell content.
        :type update_cell_dialog: QDialog
        :return: None
        """
        # look for specific columns to call the correct data validation method
        if self.line_empty(new_input.text(), self.expense_header_labels[column]):
            if column in (2, 3):
                if self.validate_date(new_input):
                    update_cell_dialog.accept()
                    return
                return
            elif column == 5:
                if self.validate_amount(new_input):
                    update_cell_dialog.accept()
                    return
                return
            else:
                if new_input.text().lower() in self.budget.expense_goals:
                    QMessageBox.warning(self, "Non-unique Name of Goal",
                                        f"Name of Goal: {new_input.text()} is not unique. "
                                        f"Enter unique name.")
                    return
            update_cell_dialog.accept()

    '''
    end adding and removing from tables
    '''
    '''
    save, delete, and load budget section
    '''

    # save, load, delete, and extract all call the budget method. Load adds the lists back to the tables
    #
    # save budget (Requirement 1.3.6)
    #
    def save_budget_dialog(self):
        """
        Opens a dialog box to save the current budget to a specified file path.

        :return: None
        """

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Budget", "", "Text Files (*.txt)")
        if file_path:
            budget_name = os.path.splitext(os.path.basename(file_path))[0]
            budget_name += ".txt"
            self.budget.save_budget(budget_name)

    #
    # load budget (Requirement 1.3.7)
    #
    def load_budget_dialog(self):
        """
        Opens a dialog box to load a budget from a specified file path.

        :return: None
        """

        file_path, _ = QFileDialog.getOpenFileName(self, "Load Budget", "", "Text Files (*.txt)")
        if file_path:
            budget_name = os.path.splitext(os.path.basename(file_path))[0]
            budget_name += ".txt"
            self.budget.load_budget(budget_name)

        # this will load the expense objects first
        for transaction_object in self.budget.expense_transactions:
            self.add_transaction_lists_to_table(transaction_object)

        # then the income transactions
        for transaction_object in self.budget.income_transactions:
            self.add_transaction_lists_to_table(transaction_object)

        # finally the goal objects
        for expense_goal in self.budget.expense_goals.values():
            self.add_expense_goal_list_to_table(expense_goal)

        self.update_under_table_hud()

    #
    # delete budget (Requirement 1.3.8)
    #
    def delete_budget_dialog(self):
        """
        Opens a dialog box to delete a budget from a specified file path.

        :return: None
        """

        file_path, _ = QFileDialog.getOpenFileName(self, "Delete Budget", "", "Text Files (*.txt)")
        if file_path:
            budget_name = os.path.splitext(os.path.basename(file_path))[0]
            budget_name += ".txt"
            self.budget.delete_budget(budget_name)

    #
    # export transactions (Requirement 1.3.5)
    #
    def export_budget_dialog(self):
        """
        Opens a dialog box to export the budget transactions to a specified Excel file.

        :return: None
        """
        # file_path, _ = QFileDialog.getOpenFileName(self, "Export Budget", "", "Excel Files (*.xlsx)")
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Budget", "", "Excel Files (*.xlsx)")
        if file_path:
            budget_name = os.path.splitext(os.path.basename(file_path))[0]
            budget_name += ".xlsx"
            self.budget.export_transactions(budget_name)

    '''
    end save, delete and load budget section
    '''
    '''
    begin data validation section
    '''

    def validate_date(self, line_edit: QLineEdit):
        """
        Validates if the input in a QLineEdit represents a date in the format DD/MM/YY.

        :param line_edit: The QLineEdit containing the date text to be validated.
        :type line_edit: QLineEdit
        :return: True if the date is valid, False otherwise.
        """

        date_text = line_edit.text()

        date_pattern = re.compile(r'\d{2}\/\d{2}/\d{2}')

        if not re.match(date_pattern, date_text):
            # Show what format it should look like
            QMessageBox.warning(self, "Invalid Date", "Please enter a date in the format DD/MM/YY")

            # Clear the QLineEdit
            line_edit.clear()
            line_edit.setFocus()

            return False
        return True

    def validate_amount(self, line_edit: QLineEdit):
        """
        Validates if the input in a QLineEdit represents a valid float amount.

        :param line_edit: The QLineEdit containing the amount text to be validated.
        :type line_edit: QLineEdit
        :return: True if the amount is valid, False otherwise.
        """

        amount = line_edit.text()

        try:
            check_for_float_type = float(amount)
            check_for_float_type = "{:.2f}".format(check_for_float_type)
            line_edit.setText(check_for_float_type)
            return True
        except:
            QMessageBox.warning(self, "Invalid Amount", "Must be a float, with no characters except a decimal point")
            # Clear the QLineEdit
            line_edit.clear()
            line_edit.setFocus()
            return False

    def line_empty(self, line_text: str, line_name: str):
        """
        Checks if a line (text input) is empty and displays a warning message if it is.

        :param line_text: The text content of the line to be checked.
        :type line_text: str
        :param line_name: The name or description of the line, used in the warning message.
        :type line_name: str
        :return: True if the line is not empty, False otherwise.
        """
        if line_text == "":
            QMessageBox.warning(self, f"Blank {line_name}", f"{line_name} must not be empty.")
            # Transaction Tracker tab
            if line_name == "Transaction Date":
                self.date.setFocus()  # Input a date (Requirement 1.1.3)
            elif line_name == "Transaction Amount":
                self.transaction_amount.setFocus()  # Input a float amount (Requirement 1.1.5)
            # Expense Goal tab
            elif line_name == "Name of Goal":  # input goal name (Requirement 1.2.8)
                self.name_of_goal.setFocus()
            elif line_name == "Goal Amount":  # input goal amount (Requirement 1.2.7)
                self.goal_amount.setFocus()
            elif line_name == "Begin Date":  # input begin date (Requirement 1.2.5)
                self.begin_date.setFocus()
            elif line_name == "End Date":  # input end date (Requirement 1.2.6)
                self.end_date.setFocus()
            # elif line_name == "Date Spent":
            #   self.date_spent.setFocus()
            # return False
        else:
            return True
    '''
    end data validation section
    '''
    '''
    begin updating and clearing UI as needed
    '''
    def update_under_table_hud(self):
        """
        Updates the labels under the table with current budget information.

        :return: None
        """
        #
        # total expenses under table (Requirement 1.1.10)
        #
        self.total_expenses_label.setText(f"Total Expenses: {self.budget.total_expenses}")

        #
        # total income under table (Requirement 1.2.3)
        #
        self.total_income_label.setText(f"Total Income: {self.budget.total_income}")

        self.balance_label.setText(f"Balance: {self.budget.balance}")

    def clear_transaction_ui(self):
        """
        Clears the user interface elements related to transaction input.

        :return: None
        """

        self.transaction_amount.clear()  # Input a float amount (Requirement 1.1.5)
        self.date.clear()  # Input a date (Requirement 1.1.3)
        self.transaction_note.clear()  # Input a note (Requirement 1.1.6)
        self.vendor.clear()  # Input a Vendor (Requirement 1.1.4)
        self.transaction_type.setFocus()  # Select a transaction type (Requirement 1.1.2)

    def clear_expense_goal_ui(self):
        """
        Clears the user interface elements related to expense goal input.

        :return: None
        """

        self.name_of_goal.clear()  # input goal name (Requirement 1.2.8)
        self.goal_amount.clear()  # input goal amount (Requirement 1.2.7)
        self.begin_date.clear()  # input begin date (Requirement 1.2.5)
        self.end_date.clear()  # input end date (Requirement 1.2.6)
        # self.date_spent.clear()
        self.expense_goal_notes.clear()  # input goal notes (Requirement 1.2.10)
    '''
    end updating and clearing UI as needed
    '''


#
#  Open Application (Requirement 1.1.1)
#
if __name__ == "__main__":
    app = QApplication([])
    window = BudgetTrackerApp()
    app.exec_()
