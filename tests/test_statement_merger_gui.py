import os
import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from PyQt6 import QtWidgets, QtCore

# Add the parent directory to the path to import from the src package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from UI.base_window import BaseWindow
from UI.statement_merger_gui import MainWindow


@pytest.fixture
def app(qtbot):
    """
    PyQt application fixture - ensures a Qt application exists for the tests.
    Without this, creating any Qt widgets will fail.
    """
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)


@pytest.fixture
def base_window(qtbot, monkeypatch):
    """
    Creates a BaseWindow instance with mocked UI components for testing.
    """
    # Mock the resource_path function to avoid file path issues during testing
    with patch('UI.base_window.resource_path', return_value=os.path.join("UI", "window.ui")):
        # Mock the loadUi function to avoid actual UI loading
        with patch('PyQt6.uic.loadUi'):
            window = BaseWindow()

            # Create mock UI elements as they appear in your code
            window.button_choose_statements = MagicMock()
            window.input_file_selection = MagicMock()
            window.text_edit_file_list = MagicMock()

            # Add window to qtbot
            qtbot.addWidget(window)
            return window


def test_choose_button_exists(base_window):
    """
    Test that the 'Choose Statements' button exists.
    """
    assert base_window.button_choose_statements is not None, "Add statements button not found"


def test_open_file_dialog(base_window, monkeypatch):
    """
    Test that clicking the 'Choose Statements' button opens the file dialog.
    """
    # Mock QFileDialog.getOpenFileNames to return an empty result
    mock_get_files = MagicMock(return_value=([], ""))
    monkeypatch.setattr(QtWidgets.QFileDialog, "getOpenFileNames", mock_get_files)

    # Call the open_file_dialog method directly (simulating button click)
    base_window.open_file_dialog()

    # Check that the dialog was opened
    mock_get_files.assert_called_once()


def test_dialog_cancel_no_selection(base_window, monkeypatch):
    """
    Test that closing the dialog without selecting files doesn't break anything.
    """
    # Mock QFileDialog.getOpenFileNames to return empty selection
    mock_get_files = MagicMock(return_value=([], ""))
    monkeypatch.setattr(QtWidgets.QFileDialog, "getOpenFileNames", mock_get_files)

    # Call the method directly
    base_window.open_file_dialog()

    # Check that the selected_files list is empty
    assert base_window.selected_files == []


def test_single_file_selection(base_window, monkeypatch):
    """
    Test that selecting a single file updates the UI correctly.
    """
    # Single file path
    file_path = "/path/to/file1.csv"

    # Mock QFileDialog.getOpenFileNames to return a single file
    mock_get_files = MagicMock(return_value=([file_path], ""))
    monkeypatch.setattr(QtWidgets.QFileDialog, "getOpenFileNames", mock_get_files)

    # Call the method directly
    base_window.open_file_dialog()

    # Check that the file is stored in selected_files
    assert base_window.selected_files == [file_path]

    # Check that the file list text was updated with the file path
    base_window.text_edit_file_list.setText.assert_called_once_with(file_path)


def test_multiple_files_selection(base_window, monkeypatch):
    """
    Test that selecting multiple files updates the UI correctly.
    """
    # Multiple file paths
    file_paths = [
        "/path/to/file1.csv",
        "/path/to/file2.csv",
        "/path/to/file3.csv"
    ]

    # Mock QFileDialog.getOpenFileNames to return multiple files
    mock_get_files = MagicMock(return_value=(file_paths, ""))
    monkeypatch.setattr(QtWidgets.QFileDialog, "getOpenFileNames", mock_get_files)

    # Call the method directly
    base_window.open_file_dialog()

    # Check that the files are stored in selected_files
    assert base_window.selected_files == file_paths

    # Check that the file list text was updated with all file paths
    expected_text = "\n".join(file_paths)
    base_window.text_edit_file_list.setText.assert_called_once_with(expected_text)


def test_sequential_file_selections(base_window, monkeypatch):
    """
    Test that selecting files sequentially updates correctly.
    First select one file, then select multiple files in a second operation.
    """
    # First selection - one file
    first_file = "/path/to/first_file.csv"
    mock_get_files_1 = MagicMock(return_value=([first_file], ""))
    monkeypatch.setattr(QtWidgets.QFileDialog, "getOpenFileNames", mock_get_files_1)

    # First selection
    base_window.open_file_dialog()

    # Check first update
    assert base_window.selected_files == [first_file]
    base_window.text_edit_file_list.setText.assert_called_once_with(first_file)

    # Reset mocks for next call
    base_window.text_edit_file_list.reset_mock()

    # Second selection - multiple files
    more_files = [
        "/path/to/second_file.csv",
        "/path/to/third_file.csv"
    ]
    mock_get_files_2 = MagicMock(return_value=(more_files, ""))
    monkeypatch.setattr(QtWidgets.QFileDialog, "getOpenFileNames", mock_get_files_2)

    # Second selection
    base_window.open_file_dialog()

    # Check that only the new files are stored (replacing previous selection)
    assert base_window.selected_files == more_files

    # Check text field updated with new files only (as per your code)
    expected_text = "\n".join(more_files)
    base_window.text_edit_file_list.setText.assert_called_once_with(expected_text)