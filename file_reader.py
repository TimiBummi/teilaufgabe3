import pandas as pd
from pathlib import Path
from typing import Union, Optional


class FileReader:
    @staticmethod
    def read_ods(
        file_path: Union[str, Path],
        sheet_name: Union[str, int, None] = 0,
        **kwargs
    ) -> pd.DataFrame:
        """
        Read an ODS file into a pandas DataFrame.

        Parameters
        ----------
        file_path : str | Path
            Path to the .ods file
        sheet_name : str | int | None, default 0
            Sheet to read. Use None to read all sheets (returns dict).
        **kwargs
            Forwarded to pandas.read_excel

        Returns
        -------
        pd.DataFrame
            Loaded spreadsheet data
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"ODS file not found: {file_path}")

        if file_path.suffix.lower() != ".ods":
            raise ValueError("File must have .ods extension")

        return pd.read_excel(
            file_path,
            sheet_name=sheet_name,
            engine="odf",
            **kwargs
        )
