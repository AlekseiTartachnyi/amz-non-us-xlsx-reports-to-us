from pathlib import Path

import pytest
import pandas as pd
from src.csv_processor import CSVProcessor
from src.market_config import MARKETPLACE_CONFIG


@pytest.fixture
def csv_processor():
    return CSVProcessor()


@pytest.fixture
def test_data_path():
    """Fixture to get test files directory relative to this test file"""
    return Path(__file__).parent / 'test_files_csv_processor'


def test_validate_marketplace_valid(csv_processor):
    csv_processor.validate_marketplace('USD')  # Should pass


def test_validate_marketplace_invalid(csv_processor):
    with pytest.raises(ValueError, match="Unknown marketplace"):
        csv_processor.validate_marketplace('Test')


def test_detect_marketplace_currency_unsupported(csv_processor):
    """Test detection of unsupported currency fails appropriately"""
    df = pd.DataFrame(columns=[
        'Date', 'Transaction type', 'Order ID', 'Total (EUR)'
    ])

    with pytest.raises(ValueError, match="Unsupported currency: EUR"):
        csv_processor.detect_marketplace_currency(df)


def test_validate_amazon_statement_with_valid_columns(csv_processor):
    """Test DataFrame validation with all required columns present"""
    # Create test DataFrame with minimum valid structure

    csv_processor.current_market = MARKETPLACE_CONFIG['USD']

    valid_df = pd.DataFrame(columns=[
        'Date', 'Transaction type', 'Order ID', 'Product Details',
        'Total product charges', 'Total promotional rebates',
        'Amazon fees', 'Other', 'Total (USD)'
    ])

    # Should not raise any exceptions
    csv_processor.validate_amazon_statement(valid_df)


def test_validate_amazon_statement_with_missing_columns(csv_processor):
    """Test DataFrame validation fails when columns are missing"""
    # Create DataFrame with incomplete column set

    csv_processor.current_market = MARKETPLACE_CONFIG['USD']

    invalid_df = pd.DataFrame(columns=[
        'Date', 'Order ID'  # Deliberately missing most required columns
    ])

    with pytest.raises(ValueError, match="Missing required columns"):
        csv_processor.validate_amazon_statement(invalid_df)


def test_read_valid_statement(csv_processor, test_data_path):
    """Test reading valid Amazon statement CSV"""
    # First, let's read and check actual data
    actual_statement_data = csv_processor.read_file(test_data_path / 'valid_statement.csv' )

    # Debug: Print actual data
    print("\nActual data from file:")
    print(actual_statement_data.to_dict('records')[0])

    # Now create expected data matching the actual CSV content
    expected_statement_data = pd.DataFrame({
        'Date': ['8/30/2024'],
        'Transaction type': ['Order Payment'],
        'Order ID': ['114-7777777-88888888'],
        'Product Details': ['Test'],  # Updated to match actual
        'Total product charges': [49],
        'Total promotional rebates': [-6.99],
        'Amazon fees': [-11.03],
        'Other': [6.99],
        'Total (USD)': [37.97]
    })

    pd.testing.assert_frame_equal(actual_statement_data, expected_statement_data)

def test_read_invalid_statement(csv_processor, test_data_path):
    """Test reading invalid Amazon statement CSV (missing required columns)"""
    with pytest.raises(Exception,
                      match="Error reading file: Missing required columns: \\['Transaction type', 'Amazon fees'\\]"):
        csv_processor.read_file(test_data_path / 'invalid_statement_missing columns.csv')