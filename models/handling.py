"""Making table for company information"""

import csv
import os
import pandas as pd
import pathlib

class CsvWriter:
    """Write DataFrame to a CSV file."""
    
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        # ファイルが存在しない場合は空のCSVファイルを作成
        if not os.path.exists(csv_file_path):
            pathlib.Path(csv_file_path).touch()

    def write_dataframe(self, df, mode='w', header=True):
        """
        Write a DataFrame to a CSV file.

        Parameters:
            df (pd.DataFrame): 書き込むデータフレーム。
            mode (str): 書き込みモード ('w' = 上書き, 'a' = 追記)。
            header (bool): ヘッダー行を含めるかどうか。
        """
        if not isinstance(df, pd.DataFrame):
            raise ValueError("The input data must be a pandas DataFrame.")
        
        df.to_csv(self.csv_file_path, mode=mode, header=header, index=False, encoding='utf-8-sig')
        print(f"DataFrame written to {self.csv_file_path}")