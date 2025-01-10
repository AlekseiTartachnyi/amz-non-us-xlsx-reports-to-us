import pandas as pd
from typing import Union
from pathlib import Path
from .market_config import MARKETPLACE_CONFIG


class CSVProcessor:
    def __init__(self):
        self.raw_data = None
        self.current_market = None

    def validate_marketplace(self, marketplace: str) -> None:
        """
        Validate if marketplace is supported
        Raises ValueError if marketplace is not in config
        """
        if marketplace not in MARKETPLACE_CONFIG:
            raise ValueError(
                f"Unknown marketplace: {marketplace}. "
                f"Supported markets: {list(MARKETPLACE_CONFIG.keys())}"
            )

    def detect_marketplace_currency(self, df: pd.DataFrame) -> str:
        """
        Extract currency from Total column in the DataFrame.

        Args:
            df: pandas DataFrame containing Amazon statement data

        Returns:
            str: Currency code (USD, CAD, AUD)
        """
        total_column = next(
            (col for col in df.columns if col.startswith('Total (')),
            None
        )

        currency = total_column[total_column.find('(') + 1:total_column.find(')')]

        if currency not in MARKETPLACE_CONFIG:
            raise ValueError(
                f"Unsupported currency: {currency}. "
                f"Supported currencies: {list(MARKETPLACE_CONFIG.keys())}"
            )

        return currency


    def read_file(self, file_source: Union[str, Path, bytes]) -> pd.DataFrame:
        """
        Read Amazon statement file and perform validation

        Args:
            file_source: CSV file (path or bytes)

        Returns:
            pandas DataFrame with the file content
        """
        try:
            df_amazon_statement = pd.read_csv(file_source)
            self.validate_amazon_statement(df_amazon_statement)

            currency = self.detect_marketplace_currency(df_amazon_statement)
            self.validate_marketplace(currency)

            self.current_market = MARKETPLACE_CONFIG[currency]
            self.raw_data = df_amazon_statement

            return df_amazon_statement

        except Exception as e:
            raise Exception(f"Error reading file: {str(e)}")


    def validate_amazon_statement(self, df_amazon_statement: pd.DataFrame) -> None:
        """
        Check if the file looks like an Amazon statement
        Raises ValueError if validation fails
        """

        required_columns = [
            'Date',
            'Transaction type',
            'Order ID',
            'Product Details',
            'Total product charges',
            'Total promotional rebates',
            'Amazon fees',
            'Other'
        ]

        missing_columns = [column for column in required_columns if column not in df_amazon_statement.columns]

        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        # Check if there's any 'Total (*)' column
        total_column = next(
            (col for col in df_amazon_statement.columns if col.startswith('Total (')),
            None
        )

        if not total_column:
            raise ValueError("Missing required 'Total' column")