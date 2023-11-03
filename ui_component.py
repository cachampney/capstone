# ui_component.py
import os, re
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, \
    QListWidgetItem, QMessageBox, QFileDialog, QComboBox, QTableWidget, QTableWidgetItem, QTabWidget, QDialog, \
    QAbstractItemView

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


class BudgetTrackerApp(QTabWidget):

    # Import global row, transaction, and budget variable. This will make manipulating these in the methods much easier
    row = 0
    budget = Budget()

    def __init__(self):

            super().__init__()

            '''
            This section is meant to assign the values to the initial windows and tabs. 
            '''

            # Create the two tabs
            self.budget_tracker_tab = QWidget()
            self.expense_goal_tab = QWidget()


            # Set up the layout
            budget_tracker_tab_layout = QVBoxLayout()
            self.budget_tracker_tab.setLayout(budget_tracker_tab_layout)

            expense_goal_tab_layout = QVBoxLayout()
            self.expense_goal_tab.setLayout(expense_goal_tab_layout)

            self.addTab(self.budget_tracker_tab, "Transaction Tracker")
            self.addTab(self.expense_goal_tab, "Expense Goals")

            self.setWindowTitle("Budget Tracker")
            self.setGeometry(900, 200, 800, 600)

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
            self.transaction_table = QTableWidget()
            self.total_expenses_label = QLabel(f"Total Expenses: {self.budget.total_expenses}")
            self.total_income_label = QLabel(f"Total Income: {self.budget.total_income}")
            self.balance_label = QLabel(f"Balance: {self.budget.balance}")

            # Adding pre-determined strings for Transaction Type and Category drop down boxes
            self.transaction_type.addItem("Expense")
            self. transaction_type.addItem("Income")

            for transaction_index, transaction_category in enumerate(self.budget.categories):
                self.transaction_category.addItem(transaction_category)
                transaction_index += 1

            # Create buttons
            self.add_transaction_button = QPushButton("Add Transaction")
            self.remove_transaction_button = QPushButton("Remove Transaction")
            self.save_transaction_button = QPushButton("Save Budget")
            self.load_transaction_button = QPushButton("Load Budget")
            self.delete_transaction_button = QPushButton("Delete Budget")

            # Connect buttons to their respective functions
            self.add_transaction_button.clicked.connect(self.add_transaction)
            self.remove_transaction_button.clicked.connect(lambda: self.remove_from_table(self.transaction_table))
            self.save_transaction_button.clicked.connect(self.save_budget_dialog)
            self.load_transaction_button.clicked.connect(self.load_budget_dialog)
            self.delete_transaction_button.clicked.connect(self.delete_budget_dialog)

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
            budget_third_row_layout.addWidget(QLabel("Note:"))
            budget_third_row_layout.addWidget(self.transaction_note)
            budget_third_row_layout.addWidget(QLabel("Category:"))
            budget_third_row_layout.addWidget(self.transaction_category)
            budget_tracker_tab_layout.addLayout(budget_third_row_layout)

            # Add "add/remove transaction buttons" onto the fourth row
            budget_fourth_row_layout = QHBoxLayout()
            budget_fourth_row_layout.addWidget(self.add_transaction_button)
            budget_fourth_row_layout.addWidget(self.remove_transaction_button)
            budget_tracker_tab_layout.addLayout(budget_fourth_row_layout)

            # Add buttons to save, delete, and load a budget
            budget_tracker_tab_layout.addWidget(self.save_transaction_button)
            budget_tracker_tab_layout.addWidget(self.load_transaction_button)
            budget_tracker_tab_layout.addWidget(self.delete_transaction_button)

            # Set the number of columns to match the expected input and name them.
            self.transaction_table.setColumnCount(6)
            self.transaction_table_headers = ["Date", "Type", "Amount", "Vendor", "Category", "Note"]
            self.transaction_table.setHorizontalHeaderLabels(self.transaction_table_headers)

            # Add display to show list of transactions and set default sortingEnabled to true
            budget_tracker_tab_layout.addWidget(self.transaction_table)
            self.transaction_table.setSortingEnabled(True)

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
            self.amount_spent = QLineEdit()
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
            self.update_cell_button.clicked.connect(lambda: self.update_cell(self.expense_goal_table))
            self.remove_goal_button.clicked.connect(lambda: self.remove_from_table(self.expense_goal_table))

            # Verify goal amounts and goal date format
            self.begin_date.editingFinished.connect(lambda: self.validate_date(self.begin_date))
            self.end_date.editingFinished.connect(lambda: self.validate_date(self.end_date))
            self.date_spent.editingFinished.connect(lambda: self.validate_date(self.date_spent))
            self.amount_spent.editingFinished.connect(lambda: self.validate_amount(self.amount_spent))
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
            expense_third_row_layout.addWidget(QLabel("Amount Spent: "))
            expense_third_row_layout.addWidget(self.amount_spent)
            expense_third_row_layout.addWidget(QLabel("Date Spent: "))
            expense_third_row_layout.addWidget(self.date_spent)
            expense_goal_tab_layout.addLayout(expense_third_row_layout)

            # Add Category and Goal amount to the fourth row
            expense_fourth_row_layout = QHBoxLayout()
            expense_fourth_row_layout.addWidget(QLabel("Category: "))
            expense_fourth_row_layout.addWidget(self.expense_goal_category)
            expense_fourth_row_layout.addStretch(1)
            expense_fourth_row_layout.addWidget(QLabel(f"Goal Amount: ")) #Don't forget to come back to add the goal amt
            expense_fourth_row_layout.addStretch(1)
            expense_goal_tab_layout.addLayout(expense_fourth_row_layout)

            # Add goal notes as the last line
            expense_fifth_row_layout = QHBoxLayout()
            expense_fifth_row_layout.addWidget(QLabel("Expense Goal Note: "))
            expense_fifth_row_layout.addWidget(self.expense_goal_notes)
            expense_goal_tab_layout.addLayout(expense_fifth_row_layout)

            # Add buttons to add a goal, edit, remove, or save a goal
            expense_goal_tab_layout.addWidget(self.add_goal_button)
            expense_goal_tab_layout.addWidget(self.remove_goal_button)

            # Set the number of columns to match the expected input and name them.
            self.expense_goal_table.setColumnCount(8)
            self.expense_header_labels = ["Goal Name", "Category", "Begin Date", "End Date",
                                                              "Current Amount", "Goal Amount", "Balance", "Note"]
            self.expense_goal_table.setHorizontalHeaderLabels(self.expense_header_labels)

            # Add display to show list of transactions and allow for default sorting
            expense_goal_tab_layout.addWidget(self.expense_goal_table)
            self.expense_goal_table.setSortingEnabled(True)

            # Check for data validity and allow the end user to commit the changes within the table widget
            #self.expense_goal_table.currentCellChanged.connect(self.edit_expense_table)

            # Add update cell button to bottom of window
            expense_goal_tab_layout.addWidget(self.update_cell_button)

            self.show()
            '''
            This ends the goal tab section
            '''

    '''
    This section adds and removes and edits from the different tables
    '''
    def add_transaction(self):

        # Enforce both transaction and date to not be empty before adding the transaction.
        if not self.line_empty(self.transaction_amount.text(), "Transaction Amount"):
            return

        if not self.line_empty(self.date.text(), "Transaction Date"):
            return

        # Create a new Transaction object.
        transaction = Transaction()

        # Clear the table so we can then re-import the expense and income tables from the budget class. Set row count to
        # 0 so it clears out the empty rows.
        self.transaction_table.setRowCount(0)
        self.row = 0

        # Update transaction object.
        transaction.edit(self.transaction_type.currentText(), self.date.text(), float(self.transaction_amount.text()),
                              self.vendor.text(), self.transaction_category.currentText(), self.transaction_note.text())

        # Update budget class. This will allow us to save and load budgets easier as well as update the table.
        self.budget.add_transaction(transaction)

        # Pull the attributes out from both expense and income lists and insert them into the table.
        self.add_expense_list_to_table()
        self.add_income_list_to_table()

        # Update table
        self.transaction_table.update()

        # Clear fields for end user
        self.clear_transaction_ui()

        # Update total expenses, income and balance
        self.update_under_table_hud()

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
                self.budget.delete_transaction(budget_obj)
                self.row -= 1
                self.update_under_table_hud()
            else:
                # Remove the goal object from its respective list
                self.budget.delete_expense_goal(budget_obj.name)

        else:
            QMessageBox.warning(self, "Remove from table", "No row was selected.")
            return

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
        if not self.line_empty(self.amount_spent.text(), "Amount Spent"):
            return
        if not self.line_empty(self.date_spent.text(), "Date Spent"):
            return

        # create the goal object, then add it to the dictionary
        goal = Goal(self.name_of_goal.text(), self.begin_date.text(), self.end_date.text(),
                    self.expense_goal_notes.text(), self.goal_amount.text(), self.date_spent.text(),
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

        # Clear the table, so we can then re-import the expense goal table from the budget class.
        self.expense_goal_table.setRowCount(0)

        # Pull the attributes out of the goal list and insert them into the table
        self.add_expense_goal_list_to_table()

        # Update table
        self.expense_goal_table.update()

        # Clear fields for end user
        self.clear_expense_goal_ui()

    def add_expense_list_to_table(self):
        for row, expense_transaction in enumerate(self.budget.expense_transactions):

            # Create a variable so we can store the object into the QTableWidget. This will allow us to pull this
            # exact object back out when we delete it from the table.
            expense_object_date = QTableWidgetItem(expense_transaction.date)
            expense_object_date.setData(Qt.UserRole, expense_transaction)

            # Add expense transaction to the table
            self.transaction_table.insertRow(self.row)
            self.transaction_table.setItem(self.row, 0, expense_object_date)
            self.transaction_table.setItem(self.row, 1, QTableWidgetItem(expense_transaction.transaction_type))
            self.transaction_table.setItem(self.row, 2, QTableWidgetItem(str(expense_transaction.amount)))
            self.transaction_table.setItem(self.row, 3, QTableWidgetItem(expense_transaction.vendor))
            self.transaction_table.setItem(self.row, 4, QTableWidgetItem(expense_transaction.category))
            self.transaction_table.setItem(self.row, 5, QTableWidgetItem(expense_transaction.note))
            self.row += 1 # keep track of the universal row. Will need this for both lists

    def add_income_list_to_table(self):
        for row, income_transaction in enumerate(self.budget.income_transactions):

            # Create a variable so we can store the object into the QTableWidget. This will allow us to pull this
            # exact object back out when we delete it from the table.
            income_object_date = QTableWidgetItem(income_transaction.date)
            income_object_date.setData(Qt.UserRole, income_transaction)

            # Add income transaction to table
            self.transaction_table.insertRow(self.row)
            self.transaction_table.setItem(self.row, 0, income_object_date)
            self.transaction_table.setItem(self.row, 1, QTableWidgetItem(income_transaction.transaction_type))
            self.transaction_table.setItem(self.row, 2, QTableWidgetItem(str(income_transaction.amount)))
            self.transaction_table.setItem(self.row, 3, QTableWidgetItem(income_transaction.vendor))
            self.transaction_table.setItem(self.row, 4, QTableWidgetItem(income_transaction.category))
            self.transaction_table.setItem(self.row, 5, QTableWidgetItem(income_transaction.note))
            self.row += 1  # keep track of the universal row. Will need this for both lists

    def add_expense_goal_list_to_table(self):
        for expense_goal in self.budget.expense_goals.values():

            # Create a variable, so we can store the object into the QTableWidget. This will allow us to pull this
            # exact object back out when we delete it from the table.
            expense_goal_object_name = QTableWidgetItem(expense_goal.name)
            expense_goal_object_name.setData(Qt.UserRole, expense_goal)

            # Add expense goal to table
            row = self.expense_goal_table.rowCount()
            self.expense_goal_table.insertRow(row)
            self.expense_goal_table.setItem(row, 0, expense_goal_object_name)
            self.expense_goal_table.setItem(row, 1, QTableWidgetItem(expense_goal.category))
            self.expense_goal_table.setItem(row, 2, QTableWidgetItem(expense_goal.start_date))
            self.expense_goal_table.setItem(row, 3, QTableWidgetItem(expense_goal.end_date))
            self.expense_goal_table.setItem(row, 4, QTableWidgetItem("0"))
            self.expense_goal_table.setItem(row, 5, QTableWidgetItem(str(expense_goal.target_amount)))
            self.expense_goal_table.setItem(row, 6, QTableWidgetItem("0"))
            self.expense_goal_table.setItem(row, 7, QTableWidgetItem(expense_goal.note))

    def update_cell(self, table):

        # Set selected item to the currently clicked item
        selected_item = table.currentItem()

        # get the current row and column for the selected cell
        if selected_item:
            current_row = self.expense_goal_table.row(selected_item)
            current_column = self.expense_goal_table.column(selected_item)

        # Current amount and balance are not able to be updated directly by the end user.
        if current_column in (4, 6):
            QMessageBox.warning(self, "None Editable Cell", f"{self.expense_header_labels[current_column]} "
                                                      f"is not an editable cell")
            return

        # create a dialog box to update the cells
        update_cell_dialog = QDialog()
        update_cell_dialog.setWindowTitle("Cell Update")
        update_cell_dialog.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)
        update_cell_dialog.resize(100, 75)

        # update lists and validate information being input
        self.save_changes(update_cell_dialog, current_row, current_column, selected_item)

    def save_changes(self, update_cell_dialog, row, column, selected_item):

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
            insert_layout(update_cell_dialog, new_input_line, save_changes_button,
                                                          layout, prompt)

            # validate that the updates hold the same restrictions as initial input
            save_changes_button.clicked.connect(lambda: self.validate_updates(column,
                                                                              new_input_line, update_cell_dialog))
        elif column == 7:
            new_input_line = QLineEdit()
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
                cell_to_update_obj.update_attribute("name", new_input_line.text())
            elif column == 1:
                cell_to_update_obj.update_attribute("category", new_input_line.currentText())
            elif column == 2:
                cell_to_update_obj.update_attribute("start_date", new_input_line.text())
            elif column == 3:
                cell_to_update_obj.update_attribute("end_date", new_input_line.text())
            elif column == 5:
                cell_to_update_obj.update_attribute("target_amount", new_input_line.text())
            elif column == 7:
                cell_to_update_obj.update_attribute("note", new_input_line.text())

            self.budget.delete_expense_goal(self.expense_goal_table.item(row, 0).text())
            self.budget.add_expense_goal(cell_to_update_obj)
            self.expense_goal_table.setRowCount(0)
            self.add_expense_goal_list_to_table()

    def validate_updates(self, column, new_input, update_cell_dialog):
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
            update_cell_dialog.accept()

    '''
    end adding and removing from tables
    '''
    '''
    save, delete, and load budget section
    '''
    def save_budget_dialog(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Budget", "", "Text Files (*.txt)")
        if file_path:
            encounter_name = os.path.splitext(os.path.basename(file_path))[0]
            self.data_manager.save_encounter(encounter_name)
            self.update_transaction_table()

    def load_budget_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Budget", "", "Text Files (*.txt)")
        if file_path:
            encounter_name = os.path.splitext(os.path.basename(file_path))[0]
            self.data_manager.load_encounter(encounter_name)
            self.update_transaction_table()

    def delete_budget_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Delete Budget", "", "Text Files (*.txt)")
        if file_path:
            encounter_name = os.path.splitext(os.path.basename(file_path))[0]
            self.data_manager.delete_encounter(encounter_name)
            self.update_transaction_table()

    def update_transaction_table(self):
        self.transaction_table.clear()
        transaction_table = self.data_manager.get_initiative_order()
        for participant, initiative in transaction_table:
            tList = QListWidgetItem(f"{participant}: {initiative}")
            self.transaction_table.addItem(tList)
    '''
    end save, delete and load budget section
    '''
    '''
    begin data validation section
    '''
    # Table flag will be an int, 0 = expense table and 1 = transaction table.

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
            elif line_name == "Amount Spent":
                self.amount_spent.setFocus()
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
        self.amount_spent.clear()
        self.date_spent.clear()
        self.expense_goal_notes.clear()
    '''
    end updating and clearing UI as needed
    '''

if __name__ == "__main__":

    app = QApplication([])
    window = BudgetTrackerApp()
    app.exec_()
