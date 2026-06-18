"""
utils.py
========
Cac ham tien ich dung chung cho toan bo project:
  - Xu ly rating (scale 1-5)
  - Mapping ten cot -> nhan hien thi
  - Tao mau sac, icon
  - Helper function cho visualization
"""

import numpy as np
import pandas as pd

# === Dinh nghia mau sac ===
COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c",
    "danger": "#d62728",
    "warning": "#ffbb78",
    "purple": "#9467bd",
    "brown": "#8c564b",
    "pink": "#e377c2",
    "gray": "#7f7f7f",
    "olive": "#bcbd22",
    "cyan": "#17becf",
}

CS_COLORS = {
    "tu_dong_cao": "#2ca02c",    # Xanh la: tu dong hoa cao
    "tu_dong_thap": "#d62728",   # Do: can nhieu nguoi
    "trung_binh": "#ffbb78",     # Cam: trung binh
    "can_thiep": "#1f77b4",      # Xanh duong: can AI ho tro
}

# === Rating label mapping ===
RATING_LABELS = {
    1: "Rat thap",
    2: "Thap",
    3: "Trung binh",
    4: "Cao",
    5: "Rat cao",
}

# === Ten cot can doc cho tung bang ===
COLUMN_MAP = {
    "desire": {
        "task_id": "Task ID",
        "occupation": "Occupation (O*NET-SOC Title)",
        "task": "Task",
        "automation_desire": "Automation Desire Rating",
        "core_skill": "Core Skill Rating",
        "job_security": "Job Security Rating",
        "enjoyment": "Enjoyment Rating",
        "time": "Time",
        "domain_expertise": "Domain Expertise Requirement",
        "interpersonal": "Interpersonal Communication Requirement",
        "uncertainty": "Involved Uncertainty",
        "physical": "Physical Action Requirement",
        "agency": "Human Agency Scale Rating",
    },
    "capability": {
        "task_id": "Task ID",
        "occupation": "Occupation (O*NET-SOC Title)",
        "task": "Task",
        "automation_capacity": "Automation Capacity Rating",
        "domain_expertise": "Domain Expertise Requirement",
        "interpersonal": "Interpersonal Communication Requirement",
        "uncertainty": "Involved Uncertainty",
        "physical": "Physical Action Requirement",
        "agency": "Human Agency Scale Rating",
    },
}


def rating_to_label(rating: float) -> str:
    """
    Chuyen diem rating (1-5) sang nhan chu thich.

    Args:
        rating: Gia tri float 1-5

    Returns:
        Chuoi mo ta
    """
    r = int(round(rating))
    return RATING_LABELS.get(r, "Khong xac dinh")


def rating_to_color(rating: float) -> str:
    """
    Rating cang cao -> mau cang xanh (de tu dong hoa).
    Rating cang thap -> mau cang do (kho tu dong hoa).

    Args:
        rating: Gia tri 1-5

    Returns:
        Ma mau hex
    """
    if rating >= 4:
        return CS_COLORS["tu_dong_cao"]
    elif rating >= 3:
        return CS_COLORS["trung_binh"]
    else:
        return CS_COLORS["tu_dong_thap"]


def gap_color(desire: float, capability: float) -> str:
    """
    Khoang cach giua mong muon va kha nang -> mau sac.

    Args:
        desire: Diem mong muon tu dong hoa (1-5)
        capability: Diem kha nang cong nghe (1-5)

    Returns:
        Ma mau: gap > 1 -> do (khao sat cao hon kha nang)
                gap < -1 -> xanh (kha nang vuot mong muon)
                khac -> xam
    """
    gap = desire - capability
    if gap > 1.5:
        return COLORS["danger"]   # Ky vong cao nhung CN chua theo kip
    elif gap < -1.5:
        return COLORS["success"]  # CN vuot xa nhu cau
    else:
        return COLORS["gray"]     # Can bang


def normalize_series(s: pd.Series) -> pd.Series:
    """
    Chuan hoa min-max ve khoang [0, 1].

    Args:
        s: Series so

    Returns:
        Series da chuan hoa
    """
    return (s - s.min()) / (s.max() - s.min() + 1e-9)


def occupation_icon(occ: str) -> str:
    """
    Tra ve icon cho tung nghe CS.

    Args:
        occ: Ten nghe

    Returns:
        Emoji icon
    """
    icons = {
        "Computer Programmers": "💻",
        "Computer Systems Analysts": "🔍",
        "Computer Systems Engineers/Architects": "🏗️",
        "Computer Network Support Specialists": "🌐",
        "Computer User Support Specialists": "🖥️",
        "Computer and Information Research Scientists": "🔬",
        "Computer and Information Systems Managers": "📊",
        "Software Quality Assurance Analysts and Testers": "✅",
        "Web Developers": "🌍",
        "Database Administrators": "🗄️",
        "Network and Computer Systems Administrators": "🔧",
        "Information Security Analysts": "🔒",
        "Information Technology Project Managers": "📋",
        "Web Administrators": "⚙️",
    }
    return icons.get(occ, "🤖")


def format_percent(val: float) -> str:
    """Dinh dang phan tram."""
    return f"{val:.1f}%"


def format_rating(val: float) -> str:
    """Dinh dang rating."""
    return f"{val:.2f} / 5.00"
