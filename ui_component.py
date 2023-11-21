# ui_component.py
import operator
import os, re
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, \
    QListWidgetItem, QMessageBox, QFileDialog, QComboBox, QTableWidget, QTableWidgetItem, QTabWidget, QDialog, \
    QAbstractItemView, QAction, QMainWindow, QHeaderView

import transaction
from transaction import Transaction
from budget import Budget
from goal import Goal


def insert_layout(update_cell_dialog, new_input_line, save_changes_button, layout, prompt):
    save_layout_first_row = QHBoxLayout()  # Create a QHBoxLayout instance
    save_layout_first_row.addWidget(new_input_line)

    save_layout_second_row = QHBoxLayout()  # Create a QHBoxLayout instance
    save_layout_second_row.addWidget(save_changes_button)

    layout.addWidget(prompt)
    layout.addLayout(save_layout_first_row)
    layout.addLayout(save_layout_second_row)

    update_cell_dialog.setLayout(layout)


class BudgetTrackerApp(QMainWindow):
    # Import global row, transaction, and budget variable. This will make manipulating these in the methods much easier
    row = 0
    budget = Budget()
    sort_order = None

    def __init__(self):
            super().__init__()

            '''
            This section is meant to assign the values to the initial windows and tabs. 
            '''
            self.last_clicked_column = None

            # Create the two tabs
            self.budget_tracker_tab = QWidget()
            self.expense_goal_tab = QWidget()

            # Set up the layout
            budget_tracker_tab_layout = QVBoxLayout()
            self.budget_tracker_tab.setLayout(budget_tracker_tab_layout)

            expense_goal_tab_layout = QVBoxLayout()
            self.expense_goal_tab.setLayout(expense_goal_tab_layout)

            # Create a QTabWidget and add the tabs
            self.tabs = QTabWidget(self)
            self.tabs.addTab(self.budget_tracker_tab, "Transaction Tracker")
            self.tabs.addTab(self.expense_goal_tab, "Expense Goals")

            self.setCentralWidget(self.tabs)  # Set the QTabWidget as the central widget

            self.setWindowTitle("Budget Tracker")
            self.setGeometry(900, 200, 800, 600)

            # Create a menu bar
            menubar = self.menuBar()

            # Create a File menu
            file_menu = menubar.addMenu('File')

            # create actions to add to the File menu
            save_action = QAction('Save', self)
            save_action.triggered.connect(self.save_budget_dialog)

            load_action = QAction('Load', self)
            load_action.triggered.connect(self.load_budget_dialog)

            delete_action = QAction('Delete', self)
            delete_action.triggered.connect(self.delete_budget_dialog)

            export_action = QAction('Export to Excel', self)
            export_action.triggered.connect(self.export_budget_dialog)

            # Add actions to the File menu
            file_menu.addAction(save_action)
            file_menu.addAction(load_action)
            file_menu.addAction(delete_action)
            file_menu.addAction(export_action)

            '''
            Begin block of code for the Transaction tracker. 
            '''
            # UI Widgets
            self.transaction_type = QComboBox()
            self.date = QLineEdit()
            self.vendor = QLineEdit()
            self.transaction_amount = QLineEdit()
            self.transaction_note = QLineEdit()
            self.transaction_note.setMaxLength(150)
            self.transaction_category = QComboBox()
            self.expense_goals = QComboBox()
            self.expense_goals.setFixedWidth(100)
            self.transaction_table = QTableWidget()
            self.transaction_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.total_expenses_label = QLabel(f"Total Expenses: {self.budget.total_expenses}")
            self.total_income_label = QLabel(f"Total Income: {self.budget.total_income}")
            self.balance_label = QLabel(f"Balance: {self.budget.balance}")

            # Adding pre-determined strings for Transaction Type and Category drop down boxes
            self.transaction_type.addItem("Expense")
            self. transaction_type.addItem("Income")

            for transaction_index, transaction_category in enumerate(self.budget.categories):
                self.transaction_category.addItem(transaction_category)
                transaction_index += 1

            for expense_goal_index, expense_goal_name in enumerate(self.budget.expense_goals):
                self.expense_goals.addItem(expense_goal_name)

            self.expense_goals.addItem("N/A")

            # Create buttons
            self.add_transaction_button = QPushButton("Add Transaction")
            self.remove_transaction_button = QPushButton("Remove Transaction")
            self.update_transaction_cells = QPushButton("Update Cell")

            # Connect buttons to their respective functions
            self.add_transaction_button.clicked.connect(self.add_transaction)
            self.remove_transaction_button.clicked.connect(lambda: self.remove_from_table(self.transaction_table))
            self.update_transaction_cells.clicked.connect(lambda: self.update_transaction_cell_method(
                self.transaction_table))

            # Verify transaction amount and date format
            self.date.editingFinished.connect(lambda: self.validate_date(self.date))
            self.transaction_amount.editingFinished.connect(lambda: self.validate_amount(self.transaction_amount))

            # Add Transaction Type and date on the first row
            budget_first_row_layout = QHBoxLayout()
            budget_first_row_layout.addWidget(QLabel("Transaction Type:"))
            budget_first_row_layout.addWidget(self.transaction_type)
            budget_first_row_layout.addWidget(QLabel("Date:"))
            budget_first_row_layout.addWidget(self.date)
            budget_tracker_tab_layout.addLayout(budget_first_row_layout)

            # Add Vendor and Transaction Amount to the second row
            budget_second_row_layout = QHBoxLayout()
            budget_second_row_layout.addWidget(QLabel("Vendor:"))
            budget_second_row_layout.addWidget(self.vendor)
            budget_second_row_layout.addWidget(QLabel("Transaction Amount:"))
            budget_second_row_layout.addWidget(self.transaction_amount)
            budget_tracker_tab_layout.addLayout(budget_second_row_layout)

            # Add Transaction Note and Category drop down box onto the third row
            budget_third_row_layout = QHBoxLayout()
            budget_third_row_layout.addWidget(QLabel("Expense Goal:"))
            budget_third_row_layout.addWidget(self.expense_goals)
            budget_third_row_layout.addWidget(QLabel("Category:"))
            budget_third_row_layout.addWidget(self.transaction_category)
            budget_third_row_layout.addWidget(QLabel("Note:"))
            budget_third_row_layout.addWidget(self.transaction_note)
            budget_tracker_tab_layout.addLayout(budget_third_row_layout)

            # Add "add/remove transaction buttons" onto the fourth row
            budget_fifth_row_layout = QHBoxLayout()
            budget_fifth_row_layout.addWidget(self.add_transaction_button)
            budget_fifth_row_layout.addWidget(self.remove_transaction_button)
            budget_tracker_tab_layout.addLayout(budget_fifth_row_layout)

            # Set the number of columns to match the expected input and name them.
            self.transaction_table.setColumnCount(7)
            self.transaction_table_headers = ["Date", "Type", "Amount", "Vendor", "Category", "Note",  "Expense Goal"]
            self.transaction_table.setHorizontalHeaderLabels(self.transaction_table_headers)

            # Add display to show list of transactions and set default sortingEnabled to true
            budget_tracker_tab_layout.addWidget(self.transaction_table)
            self.transaction_table.setSortingEnabled(True)

            budget_tracker_tab_layout.addWidget(self.update_transaction_cells)

            # Add the labels to the layout
            budget_tracker_tab_layout.addWidget(self.total_expenses_label)
            budget_tracker_tab_layout.addWidget(self.total_income_label)
            budget_tracker_tab_layout.addWidget(self.balance_label)

            # allow editing of the transaction table


            '''
            end block of code for the transition tracker and begin code for expense goal.
            '''

            # UI Widgets
            self.name_of_goal = QLineEdit()
            self.begin_date = QLineEdit()
            self.end_date = QLineEdit()
            self.date_spent = QLineEdit()
            self.goal_amount = QLineEdit()
            self.expense_goal_category = QComboBox()
            self.expense_goal_notes = QLineEdit()
            self.expense_goal_notes.setMaxLength(150)
            self.expense_goal_table = QTableWidget()
            self.expense_goal_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

            # Adding pre-determined strings for Category drop down boxes
            for expense_index, goal_category in enumerate(self.budget.categories):
                self.expense_goal_category.addItem(goal_category)
                expense_index += 1

            # Create buttons
            self.add_goal_button = QPushButton("Add Goal")
            self.update_cell_button = QPushButton("Update Cell")
            self.remove_goal_button = QPushButton("Remove Goal")

            # Connect buttons to their respective functions
            self.add_goal_button.clicked.connect(self.add_goal)
            self.update_cell_button.clicked.connect(lambda: self.update_goal_cell(self.expense_goal_table))
            self.remove_goal_button.clicked.connect(lambda: self.remove_from_table(self.expense_goal_table))

            # Verify goal amounts and goal date format
            self.begin_date.editingFinished.connect(lambda: self.validate_date(self.begin_date))
            self.end_date.editingFinished.connect(lambda: self.validate_date(self.end_date))
            self.date_spent.editingFinished.connect(lambda: self.validate_date(self.date_spent))
            self.goal_amount.editingFinished.connect(lambda: self.validate_amount(self.goal_amount))

            # Add Name of goal to the first row
            expense_first_row_layout = QHBoxLayout()
            expense_first_row_layout.addWidget(QLabel("Name of Goal: "))
            expense_first_row_layout.addWidget(self.name_of_goal)
            expense_first_row_layout.addWidget(QLabel("Goal Amount: "))
            expense_first_row_layout.addWidget(self.goal_amount)
            expense_goal_tab_layout.addLayout(expense_first_row_layout)

            # Add Begin date and End date to the second row
            expense_second_row_layout = QHBoxLayout()
            expense_second_row_layout.addWidget(QLabel("Begin Date: "))
            expense_second_row_layout.addWidget(self.begin_date)
            expense_second_row_layout.addWidget(QLabel("End Date: "))
            expense_second_row_layout.addWidget(self.end_date)
            expense_goal_tab_layout.addLayout(expense_second_row_layout)

            # Add Amount spent, Date spent, and amount goal to the third row
            expense_third_row_layout = QHBoxLayout()
            expense_third_row_layout.addWidget(QLabel("Date Spent: "))
            expense_third_row_layout.addWidget(self.date_spent)
            expense_third_row_layout.addWidget(QLabel("Expense Goal Note: "))
            expense_third_row_layout.addWidget(self.expense_goal_notes)
            expense_goal_tab_layout.addLayout(expense_third_row_layout)

            # Add Category and Goal amount to the fourth row
            expense_fourth_row_layout = QHBoxLayout()
            expense_fourth_row_layout.addWidget(QLabel("Category: "))
            expense_fourth_row_layout.addWidget(self.expense_goal_category)
            expense_fourth_row_layout.addStretch(1)
            expense_fourth_row_layout.addWidget(QLabel(f"Goal Amount: ")) #Don't forget to come back to add the goal amt
            expense_fourth_row_layout.addStretch(1)
            expense_goal_tab_layout.addLayout(expense_fourth_row_layout)

            # Add buttons to add a goal, edit, remove, or save a goal
            expense_goal_tab_layout.addWidget(self.add_goal_button)
            expense_goal_tab_layout.addWidget(self.remove_goal_button)

            # Set the number of columns to match the expected input and name them.
            self.expense_goal_table.setColumnCount(8)
            self.expense_header_labels = ["Goal Name", "Category", "Begin Date", "End Date",
                                                              "Current \n Amount", "Goal Amount", " Remaining \n Balance", "Note"]
            self.expense_goal_table.setHorizontalHeaderLabels(self.expense_header_labels)

            # Add display to show list of transactions and allow for default sorting
            expense_goal_tab_layout.addWidget(self.expense_goal_table)
            self.expense_goal_table.setSortingEnabled(True)

            # Add update cell button to bottom of window
            expense_goal_tab_layout.addWidget(self.update_cell_button)

            self.show()
            '''
            This ends the goal tab section
            '''

    '''
    This section adds and removes and edits from the different tables
    '''

    # this looks to make sure certain items in the transaction are not empty, then adds them to the budget class
    def add_transaction(self):

        # Enforce both transaction and date to not be empty before adding the transaction.
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

        # if it's a new goal, and it's an actual goal, then we need to manipulate the goal
        if transaction.get("expense_goal") != "N/A":
            goal = self.budget.new_transaction_update_goal_amount(transaction)
            self.add_expense_goal_list_to_table(goal)

        # Update budget class. This will allow us to save and load budgets easier as well as update the table.
        self.budget.add_transaction(transaction)

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
    def remove_from_table(self, table):

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
                if budget_obj.expense_goal != "N/A":
                    goal = self.budget.get_expense_goal(budget_obj.expense_goal)
                    self.budget.update_transaction_expense_goal_cell(budget_obj)
                    self.add_expense_goal_list_to_table(goal)
                self.budget.delete_transaction(budget_obj)
                self.update_under_table_hud()
            else:
                # Remove the goal object from its respective list
                self.budget.delete_expense_goal(budget_obj.name)

                # update the goal Q Combo Box
                self.expense_goals.clear()
                self.expense_goals.addItem("N/A")
                for expense_goal_index, expense_goal_name in enumerate(self.budget.expense_goals):
                    self.expense_goals.addItem(expense_goal_name)

        else:
            QMessageBox.warning(self, "Remove from table", "No row was selected.")
            return

    # adds en expense goal to the table and dictionary in the budget class
    def add_goal(self):
        # Make sure no lines are empty as all need to be filled out to add a goal
        if not self.line_empty(self.name_of_goal.text(), "Name of Goal"):
            return
        if not self.line_empty(self.goal_amount.text(), "Goal Amount"):
            return
        if not self.line_empty(self.begin_date.text(), "Begin Date"):
            return
        if not self.line_empty(self.end_date.text(), "End Date"):
            return
        if not self.line_empty(self.date_spent.text(), "Date Spent"):
            return

        # create the goal object, then add it to the dictionary
        goal = Goal(self.name_of_goal.text(), self.begin_date.text(), self.end_date.text(),
                    self.expense_goal_notes.text(), (float(self.goal_amount.text())), self.date_spent.text(),
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
    def add_transaction_lists_to_table(self, transaction_object):

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
    def add_expense_goal_list_to_table(self, goal_object):

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
        else:
            row_position = self.expense_goal_table.rowCount()
            # Create a variable, so we can store the object into the QTableWidget. This will allow us to pull this
            # exact object back out when we delete it from the table.
            expense_goal_object_name = QTableWidgetItem(goal_object.name)
            expense_goal_object_name.setData(Qt.UserRole, goal_object)
            goal_object.set_startBalance()
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
    def update_transaction_cell_method(self, table):

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
        self.save_transaction_changes(update_cell_dialog, current_row, current_column)

    # called from the method above
    def save_transaction_changes(self, update_cell_dialog, row, column):
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
                if transaction_obj.expense_goal != "N/A":
                    self.budget.update_transaction_expense_goal_cell(transaction_obj)
                transaction_obj.update_attribute("transaction_type", new_input_line.currentText())
                self.transaction_table.setItem(row, column, QTableWidgetItem(new_input_line.currentText()))
                self.budget.add_transaction(transaction_obj)
                if transaction_obj.expense_goal != "N/A":
                    self.budget.new_transaction_update_goal_amount(transaction_obj)
                    goal = self.budget.get_expense_goal(transaction_obj.expense_goal)
                    self.add_expense_goal_list_to_table(goal)
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
                        transaction_obj.update_attribute("expense_goal", new_input_line.currentText())
                        self.transaction_table.setItem(row, column, QTableWidgetItem(new_input_line.currentText()))
                        self.add_expense_goal_list_to_table(self.budget.new_transaction_update_goal_amount(transaction_obj))
                        self.update
                    elif new_trans_string != "N/A" and original_trans_string != "N/A":
                        goal = self.budget.get_expense_goal(transaction_obj.expense_goal)
                        self.budget.update_transaction_expense_goal_cell(transaction_obj)
                        self.add_expense_goal_list_to_table(goal)
                        transaction_obj.update_attribute("expense_goal", new_input_line.currentText())
                        self.transaction_table.setItem(row, column, QTableWidgetItem(new_input_line.currentText()))
                        self.add_expense_goal_list_to_table(self.budget.new_transaction_update_goal_amount(transaction_obj))
                    elif new_trans_string == "N/A":
                        goal = self.budget.get_expense_goal(transaction_obj.expense_goal)
                        self.budget.update_transaction_expense_goal_cell(transaction_obj)
                        self.add_expense_goal_list_to_table(goal)
                        transaction_obj.update_attribute("expense_goal", new_input_line.currentText())
                        self.transaction_table.setItem(row, column, QTableWidgetItem(new_input_line.currentText()))



    # calls methods below to verify actual data validation
    def validate_transaction_updates(self, column, new_input_line, update_cell_dialog):
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
    def update_goal_cell(self, table):

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
        if current_column in (4, 6):
            QMessageBox.warning(self, "None Editable Cell", f"{self.expense_header_labels[current_column]} "
                                                      f"is not an editable cell")

        # create a dialog box to update the cells
        update_cell_dialog = QDialog()
        update_cell_dialog.setWindowTitle(f"{self.expense_header_labels[current_column]} Cell Update")
        update_cell_dialog.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)
        update_cell_dialog.resize(200, 75)

        # update lists and validate information being input
        self.save_goal_changes(update_cell_dialog, current_row, current_column, table)

    # called from the method above
    def save_goal_changes(self, update_cell_dialog, row, column, table):
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
            insert_layout(update_cell_dialog, new_input_line, save_changes_button,
                                                          layout, prompt)

            # validate that the updates hold the same restrictions as initial input
            save_changes_button.clicked.connect(lambda: self.validate_goal_updates(column,
                                                                              new_input_line, update_cell_dialog))
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
                new_obj = Goal(new_input_line.text(), cell_to_update_obj.get("start_date"), cell_to_update_obj.get("end_date"),
                               cell_to_update_obj.get("note"), cell_to_update_obj.get("target_amount"),
                               cell_to_update_obj.get("date_spent"), cell_to_update_obj.get("category"))

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
            elif column == 7:
                cell_to_update_obj.update_attribute("note", new_input_line.text())
                self.expense_goal_table.setItem(row, column, QTableWidgetItem(new_input_line.text()))

        # update the goal Q Combo Box
        self.expense_goals.clear()
        for expense_goal_index, expense_goal_name in enumerate(self.budget.expense_goals):
            self.expense_goals.addItem(expense_goal_name)

    # calls methods below to verify actual data validation
    def validate_goal_updates(self, column, new_input, update_cell_dialog):
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
    def save_budget_dialog(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Budget", "", "Text Files (*.txt)")
        if file_path:
            budget_name = os.path.splitext(os.path.basename(file_path))[0]
            budget_name += ".txt"
            self.budget.save_budget(budget_name)

    def load_budget_dialog(self):
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

    def delete_budget_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Delete Budget", "", "Text Files (*.txt)")
        if file_path:
            budget_name = os.path.splitext(os.path.basename(file_path))[0]
            budget_name += ".txt"
            self.budget.delete_budget.delete_encounter(budget_name)

    def export_budget_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Export Budget", "", "Excel Files (*.xlsx)")
        if file_path:
            budget_name = os.path.splitext(os.path.basename(file_path))[0]
            budget_name += ".xlsx"
            self.budget.export_transactions.delete_encounter(budget_name)


    '''
    end save, delete and load budget section
    '''
    '''
    begin data validation section
    '''

    def validate_date(self, line_edit):
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

    def validate_amount(self, line_edit):
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

    def line_empty(self, line_text, line_name):
        if line_text == "":
            QMessageBox.warning(self, f"Blank {line_name}", f"{line_name} must not be empty.")
            # Transaction Tracker tab
            if line_name == "Transaction Date":
                self.date.setFocus()
            elif line_name == "Transaction Amount":
                self.transaction_amount.setFocus()
            # Expense Goal tab
            elif line_name == "Name of Goal":
                self.name_of_goal.setFocus()
            elif line_name == "Goal Amount":
                self.goal_amount.setFocus()
            elif line_name == "Begin Date":
                self.begin_date.setFocus()
            elif line_name == "End Date":
                self.end_date.setFocus()
            elif line_name == "Date Spent":
                self.date_spent.setFocus()
            return False
        else:
            return True
    '''
    end data validation section
    '''
    '''
    begin updating and clearing UI as needed
    '''
    def update_under_table_hud(self):
        self.total_expenses_label.setText(f"Total Expenses: {self.budget.total_expenses}")
        self.total_income_label.setText(f"Total Income: {self.budget.total_income}")
        self.balance_label.setText(f"Balance: {self.budget.balance}")

    def clear_transaction_ui(self):
        self.transaction_amount.clear()
        self.date.clear()
        self.transaction_note.clear()
        self.vendor.clear()
        self.transaction_type.setFocus()

    def clear_expense_goal_ui(self):
        self.name_of_goal.clear()
        self.goal_amount.clear()
        self.begin_date.clear()
        self.end_date.clear()
        self.date_spent.clear()
        self.expense_goal_notes.clear()
    '''
    end updating and clearing UI as needed
    '''

if __name__ == "__main__":

    app = QApplication([])
    window = BudgetTrackerApp()
    app.exec_()