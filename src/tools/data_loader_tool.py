import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from typing import Callable
import pandas as pd
from langchain.tools import BaseTool
from paths import DATA_PATH
from pydantic import PrivateAttr
from datetime import datetime

def loadData(start_date, end_date):
    files = os.listdir(DATA_PATH)
    files_no_ext = [os.path.splitext(f)[0] for f in files]
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    filtered_files = []
    for f in files_no_ext:
        try:
            file_date = datetime.strptime(f, "%Y-%m-%d")
            if start <= file_date <= end:
                filtered_files.append(f)
        except ValueError:
            continue
    df_list = []
    for file in filtered_files:
        temp_df = pd.read_csv(os.path.join(DATA_PATH, (file) + ".csv"))
        df_list.append(temp_df)
    if df_list:
        df = pd.concat(df_list, ignore_index=True)
    else:
        df = pd.DataFrame()
    if df.empty:
        return pd.DataFrame()
    return df

class DataLoadingTool(BaseTool):
    name: str = "data_loader"
    description: str = (
        "Tool to load order data from CSV files between two given dates. "
        "The input must be a single string containing the start and end dates, "
        "formatted exactly as: YYYY-MM-DD, YYYY-MM-DD (no quotes around dates). "
        "It returns a pandas DataFrame with the concatenated data from all matching files.\n\n"
        "Examples of valid input:\n"
        "- 2024-12-01, 2024-12-31\n"
        "- 2025-01-01, 2025-03-15\n"
        "- 2025-05-01, 2025-05-20"
    )

    _set_df_callback: Callable[[pd.DataFrame], None] = PrivateAttr()

    def __init__(self, set_df_callback: Callable[[pd.DataFrame], None], **kwargs):
        super().__init__(**kwargs)
        self._set_df_callback = set_df_callback

    def _run(self, query) -> str:
        try:
            start_date, end_date = query.split(",")
            start_date = start_date.strip()
            end_date = end_date.strip()
            df = loadData(start_date, end_date)
            self._set_df_callback(df)
            return "Data loaded successfully"
        except Exception as e:
            return f"Failed to load data: {e}"

    async def _arun(self) -> str:
        return self._run()