import pytest
import pandas as pd
from pathlib import Path

from src.statement_merger import StatementMerger


@pytest.fixture
def statement_merger():
    return StatementMerger('d45814ac3d6a60ce8e3c5f191cf7d507')  # FRED API key


@pytest.fixture
def test_data_path():
    """Fixture to get test files directory"""
    return Path(__file__).parent / 'test_files_statement_merger'


def test_single_us_statement(statement_merger, test_data_path):
    """Test processing single US statement file"""
    # Process single file
    actual_data = statement_merger.merge_statements(
        test_data_path / 'us_statements' / 'valid_statement.csv'
    )

    # Create expected data
    expected_data = pd.DataFrame({
        'Date': ['8/30/2024'],
        'Transaction type': ['Order Payment'],
        'Order ID': ['114-7777777-88888888'],
        'Product Details': ['Test'],
        'Total product charges': [49],
        'Total promotional rebates': [-6.99],
        'Amazon fees': [-11.03],
        'Other': [6.99],
        'Total (USD)': [37.97]
    })

    # Compare results
    pd.testing.assert_frame_equal(actual_data, expected_data)


def test_multiple_us_statements(statement_merger, test_data_path):
    """Test processing multiple US statement files"""
    # Get all CSV files from us_statements folder
    us_statements_path = test_data_path / 'us_multiple_statements'
    actual_data = statement_merger.merge_statements(list(us_statements_path.glob('*.csv')))

    # Load pre-prepared expected result
    expected_data = pd.read_csv(test_data_path / 'expected_merged_us.csv')

    pd.testing.assert_frame_equal(actual_data, expected_data)


def test_multiple_non_us_statements(statement_merger, test_data_path):
    """Test processing multiple non-US statement files"""
    # Get all CSV files from non_us_statements folder
    non_us_path = test_data_path / 'non_us_statements'
    actual_data = statement_merger.merge_statements(list(non_us_path.glob('*.csv')))

    # Load pre-prepared expected result with converted currencies and dates
    expected_data = pd.read_csv(test_data_path / 'expected_merged_non_us.csv')

    pd.testing.assert_frame_equal(actual_data, expected_data)


def test_mixed_statements(statement_merger, test_data_path):
    """Test processing mix of US and non-US statement files"""
    mixed_path = test_data_path / 'mixed_statements'
    actual_data = statement_merger.merge_statements(list(mixed_path.glob('*.csv')))

    # Load pre-prepared expected result
    expected_data = pd.read_csv(test_data_path / 'expected_merged_mixed.csv')

    pd.testing.assert_frame_equal(actual_data, expected_data)


def test_invalid_statement(statement_merger, test_data_path):
    """Test handling of invalid statement file"""
    invalid_path = test_data_path / 'invalid_statements' / 'invalid_statement.csv'

    with pytest.raises(Exception, match="Error processing.*Missing required columns"):
        statement_merger.merge_statements(invalid_path)

def test_mixed_valid_invalid_files(statement_merger, test_data_path):
    """Test processing folder with both valid and invalid files"""
    mixed_valid_invalid_path = test_data_path / 'mixed_valid_invalid'

    with pytest.raises(Exception, match="Error processing"):
        statement_merger.merge_statements(list(mixed_valid_invalid_path.glob('*.csv')))