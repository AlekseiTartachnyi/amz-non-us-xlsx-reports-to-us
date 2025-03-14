import os
import sys
from PyQt6 import QtWidgets, uic
from src.utils import resource_path


class BaseWindow(QtWidgets.QDialog):
    """
    Base window class that provides common functionality for UI windows.
    """

    def __init__(self, ui_file="window.ui"):
        """
        Initialize the base window.

        Args:
            ui_file: Name of the UI file in the UI directory
        """
        super(BaseWindow, self).__init__()

        # Load UI
        ui_path = resource_path(os.path.join("UI", ui_file))
        uic.loadUi(ui_path, self)

        # Store selected file paths
        self.selected_files = []

        # Common UI elements - to be accessed by child classes
        self.button_choose_statements = self.findChild(QtWidgets.QPushButton, "buttonAddStatements")
        self.text_edit_file_list = self.findChild(QtWidgets.QTextBrowser, "fileListTextEdit")

        # Connect signals to slots
        if self.button_choose_statements:
            self.button_choose_statements.clicked.connect(self.open_file_dialog)

    def open_file_dialog(self):
        """Open file dialog to select Amazon statement CSV files"""
        options = QtWidgets.QFileDialog.Option.ReadOnly
        file_filter = "CSV Files (*.csv);;All Files (*)"

        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            "Select Amazon Statement Files",
            "",  # Start in the current directory
            file_filter,
            options=options
        )

        if files:
            self.selected_files = files
            self.update_file_selection_display(files)

    def update_file_selection_display(self, files):
        """
        Update UI to display selected files.

        Args:
            files: List of selected file paths
        """
        # Update the UI to show how many files were selected
        files_count = len(files)
        file_label = f"{files_count} file{'s' if files_count > 1 else ''} selected"


        # Display selected files in the text edit
        if self.text_edit_file_list:
            # Create a formatted list of files
            file_list_text = "\n".join(files)
            self.text_edit_file_list.setText(file_list_text)