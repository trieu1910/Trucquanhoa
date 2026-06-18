# -*- coding: utf-8 -*-
"""
AI Agent CS Analyzer
====================
Phan tich & khuyen nghi AI Agent trong Khoa hoc May tinh
Dung Streamlit + WorkBank data

SO DO LUONG:
  WorkBank (4 CSV)
       │
       ▼
  load_data() ──► loc 14 nghe CS
       │
       ▼
  calc_scores() ──► API | Readiness | Gap | Collab
       │
       ├──► page_dashboard()   : Tong quan
       ├──► page_detail()      : 1 nghe + top_tasks() + agent
       ├──► page_recommend()   : Bang khuyen nghi
       └──► page_compare()     : So sanh nhieu nghe

Chay: pip install streamlit pandas plotly && streamlit run app.py
"""

# === Thu vien ===
import streamlit as st     # Tao web app
import pandas as pd        # Xu ly du lieu bang
import numpy as np         # Tinh toan so
import plotly.express as px   # Ve bieu do nhanh
import plotly.graph_objects as go  # Ve bieu do tuy chinh
from pathlib import Path   # Xu ly duong dan file

# === Cai dat trang web: title, icon, che do rong ===
st.set_page_config(page_title="AI Agent CS", page_icon="🤖", layout="wide")

# === DANH SACH 14 NGHE TRONG LINH VUC KHOA HOC MAY TINH ===
# Day la cac nghe duoc loc tu WorkBank dataset
# Moi nghe co ma O*NET-SOC rieng
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

# === DINH NGHIA 8 LOAI AI AGENT ===
# Moi agent co: ten, icon, mo ta, cong nghe, do phuc tap (1=thap, 3=cao)
# Day la nhung agent pho bien nhat trong CS hien nay
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

# === MAP: MOI NGHE -> AGENT KHUYEN NGHI ===
# Mo^i nghe duoc: (danh sach agent_id, ly do)
# Duoc xay dung tu phan tich WorkBank + dac thu tung nghe
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


# ============================================================
# PHAN 1: LOAD DU LIEU TU FILE CSV
# ============================================================

@st.cache_data
def load_data():
    """
    Doc 4 file CSV tu thu muc workbank1/ (cap tren).
    Chi lay nhung dong thuoc 14 nghe CS.
    Ket qua duoc cache de khoi doc lai khi refresh.
    """
    # Di len 1 cap: tu ai_agent_cs/ -> workbank1/
    base = Path(__file__).resolve().parent.parent

    # Ham doc 1 file va loc nghe CS
    def read(name):
        df = pd.read_csv(base / name, encoding="utf-8", low_memory=False)
        return df[df["Occupation (O*NET-SOC Title)"].isin(CS_JOBS)].copy()

    # Tra ve 4 bang du lieu
    return {
        "tasks": read("task_statement_with_metadata.csv"),   # Mo ta cong viec tu O*NET
        "desires": read("domain_worker_desires.csv"),         # Khao sat mong muon tu dong hoa
        "workers": read("domain_worker_metadata.csv"),         # Thong tin nguoi tham gia
        "expert": read("expert_rated_technological_capability.csv"),  # Danh gia chuyen gia
    }


# ============================================================
# PHAN 2: TINH TOAN CHI SO
# ============================================================

def calc_scores(data):
    """
    Tinh 4 chi so chinh cho tung nghe:
      - API: Tiem nang tu dong hoa (0-100%)
      - Readiness: Muc do san sang cua cong nghe (0-100%)
      - Collab: Muc do phu hop cho hop tac nguoi-AI (0-100%)
      - Gap: Chenh lech Desire - Capacity (am/duong)

    Cach tinh:
      1. Gom 4 bang du lieu theo Occupation
      2. Tinh trung binh cho tung chi so
      3. Ap dung cong thuc da dinh nghia
    """
    # Buoc 1: Gom nhom va tinh trung binh cho tung nghe
    d = data["desires"].groupby("Occupation (O*NET-SOC Title)")["Automation Desire Rating"].mean()
    c = data["expert"].groupby("Occupation (O*NET-SOC Title)")["Automation Capacity Rating"].mean()
    u = data["expert"].groupby("Occupation (O*NET-SOC Title)")["Involved Uncertainty"].mean()
    e = data["expert"].groupby("Occupation (O*NET-SOC Title)")["Domain Expertise Requirement"].mean()
    i = data["expert"].groupby("Occupation (O*NET-SOC Title)")["Interpersonal Communication Requirement"].mean()
    a = data["desires"].groupby("Occupation (O*NET-SOC Title)")["Human Agency Scale Rating"].mean()

    # Buoc 2: Gom vao 1 bang
    df = pd.DataFrame({"desire": d, "capacity": c, "uncertainty": u,
                       "expertise": e, "interpersonal": i, "agency": a})

    # Buoc 3: Tinh API - trong so: Desire 40%, Capacity 40%, chuyen mon 10%, giao tiep 10%
    df["api"] = (df["desire"]*0.4 + df["capacity"]*0.4
                 + (6-df["expertise"])*0.1 + (6-df["interpersonal"])*0.1)
    df["api"] = ((df["api"]-1)/4*100).clip(0, 100)  # Chuan hoa ve 0-100%

    # Buoc 4: Tinh Readiness - cong nghe san sang = f(Capacity, Uncertainty)
    df["readiness"] = ((df["capacity"] + (6-df["uncertainty"]))/2)
    df["readiness"] = ((df["readiness"]-1)/4*100).clip(0, 100)

    # Buoc 5: Tinh Collab - muc do phu hop cho nguoi + AI
    df["collab"] = df["agency"]*0.6 + 0.4
    df["collab"] = ((df["collab"]-1)/4*100).clip(0, 100)

    # Buoc 6: Tinh Gap = Desire - Capacity (duong = thieu, am = thua)
    df["gap"] = df["desire"] - df["capacity"]

    # Sap xep: nghe co API cao nhat len dau
    return df.sort_values("api", ascending=False)


def top_tasks(occ, data, n=5):
    """
    Tim n task co tiem nang tu dong hoa cao nhat
    cho mot nghe cu the.
    Diem = (Desire + Capacity) / 2, moi yeu to 50%.

    Args:
        occ: Ten nghe (vd: "Computer Programmers")
        data: Dict 4 bang du lieu
        n: So luong task muon lay

    Returns:
        DataFrame: [Task, score]
    """
    # Loc 3 bang theo nghe
    d = data["desires"][data["desires"]["Occupation (O*NET-SOC Title)"] == occ]
    c = data["expert"][data["expert"]["Occupation (O*NET-SOC Title)"] == occ]
    t = data["tasks"][data["tasks"]["Occupation (O*NET-SOC Title)"] == occ]

    # Neu khong co du lieu -> tra ve rong
    if d.empty or c.empty:
        return pd.DataFrame()

    # Tinh diem trung binh Desire va Capacity cho tung Task ID
    desire = d.groupby("Task ID")["Automation Desire Rating"].mean().rename("desire")
    cap = c.groupby("Task ID")["Automation Capacity Rating"].mean().rename("capacity")

    # Ket hop va tinh tong diem
    merged = desire.to_frame().join(cap, how="outer")
    merged["score"] = merged["desire"].fillna(3)*0.5 + merged["capacity"].fillna(3)*0.5
    merged = merged.sort_values("score", ascending=False).head(n)

    # Ghep voi mo ta task tu bang tasks
    info = t[["Task ID", "Task"]].drop_duplicates("Task ID")
    merged = merged.reset_index().merge(info, on="Task ID", how="left")

    return merged[["Task", "score"]]


# ============================================================
# PHAN 3: GIAO DIEN NGUOI DUNG (UI)
# ============================================================

def sidebar():
    """
    Tao thanh ben trai voi menu dieu huong.
    Nguoi dung chon trang bang nut radio.
    """
    with st.sidebar:
        st.markdown("# 🤖 AI Agent CS")
        # Menu chinh: 4 trang
        page = st.radio("", [
            "📊 Dashboard",
            "💼 Chi tiet",
            "🤖 Khuyen nghi",
            "📈 So sanh",
        ], label_visibility="collapsed")
        st.caption("WorkBank dataset | 14 CS occupations")
    return page


# ============================================================
# PHAN 4: CAC TRANG
# ============================================================

def page_dashboard(data):
    """
    Trang 1 - Dashboard: Tong quan tat ca chi so.
    Hien thi:
      - 4 the metric (so nghe, API TB, Top nghe, Readiness TB)
      - Bieu do cot API cho 14 nghe
      - Bang chi tiet API, Readiness, Collab, Gap
    """
    st.title("📊 Tong quan AI Agent - Khoa hoc May tinh")
    scores = calc_scores(data)

    # 4 the thong tin nhanh
    a, b, c, d = st.columns(4)
    a.metric("CS Occupations", len(scores))
    b.metric("API TB", f"{scores['api'].mean():.1f}%")
    c.metric("Top", f"{scores.index[0]}", help=f"API={scores['api'].iloc[0]:.1f}%")
    d.metric("Readiness TB", f"{scores['readiness'].mean():.1f}%")

    # Bieu do cot: API Score tung nghe, mau xanh-do theo gia tri
    fig = px.bar(scores.reset_index().sort_values("api"),
                 x="api", y="Occupation (O*NET-SOC Title)",
                 color="api", color_continuous_scale="RdYlGn",
                 text_auto=".1f", labels={"api": "API %"})
    fig.update_traces(textposition="outside")
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

    # Bang du lieu: hien thi 4 cot chinh
    st.subheader("📋 Tong hop")
    display = scores[["api", "readiness", "collab", "gap"]].round(1)
    # Them icon cho moi nghe de de nhin
    display.index = [f"{e} {j}" for e, j in
                     zip(["🖥️","🔍","🏗️","🌐","💻","🔬","📊","✅","🌍","🗄️","🔧","🔒","📋","⚙️"],
                         display.index)]
    st.dataframe(display, use_container_width=True)


def page_detail(data):
    """
    Trang 2 - Chi tiet: Xem thong tin 1 nghe cu the.
    Nguoi dung chon nghe tu dropdown.
    Hien thi:
      - 3 chi so chinh (API, Readiness, Collab)
      - Top 5 task co the tu dong hoa
      - AI Agent khuyen nghi + cong nghe
    """
    st.title("💼 Chi tiet Occupation")

    # Dropdown chon nghe
    occ = st.selectbox("Chon nghe:", CS_JOBS)

    # Hien thi 3 chi so
    scores = calc_scores(data)
    if occ in scores.index:
        r = scores.loc[occ]
        col1, col2, col3 = st.columns(3)
        col1.metric("API", f"{r['api']:.1f}%")
        col2.metric("Readiness", f"{r['readiness']:.1f}%")
        col3.metric("Collab", f"{r['collab']:.1f}%")

    # Bang top task co diem cao nhat
    st.subheader("🎯 Top task nen uu tien")
    tasks = top_tasks(occ, data)
    if not tasks.empty:
        st.dataframe(tasks, use_container_width=True, hide_index=True)
    else:
        st.info("Chua co du lieu")

    # Hien thi agent khuyen nghi
    st.subheader("🤖 AI Agent de xuat")
    if occ in RECS:
        agent_ids, reason = RECS[occ]  # Lay tu mapping
        st.success(f"**{reason}**")
        cols = st.columns(len(agent_ids))
        for i, aid in enumerate(agent_ids):
            ag = AGENTS[aid]
            with cols[i]:
                st.markdown(f"### {ag['icon']} {ag['name']}")
                st.caption(ag["desc"])
                st.markdown(f"Cong nghe: `{ag['tech']}`")


def page_recommend(data):
    """
    Trang 3 - Khuyen nghi: Bang tong hop agent cho moi nghe.
    Hien thi:
      - Danh muc 8 agent (dang expander)
      - Bang: nghe -> agent de xuat -> API -> muc uu tien
      - Bieu do tron phan bo uu tien
    """
    st.title("🤖 Khuyen nghi AI Agent")
    scores = calc_scores(data)

    # Expander chua danh muc agent
    with st.expander("📚 Danh muc Agent (nhan de xem)"):
        cols = st.columns(4)
        for i, (_, ag) in enumerate(AGENTS.items()):
            with cols[i % 4]:
                st.markdown(f"**{ag['icon']} {ag['name']}**")
                st.caption(ag["desc"])

    # Tao bang recommend: moi dong = 1 nghe
    rows = []
    for occ in scores.index:
        if occ in RECS:
            aids, _ = RECS[occ]
            # Tao chuoi: icon + ten agent, cach nhau boi ", "
            agent_str = ", ".join([AGENTS[a]["icon"] + AGENTS[a]["name"] for a in aids])
            # Xep loai uu tien: Cao > 55%, TB > 40%, Thap <= 40%
            pri = "Cao" if scores.loc[occ, "api"] > 55 else ("TB" if scores.loc[occ, "api"] > 40 else "Thap")
            rows.append({"Occupation": occ, "Agent": agent_str,
                         "API": f"{scores.loc[occ, 'api']:.1f}%", "Priority": pri})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Bieu do tron: ti le Cao / TB / Thap
    cao = sum(1 for r in rows if r["Priority"] == "Cao")
    tb = sum(1 for r in rows if r["Priority"] == "TB")
    thap = sum(1 for r in rows if r["Priority"] == "Thap")
    fig = px.pie(names=["Cao", "TB", "Thap"],
                 values=[cao, tb, thap],
                 title="Muc do uu tien",
                 color=["Cao", "TB", "Thap"],
                 color_discrete_map={"Cao": "#2ca02c", "TB": "#ffbb78", "Thap": "#d62728"})
    st.plotly_chart(fig, use_container_width=True)


def page_compare(data):
    """
    Trang 4 - So sanh: So sanh 2-4 nghe cung luc.
    Hien thi:
      - Bieu do Radar: API, Readiness, Collab
      - Bieu do cot: Desire vs Capacity
    """
    st.title("📈 So sanh Occupations")
    scores = calc_scores(data)

    # Multiselect cho phep chon nhieu nghe
    chon = st.multiselect("Chon nghe (2-4):", CS_JOBS, default=CS_JOBS[:3])
    if len(chon) >= 2:
        df = scores.loc[chon].reset_index()

        # Radar chart: moi nghe la 1 hinh tren cung bieu do
        fig = go.Figure()
        for _, row in df.iterrows():
            vals = [row["api"], row["readiness"], row["collab"]]
            fig.add_trace(go.Scatterpolar(
                r=vals + [vals[0]],
                theta=["API", "Readiness", "Collab"] + ["API"],
                name=row["Occupation (O*NET-SOC Title)"],
                fill="toself"))
        fig.update_layout(polar=dict(radialaxis=dict(range=[0, 100])), height=500)
        st.plotly_chart(fig, use_container_width=True)

        # Bieu do cot so sanh Desire (mong muon) vs Capacity (kha nang)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="Desire", x=df["Occupation (O*NET-SOC Title)"], y=df["desire"]))
        fig2.add_trace(go.Bar(name="Capacity", x=df["Occupation (O*NET-SOC Title)"], y=df["capacity"]))
        fig2.update_layout(barmode="group", title="Desire vs Capacity", height=400)
        st.plotly_chart(fig2, use_container_width=True)


# ============================================================
# PHAN 5: MAIN - KHOI DONG APP
# ============================================================

def main():
    """
    Ham chay chinh:
      1. Load du lieu (neu loi -> dung lai)
      2. Hien sidebar de chon trang
      3. Dua vao trang da chon -> goi ham tuong ung
    """
    # Load du lieu, neu loi thi bao va dung
    try:
        data = load_data()
    except Exception as e:
        st.error(f"Loi load data: {e}")
        st.stop()

    # Hoi nguoi dung muon vao trang nao
    page = sidebar()

    # Chuyen huong: dict mapping ten trang -> ham
    pages = {
        "📊 Dashboard": page_dashboard,
        "💼 Chi tiet": page_detail,
        "🤖 Khuyen nghi": page_recommend,
        "📈 So sanh": page_compare,
    }
    pages[page](data)


# Diem bat dau khi chay `python app.py` hoac `streamlit run app.py`
if __name__ == "__main__":
    main()
