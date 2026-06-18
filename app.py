# -*- coding: utf-8 -*-
"""
AI Agent CS Analyzer
====================
Phan tich & khuyen nghi AI Agent trong Khoa hoc May tinh
Dung Streamlit + WorkBank data

Chay: pip install streamlit pandas plotly && streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# === Cau hinh trang ===
st.set_page_config(page_title="AI Agent CS", page_icon="🤖", layout="wide")

# === CAC NGHE CS ===
CS_JOBS = [
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

# === AI AGENTS ===
AGENTS = {
    "code": {"name": "Code Agent", "icon": "⚡", "desc": "Sinh code, sua loi, refactor tu dong",
             "tech": "GPT-4, Copilot, Codeium, Tree-sitter", "level": 1},
    "rpa": {"name": "RPA Agent", "icon": "🤖", "desc": "Tu dong hoa nhap lieu, xu ly form, lap lich",
            "tech": "Selenium, PyAutoGUI, UiPath", "level": 1},
    "monitor": {"name": "Monitor Agent", "icon": "📡", "desc": "Giam sat he thong, canh bao bat thuong",
                "tech": "Prometheus, Grafana, ELK", "level": 1},
    "analytic": {"name": "Analytic Agent", "icon": "📊", "desc": "Phan tich data, phat hien pattern, du bao",
                 "tech": "Pandas, sklearn, LangChain, TensorFlow", "level": 2},
    "security": {"name": "Security Agent", "icon": "🔒", "desc": "Phat hien xam nhap, kiem tra bao mat",
                 "tech": "Wazuh, Splunk, ML models", "level": 2},
    "copilot": {"name": "Copilot Agent", "icon": "👨‍💻", "desc": "Tro ly AI realtime cho developer",
                "tech": "GitHub Copilot, Cursor, OpenAPI", "level": 2},
    "autonomous": {"name": "Auto Agent", "icon": "🧠", "desc": "Tu quyet dinh & thuc thi khong can nguoi",
                   "tech": "AutoGPT, CrewAI, RL", "level": 3},
    "collab": {"name": "Collab Agent", "icon": "🤝", "desc": "Hop tac nguoi-AI, chia task, hoc tu feedback",
               "tech": "AutoGen, RAG, Copilot Studio", "level": 3},
}

# Agent khuyen nghi cho tung nghe (da duoc toi uu tu phan tich)
RECS = {
    "Computer Programmers": (["copilot", "code", "rpa"], "Code + RPA la chinh"),
    "Computer Systems Analysts": (["analytic", "collab", "code"], "Can phan tich nhieu"),
    "Computer Systems Engineers/Architects": (["collab", "analytic", "security"], "Thiet ke + Bao mat"),
    "Computer Network Support Specialists": (["monitor", "rpa", "autonomous"], "Giam sat la chinh"),
    "Computer User Support Specialists": (["copilot", "rpa", "monitor"], "Ho tro nguoi dung"),
    "Computer and Information Research Scientists": (["analytic", "autonomous", "collab"], "Nghien cuu"),
    "Computer and Information Systems Managers": (["analytic", "monitor", "collab"], "Quan ly tong the"),
    "Software Quality Assurance Analysts and Testers": (["code", "rpa", "analytic"], "Test automation"),
    "Web Developers": (["copilot", "code", "monitor"], "Web dev + deploy"),
    "Database Administrators": (["monitor", "rpa", "autonomous"], "Backup + giam sat"),
    "Network and Computer Systems Administrators": (["monitor", "rpa", "security"], "Admin + security"),
    "Information Security Analysts": (["security", "monitor", "analytic"], "Bao mat la chinh"),
    "Information Technology Project Managers": (["analytic", "collab", "monitor"], "Quan ly du an"),
    "Web Administrators": (["monitor", "rpa", "security"], "Web admin"),
}


# === LOAD DATA ===
@st.cache_data
def load_data():
    """Doc 4 file CSV tu workbank, loc cac nghe CS."""
    base = Path(__file__).resolve().parent.parent
    def read(name):
        df = pd.read_csv(base / name, encoding="utf-8", low_memory=False)
        return df[df["Occupation (O*NET-SOC Title)"].isin(CS_JOBS)].copy()

    return {
        "tasks": read("task_statement_with_metadata.csv"),
        "desires": read("domain_worker_desires.csv"),
        "workers": read("domain_worker_metadata.csv"),
        "expert": read("expert_rated_technological_capability.csv"),
    }


# === PHAN TICH ===
def calc_scores(data):
    """Tinh API, Readiness, Gap cho tung nghe."""
    d = data["desires"].groupby("Occupation (O*NET-SOC Title)")["Automation Desire Rating"].mean()
    c = data["expert"].groupby("Occupation (O*NET-SOC Title)")["Automation Capacity Rating"].mean()
    u = data["expert"].groupby("Occupation (O*NET-SOC Title)")["Involved Uncertainty"].mean()
    e = data["expert"].groupby("Occupation (O*NET-SOC Title)")["Domain Expertise Requirement"].mean()
    i = data["expert"].groupby("Occupation (O*NET-SOC Title)")["Interpersonal Communication Requirement"].mean()
    a = data["desires"].groupby("Occupation (O*NET-SOC Title)")["Human Agency Scale Rating"].mean()

    df = pd.DataFrame({"desire": d, "capacity": c, "uncertainty": u, "expertise": e, "interpersonal": i, "agency": a})
    df["api"] = (df["desire"]*0.4 + df["capacity"]*0.4 + (6-df["expertise"])*0.1 + (6-df["interpersonal"])*0.1)
    df["api"] = ((df["api"]-1)/4*100).clip(0, 100)
    df["readiness"] = ((df["capacity"] + (6-df["uncertainty"]))/2)
    df["readiness"] = ((df["readiness"]-1)/4*100).clip(0, 100)
    df["collab"] = df["agency"]*0.6 + 0.4   # normalized
    df["collab"] = ((df["collab"]-1)/4*100).clip(0, 100)
    df["gap"] = df["desire"] - df["capacity"]
    return df.sort_values("api", ascending=False)


def top_tasks(occ, data, n=5):
    """Tim task co tiem nang automation cao nhat cho 1 nghe."""
    d = data["desires"][data["desires"]["Occupation (O*NET-SOC Title)"] == occ]
    c = data["expert"][data["expert"]["Occupation (O*NET-SOC Title)"] == occ]
    t = data["tasks"][data["tasks"]["Occupation (O*NET-SOC Title)"] == occ]

    if d.empty or c.empty:
        return pd.DataFrame()

    desire = d.groupby("Task ID")["Automation Desire Rating"].mean().rename("desire")
    cap = c.groupby("Task ID")["Automation Capacity Rating"].mean().rename("capacity")
    merged = desire.to_frame().join(cap, how="outer")
    merged["score"] = merged["desire"].fillna(3)*0.5 + merged["capacity"].fillna(3)*0.5
    merged = merged.sort_values("score", ascending=False).head(n)

    info = t[["Task ID", "Task"]].drop_duplicates("Task ID")
    merged = merged.reset_index().merge(info, on="Task ID", how="left")
    return merged[["Task", "score"]]


# === UI ===
def sidebar():
    with st.sidebar:
        st.markdown("# 🤖 AI Agent CS")
        page = st.radio("", [
            "📊 Dashboard",
            "💼 Chi tiet",
            "🤖 Khuyen nghi",
            "📈 So sanh",
        ], label_visibility="collapsed")
        st.caption("WorkBank dataset | 14 CS occupations")
    return page


# === PAGES ===

def page_dashboard(data):
    st.title("📊 Tong quan AI Agent - Khoa hoc May tinh")
    scores = calc_scores(data)

    # Metric cards
    a, b, c, d = st.columns(4)
    a.metric("CS Occupations", len(scores))
    b.metric("API TB", f"{scores['api'].mean():.1f}%")
    c.metric("Top", f"{scores.index[0]}", help=f"API={scores['api'].iloc[0]:.1f}%")
    d.metric("Readiness TB", f"{scores['readiness'].mean():.1f}%")

    # Bieu do API
    fig = px.bar(scores.reset_index().sort_values("api"),
                 x="api", y="Occupation (O*NET-SOC Title)",
                 color="api", color_continuous_scale="RdYlGn",
                 text_auto=".1f", labels={"api": "API %"})
    fig.update_traces(textposition="outside")
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

    # Bang
    st.subheader("📋 Tong hop")
    display = scores[["api", "readiness", "collab", "gap"]].round(1)
    display.index = [f"{e} {j}" for e, j in zip(["🖥️","🔍","🏗️","🌐","💻","🔬","📊","✅","🌍","🗄️","🔧","🔒","📋","⚙️"], display.index)]
    st.dataframe(display, use_container_width=True)


def page_detail(data):
    st.title("💼 Chi tiet Occupation")
    occ = st.selectbox("Chon nghe:", CS_JOBS)

    scores = calc_scores(data)
    if occ in scores.index:
        r = scores.loc[occ]
        col1, col2, col3 = st.columns(3)
        col1.metric("API", f"{r['api']:.1f}%")
        col2.metric("Readiness", f"{r['readiness']:.1f}%")
        col3.metric("Collab", f"{r['collab']:.1f}%")

    # Top tasks
    st.subheader("🎯 Top task nen uu tien")
    tasks = top_tasks(occ, data)
    if not tasks.empty:
        st.dataframe(tasks, use_container_width=True, hide_index=True)
    else:
        st.info("Chua co du lieu")

    # Agent de xuat
    st.subheader("🤖 AI Agent de xuat")
    if occ in RECS:
        agent_ids, reason = RECS[occ]
        st.success(f"**{reason}**")
        cols = st.columns(len(agent_ids))
        for i, aid in enumerate(agent_ids):
            ag = AGENTS[aid]
            with cols[i]:
                st.markdown(f"### {ag['icon']} {ag['name']}")
                st.caption(ag["desc"])
                st.markdown(f"Cong nghe: `{ag['tech']}`")


def page_recommend(data):
    st.title("🤖 Khuyen nghi AI Agent")
    scores = calc_scores(data)

    # Gioi thieu agent
    with st.expander("📚 Danh muc Agent (nhan de xem)"):
        cols = st.columns(4)
        for i, (_, ag) in enumerate(AGENTS.items()):
            with cols[i % 4]:
                st.markdown(f"**{ag['icon']} {ag['name']}**")
                st.caption(ag["desc"])

    # Bang recommend
    rows = []
    for occ in scores.index:
        if occ in RECS:
            aids, _ = RECS[occ]
            rows.append({
                "Occupation": occ,
                "Agent": ", ".join([AGENTS[a]["icon"] + AGENTS[a]["name"] for a in aids]),
                "API": f"{scores.loc[occ, 'api']:.1f}%",
                "Priority": "Cao" if scores.loc[occ, "api"] > 55 else ("TB" if scores.loc[occ, "api"] > 40 else "Thap"),
            })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Phan phoi
    fig = px.pie(names=["Cao", "TB", "Thap"],
                 values=[sum(1 for r in rows if r["Priority"]=="Cao"),
                         sum(1 for r in rows if r["Priority"]=="TB"),
                         sum(1 for r in rows if r["Priority"]=="Thap")],
                 title="Muc do uu tien", color=["Cao","TB","Thap"],
                 color_discrete_map={"Cao":"#2ca02c","TB":"#ffbb78","Thap":"#d62728"})
    st.plotly_chart(fig, use_container_width=True)


def page_compare(data):
    st.title("📈 So sanh Occupations")
    scores = calc_scores(data)

    chon = st.multiselect("Chon nghe (2-4):", CS_JOBS, default=CS_JOBS[:3])
    if len(chon) >= 2:
        df = scores.loc[chon].reset_index()
        fig = go.Figure()
        for _, row in df.iterrows():
            vals = [row["api"], row["readiness"], row["collab"]]
            fig.add_trace(go.Scatterpolar(r=vals+[vals[0]],
                          theta=["API","Readiness","Collab"]+["API"],
                          name=row["Occupation (O*NET-SOC Title)"], fill="toself"))
        fig.update_layout(polar=dict(radialaxis=dict(range=[0,100])), height=500)
        st.plotly_chart(fig, use_container_width=True)

        # Desire vs Capacity
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="Desire", x=df["Occupation (O*NET-SOC Title)"], y=df["desire"]))
        fig2.add_trace(go.Bar(name="Capacity", x=df["Occupation (O*NET-SOC Title)"], y=df["capacity"]))
        fig2.update_layout(barmode="group", title="Desire vs Capacity", height=400)
        st.plotly_chart(fig2, use_container_width=True)


# === MAIN ===
def main():
    try:
        data = load_data()
    except Exception as e:
        st.error(f"Loi load data: {e}")
        st.stop()

    page = sidebar()
    {"📊 Dashboard": page_dashboard,
     "💼 Chi tiet": page_detail,
     "🤖 Khuyen nghi": page_recommend,
     "📈 So sanh": page_compare}[page](data)


if __name__ == "__main__":
    main()
