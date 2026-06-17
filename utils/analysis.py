"""
analysis.py
Handles all data loading, cleaning, and KPI computation
for the UAC Care Transition Efficiency project.
"""

import pandas as pd
import numpy as np

DATA_PATH = "data/HHS_Unaccompanied_Alien_Children_Program.csv"

# ── Column mapping ──────────────────────────────────────────────────────────
COL_MAP = {
    "Children apprehended and placed in CBP custody*": "cbp_intake",
    "Children in CBP custody":                         "cbp_load",
    "Children transferred out of CBP custody":         "cbp_transfers",
    "Children in HHS Care":                            "hhs_load",
    "Children discharged from HHS Care":               "hhs_discharges",
}


def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    """
    Load, clean, and return the UAC dataset as a ready-to-use DataFrame.
    Steps performed:
      1. Drop fully blank rows (rows 720-1169 in raw file).
      2. Parse 'Date' as datetime.
      3. Strip commas from 'Children in HHS Care' and cast to float.
      4. Rename columns to short aliases via COL_MAP.
      5. Sort chronologically and reset index.
    """
    df = pd.read_csv(path)

    # Drop blank rows (450 NaN rows at the bottom of the raw file)
    df = df.dropna(subset=["Date"]).copy()

    # Fix HHS Care column — stored as "2,484" strings
    df["Children in HHS Care"] = (
        df["Children in HHS Care"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .astype(float)
    )

    # Parse dates
    df["Date"] = pd.to_datetime(df["Date"])

    # Rename to short names
    df.rename(columns=COL_MAP, inplace=True)

    # Sort oldest → newest
    df = df.sort_values("Date").reset_index(drop=True)

    return df


def compute_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute all five KPIs and temporal features on top of the clean DataFrame.

    KPIs:
      transfer_efficiency    = cbp_transfers / cbp_load          (0–1+ ratio)
      discharge_effectiveness= hhs_discharges / hhs_load         (0–1 ratio)
      pipeline_throughput    = (transfers + discharges) / (intake + transfers)
      backlog_rate           = cbp_intake - hhs_discharges        (net daily load)
      outcome_stability      = 7-day rolling std of discharge_effectiveness

    Temporal features:
      weekday, month, is_weekend, year, quarter
    """
    df = df.copy()

    # KPI 1 — Transfer Efficiency Ratio
    df["transfer_efficiency"] = (
        df["cbp_transfers"] / df["cbp_load"].replace(0, np.nan)
    )

    # KPI 2 — Discharge Effectiveness Index
    df["discharge_effectiveness"] = (
        df["hhs_discharges"] / df["hhs_load"].replace(0, np.nan)
    )

    # KPI 3 — Pipeline Throughput Rate
    total_exits   = df["cbp_transfers"] + df["hhs_discharges"]
    total_entries = (df["cbp_intake"] + df["cbp_transfers"]).replace(0, np.nan)
    df["pipeline_throughput"] = total_exits / total_entries

    # KPI 4 — Backlog Accumulation Rate (positive = more entering than leaving)
    df["backlog_rate"] = df["cbp_intake"] - df["hhs_discharges"]

    # KPI 5 — Outcome Stability Score (lower = more stable)
    df["outcome_stability"] = (
        df["discharge_effectiveness"].rolling(window=7, min_periods=3).std()
    )

    # Temporal
    df["weekday"]    = df["Date"].dt.day_name()
    df["month"]      = df["Date"].dt.to_period("M").astype(str)
    df["year"]       = df["Date"].dt.year
    df["quarter"]    = df["Date"].dt.to_period("Q").astype(str)
    df["is_weekend"] = df["Date"].dt.dayofweek >= 5

    return df


def get_summary(df: pd.DataFrame) -> dict:
    """Return a dict of headline summary stats used in KPI cards."""
    return {
        "avg_transfer_efficiency":     df["transfer_efficiency"].mean(),
        "avg_discharge_effectiveness": df["discharge_effectiveness"].mean(),
        "avg_pipeline_throughput":     df["pipeline_throughput"].mean(),
        "avg_backlog_rate":            df["backlog_rate"].mean(),
        "avg_outcome_stability":       df["outcome_stability"].mean(),
        "total_days":                  len(df),
        "date_min":                    df["Date"].min(),
        "date_max":                    df["Date"].max(),
        "max_hhs_load":                df["hhs_load"].max(),
        "max_cbp_intake":              df["cbp_intake"].max(),
    }
