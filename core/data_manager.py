"""data_manager.py

Highly-advanced Pandas-based data management module for the
"Study Hours vs Performance" project (production-style).

What it provides (high level):
- A `DataManager` class that encapsulates a pandas DataFrame and offers
  robust, well-documented methods for loading, saving, validating and
  manipulating records.
- Defensive programming: validation, type conversion, clear exceptions,
  atomic saves (write-to-temp + rename), and optional automatic backups.
- Utilities: search, update, delete, deduplicate, summary export.
- Safe CSV/Excel IO and integration-friendly API signatures for other modules.

Dependencies: pandas, numpy
Install: pip install pandas numpy

Author: Generated for student Pandas-module (advanced, production-style)
"""

from __future__ import annotations

import os
import tempfile
import shutil
import logging
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any, Union

import pandas as pd
import numpy as np

# --------------------------- Configuration ---------------------------

DEFAULT_COLUMNS = ["Name", "Study Hours", "Marks"]
DEFAULT_CSV = os.path.join("data", "study_data.csv")
BACKUP_DIR = os.path.join("data", "backups")

# Configure module-level logger
logger = logging.getLogger("data_manager")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)


# --------------------------- Exceptions ---------------------------

class DataManagerError(Exception):
    """Base exception for DataManager-related errors."""


class ValidationError(DataManagerError):
    """Raised when record validation fails."""


# --------------------------- Dataclass Record ---------------------------

@dataclass
class StudyRecord:
    """Structured type for a single study record."""

    Name: str
    Study_Hours: float
    Marks: float

    def to_row(self) -> Dict[str, Any]:
        """Convert to a dict shaped to DataFrame columns."""
        return {"Name": self.Name, "Study Hours": self.Study_Hours, "Marks": self.Marks}


# --------------------------- Helper utilities ---------------------------

def ensure_data_folder_exists(path: str = "data") -> None:
    os.makedirs(path, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)


def atomic_write_df(df: pd.DataFrame, target_path: str, **to_csv_kwargs) -> None:
    """Write DataFrame atomically: write to temp then rename.

    This reduces chance of a corrupted CSV if the program is interrupted.
    """
    ensure_data_folder_exists(os.path.dirname(target_path) or "data")
    dirpath = os.path.dirname(target_path) or "."
    fd, tmp_path = tempfile.mkstemp(prefix=".tmp-study-data-", dir=dirpath)
    os.close(fd)
    try:
        df.to_csv(tmp_path, index=False, **to_csv_kwargs)
        # On POSIX systems, os.replace is atomic.
        os.replace(tmp_path, target_path)
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                logger.debug("Could not remove temporary file %s", tmp_path)


# --------------------------- DataManager Class ---------------------------

class DataManager:
    """Encapsulate the study dataset with safe IO and manipulation helpers.

    Example usage:
        dm = DataManager()
        dm.load()  # loads DEFAULT_CSV or starts empty
        dm.add_record(name, hours, marks)
        dm.save()

    Public methods are documented with docstrings and type hints to make
    integration straightforward for other team members.
    """

    def __init__(self, csv_path: str = DEFAULT_CSV, columns: Optional[List[str]] = None, autosave: bool = False):
        self.csv_path = csv_path
        self.columns = columns or DEFAULT_COLUMNS.copy()
        self.autosave = bool(autosave)
        self._df = pd.DataFrame(columns=self.columns)
        ensure_data_folder_exists(os.path.dirname(self.csv_path) or "data")
        logger.info("DataManager initialized (csv_path=%s, autosave=%s)", self.csv_path, self.autosave)

    # --------------------- Loading / Saving ---------------------

    def load(self) -> pd.DataFrame:
        """Load dataset from CSV into memory. If file not found, keep empty DataFrame.

        Returns:
            The in-memory DataFrame reference.
        """
        if os.path.exists(self.csv_path):
            try:
                df = pd.read_csv(self.csv_path)
                # Normalize columns if necessary
                missing = [c for c in self.columns if c not in df.columns]
                for c in missing:
                    df[c] = np.nan
                df = df[self.columns]
                self._df = df
                logger.info("Loaded %d records from %s", len(self._df), self.csv_path)
            except Exception as e:
                logger.exception("Failed to load CSV file: %s", e)
                raise DataManagerError("Failed to read CSV: " + str(e))
        else:
            logger.info("CSV not found at %s — starting with empty dataset.", self.csv_path)
            self._df = pd.DataFrame(columns=self.columns)
        return self._df

    def save(self, make_backup: bool = True) -> None:
        """Save in-memory DataFrame to CSV using atomic write.

        Args:
            make_backup: If True, create a dated backup of existing CSV before overwrite.
        """
        # Backup existing file
        if make_backup and os.path.exists(self.csv_path):
            backup_name = f"study_data_backup_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
            backup_path = os.path.join(BACKUP_DIR, backup_name)
            try:
                shutil.copy2(self.csv_path, backup_path)
                logger.info("Backup created: %s", backup_path)
            except Exception as e:
                logger.warning("Could not create backup: %s", e)

        try:
            atomic_write_df(self._df, self.csv_path)
            logger.info("Saved %d records to %s", len(self._df), self.csv_path)
        except Exception as e:
            logger.exception("Failed to save data: %s", e)
            raise DataManagerError("Failed to save data: " + str(e))

    # --------------------- Record validation ---------------------

    def _validate_and_normalize_record(self, name: str, hours: Union[int, float, str], marks: Union[int, float, str]) -> StudyRecord:
        """Validate inputs and return a normalized StudyRecord.

        Rules:
            - Name: non-empty string (trimmed)
            - Study Hours: numeric >= 0
            - Marks: numeric 0..100 (you can change range if needed)

        Raises:
            ValidationError on invalid input.
        """
        # Name
        if not isinstance(name, str):
            raise ValidationError("Name must be a string")
        name_clean = name.strip()
        if name_clean == "":
            raise ValidationError("Name must not be empty")

        # Hours
        try:
            hours_val = float(hours)
        except Exception:
            raise ValidationError("Study Hours must be numeric")
        if hours_val < 0:
            raise ValidationError("Study Hours must be >= 0")

        # Marks
        try:
            marks_val = float(marks)
        except Exception:
            raise ValidationError("Marks must be numeric")
        if not (0 <= marks_val <= 100):
            raise ValidationError("Marks must be between 0 and 100")

        return StudyRecord(Name=name_clean, Study_Hours=hours_val, Marks=marks_val)

    # --------------------- CRUD Operations ---------------------

    def add_record(self, name: str, hours: Union[int, float, str], marks: Union[int, float, str]) -> pd.DataFrame:
        """Add a validated record to the DataFrame and optionally autosave.

        Returns the updated DataFrame.
        """
        rec = self._validate_and_normalize_record(name, hours, marks)
        self._df = pd.concat([self._df, pd.DataFrame([rec.to_row()])], ignore_index=True)
        logger.info("Added record: %s", rec)
        if self.autosave:
            self.save()
        return self._df

    def update_record(self, index: int, **fields) -> pd.DataFrame:
        """Update an existing row by integer index. Valid fields: Name, Study Hours, Marks.

        Example:
            dm.update_record(3, Name='Ali', Marks=85)

        Raises IndexError if index invalid, ValidationError for bad values.
        """
        if index < 0 or index >= len(self._df):
            raise IndexError("Index out of range")

        # Work on a copy of the row to validate
        row = self._df.loc[index].to_dict()
        new_row = row.copy()
        for k, v in fields.items():
            if k not in self.columns:
                raise ValidationError(f"Unknown field: {k}")
            new_row[k] = v

        # Validate using normalize function
        rec = self._validate_and_normalize_record(new_row["Name"], new_row["Study Hours"], new_row["Marks"])
        # Apply
        for col, val in rec.to_row().items():
            self._df.at[index, col] = val
        logger.info("Updated index %d -> %s", index, rec)
        if self.autosave:
            self.save()
        return self._df

    def delete_record(self, index: int) -> pd.DataFrame:
        """Delete a row by index and reindex the DataFrame.

        Raises IndexError if index out of range.
        """
        if index < 0 or index >= len(self._df):
            raise IndexError("Index out of range")
        self._df = self._df.drop(index).reset_index(drop=True)
        logger.info("Deleted record at index %d", index)
        if self.autosave:
            self.save()
        return self._df

    # --------------------- Search / Filter ---------------------

    def search(self, name_substr: Optional[str] = None, min_hours: Optional[float] = None, max_hours: Optional[float] = None, min_marks: Optional[float] = None, max_marks: Optional[float] = None) -> pd.DataFrame:
        """Return a filtered DataFrame according to the provided criteria.

        All filters are optional; pass None to skip a filter.
        The name search is case-insensitive and searches for substring.
        """
        df = self._df
        if name_substr is not None:
            mask = df["Name"].fillna("").str.contains(str(name_substr), case=False, na=False)
            df = df[mask]
        if min_hours is not None:
            df = df[df["Study Hours"] >= float(min_hours)]
        if max_hours is not None:
            df = df[df["Study Hours"] <= float(max_hours)]
        if min_marks is not None:
            df = df[df["Marks"] >= float(min_marks)]
        if max_marks is not None:
            df = df[df["Marks"] <= float(max_marks)]
        return df.reset_index(drop=True)

    # --------------------- Deduplication & Cleaning ---------------------

    def deduplicate(self, subset: Optional[List[str]] = None, keep: str = "first") -> pd.DataFrame:
        """Remove duplicate rows. By default, duplicates are checked on all columns.

        Args:
            subset: column list to consider for duplicates (e.g. ['Name']).
            keep: which duplicate to keep: 'first'|'last'|False -> raises error for ambiguous
        """
        before = len(self._df)
        self._df = self._df.drop_duplicates(subset=subset, keep=keep).reset_index(drop=True)
        after = len(self._df)
        logger.info("Deduplicated dataset: %d -> %d records", before, after)
        if self.autosave:
            self.save()
        return self._df

    def clean_whitespace(self) -> pd.DataFrame:
        """Trim whitespace in string columns (useful for 'Name')."""
        if "Name" in self._df.columns:
            self._df["Name"] = self._df["Name"].astype(str).str.strip()
        return self._df

    # --------------------- Summaries / Exports ---------------------

    def summary_statistics(self) -> Dict[str, Any]:
        """Return basic summary stats that NumPy module can also compute.

        Returns a dictionary with keys: n, mean_hours, mean_marks, max_hours, min_hours, correlation_hours_marks
        """
        df = self._df.copy()
        if df.empty:
            return {
                "n": 0,
                "mean_hours": None,
                "mean_marks": None,
                "max_hours": None,
                "min_hours": None,
                "correlation": None,
            }
        n = len(df)
        mean_hours = float(df["Study Hours"].mean())
        mean_marks = float(df["Marks"].mean())
        max_hours = float(df["Study Hours"].max())
        min_hours = float(df["Study Hours"].min())
        # correlation (pearson) — handle constant series
        try:
            corr = float(df["Study Hours"].corr(df["Marks"]))
        except Exception:
            corr = None
        return {
            "n": n,
            "mean_hours": mean_hours,
            "mean_marks": mean_marks,
            "max_hours": max_hours,
            "min_hours": min_hours,
            "correlation": corr,
        }

    def export_excel(self, excel_path: str) -> None:
        """Export the current DataFrame to an Excel file (xlsx)."""
        try:
            ensure_data_folder_exists(os.path.dirname(excel_path) or "data")
            self._df.to_excel(excel_path, index=False)
            logger.info("Exported dataset to %s", excel_path)
        except Exception as e:
            logger.exception("Failed exporting excel: %s", e)
            raise DataManagerError("Failed exporting excel: " + str(e))

    # --------------------- Utility / Integration ---------------------

    def get_dataframe(self) -> pd.DataFrame:
        """Return the internal DataFrame (a shallow copy to avoid accidental modification)."""
        return self._df.copy()

    def replace_dataframe(self, df: pd.DataFrame) -> None:
        """Replace internal DataFrame (ensure it has required columns)."""
        for c in self.columns:
            if c not in df.columns:
                df[c] = np.nan
        self._df = df[self.columns].copy().reset_index(drop=True)
        logger.info("Internal DataFrame replaced (len=%d)", len(self._df))
        if self.autosave:
            self.save()

    def backup(self, dst_folder: Optional[str] = None) -> str:
        """Create a timestamped CSV backup of current in-memory DataFrame and return path."""
        dst_folder = dst_folder or BACKUP_DIR
        ensure_data_folder_exists(dst_folder)
        backup_name = f"inmemory_backup_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
        path = os.path.join(dst_folder, backup_name)
        try:
            atomic_write_df(self._df, path)
            logger.info("Created in-memory backup: %s", path)
            return path
        except Exception as e:
            logger.exception("Backup failed: %s", e)
            raise DataManagerError("Backup failed: " + str(e))

    # Context manager support
    def __enter__(self) -> "DataManager":
        return self

    def __exit__(self, exc_type, exc, tb):
        # On context exit, optionally save if autosave flagged.
        if self.autosave:
            try:
                self.save()
            except Exception:
                logger.exception("Failed saving on context exit")


# --------------------------- Example usage / self-test ---------------------------

if __name__ == "__main__":
    # Basic demo to show interfacing for other members. This block can be
    # removed in production or left to help with manual testing.
    dm = DataManager(autosave=False)
    dm.load()

    print("Current records:\n", dm.get_dataframe())

    # Add a record
    try:
        dm.add_record("Ali Khan", 3.5, 78)
        dm.add_record("Sana", "2", "88")  # string inputs accepted and converted
    except ValidationError as e:
        print("Validation error:", e)

    print("After adds:\n", dm.get_dataframe())

    # Update
    try:
        dm.update_record(0, Marks=80)
    except Exception as e:
        print("Update failed:", e)

    print("Summary stats:", dm.summary_statistics())

    # Save to default CSV
    dm.save()

    # Export to Excel
    dm.export_excel(os.path.join("data", "study_data_export.xlsx"))

    print("Demo finished.")
