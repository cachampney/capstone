# ui_component.py
import os, re

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, \
    QListWidget, QListWidgetItem, QMessageBox, QFileDialog, QComboBox, QTableWidget, QTableWidgetItem
from transaction import Transaction
from budget import Budget



class BudgetTrackerApp(QWidget):

    # Import global row, transaction, and budget variable. This will make manipulating these in the methods much easier
    # to work with.
    row = 0
    budget = Budget()

    def __init__(self):

            super().__init__()

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
            self.balance_label = QLabel("Balance:")

            # Set the number of columns to match the expected input and name them.
            self.transaction_table.setColumnCount(6)
            self.transaction_table.setHorizontalHeaderLabels(["Date", "Type", "Amount", "Vendor", "Category", "Note"])

            # Adding pre-determined strings for Transaction Type and Category drop down boxes
            self.transaction_type.addItem("Expense")
            self.transaction_type.addItem("Income")

            self.transaction_category.addItem("Utilities")
            self.transaction_category.addItem("Gas")
            self.transaction_category.addItem("Entertainment")
            self.transaction_category.addItem("Rent/Housing")
            self.transaction_category.addItem("Groceries")
            self.transaction_category.addItem("Other")

            # Create buttons
            self.add_transaction_button = QPushButton("Add Transaction")
            self.remove_transaction_button = QPushButton("Remove Transaction")
            self.save_transaction_button = QPushButton("Save Budget")
            self.load_transaction_button = QPushButton("Load Budget")
            self.delete_transaction_button = QPushButton("Delete Budget")

            # Connect buttons to their respective functions
            self.add_transaction_button.clicked.connect(self.add_transaction)
            self.remove_transaction_button.clicked.connect(self.remove_transaction)
            self.save_transaction_button.clicked.connect(self.save_budget_dialog)
            self.load_transaction_button.clicked.connect(self.load_budget_dialog)
            self.delete_transaction_button.clicked.connect(self.delete_budget_dialog)

            # Verify transaction amount, date format, and character length on note
            self.date.editingFinished.connect(self.validate_date)
            self.transaction_amount.editingFinished.connect(self.validate_transaction_amount)

            # Set up the layout
            layout = QVBoxLayout()

            # Add Transaction Type and date on the first row
            budget_first_row_layout = QHBoxLayout()
            budget_first_row_layout.addWidget(QLabel("Transaction Type:"))
            budget_first_row_layout.addWidget(self.transaction_type)
            budget_first_row_layout.addWidget(QLabel("Date:"))
            budget_first_row_layout.addWidget(self.date)
            layout.addLayout(budget_first_row_layout)

            # Add Vendor and Transaction Amount to the second row
            budget_second_row_layout = QHBoxLayout()
            budget_second_row_layout.addWidget(QLabel("Vendor:"))
            budget_second_row_layout.addWidget(self.vendor)
            budget_second_row_layout.addWidget(QLabel("Transaction Amount:"))
            budget_second_row_layout.addWidget(self.transaction_amount)
            layout.addLayout(budget_second_row_layout)

            # Add Transaction Note and Category drop down box onto the third row
            budget_third_row_layout = QHBoxLayout()
            budget_third_row_layout.addWidget(QLabel("Note:"))
            budget_third_row_layout.addWidget(self.transaction_note)
            budget_third_row_layout.addWidget(QLabel("Category:"))
            budget_third_row_layout.addWidget(self.transaction_category)
            layout.addLayout(budget_third_row_layout)

            # Add "add/remove transaction buttons" onto the fourth row
            budget_fourth_row_layout = QHBoxLayout()
            budget_fourth_row_layout.addWidget(self.add_transaction_button)
            budget_fourth_row_layout.addWidget(self.remove_transaction_button)
            layout.addLayout(budget_fourth_row_layout)

            # Add buttons to save, delete, and load a budget
            layout.addWidget(self.save_transaction_button)
            layout.addWidget(self.load_transaction_button)
            layout.addWidget(self.delete_transaction_button)

            # Add display to show list of transactions
            layout.addWidget(self.transaction_table)

            # Add the labels to the layout
            layout.addWidget(self.total_expenses_label)
            layout.addWidget(self.total_income_label)
            layout.addWidget(self.balance_label)

            self.setLayout(layout)
            self.setWindowTitle("Budget Tracker")

            self.show()

    def add_transaction(self):

        # Enforce both transaction and date to not be empty before adding the transaction.
        if self.transaction_amount.text() == "":
            QMessageBox.warning(self, "Blank transaction amount", "Transaction amount must not be empty.")
            self.transaction_amount.setFocus()
            return

        if self.date.text() == "":
            QMessageBox.warning(self, "Blank date", "Transaction date must not be blank.")
            self.date.setFocus()
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
        self.clear_ui()

        # Update total expenses, income and balance
        self.update_under_table_hud()

    def remove_transaction(self):

        # Set selected item to the currently clicked item
        selected_item = self.transaction_table.selectedItems()

        if selected_item:
            # gives us the row int, which is important for removing income/expense objects
            selected_row = selected_item[0].row()

            remove_transaction = self.transaction_table.item(selected_row, 0)
            transaction_obj = remove_transaction.data(Qt.UserRole)

            # Remove the row from the table itself
            self.transaction_table.removeRow(selected_row)

            # Remove the transaction object from its respective list
            self.budget.delete_transaction(transaction_obj)

            self.row -= 1
        else:
            QMessageBox.warning(self, "Remove Transaction", "No row was selected.")

        self.update_under_table_hud()

    def save_budget_dialog(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Encounter", "", "Text Files (*.txt)")
        if file_path:
            encounter_name = os.path.splitext(os.path.basename(file_path))[0]
            self.data_manager.save_encounter(encounter_name)
            self.update_transaction_table()

    def load_budget_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Encounter", "", "Text Files (*.txt)")
        if file_path:
            encounter_name = os.path.splitext(os.path.basename(file_path))[0]
            self.data_manager.load_encounter(encounter_name)
            self.update_transaction_table()

    def delete_budget_dialog(self):

        file_path, _ = QFileDialog.getOpenFileName(self, "Delete Encounter", "", "Text Files (*.txt)")
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

    def validate_date(self):
        date_text = self.date.text()

        date_pattern = re.compile(r'\d{2}\/\d{2}/\d{2}')

        if not re.match(date_pattern, date_text):
            # Show what format it should look like
            QMessageBox.warning(self, "Invalid Date", "Please enter a date in the format DD/MM/YY")

            # Clear the QLineEdit
            self.date.clear()
            self.date.setFocus()

    def validate_transaction_amount(self):
        amount = self.transaction_amount.text()

        try:
            check_for_float_type = float(amount)
            check_for_float_type = "{:.2f}".format(check_for_float_type)
            self.transaction_amount.setText(check_for_float_type)

        except:
            QMessageBox.warning(self, "Invalid Amount", "Must be a float, with no characters except a decimal point")
            # Clear the QLineEdit
            self.transaction_amount.clear()
            self.transaction_amount.setFocus()

    def update_under_table_hud(self):
        self.total_expenses_label.setText(f"Total Expenses: {self.budget.total_expenses}")
        self.total_income_label.setText(f"Total Income: {self.budget.total_income}")

    def clear_ui(self):
        self.transaction_amount.clear()
        self.date.clear()
        self.transaction_note.clear()
        self.vendor.clear()
        self.transaction_type.setFocus()

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

if __name__ == "__main__":

    app = QApplication([])
    window = BudgetTrackerApp()
    app.exec_()
