# ui_component.py
import os, traceback
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, \
    QListWidget, QListWidgetItem, QMessageBox, QFileDialog, QComboBox


class BudgetTrackerApp(QWidget):
    def __init__(self):
        super().__init__()

        # UI Widgets
        self.transaction_type = QComboBox()
        self.date = QLineEdit()
        self.vendor = QLineEdit()
        self.transaction_amount = QLineEdit()
        self.transaction_note = QLineEdit()
        self.transaction_category = QComboBox()
        self.transaction_list = QListWidget()
        self.total_expenses_label = QLabel("Total Expenses:")
        self.total_income_label = QLabel("Total Income:")
        self.balance_label = QLabel("Balance:")

        # Adding pre-determined strings for Transaction Type and Category drop down boxes
        self.transaction_type.addItem("Expense")
        self.transaction_type.addItem("Income")

        self.transaction_category.addItem("Utilities")
        self.transaction_category.addItem("Gas")
        self.transaction_category.addItem("Entertainment")
        self.transaction_category.addItem("Rent/Housing")
        self.transaction_category.addItem("Groceries")
        self.transaction_category.addItem("Other")

        # Buttons
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
        layout.addWidget(self.transaction_list)

        # Add the labels to the layout
        layout.addWidget(self.total_expenses_label)
        layout.addWidget(self.total_income_label)
        layout.addWidget(self.balance_label)

        self.setLayout(layout)
        self.setWindowTitle("Budget Tracker")

        # Update the turn labels based on the initial initiative order
        # self.update_turn_labels()

        self.show()

    def add_transaction(self):
        name = self.transaction_type.text()
        initiative = self.date.text()
        if name and initiative.isdigit():
            initiative = int(initiative)
            self.data_manager.add_transaction(name, initiative)
            self.update_transaction_list()

            # Clear the input fields
            self.transaction_type.clear()
            self.date.clear()
            self.update_turn_labels()
        else:
            QMessageBox.warning(self, "Invalid Input",
                                "Please enter a valid Transaction Type and a positive integer initiative.")

    def remove_transaction(self):
        selected_items = self.transaction_list.selectedItems()
        if selected_items:
            for item in selected_items:
                text = item.text()
                participant, _ = text.split(": ")
                self.data_manager.remove_transaction(participant)
            self.update_transaction_list()
            self.update_turn_labels()

    def save_budget_dialog(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Encounter", "", "Text Files (*.txt)")
        if file_path:
            encounter_name = os.path.splitext(os.path.basename(file_path))[0]
            self.data_manager.save_encounter(encounter_name)
            self.update_transaction_list()

    def load_budget_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Encounter", "", "Text Files (*.txt)")
        if file_path:
            encounter_name = os.path.splitext(os.path.basename(file_path))[0]
            self.data_manager.load_encounter(encounter_name)
            self.update_transaction_list()

    def delete_budget_dialog(self):

        file_path, _ = QFileDialog.getOpenFileName(self, "Delete Encounter", "", "Text Files (*.txt)")
        if file_path:
            encounter_name = os.path.splitext(os.path.basename(file_path))[0]
            self.data_manager.delete_encounter(encounter_name)
            self.update_transaction_list()

    def delete_encounter(self):
        encounter_name = self.encounter_name_input.text()
        if encounter_name.isalnum():
            self.data_manager.delete_encounter(encounter_name)
            self.update_transaction_list()

            # Clear the encounter name input field
            self.encounter_name_input.clear()

    def update_transaction_list(self):
        self.transaction_list.clear()
        initiative_order = self.data_manager.get_initiative_order()
        for participant, initiative in initiative_order:
            IOrder = QListWidgetItem(f"{participant}: {initiative}")
            self.transaction_list.addItem(IOrder)


if __name__ == "__main__":
    app = QApplication([])
    window = BudgetTrackerApp()
    app.exec_()
