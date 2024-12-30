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

    def read_file(self, file_source: Union[str, Path, bytes], marketplace: str) -> pd.DataFrame:
        """
        Read Amazon statement file and perform initial validation

        Args:
            file_source: Excel file (path or bytes)
            marketplace: Market code (US, CA, AU)
        Returns:
            pandas DataFrame with the file content
        """
        try:
            self.validate_marketplace(marketplace)
            df_amazon_statement = pd.read_csv(file_source)
            self.validate_amazon_statement(df_amazon_statement)

            self.raw_data = df_amazon_statement
            self.current_market = MARKETPLACE_CONFIG[marketplace]
            return df_amazon_statement

        except Exception as e:
            raise Exception(f"Error reading file: {str(e)}")

    def validate_amazon_statement(self, df_amazon_statement: pd.DataFrame) -> None:
        """
        Check if the file looks like an Amazon statement
        Raises ValueError if validation fails
        """
        currency = self.current_market['currency']

        required_columns = [
            'Date',
            'Transaction type',
            'Order ID',
            'Product Details',
            'Total product charges',
            'Total promotional rebates',
            'Amazon fees',
            'Other',
            f'Total ({currency})'
        ]

        missing_columns = [column for column in required_columns if column not in df_amazon_statement.columns]

        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
