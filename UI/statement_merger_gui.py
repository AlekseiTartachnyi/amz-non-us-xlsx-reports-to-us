from PyQt6 import QtWidgets
import sys
from UI.base_window import BaseWindow


class MainWindow(BaseWindow):
    """
    Main window for the Amazon Statement Merger application.
    Inherits common functionality from BaseWindow.
    """

    def __init__(self):
        """Initialize the main window for statement merger."""
        super(MainWindow, self).__init__("window.ui")

        # Additional UI elements specific to the main window
        # For example, if you have a process button:
        self.process_button = self.findChild(QtWidgets.QPushButton, "processButton")
        if self.process_button:
            self.process_button.clicked.connect(self.process_files)

        # Additional initialization specific to the merger application
        self.setWindowTitle("Amazon Statement Merger")

    def process_files(self):
        """
        Process the selected files.
        This is a placeholder for the actual processing logic.
        """
        # Implement the file processing logic here
        if not self.selected_files:
            # Show message that no files are selected
            return

        # Process files logic would go here
        # For example:
        # 1. Get API key from UI
        # 2. Create StatementMerger instance
        # 3. Call merge_statements method
        # 4. Handle results (display, save, etc.)

        # Update UI to show processing result
        # This is a placeholder
        if self.file_list_text_edit:
            self.file_list_text_edit.append("\nProcessing complete!")


def main():
    """
    Main entry point for the application.
    """
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()