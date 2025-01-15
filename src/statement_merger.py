from pathlib import Path
from typing import Union, List
import pandas as pd

from .csv_processor import CSVProcessor
from .data_processor import DataProcessor


class StatementMerger:
    """
    Handles merging of multiple Amazon marketplace statements into a single DataFrame
    """

    def __init__(self, api_key: str):
        """
        Initialize merger with required processors

        Args:
            api_key: FRED API key for currency conversion
        """
        self.csv_processor = CSVProcessor()
        self.data_processor = DataProcessor(api_key)
        self.merged_data = None


    def _needs_currency_conversion(self, df: pd.DataFrame) -> bool:
        """Check if currency needs conversion"""
        total_col = next(col for col in df.columns if col.startswith('Total ('))
        return 'USD' not in total_col

    def merge_statements(self, file_paths: Union[str, Path, List[Union[str, Path]]]) -> pd.DataFrame:
        """
        Process and merge one or multiple Amazon statement files

        Args:
            file_paths: Single file path or list of file paths to process

        Returns:
            pandas DataFrame containing merged and processed data

        Raises:
            Exception: If file processing fails
        """
        # Convert single path to list for uniform processing
        if isinstance(file_paths, (str, Path)):
            file_paths = [file_paths]

        # Convert all paths to Path objects
        file_paths = [Path(f) for f in file_paths]

        merged_df = None

        for file_path in file_paths:
            try:
                # Read and validate CSV
                statement_data = self.csv_processor.read_file(file_path)

                # Transform dates if needed
                if self._needs_date_conversion(statement_data):
                    statement_data = self.data_processor.transform_to_us_date_format(statement_data)
                    statement_data = self.data_processor.transform_currency(statement_data)

                # Merge with existing data or create new DataFrame
                if merged_df is None:
                    merged_df = statement_data
                else:
                    merged_df = pd.concat([merged_df, statement_data], ignore_index=True)

            except Exception as e:
                raise Exception(f"Error processing {file_path}: {str(e)}")


        self.merged_data = merged_df.copy()

        return self.merged_data

    def _needs_date_conversion(self, df: pd.DataFrame) -> bool:
        """Check if date format needs conversion"""
        try:
            # Try parsing first date as DD/MM/YYYY
            sample_date = pd.to_datetime(df['Date'].iloc[0], format='%d/%m/%Y')
            return True  # If successful, needs conversion
        except ValueError:
            return False  # Already in US format
