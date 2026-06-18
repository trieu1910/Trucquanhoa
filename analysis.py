"""
analysis.py
===========
Module phan tich du lieu WorkBank cho linh vuc Khoa hoc May tinh.
Cung cap cac ham tinh toan chi so:
  - Automation Potential Index (API) - Chi so tiem nang tu dong hoa
  - AI Readiness Score - Diem san sang cho AI
  - Human-AI Collaboration Score - Diem hop tac nguoi-may
  - Gap Analysis - Phan tich khoang cach giua mong muon va thuc te
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class CSAnalyzer:
    """
    Phan tich du lieu WorkBank cho cac nghe Khoa hoc May tinh.

    Usage:
        analyzer = CSAnalyzer(desire_df, capability_df, tasks_df)
        scores = analyzer.compute_all_scores()
    """

    def __init__(
        self,
        desires: pd.DataFrame,
        capability: pd.DataFrame,
        tasks: pd.DataFrame,
    ):
        """
        Args:
            desires: DataFrame tu domain_worker_desires.csv (da loc CS)
            capability: DataFrame tu expert_rated_technological_capability.csv
            tasks: DataFrame tu task_statement_with_metadata.csv
        """
        self.desires = desires
        self.capability = capability
        self.tasks = tasks

        # Chuan hoa ten cot
        self.occ_col = "Occupation (O*NET-SOC Title)"
        self.task_col = "Task"
        self.task_id_col = "Task ID"

    def compute_automation_potential(self) -> pd.DataFrame:
        """
        Tinh chi so Automation Potential Index (API) cho tung nghe.

        API = trung binh cua:
          - Automation Desire Rating (mong muon tu nguoi lao dong)
          - Automation Capacity Rating (kha nang tu chuyen gia)
          - (nghich dao) Domain Expertise Requirement
          - (nghich dao) Interpersonal Communication Requirement

        Returns:
            DataFrame: [occupation, api_score, desire_mean, capacity_mean]
        """
        # --- Tinh desire trung binh theo occupation ---
        desire_cols = ["Automation Desire Rating", "Time"]
        desire_avg = (
            self.desires.groupby(self.occ_col)[desire_cols]
            .mean()
            .rename(columns={"Automation Desire Rating": "desire_mean"})
        )

        # --- Tinh capacity trung binh (tu expert rating) ---
        cap_cols = {
            "Automation Capacity Rating": "capacity_mean",
            "Involved Uncertainty": "uncertainty_mean",
            "Domain Expertise Requirement": "expertise_mean",
            "Interpersonal Communication Requirement": "interpersonal_mean",
        }
        cap_avg = (
            self.capability.groupby(self.occ_col)[list(cap_cols.keys())]
            .mean()
            .rename(columns=cap_cols)
        )

        # Ket hop
        result = desire_avg.join(cap_avg, how="outer")

        # Tinh API = desire * 0.4 + capacity * 0.4
        #           + (6 - expertise) * 0.1 + (6 - interpersonal) * 0.1
        # Y nghia: chuyen mon hoac giao tiep cang cao -> API cang thap
        result["api_score"] = (
            result["desire_mean"].fillna(3) * 0.4
            + result["capacity_mean"].fillna(3) * 0.4
            + (6 - result["expertise_mean"].fillna(3)) * 0.1
            + (6 - result["interpersonal_mean"].fillna(3)) * 0.1
        )

        # Chuan hoa API ve thang 0-100
        result["api_score"] = ((result["api_score"] - 1) / 4 * 100).clip(0, 100)

        result = result.reset_index()
        return result.sort_values("api_score", ascending=False)

    def compute_gap_analysis(self) -> pd.DataFrame:
        """
        Phan tich Gap giua Mong muon (Desire) va Kha nang (Capability).

        Gap > 0: Nguoi lao dong muon tu dong hoa nhieu hon kha nang hien tai
        Gap < 0: Cong nghe co the lam nhieu hon mong muon

        Returns:
            DataFrame: [occupation, desire_mean, capacity_mean, gap]
        """
        # Desire trung binh
        desire_mean = (
            self.desires.groupby(self.occ_col)["Automation Desire Rating"]
            .mean()
            .rename("desire_mean")
        )

        # Capacity trung binh
        capacity_mean = (
            self.capability.groupby(self.occ_col)["Automation Capacity Rating"]
            .mean()
            .rename("capacity_mean")
        )

        result = pd.DataFrame({
            "desire_mean": desire_mean,
            "capacity_mean": capacity_mean,
        }).dropna()

        result["gap"] = result["desire_mean"] - result["capacity_mean"]
        result = result.reset_index()
        return result.sort_values("gap", ascending=False)

    def compute_ai_readiness(self) -> pd.DataFrame:
        """
        Tinh AI Readiness Score cho tung nghe.

        Cong thuc:
          readiness = (capacity_mean + (6 - uncertainty_mean)) / 2
          - capacity_mean cao: cong nghe san sang
          - uncertainty_mean thap: it bat dinh -> de AI hoa

        Returns:
            DataFrame: [occupation, readiness_score, capacity_mean, uncertainty_mean]
        """
        cap = (
            self.capability.groupby(self.occ_col)[
                ["Automation Capacity Rating", "Involved Uncertainty"]
            ]
            .mean()
            .rename(columns={
                "Automation Capacity Rating": "capacity_mean",
                "Involved Uncertainty": "uncertainty_mean",
            })
        )

        cap["readiness_score"] = (
            cap["capacity_mean"] + (6 - cap["uncertainty_mean"])
        ) / 2

        cap["readiness_score"] = ((cap["readiness_score"] - 1) / 4 * 100).clip(0, 100)
        cap = cap.reset_index()
        return cap.sort_values("readiness_score", ascending=False)

    def compute_human_ai_collab(self) -> pd.DataFrame:
        """
        Tinh chi so Human-AI Collaboration.

        Diem cao -> cong viec phu hop voi hinh thuc nguoi + AI cung lam.
        Duoc tinh tu:
          - Human Agency Scale Rating (mong muon giu lai quyen con nguoi)
          - Cac ly do giu lai con nguoi (Empathy, Ethical, v.v.)

        Returns:
            DataFrame: [occupation, agency_mean, collab_score]
        """
        # Su dung desire data de phan tich agency
        agency_cols = [
            "Human Agency Scale Rating",
            "Reasons for Human Agency - Empathy",
            "Reasons for Human Agency - Ethical",
            "Reasons for Human Agency - Control",
            "Reasons for Human Agency - Quality Oversight",
        ]

        ag = self.desires.groupby(self.occ_col)[agency_cols[0]].mean().rename("agency_mean")

        # Dem so luong ly do giu lai con nguoi (Empathy, Ethical, etc.)
        reason_cols = agency_cols[1:]
        if all(c in self.desires.columns for c in reason_cols):
            # Chuyen True/False -> 1/0
            for c in reason_cols:
                self.desires[c] = self.desires[c].apply(
                    lambda x: 1 if str(x).strip().upper() == "TRUE" else 0
                )
            reasons_sum = self.desires.groupby(self.occ_col)[reason_cols].sum()
            reasons_sum["total_reasons"] = reasons_sum.sum(axis=1)
            ag = ag.to_frame().join(reasons_sum[["total_reasons"]], how="left")
        else:
            ag = ag.to_frame()
            ag["total_reasons"] = 0

        # Collab score: agency cao + nhieu ly do bao toan con nguoi
        ag["collab_score"] = (
            ag["agency_mean"] * 0.6
            + (ag["total_reasons"] / ag["total_reasons"].max() * 5).fillna(2.5) * 0.4
        )
        ag["collab_score"] = ((ag["collab_score"] - 1) / 4 * 100).clip(0, 100)

        ag = ag.reset_index()
        return ag.sort_values("collab_score", ascending=False)

    def compute_all_scores(self) -> pd.DataFrame:
        """
        Tinh toan tat ca cac chi so va gop lai.

        Returns:
            DataFrame tong hop cac chi so cho tung nghe CS
        """
        api = self.compute_automation_potential()
        gap = self.compute_gap_analysis()
        readiness = self.compute_ai_readiness()
        collab = self.compute_human_ai_collab()

        # Gop lai
        merged = api[[self.occ_col, "api_score"]].merge(
            gap[[self.occ_col, "desire_mean", "capacity_mean", "gap"]],
            on=self.occ_col, how="outer"
        ).merge(
            readiness[[self.occ_col, "readiness_score"]],
            on=self.occ_col, how="outer"
        ).merge(
            collab[[self.occ_col, "collab_score"]],
            on=self.occ_col, how="outer"
        )

        return merged.sort_values("api_score", ascending=False)

    def get_top_tasks_for_automation(self, occupation: str, top_n: int = 10) -> pd.DataFrame:
        """
        Tim cac task co tiem nang tu dong hoa cao nhat cho mot nghe cu the.

        Args:
            occupation: Ten nghe (vd: 'Computer Programmers')
            top_n: So luong task muon lay

        Returns:
            DataFrame cac task co desire + capacity cao
        """
        # Lay desire data cho occupation nay
        d = self.desires[self.desires[self.occ_col] == occupation].copy()
        c = self.capability[self.capability[self.occ_col] == occupation]
        t = self.tasks[self.tasks[self.occ_col] == occupation]

        # Tinh diem tong hop
        if not d.empty and not c.empty:
            # Trung binh desire cho tung task (neu nhieu nguoi danh gia)
            task_desire = d.groupby(self.task_id_col)["Automation Desire Rating"].mean().rename("desire")
            task_cap = c.groupby(self.task_id_col)["Automation Capacity Rating"].mean().rename("capacity")

            task_scores = task_desire.to_frame().join(task_cap, how="outer")
            task_scores["total_score"] = (
                task_scores["desire"].fillna(3) * 0.5
                + task_scores["capacity"].fillna(3) * 0.5
            )
            task_scores = task_scores.sort_values("total_score", ascending=False).head(top_n)

            # Ghep voi mo ta task
            if self.task_col in t.columns:
                task_info = t[[self.task_id_col, self.task_col]].drop_duplicates(self.task_id_col)
                task_scores = task_scores.reset_index().merge(task_info, on=self.task_id_col, how="left")

            return task_scores

        return pd.DataFrame()


if __name__ == "__main__":
    print("=== Kiem tra Analyzer ===")
    from data_loader import load_cs_data

    data = load_cs_data()
    analyzer = CSAnalyzer(data["desires"], data["capability"], data["tasks"])
    scores = analyzer.compute_all_scores()
    print(scores.to_string())
