import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6 import QtWidgets
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt

from UI.base_window import BaseWindow
from src.utils import resource_path


# Test window that inherits from BaseWindow for testing
class TestWindow(BaseWindow):
    """Test implementation of BaseWindow for unit testing."""

    def __init__(self):
        super(TestWindow, self).__init__("window.ui")

        # Flag to check if process_files was called (for testing)
        self.process_called = False

    def process_files(self):
        """Test implementation of process_files."""
        self.process_called = True


# Fixtures
@pytest.fixture
def app():
    """Create QApplication instance for tests."""
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    yield app


@pytest.fixture
def test_window(app):
    """Create test window instance."""
    window = TestWindow()
    yield window
    window.close()


# Tests for the utils.py functions
def test_resource_path():
    """Test resource_path function."""
    test_path = os.path.join("test", "path")
    result = resource_path(test_path)

    # Without PyInstaller, should return path relative to current directory
    assert result.endswith(test_path)


# Tests for the BaseWindow class
class TestBaseWindow:

    def test_initialization(self, test_window):
        """Test window initialization."""
        assert test_window is not None
        assert isinstance(test_window, BaseWindow)
        assert test_window.selected_files == []

    @patch('PyQt6.QtWidgets.QFileDialog.getOpenFileNames')
    def test_open_file_dialog(self, mock_get_files, test_window):
        """Test open_file_dialog method with mocked file dialog."""
        # Set up mock return values
        test_files = [
            "/path/to/file1.csv",
            "/path/to/file2.csv"
        ]
        mock_get_files.return_value = (test_files, "CSV Files (*.csv)")

        # Call the method
        test_window.open_file_dialog()

        # Verify mock was called
        mock_get_files.assert_called_once()

        # Verify files were stored
        assert test_window.selected_files == test_files

        # Verify UI was updated
        if test_window.file_selection_input:
            assert test_window.file_selection_input.text() == "2 files selected"

        if test_window.file_list_text_edit:
            assert test_window.file_list_text_edit.toPlainText() == "\n".join(test_files)

    def test_update_file_selection_display(self, test_window):
        """Test update_file_selection_display method."""
        test_files = ["/path/to/file.csv"]

        # Call the method
        test_window.update_file_selection_display(test_files)

        # Verify UI was updated correctly
        if test_window.file_selection_input:
            assert test_window.file_selection_input.text() == "1 file selected"

        if test_window.file_list_text_edit:
            assert test_window.file_list_text_edit.toPlainText() == test_files[0]

        # Test with multiple files
        test_files = ["/path/to/file1.csv", "/path/to/file2.csv"]
        test_window.update_file_selection_display(test_files)

        if test_window.file_selection_input:
            assert test_window.file_selection_input.text() == "2 files selected"


# Integration test with mocked UI components
class TestUIIntegration:

    @patch('UI.base_window.BaseWindow.open_file_dialog')
    def test_choose_button_connection(self, mock_open_dialog, test_window):
        """Test that clicking the choose button calls open_file_dialog."""
        # Check if the button exists first
        if test_window.choose_statements_button:
            # Simulate clicking the button
            QTest.mouseClick(test_window.choose_statements_button, Qt.MouseButton.LeftButton)

            # Verify the method was called
            mock_open_dialog.assert_called_once()