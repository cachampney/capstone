# ui_component.py
import os, traceback
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QMessageBox, QFileDialog
from data_manager import DataManager

class InitiativeTrackerApp(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize the data management component
        self.data_manager = DataManager()

        # Initialize the turn index to 0 (first participant's turn)
        self.turn_index = 0

        # UI Widgets
        self.participant_name_input = QLineEdit()
        self.initiative_input = QLineEdit()
        self.initiative_list = QListWidget() 
        self.current_turn_label = QLabel("Current Turn:")
        self.on_deck_label = QLabel("On Deck:")
        self.third_in_line_label = QLabel("Third in Line:")

        # Buttons
        self.add_participant_button = QPushButton("Add Participant")
        self.remove_participant_button = QPushButton("Remove Participant")
        self.save_encounter_button = QPushButton("Save Encounter")
        self.load_encounter_button = QPushButton("Load Encounter")
        self.delete_encounter_button = QPushButton("Delete Encounter")
        self.next_turn_button = QPushButton("Next Turn")
        self.previous_turn_button = QPushButton("Previous Turn")

        # Connect buttons to their respective functions
        self.add_participant_button.clicked.connect(self.add_participant)
        self.remove_participant_button.clicked.connect(self.remove_participant)
        self.save_encounter_button.clicked.connect(self.save_encounter_dialog)
        self.load_encounter_button.clicked.connect(self.load_encounter_dialog)
        self.delete_encounter_button.clicked.connect(self.delete_encounter_dialog)
        self.next_turn_button.clicked.connect(self.next_turn)
        self.previous_turn_button.clicked.connect(self.previous_turn)

        # Set up the layout
        layout = QVBoxLayout()

        # Add participant name and initiative on the same row
        participant_initiative_layout = QHBoxLayout()
        participant_initiative_layout.addWidget(QLabel("Participant Name:"))
        participant_initiative_layout.addWidget(self.participant_name_input)
        participant_initiative_layout.addWidget(QLabel("Initiative:"))
        participant_initiative_layout.addWidget(self.initiative_input)
        layout.addLayout(participant_initiative_layout)

        # Add participant buttons on the same row
        participant_buttons_layout = QHBoxLayout()
        participant_buttons_layout.addWidget(self.add_participant_button)
        participant_buttons_layout.addWidget(self.remove_participant_button)
        layout.addLayout(participant_buttons_layout)

        # Add encounter buttons
        layout.addWidget(self.save_encounter_button)
        layout.addWidget(self.load_encounter_button)
        layout.addWidget(self.delete_encounter_button)
        
        # Add display to show list of participants
        layout.addWidget(self.initiative_list)
        
        # Add the labels to the layout
        layout.addWidget(self.current_turn_label)
        layout.addWidget(self.on_deck_label)
        layout.addWidget(self.third_in_line_label)
        
        # Add the buttons to the layout
        layout.addWidget(self.next_turn_button)
        layout.addWidget(self.previous_turn_button)

        self.setLayout(layout)
        self.setWindowTitle("Initiative Tracker")

        # Update the turn labels based on the initial initiative order
        self.update_turn_labels()
        
        self.show()
        
    def next_turn(self):
        initiative_order = self.data_manager.get_initiative_order()
        if len(initiative_order) > 1:
            # Increment the turn index, and handle returning to the top of the initiative order
            self.turn_index = (self.turn_index + 1) % len(initiative_order)
            self.update_turn_labels()

    def previous_turn(self):
        initiative_order = self.data_manager.get_initiative_order()
        if len(initiative_order) > 1:
            # Decrement the turn index, and handle cycling back to the bottom of the initiative order
            self.turn_index = (self.turn_index - 1) % len(initiative_order)
            self.update_turn_labels()
        
    def update_turn_labels(self):
        initiative_order = self.data_manager.get_initiative_order()

        if initiative_order:
            # Use the turn index to determine the current turn participant
            current_turn, current_initiative = initiative_order[self.turn_index]
            self.current_turn_label.setText(f"Current Turn: {current_turn} ({current_initiative})")

            # Use the turn index to determine the on deck participant (next turn)
            on_deck_index = (self.turn_index + 1) % len(initiative_order)
            on_deck_turn, on_deck_initiative = initiative_order[on_deck_index]
            self.on_deck_label.setText(f"On Deck: {on_deck_turn} ({on_deck_initiative})")

            # Use the turn index to determine the third in line participant
            third_in_line_index = (self.turn_index + 2) % len(initiative_order)
            third_in_line_turn, third_in_line_initiative = initiative_order[third_in_line_index]
            self.third_in_line_label.setText(f"Third in Line: {third_in_line_turn} ({third_in_line_initiative})")


    def add_participant(self):
        name = self.participant_name_input.text()
        initiative = self.initiative_input.text()
        if name and initiative.isdigit():
            initiative = int(initiative)
            self.data_manager.add_participant(name, initiative)
            self.update_initiative_list()

            # Clear the input fields
            self.participant_name_input.clear()
            self.initiative_input.clear()
            self.update_turn_labels()
        else:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid participant name and a positive integer initiative.")

    def remove_participant(self):
        selected_items = self.initiative_list.selectedItems()
        if selected_items:
            for item in selected_items:
                text = item.text()
                participant, _ = text.split(": ")
                self.data_manager.remove_participant(participant)
            self.update_initiative_list()
            self.update_turn_labels()

    def save_encounter_dialog(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Encounter", "", "Text Files (*.txt)")
        if file_path:
            encounter_name = os.path.splitext(os.path.basename(file_path))[0]
            self.data_manager.save_encounter(encounter_name)
            self.update_initiative_list()
        

    

    def load_encounter_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Encounter", "", "Text Files (*.txt)")
        if file_path:
            encounter_name = os.path.splitext(os.path.basename(file_path))[0]                
            self.data_manager.load_encounter(encounter_name)
            self.update_initiative_list()       

    def delete_encounter_dialog(self):
        
        file_path, _ = QFileDialog.getOpenFileName(self, "Delete Encounter", "", "Text Files (*.txt)")
        if file_path:
            encounter_name = os.path.splitext(os.path.basename(file_path))[0]                
            self.data_manager.delete_encounter(encounter_name)
            self.update_initiative_list()

    def delete_encounter(self):
        encounter_name = self.encounter_name_input.text()
        if encounter_name.isalnum():
            self.data_manager.delete_encounter(encounter_name)
            self.update_initiative_list()

            # Clear the encounter name input field
            self.encounter_name_input.clear()

    def update_initiative_list(self):
        self.initiative_list.clear()
        initiative_order = self.data_manager.get_initiative_order()
        for participant, initiative in initiative_order:
            IOrder = QListWidgetItem(f"{participant}: {initiative}")
            self.initiative_list.addItem(IOrder)

if __name__ == "__main__":
    app = QApplication([])
    window = InitiativeTrackerApp()
    app.exec_()
