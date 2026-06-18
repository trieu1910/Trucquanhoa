"""
data_loader.py
==============
Module load du lieu tu WorkBank dataset.
Chuyen: Load va tien xu ly 4 file CSV de phuc vu phan tich AI Agent.

WorkBank dataset gom:
  1. task_statement_with_metadata.csv   - Mo ta cong viec chuan O*NET
  2. domain_worker_desires.csv          - Khao sat nguoi lao dong ve mong muon tu dong hoa
  3. domain_worker_metadata.csv         - Thong tin nhan khau hoc cua nguoi tham gia
  4. expert_rated_technological_capability.csv - Danh gia chuyen gia ve kha nang cong nghe
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, List

# ---- Cac nganh nghe thuoc linh vuc Khoa hoc May tinh (Computer Science) ----
CS_OCCUPATIONS = [
    "Computer Programmers",
    "Computer Systems Analysts",
    "Computer Systems Engineers/Architects",
    "Computer Network Support Specialists",
    "Computer User Support Specialists",
    "Computer and Information Research Scientists",
    "Computer and Information Systems Managers",
    "Software Quality Assurance Analysts and Testers",
    "Web Developers",
    "Database Administrators",
    "Network and Computer Systems Administrators",
    "Information Security Analysts",
    "Information Technology Project Managers",
    "Web Administrators",
]


def load_csv(filename: str, data_dir: str = None) -> pd.DataFrame:
    """
    Load file CSV tu thu muc workbank.

    Args:
        filename: Ten file CSV (vd: 'task_statement_with_metadata.csv')
        data_dir: Duong dan den thu muc chua file. Mac dinh la thu muc cha.

    Returns:
        DataFrame chua du lieu
    """
    if data_dir is None:
        # Mac dinh: thu muc hien tai -> len 1 cap (project -> workbank)
        data_dir = Path(__file__).resolve().parent.parent

    filepath = Path(data_dir) / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Khong tim thay file: {filepath}")

    # Doc file voi encoding UTF-8, bo qua dong loi
    df = pd.read_csv(filepath, encoding="utf-8", low_memory=False)
    print(f"[OK] Da load {filename}: {df.shape[0]} dong x {df.shape[1]} cot")
    return df


def filter_cs_occupations(df: pd.DataFrame, col_name: str = "Occupation (O*NET-SOC Title)") -> pd.DataFrame:
    """
    Loc cac dong chi thuoc linh vuc Khoa hoc May tinh.

    Args:
        df: DataFrame goc
        col_name: Ten cot chua ten nghe nghiep

    Returns:
        DataFrame chi chua cac nghe CS
    """
    mask = df[col_name].isin(CS_OCCUPATIONS)
    filtered = df[mask].copy()
    print(f"[OK] Da loc {filtered.shape[0]} dong CS tu {df.shape[0]} dong")
    return filtered


def load_all_data(data_dir: str = None) -> Dict[str, pd.DataFrame]:
    """
    Load toan bo 4 file CSV cua WorkBank.

    Args:
        data_dir: Duong dan thu muc workbank

    Returns:
        Dict: {
            'tasks': task_statement df,
            'desires': domain_worker_desires df,
            'metadata': domain_worker_metadata df,
            'capability': expert_rated_capability df
        }
    """
    data = {
        "tasks": load_csv("task_statement_with_metadata.csv", data_dir),
        "desires": load_csv("domain_worker_desires.csv", data_dir),
        "metadata": load_csv("domain_worker_metadata.csv", data_dir),
        "capability": load_csv("expert_rated_technological_capability.csv", data_dir),
    }
    return data


def load_cs_data(data_dir: str = None) -> Dict[str, pd.DataFrame]:
    """
    Load toan bo du lieu va loc ra cac nghe CS.

    Returns:
        Dict chua DataFrame da loc theo CS occupations
    """
    raw = load_all_data(data_dir)
    cs_data = {}
    for key in raw:
        cs_data[key] = filter_cs_occupations(raw[key])
    return cs_data


def get_summary_stats(df: pd.DataFrame) -> dict:
    """
    Tinh cac thong ke co ban cho DataFrame.

    Args:
        df: DataFrame can phan tich

    Returns:
        Dict chua: so_dong, so_cot, so_nghe_duy_nhat, cot_thieu
    """
    stats = {
        "rows": df.shape[0],
        "cols": df.shape[1],
        "unique_occupations": df["Occupation (O*NET-SOC Title)"].nunique()
            if "Occupation (O*NET-SOC Title)" in df.columns else 0,
        "missing": df.isnull().sum().to_dict(),
    }
    return stats


# ============================================================
# Chay thu truc tiep: python data_loader.py
# ============================================================
if __name__ == "__main__":
    print("=== Kiem tra load du lieu ===")
    data = load_cs_data()
    for name, df in data.items():
        print(f"\n--- {name} ---")
        stats = get_summary_stats(df)
        print(f"  So dong: {stats['rows']}")
        print(f"  So nghe CS: {stats['unique_occupations']}")
        print(f"  Cac cot: {list(df.columns[:8])}...")
