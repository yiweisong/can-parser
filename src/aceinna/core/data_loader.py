import pandas as pd
from typing import Tuple, Generator
import os
from ..models.fetch_rule import DataSourceFetchRule
from ..utils.hex_parser import parse_hex_string

class DataLoader:
    @staticmethod
    def load_data(file_path: str, rule: DataSourceFetchRule) -> pd.DataFrame:
        """
        Load data from file based on the rule.
        Returns a DataFrame with columns: ['timestamp', 'message_id', 'data']
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Determine indices from rule (Assuming 0-based index from rule for now)
        # If the UI provides 1-based, we might need to subtract 1. 
        # For now, let's assume the rule stores 0-based indices.
        col_indices = [
            rule.timestamp_col_index,
            rule.message_id_col_index,
            rule.message_data_col_index
        ]
        
        # Read file
        if rule.file_type == 'xlsx':
            df = pd.read_excel(file_path, header=None) # Assuming no header or we handle it by index
        elif rule.file_type == 'csv':
            df = pd.read_csv(file_path, header=None)
        else:
            raise ValueError(f"Unsupported file type: {rule.file_type}")

        # Select relevant columns
        try:
           selected_df = df.iloc[:, col_indices].copy()
        except IndexError:
             raise ValueError(f"Column index out of range for file: {file_path}")

        # Rename columns standard names
        selected_df.columns = ['timestamp', 'message_id', 'data']
        
        # Clean and parse data
        # Ensure timestamp is numeric if possible, or keep as is? Usually timestamp is float.
        # Ensure message_id is int.
        # Ensure data is bytes.
        
        # Drop rows with NaN in critical columns
        selected_df.dropna(subset=['message_id', 'data'], inplace=True)

        # Convert message_id to int (handle hex strings if necessary, but usually CSVs have dec or hex)
        # If message_id is string and hex, we need to convert. 
        # Let's assume it might be hex string or int.
        
        def parse_id(val):
            if isinstance(val, int):
                return val
            if isinstance(val, str):
                val = val.strip()
                if val.lower().startswith('0x'):
                    return int(val, 16)
                try:
                    return int(val)
                except ValueError:
                    # Try hex without prefix if int fails? Or just return None/Error?
                    try:
                        return int(val, 16)
                    except ValueError:
                         return 0 # Or -1
            return 0

        selected_df['message_id'] = selected_df['message_id'].apply(parse_id)
        
        # Convert data column to bytes
        selected_df['data'] = selected_df['data'].apply(lambda x: parse_hex_string(str(x)))
        
        return selected_df

