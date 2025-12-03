"""
data_manager.py

Flexible DataManager for a single student's academic performance.
Each record:
- subject (one of ALLOWED_SUBJECTS)
- assessment_type (Quiz, Assignment, Midterm, Final)
- hours (float >= 0)
- marks (float, 0 <= marks <= total_marks)
- total_marks (float > 0)

Statistics use percentage = marks / total_marks * 100 and compute correlations
between hours and percentage.
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

# --------------------------
# Configuration
# --------------------------

ALLOWED_SUBJECTS = [
    "Calculus and Analytic Geometry",
    "Functional English",
    "Applications of ICT",
    "Applied Physics",
    "Introduction to Aerospace Engineering",
    "Islamic Studies",
]

ALLOWED_ASSESSMENTS = ["Quiz", "Assignment", "Midterm", "Final"]

DEFAULT_COLUMNS = ["subject", "assessment_type", "hours", "marks", "total_marks"]
DEFAULT_CSV = os.path.join("data", "study_data.csv")
BACKUP_DIR = os.path.join("data", "backups")

# Logger
logger = logging.getLogger("data_manager")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)


# --------------------------
# Exceptions
# --------------------------

class DataManagerError(Exception):
    pass


class ValidationError(DataManagerError):
    pass


# --------------------------
# Dataclass
# --------------------------

@dataclass
class StudyRecord:
    subject: str
    assessment_type: str
    hours: float
    marks: float
    total_marks: float

    def to_row(self) -> Dict[str, Any]:
        return asdict(self)


# --------------------------
# Helpers
# --------------------------

def ensure_data_folders():
    os.makedirs("data", exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)


def atomic_write_df(df: pd.DataFrame, path: str):
    ensure_data_folders()
    dirpath = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(prefix=".tmpdm-", dir=dirpath)
    os.close(fd)
    try:
        df.to_csv(tmp, index=False)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass


# --------------------------
# DataManager
# --------------------------

class DataManager:
    def __init__(self, csv_path: str = DEFAULT_CSV, autosave: bool = False):
        self.csv_path = csv_path
        self.autosave = autosave
        self._df = pd.DataFrame(columns=DEFAULT_COLUMNS)
        ensure_data_folders()
        logger.info("DataManager initialized (csv=%s, autosave=%s)", self.csv_path, self.autosave)

    # ---- Load / Save ----

    def load(self) -> pd.DataFrame:
        if os.path.exists(self.csv_path):
            try:
                df = pd.read_csv(self.csv_path)
                for c in DEFAULT_COLUMNS:
                    if c not in df.columns:
                        df[c] = np.nan
                self._df = df[DEFAULT_COLUMNS].copy().reset_index(drop=True)
                logger.info("Loaded %d rows from %s", len(self._df), self.csv_path)
            except Exception as e:
                logger.exception("Failed to load CSV: %s", e)
                raise DataManagerError("Failed to load CSV: " + str(e))
        else:
            logger.info("CSV not found — starting empty dataset.")
            self._df = pd.DataFrame(columns=DEFAULT_COLUMNS)
        return self._df

    def save(self) -> None:
        try:
            if os.path.exists(self.csv_path):
                backup_name = f"backup_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
                try:
                    shutil.copy2(self.csv_path, os.path.join(BACKUP_DIR, backup_name))
                    logger.info("Backup created: %s", backup_name)
                except Exception:
                    logger.warning("Backup creation failed; continuing save.")
            atomic_write_df(self._df, self.csv_path)
            logger.info("Saved %d rows to %s", len(self._df), self.csv_path)
        except Exception as e:
            logger.exception("Save failed: %s", e)
            raise DataManagerError("Save failed: " + str(e))

    # ---- Validation ----

    def _validate(self, subject: str, assessment_type: str, hours: Union[int, float, str],
                  marks: Union[int, float, str], total_marks: Union[int, float, str]) -> StudyRecord:

        # Subject
        if subject not in ALLOWED_SUBJECTS:
            raise ValidationError(f"Invalid subject: {subject}")

        # Assessment
        if assessment_type not in ALLOWED_ASSESSMENTS:
            raise ValidationError(f"Invalid assessment_type: {assessment_type}")

        # Hours
        try:
            hours_v = float(hours)
        except Exception:
            raise ValidationError("Hours must be numeric.")
        if hours_v < 0:
            raise ValidationError("Hours must be >= 0")

        # Total marks
        try:
            total_v = float(total_marks)
        except Exception:
            raise ValidationError("Total marks must be numeric.")
        if total_v <= 0:
            raise ValidationError("Total marks must be > 0")

        # Marks obtained
        try:
            marks_v = float(marks)
        except Exception:
            raise ValidationError("Marks must be numeric.")
        if not (0 <= marks_v <= total_v):
            raise ValidationError("Marks must be between 0 and total_marks.")

        return StudyRecord(subject=subject, assessment_type=assessment_type,
                           hours=hours_v, marks=marks_v, total_marks=total_v)

    # ---- CRUD ----

    def add_record(self, subject: str, assessment_type: str, hours: Union[int, float, str],
                   marks: Union[int, float, str], total_marks: Union[int, float, str]) -> pd.DataFrame:
        rec = self._validate(subject, assessment_type, hours, marks, total_marks)
        self._df = pd.concat([self._df, pd.DataFrame([rec.to_row()])], ignore_index=True)
        logger.info("Added record: %s", rec)
        if self.autosave:
            self.save()
        return self._df

    def update_record(self, index: int, **fields) -> pd.DataFrame:
        if index < 0 or index >= len(self._df):
            raise IndexError("Index out of range")
        current = self._df.loc[index].to_dict()
        merged = {**current, **fields}
        rec = self._validate(merged["subject"], merged["assessment_type"],
                             merged["hours"], merged["marks"], merged["total_marks"])
        self._df.loc[index] = rec.to_row()
        logger.info("Updated record %d -> %s", index, rec)
        if self.autosave:
            self.save()
        return self._df

    def delete_record(self, index: int) -> pd.DataFrame:
        if index < 0 or index >= len(self._df):
            raise IndexError("Index out of range")
        self._df = self._df.drop(index).reset_index(drop=True)
        logger.info("Deleted record at index %d", index)
        if self.autosave:
            self.save()
        return self._df

    # ---- Search / Filter ----

    def search(self, subject: Optional[str] = None, assessment_type: Optional[str] = None) -> pd.DataFrame:
        df = self._df.copy()
        if subject:
            df = df[df["subject"] == subject]
        if assessment_type:
            df = df[df["assessment_type"] == assessment_type]
        return df.reset_index(drop=True)

    # ---- Statistics ----

    def _percentage_series(self, df: pd.DataFrame) -> pd.Series:
        # compute percentage (marks/total_marks * 100), handle divide-by-zero safely
        pct = pd.to_numeric(df["marks"], errors="coerce") / pd.to_numeric(df["total_marks"], errors="coerce") * 100.0
        return pct

    def summary_statistics(self) -> Dict[str, Any]:
        df = self._df
        if df.empty:
            return {"n": 0}

        stats: Dict[str, Any] = {"n": len(df)}

        # Overall averages (hours, percentage)
        stats["overall_avg_hours"] = float(df["hours"].mean())
        stats["overall_avg_percentage"] = float(self._percentage_series(df).mean())

        # Subject-wise
        for subj in ALLOWED_SUBJECTS:
            subdf = df[df["subject"] == subj]
            if subdf.empty:
                continue
            pct = self._percentage_series(subdf)
            stats[f"{subj}_avg_hours"] = float(subdf["hours"].mean())
            stats[f"{subj}_avg_percentage"] = float(pct.mean())
            try:
                corr = None
                if pct.dropna().nunique() > 1 and subdf["hours"].dropna().nunique() > 1:
                    corr = float(subdf["hours"].astype(float).corr(pct))
                stats[f"{subj}_correlation"] = corr
            except Exception:
                stats[f"{subj}_correlation"] = None

        # Assessment-type wise
        for at in ALLOWED_ASSESSMENTS:
            subdf = df[df["assessment_type"] == at]
            if subdf.empty:
                continue
            pct = self._percentage_series(subdf)
            stats[f"{at}_avg_hours"] = float(subdf["hours"].mean())
            stats[f"{at}_avg_percentage"] = float(pct.mean())
            try:
                corr = None
                if pct.dropna().nunique() > 1 and subdf["hours"].dropna().nunique() > 1:
                    corr = float(subdf["hours"].astype(float).corr(pct))
                stats[f"{at}_correlation"] = corr
            except Exception:
                stats[f"{at}_correlation"] = None

        return stats

    # ---- Generate human summary ----

    def generate_summary(self) -> str:
        stats = self.summary_statistics()
        if stats.get("n", 0) == 0:
            return "No data available."

        lines: List[str] = []
        lines.append("STUDY PERFORMANCE SUMMARY\n")
        lines.append(f"Total Records: {stats['n']}\n\n")
        lines.append(f"Overall Avg Hours: {stats['overall_avg_hours']:.2f}\n")
        lines.append(f"Overall Avg Percentage: {stats['overall_avg_percentage']:.2f}%\n\n")

        lines.append("=== SUBJECTS ===\n")
        # strongest correlation tracking (subject)
        strongest_subj = (None, 0.0)
        for subj in ALLOWED_SUBJECTS:
            key_avg_pct = f"{subj}_avg_percentage"
            key_corr = f"{subj}_correlation"
            if key_avg_pct in stats:
                avg_pct = stats.get(key_avg_pct)
                corr = stats.get(key_corr)
                lines.append(f"{subj}\n  Avg Percentage: {avg_pct:.2f}%\n  Correlation (hours vs %): {corr if corr is not None else 'N/A'}\n\n")
                if corr is not None and (strongest_subj[0] is None or abs(corr) > abs(strongest_subj[1])):
                    strongest_subj = (subj, corr)

        lines.append("=== ASSESSMENTS ===\n")
        strongest_ass = (None, 0.0)
        for at in ALLOWED_ASSESSMENTS:
            key_avg = f"{at}_avg_percentage"
            key_corr = f"{at}_correlation"
            if key_avg in stats:
                avg_pct = stats.get(key_avg)
                corr = stats.get(key_corr)
                lines.append(f"{at}\n  Avg Percentage: {avg_pct:.2f}%\n  Correlation (hours vs %): {corr if corr is not None else 'N/A'}\n\n")
                if corr is not None and (strongest_ass[0] is None or abs(corr) > abs(strongest_ass[1])):
                    strongest_ass = (at, corr)

        lines.append("\n")
        if strongest_subj[0] is None:
            lines.append("No sufficient variability to identify strongest subject correlation.\n")
        else:
            lines.append(f"Strongest subject correlation: {strongest_subj[0]} (corr = {strongest_subj[1]:.3f})\n")
        if strongest_ass[0] is None:
            lines.append("No sufficient variability to identify strongest assessment correlation.\n")
        else:
            lines.append(f"Strongest assessment correlation: {strongest_ass[0]} (corr = {strongest_ass[1]:.3f})\n")

        return "".join(lines)

    # ---- Exports / Utilities ----

    def export_excel(self, path: str) -> None:
        try:
            ensure_data_folders()
            self._df.to_excel(path, index=False)
            logger.info("Exported to %s", path)
        except Exception as e:
            logger.exception("Export failed: %s", e)
            raise DataManagerError("Export failed: " + str(e))

    def get_dataframe(self) -> pd.DataFrame:
        return self._df.copy()

    def replace_dataframe(self, df: pd.DataFrame) -> None:
        for c in DEFAULT_COLUMNS:
            if c not in df.columns:
                df[c] = np.nan
        self._df = df[DEFAULT_COLUMNS].copy().reset_index(drop=True)
        if self.autosave:
            self.save()

    def backup(self, dst_folder: Optional[str] = None) -> str:
        dst_folder = dst_folder or BACKUP_DIR
        ensure_data_folders()
        backup_name = f"inmem_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
        path = os.path.join(dst_folder, backup_name)
        atomic_write_df(self._df, path)
        return path
