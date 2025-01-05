import pandas as pd
from fredapi import Fred
import pandas as pd

class DataProcessor:
    """
    Handles data transformation operations on Amazon marketplace statements:
    - Date format standardization
    - Currency conversion
    - Statement merging
    """
    def __init__(self, api_key):
        self.fred = Fred(api_key=api_key)
        self.series_ids = {
            'CAD': 'DEXCAUS',  # Canadian Dollar to USD
            'AUD': 'DEXUSAL'   # Australian Dollar to USD
        }



    def transform_to_us_date_format(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Transform date format from DD/MM/YYYY to US format (MM/DD/YYYY) in the dataframe.

        Args:
            dataframe: pandas DataFrame containing 'Date' column in DD/MM/YYYY format

        Returns:
            pandas DataFrame with 'Date' column converted to MM/DD/YYYY format
        """
        transformed_dataframe = dataframe.copy()

        # Convert string dates to datetime then back to string in US format
        transformed_dataframe['Date'] = pd.to_datetime(
            transformed_dataframe['Date'],
            format='%d/%m/%Y'
        ).dt.strftime('%m/%d/%Y')

        return transformed_dataframe

    def get_exchange_rate(self, currency: str, date: str) -> float:
        """
        Get exchange rate for specified currency and date from FRED API

        Args:
            currency: Currency code (CAD, AUD)
            date: Date string in YYYY-MM-DD format

        Returns:
            float: Exchange rate for specified currency and date

        Raises:
            ValueError: If currency is not supported or no data available
        """
        series_id = self.series_ids.get(currency)
        if not series_id:
            raise ValueError(f"Unsupported currency: {currency}")

        try:
            # Get the series data for the specific date
            series_data = self.fred.get_series(series_id, date)

            # Extract the rate for our specific date
            if date in series_data.index:
                rate = series_data[date]
                if pd.isna(rate):  # Check for NaN value
                    raise ValueError(f"No exchange rate data available for {currency} on {date}")
                return float(rate)
            else:
                raise ValueError(f"No exchange rate data available for {currency} on {date}")

        except Exception as e:
            raise Exception(f"Failed to fetch exchange rate: {str(e)}")

    def transform_currency(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform marketplace DataFrame:
        - Convert all numeric values from CAD/AUD to USD
        - Rename currency column from Total (CAD/AUD) to Total (USD)

        Args:
            df: pandas DataFrame with marketplace data
            marketplace: str, marketplace code ('CA' for Canada, 'AU' for Australia)

        Returns:
            DataFrame with transformed currency and renamed column
        """
        # Create a copy to avoid modifying original
        result = df.copy()

        # Get currency from Total column name
        total_column = [col for col in df.columns if col.startswith('Total (')][
            0]  # finds 'Total (CAD)' or 'Total (AUD)'
        currency = total_column[total_column.find('(') + 1:total_column.find(')')]  # extracts 'CAD' or 'AUD'

        # Numeric columns that need conversion
        numeric_cols = [
            'Total product charges',
            'Total promotional rebates',
            'Amazon fees',
            'Other',
            f'Total ({currency})'
        ]

        # Convert each row using the date's exchange rate
        for idx, row in result.iterrows():
            # Get exchange rate for this date
            date_str = pd.to_datetime(row['Date']).strftime('%Y-%m-%d')
            rate = self.get_exchange_rate(currency, date_str)

            # Convert numeric columns
            for col in numeric_cols:
                if currency == 'CAD':
                    result.at[idx, col] = row[col] / rate
                else:  # AUD
                    result.at[idx, col] = row[col] * rate

        # Rename currency column
        result = result.rename(columns={f'Total ({currency})': 'Total (USD)'})

        return result