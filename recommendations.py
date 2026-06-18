"""
recommendations.py
==================
Engine khuyen nghi AI Agent cho tung nghe trong linh vuc Khoa hoc May tinh.
Du lieu dau vao tu WorkBank dataset.

Cac loai AI Agent duoc phan loai:
  - RPA Agent (Robotic Process Automation)   : Tu dong hoa tac vu lap lai
  - Copilot Agent                             : Ho tro nguoi dung theo thoi gian thuc
  - Analytic Agent                            : Phan tich du lieu & dua ra insight
  - Autonomous Agent                          : Tu dong hoa hoan toan, khong can nguoi
  - Collaborative Agent                       : Hop tac nguoi - AI
  - Monitoring Agent                          : Giam sat & canh bao
  - Security Agent                            : Bao mat & phat hien xam nhap
  - Code Generation Agent                     : Sinh code tu dong
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np


# ============================================================
# Dinh nghia cac loai AI Agent
# ============================================================

@dataclass
class AIAgent:
    """
    Mo ta mot loai AI Agent.

    Attributes:
        id: Ma dinh danh agent
        name: Ten hien thi
        icon: Icon (emoji)
        description: Mo ta ngan
        capabilities: Danh sach kha nang chinh
        tech_stack: Cong nghe de xuat
        complexity: Do phuc tap (1-5)
    """
    id: str
    name: str
    icon: str
    description: str
    capabilities: List[str]
    tech_stack: List[str]
    complexity: int  # 1-5

    def __str__(self) -> str:
        return f"{self.icon} {self.name}: {self.description[:60]}..."


# ============================================================
# Danh muc AI Agent
# ============================================================

ALL_AGENTS = {
    "rpa": AIAgent(
        id="rpa",
        name="RPA Agent",
        icon="🤖",
        description="Robotic Process Automation - Tu dong hoa cac tac vu lap di lap lai, xu ly form, nhap lieu",
        capabilities=[
            "Tu dong nhap du lieu",
            "Xu ly form/bao cao",
            "Lich trinh tac vu",
            "Tich hop he thong ke thua",
        ],
        tech_stack=["UiPath", "Automation Anywhere", "Selenium", "Python + PyAutoGUI"],
        complexity=2,
    ),
    "copilot": AIAgent(
        id="copilot",
        name="Copilot Agent",
        icon="👨‍💻",
        description="Tro ly AI ho tro nguoi dung theo thoi gian thuc, goi y code, debug",
        capabilities=[
            "Sinh code tu dong",
            "Giai thich code",
            "Ho tro debug",
            "Viet unit test",
        ],
        tech_stack=["GitHub Copilot", "Cursor", "Codeium", "OpenAI API"],
        complexity=3,
    ),
    "analytic": AIAgent(
        id="analytic",
        name="Analytic Agent",
        icon="📊",
        description="Phan tich du lieu, phat hien mau, dua ra insight tu du lieu cong viec",
        capabilities=[
            "Phan tich log/du lieu",
            "Phat hien bat thuong",
            "Du bao xu huong",
            "Tao dashboard tu dong",
        ],
        tech_stack=["Pandas + Plotly", "TensorFlow", "LangChain", "Tableau API"],
        complexity=3,
    ),
    "autonomous": AIAgent(
        id="autonomous",
        name="Autonomous Agent",
        icon="🧠",
        description="Tu dong hoa hoan toan - agent tu quyet dinh va thuc thi khong can nguoi",
        capabilities=[
            "Ra quyet dinh tu dong",
            "Tu hoc tu du lieu",
            "Xu ly su co khong can nguoi",
            "Quan ly he thong 24/7",
        ],
        tech_stack=["Reinforcement Learning", "AutoGPT", "BabyAGI", "LangChain Agents"],
        complexity=5,
    ),
    "collaborative": AIAgent(
        id="collaborative",
        name="Collaborative Agent",
        icon="🤝",
        description="Agent hop tac - lam viec cung nguoi, thuc hien phan cong viec co the tu dong",
        capabilities=[
            "Chia task voi nguoi",
            "De xuat & cho phep duyet",
            "Hoc hoi tu phan hoi",
            "Thich nghi voi cach lam viec",
        ],
        tech_stack=["RAG Pipeline", "CrewAI", "AutoGen", "Microsoft Copilot Studio"],
        complexity=4,
    ),
    "monitor": AIAgent(
        id="monitor",
        name="Monitoring Agent",
        icon="📡",
        description="Giam sat he thong, network, ung dung - canh bao khi co bat thuong",
        capabilities=[
            "Giam sat performance",
            "Canh bao su co",
            "SLA tracking",
            "Anomaly detection",
        ],
        tech_stack=["Prometheus + Grafana", "ELK Stack", "Datadog", "Custom Python Agent"],
        complexity=2,
    ),
    "security": AIAgent(
        id="security",
        name="Security Agent",
        icon="🔒",
        description="Agent bao mat - phat hien tan cong, quan ly phan quyen, kiem tra tuan thu",
        capabilities=[
            "Phat hien xam nhap",
            "Quet lo hong bao mat",
            "Quan ly identity",
            "Kiem tra tuan thu",
        ],
        tech_stack=["Wazuh", "Splunk", "Sentinel", "Custom ML Models"],
        complexity=4,
    ),
    "codegen": AIAgent(
        id="codegen",
        name="Code Generation Agent",
        icon="⚡",
        description="Sinh code, chuyen doi code, refactoring tu dong o quy mo lon",
        capabilities=[
            "Sinh code tu yeu cau",
            "Chuyen doi ngon ngu",
            "Refactor code tu dong",
            "Tao documentation",
        ],
        tech_stack=["GPT-4/Copilot", "Tree-sitter", "AST Analysis", "OpenAI API"],
        complexity=3,
    ),
}


# ============================================================
# Mapping: Occupation -> AI Agents phu hop
# Duoc xay dung tu phan tich WorkBank data
# ============================================================

# Dinh nghia rule-based matching tu dac thu cong viec
OCCUPATION_AGENT_MAPPING = {
    "Computer Programmers": {
        "agents": ["copilot", "codegen", "rpa"],
        "explanation": "Lap trinh vien co the huong loi nhat tu code generation va copilot",
    },
    "Computer Systems Analysts": {
        "agents": ["analytic", "collaborative", "codegen"],
        "explanation": "Chuyen gia phan tich he thong can su ket hop giua phan tich du lieu va cong cu code",
    },
    "Computer Systems Engineers/Architects": {
        "agents": ["collaborative", "analytic", "security"],
        "explanation": "Kien truc su he thong can agent ho tro thiet ke, phan tich va bao mat",
    },
    "Computer Network Support Specialists": {
        "agents": ["monitor", "rpa", "autonomous"],
        "explanation": "Ho tro network co the tu dong hoa hoan toan cac tac vu giam sat va backup",
    },
    "Computer User Support Specialists": {
        "agents": ["copilot", "rpa", "collaborative"],
        "explanation": "IT support co the dung AI de tra loi cau hoi va tu dong hoa ticket",
    },
    "Computer and Information Research Scientists": {
        "agents": ["analytic", "autonomous", "collaborative"],
        "explanation": "Nha nghien cuu CS can agent phan tich du lieu va tu dong hoa thi nghiem",
    },
    "Computer and Information Systems Managers": {
        "agents": ["analytic", "monitor", "collaborative"],
        "explanation": "Quan ly he thong can dashboard thong minh va agent ho tro quyet dinh",
    },
    "Software Quality Assurance Analysts and Testers": {
        "agents": ["codegen", "rpa", "analytic"],
        "explanation": "QA co the tu dong hoa test case generation va phan tich bug reports",
    },
    "Web Developers": {
        "agents": ["copilot", "codegen", "rpa"],
        "explanation": "Web dev duoc huong loi tu copilot cho frontend/backend va tu dong hoa deploy",
    },
    "Database Administrators": {
        "agents": ["monitor", "rpa", "autonomous"],
        "explanation": "DBA can agent giam sat performance va backup tu dong",
    },
    "Network and Computer Systems Administrators": {
        "agents": ["monitor", "rpa", "security"],
        "explanation": "Admin he thong can agent giam sat, canh bao va phat hien xam nhap",
    },
    "Information Security Analysts": {
        "agents": ["security", "monitor", "analytic"],
        "explanation": "Chuyen gia bao mat can agent quet lo hong va phan tich log bao mat",
    },
    "Information Technology Project Managers": {
        "agents": ["analytic", "collaborative", "monitor"],
        "explanation": "PM IT can agent phan tich tien do, rui ro va tracking du an",
    },
    "Web Administrators": {
        "agents": ["monitor", "rpa", "security"],
        "explanation": "Web admin can agent theo doi uptime, bao mat va tu dong hoa maintain",
    },
}


class RecommendationEngine:
    """
    Engine khuyen nghi AI Agent dua tren du lieu WorkBank.
    """

    def __init__(self, analyzer=None):
        """
        Args:
            analyzer: Optional CSAnalyzer instance de lay scores
        """
        self.analyzer = analyzer

    def get_agents_for_occupation(self, occupation: str) -> Tuple[List[AIAgent], str]:
        """
        Tra ve danh sach AI Agent phu hop cho mot nghe.

        Args:
            occupation: Ten nghe nghe

        Returns:
            (list_agent, explanation): Danh sach agent va loi giai thich
        """
        mapping = OCCUPATION_AGENT_MAPPING.get(occupation)
        if mapping is None:
            # Fallback: tra ve agent generic
            return self._generic_recommendation()

        agents = [ALL_AGENTS[agent_id] for agent_id in mapping["agents"]]
        return agents, mapping["explanation"]

    def _generic_recommendation(self) -> Tuple[List[AIAgent], str]:
        """Tra ve recommendation generic khi khong co mapping."""
        return [
            ALL_AGENTS["copilot"],
            ALL_AGENTS["analytic"],
            ALL_AGENTS["rpa"],
        ], "Khuyen nghi chung cho cac nghe lien quan den may tinh"

    def get_priority_agents(self) -> Dict[str, List[AIAgent]]:
        """
        Xep hang uu tien AI Agent dua tren diem API.
        """
        if self.analyzer is None:
            return {}

        scores = self.analyzer.compute_all_scores()
        result = {}
        for _, row in scores.iterrows():
            occ = row["Occupation (O*NET-SOC Title)"]
            agents, _ = self.get_agents_for_occupation(occ)
            result[occ] = {
                "agents": agents,
                "api_score": row["api_score"],
                "readiness": row["readiness_score"],
            }
        return result

    def recommend_implementation_plan(self, occupation: str) -> Dict:
        """
        De xuat lo trinh trien khai AI Agent cho mot nghe cu the.

        Args:
            occupation: Ten nghe

        Returns:
            Dict: {
                'short_term': ...,
                'medium_term': ...,
                'long_term': ...,
                'total_impact': ...
            }
        """
        agents, explanation = self.get_agents_for_occupation(occupation)

        # Phan loai theo do phuc tap
        short_term = [a for a in agents if a.complexity <= 2]
        medium_term = [a for a in agents if a.complexity == 3]
        long_term = [a for a in agents if a.complexity >= 4]

        # Tinh impact estimate (gia dinh)
        n_agents = len(agents)
        total_impact = min(n_agents * 15, 70)  # Toi da 70%

        return {
            "short_term": short_term,
            "medium_term": medium_term,
            "long_term": long_term,
            "explanation": explanation,
            "total_impact": total_impact,
        }

    def get_all_recommendations(self) -> pd.DataFrame:
        """
        Tao bang tong hop recommendation cho tat ca nghe CS.

        Returns:
            DataFrame: [Occupation, Recommended Agents, API Score, Readiness, Priority]
        """
        if self.analyzer is None:
            return pd.DataFrame()

        scores = self.analyzer.compute_all_scores()
        rows = []
        for _, row in scores.iterrows():
            occ = row["Occupation (O*NET-SOC Title)"]
            agents, _ = self.get_agents_for_occupation(occ)
            rows.append({
                "Occupation": occ,
                "Recommended Agents": ", ".join([a.name for a in agents]),
                "Agent Icons": " ".join([a.icon for a in agents]),
                "API Score": f"{row['api_score']:.1f}",
                "Readiness Score": f"{row['readiness_score']:.1f}",
                "Priority": "Cao" if row["api_score"] > 60 else ("Trung binh" if row["api_score"] > 40 else "Thap"),
            })

        return pd.DataFrame(rows)


# ============================================================
# Chay thu
# ============================================================
if __name__ == "__main__":
    print("=== Kiem tra Recommendation Engine ===\n")

    # Test voi 2 nghe
    engine = RecommendationEngine()
    for occ in ["Computer Programmers", "Software Quality Assurance Analysts and Testers"]:
        agents, expl = engine.get_agents_for_occupation(occ)
        print(f"\n--- {occ} ---")
        print(f"  Giai thich: {expl}")
        print(f"  De xuat agents:")
        for a in agents:
            print(f"    {a.icon} {a.name}")
        plan = engine.recommend_implementation_plan(occ)
        print(f"  Ngan han: {[a.name for a in plan['short_term']]}")
        print(f"  Trung han: {[a.name for a in plan['medium_term']]}")
        print(f"  Dai han: {[a.name for a in plan['long_term']]}")
        print(f"  Impact: ~{plan['total_impact']}%")
