import pytest
import pandas as pd
from pathlib import Path

from src.data_processor import DataProcessor
from src.csv_processor import CSVProcessor


@pytest.fixture
def data_processor():

    return DataProcessor('d45814ac3d6a60ce8e3c5f191cf7d507')

@pytest.fixture
def csv_processor():  # Added fixture
    return CSVProcessor()


@pytest.fixture
def test_data_path():
    return Path(__file__).parent / 'test_files_data_processor'


def test_transform_to_us_date_format(data_processor):
    """Test date format transformation from DD/MM/YYYY to MM/DD/YYYY"""

    # Create test DataFrame with non-US date format
    input_statement_data = pd.DataFrame({
        'Date': ['03/01/2024', '25/10/2024'],  # 3rd Jan and 25th Oct
        'Transaction type': ['Order Payment', 'Order Payment'],
        'Order ID': ['114-7777777-88888888', '114-7777777-99999999'],
        'Product Details': ['Test', 'Test'],
        'Total product charges': [49, 49],
        'Total promotional rebates': [-6.99, -6.99],
        'Amazon fees': [-11.03, -11.03],
        'Other': [6.99, 6.99],
        'Total (AUD)': [37.97, 37.97]
    })

    # Expected output with US date format
    expected_statement_data = pd.DataFrame({
        'Date': ['01/03/2024', '10/25/2024'],  # Jan 3rd and Oct 25th
        'Transaction type': ['Order Payment', 'Order Payment'],
        'Order ID': ['114-7777777-88888888', '114-7777777-99999999'],
        'Product Details': ['Test', 'Test'],
        'Total product charges': [49, 49],
        'Total promotional rebates': [-6.99, -6.99],
        'Amazon fees': [-11.03, -11.03],
        'Other': [6.99, 6.99],
        'Total (USD)': [37.97, 37.97]
    })

    # Transform dates
    result = data_processor.transform_to_us_date_format(input_statement_data)

    # Compare only the Date column
    pd.testing.assert_series_equal(result['Date'], expected_statement_data['Date'])


def test_fred_connection(data_processor):
    """Test that we can connect to FRED and get exchange rates"""
    try:
        # Get CAD rate
        cad_rate = data_processor.get_exchange_rate('CAD', '2024-01-02')
        assert cad_rate is not None
        assert isinstance(cad_rate, float)

        # Get AUD rate
        aud_rate = data_processor.get_exchange_rate('AUD', '2024-01-02')
        assert aud_rate is not None
        assert isinstance(aud_rate, float)

    except Exception as e:
        pytest.fail(f"Failed to get exchange rates: {str(e)}")


def test_currency_conversion(data_processor):
    """
    Test currency conversion for CAD and AUD transactions
    Using actual historical exchange rates from FRED
    """
    # First, let's get the actual rates and calculate expected values
    test_cases = [
        # CAD test cases (Canadian sales)
        ('2023-12-01', 'CAD', 39.99, 39.99 / 1.3498),  # Using actual FRED rate
        ('2023-12-15', 'CAD', 24.99, 24.99 / 1.3415),  # Using actual FRED rate
        ('2024-01-02', 'CAD', 15.99, 15.99 / 1.3310),  # Using actual FRED rate

        # AUD test cases (Australian sales)
        ('2023-12-01', 'AUD', 29.99, 29.99 * 0.6627),  # Using actual FRED rate
        ('2023-12-15', 'AUD', 19.99, 19.99 * 0.6705),  # Using actual FRED rate
        ('2024-01-02', 'AUD', 34.99, 34.99 * 0.6754),  # Using actual FRED rate
    ]

    for date, currency, amount, expected_usd in test_cases:
        try:
            # Get exchange rate
            rate = data_processor.get_exchange_rate(currency, date)

            # Calculate USD amount
            if currency == 'AUD':
                actual_usd = amount * rate
            else:  # CAD
                actual_usd = amount / rate

            # Assert converted amount matches expected
            # Using slightly larger tolerance (0.1) because we're dealing with real market rates
            assert abs(actual_usd - expected_usd) < 0.1, \
                f"Conversion failed for {currency} {amount} on {date}. " \
                f"Expected: ${expected_usd:.2f}, Got: ${actual_usd:.2f}"

        except Exception as e:
            pytest.fail(f"Currency conversion failed: {str(e)}")


def get_canada_test_data():
    """Provides test data for Canadian marketplace"""
    input_data = pd.DataFrame({
        'Date': ['03/01/2024', '25/10/2024'],  # 3rd Jan and 25th Oct
        'Transaction type': ['Order Payment', 'Order Payment'],
        'Order ID': ['114-7777777-88888888', '114-7777777-99999999'],
        'Product Details': ['Test', 'Test'],
        'Total product charges': [49.99, 29.99],  # In CAD
        'Total promotional rebates': [-5.00, -3.00],  # In CAD
        'Amazon fees': [-11.03, -7.50],  # In CAD
        'Other': [2.50, 1.50],  # In CAD
        'Total (CAD)': [36.46, 20.99]  # In CAD
    })

    expected_data = pd.DataFrame({
        'Date': ['01/03/2024', '10/25/2024'],  # US format
        'Transaction type': ['Order Payment', 'Order Payment'],
        'Order ID': ['114-7777777-88888888', '114-7777777-99999999'],
        'Product Details': ['Test', 'Test'],
        'Total product charges': [37.56, 22.53],  # In USD
        'Total promotional rebates': [-3.76, -2.25],  # In USD
        'Amazon fees': [-8.29, -5.63],  # In USD
        'Other': [1.88, 1.13],  # In USD
        'Total (USD)': [27.39, 15.78]  # In USD
    })

    return input_data, expected_data

def test_transform_marketplace_data(data_processor):
    """
    Test data transformation for marketplaces:
    - Date format conversion (DD/MM/YYYY -> MM/DD/YYYY)
    - Currency conversion (CAD/AUD -> USD)
    """
    canada_input, canada_expected = get_canada_test_data()

    # First transform dates
    date_result = data_processor.transform_to_us_date_format(canada_input)

    # Then convert currency
    final_result = data_processor.transform_currency(date_result)

    # Compare with expected data
    pd.testing.assert_frame_equal(
        final_result,
        canada_expected,
        check_exact=False,
        rtol=0.1  # 10% tolerance for currency conversion
    )


def test_process_au_statement(csv_processor, data_processor, test_data_path):
    """Test reading and processing Australian statement"""
    # First read the CSV file
    statement_data = csv_processor.read_file(test_data_path / 'test_AUD_statement.csv' )

    # Transform dates to US format
    us_date_data = data_processor.transform_to_us_date_format(statement_data)

    # Convert currency to USD
    final_data = data_processor.transform_currency(us_date_data)

    # Print actual values to help us debug
    print("\nActual USD values after conversion:")
    print(final_data.to_dict('records')[0])

    # Create expected data with USD values (AUD * exchange_rate)
    # Using exchange rate from Aug 30, 2024 (approximately 0.676)
    expected_data = pd.DataFrame({
        'Date': ['08/30/2024'],
        'Transaction type': ['Order Payment'],
        'Order ID': ['114-7777777-88888888'],
        'Product Details': ['Test'],
        'Total product charges': [33.15],  # 49.00 * 0.676
        'Total promotional rebates': [-4.72],  # -6.99 * 0.676
        'Amazon fees': [-7.46],  # -11.03 * 0.676
        'Other': [4.72],  # 6.99 * 0.676
        'Total (USD)': [25.67]  # 37.97 * 0.676
    })

    # Compare results
    pd.testing.assert_frame_equal(
        final_data,
        expected_data,
        check_exact=False,
        rtol=0.1  # 10% tolerance for exchange rates
    )