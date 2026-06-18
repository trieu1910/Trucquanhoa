"""
app.py
======
UNG DUNG PHAN TICH & KHUYEN NGHI AI AGENT TRONG KHOA HOC MAY TINH
Su dung Streamlint + WorkBank Data + GitHub

Tac gia: AI Agent CS Analysis Team
Cong nghe: Streamlit, Pandas, Plotly, scikit-learn

Cac chuc nang chinh:
  1. Tong quan (Dashboard) - Cac chi so tong hop cho CS occupations
  2. Phan tich Automation Potential - Nghe nao co tiem nang AI nhat?
  3. Chi tiet Occupation - Xem chi tiet nghe cu the
  4. Khuyen nghi AI Agent - De xuat loai AI Agent phu hop
  5. Gap Analysis - Khoang cach giua mong muon va kha nang
  6. So sanh - So sanh nhieu nghe cung luc

Huong dan chay:
  pip install -r requirements.txt
  streamlit run app.py
"""

import sys
import os
from pathlib import Path

# Them thu muc hien tai vao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from datetime import datetime

# Import cac module tu project
from data_loader import load_cs_data, get_summary_stats, CS_OCCUPATIONS
from analysis import CSAnalyzer
from recommendations import RecommendationEngine, ALL_AGENTS, OCCUPATION_AGENT_MAPPING
from utils import (
    CS_COLORS, COLORS, RATING_LABELS,
    rating_to_label, rating_to_color, gap_color,
    occupation_icon, format_percent, format_rating,
    normalize_series,
)

# ============================================================
# CAU HINH TRANG
# ============================================================
st.set_page_config(
    page_title="AI Agent CS Analyzer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CACHE DU LIEU
# ============================================================

@st.cache_data(ttl=3600)
def load_data():
    """
    Load du lieu WorkBank va loc cac nghe CS.
    Cache 1 gio de tranh load lai nhieu lan.
    """
    data_dir = Path(__file__).resolve().parent.parent  # workbank/
    try:
        data = load_cs_data(str(data_dir))
        return data
    except FileNotFoundError:
        # Fallback: thu load tu thu muc hien tai
        data = load_cs_data()
        return data


@st.cache_resource
def get_analyzer(data):
    """Tao va cache CSAnalyzer."""
    return CSAnalyzer(data["desires"], data["capability"], data["tasks"])


@st.cache_resource
def get_engine(analyzer):
    """Tao va cache RecommendationEngine."""
    return RecommendationEngine(analyzer)


# ============================================================
# SIDE BAR
# ============================================================

def render_sidebar():
    """Hien thi sidebar voi thong tin tong quan va dieu huong."""
    with st.sidebar:
        st.markdown("# 🤖 AI Agent CS")
        st.markdown("**Phan tich & Khuyen nghi AI Agent**")
        st.markdown("----")

        # Dieu huong
        st.markdown("### 📍 Dieu huong")
        page = st.radio(
            "Chuyen muc:",
            [
                "🏠 Tong quan",
                "📈 Automation Potential",
                "💼 Chi tiet Occupation",
                "🤖 Khuyen nghi AI Agent",
                "📊 Gap Analysis",
                "⚖️ So sanh",
                "ℹ️ Ve project",
            ],
            label_visibility="collapsed",
        )

        st.markdown("----")

        # Thong tin du lieu
        st.markdown("### 📊 Du lieu")
        try:
            data = load_data()
            stats = get_summary_stats(data["tasks"])
            st.metric("CS Occupations", stats["unique_occupations"])
            st.metric("Total Tasks", stats["rows"])
        except Exception as e:
            st.warning(f"Loi load data: {e}")

        st.markdown("----")
        st.caption(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        st.caption("Data source: WorkBank Dataset")

        return page


# ============================================================
# PAGE: TONG QUAN (DASHBOARD)
# ============================================================

def render_dashboard(data, analyzer):
    """
    Trang Tong quan - Dashboard chinh.
    Hien thi:
      - Metric cards
      - Bieu do phan phoi API score
      - Bang tong hop cac nghe CS
    """
    st.title("🏠 Tong quan AI Agent trong Khoa hoc May tinh")
    st.markdown("Phan tich ti **14 Occupation** thuoc linh vuc **Computer Science** tu WorkBank dataset.")

    # --- Metric cards ---
    scores = analyzer.compute_all_scores()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("CS Occupations", scores.shape[0])
    with col2:
        st.metric("API Score TB", f"{scores['api_score'].mean():.1f}%")
    with col3:
        best_occ = scores.iloc[0]["Occupation (O*NET-SOC Title)"]
        st.metric("Top Occupation", best_occ, delta=f"{scores['api_score'].max():.1f}%")
    with col4:
        st.metric("Readiness TB", f"{scores['readiness_score'].mean():.1f}%")

    st.markdown("---")

    # --- Bieu do API Score ---
    col_left, col_right = st.columns([3, 2])
    with col_left:
        st.subheader("📈 Chi so Automation Potential Index (API)")
        fig = px.bar(
            scores.sort_values("api_score", ascending=True),
            x="api_score",
            y="Occupation (O*NET-SOC Title)",
            color="api_score",
            color_continuous_scale="RdYlGn",
            text="api_score",
            labels={"api_score": "API Score (%)", "Occupation (O*NET-SOC Title)": ""},
            title="Tiem nang tu dong hoa cua tung Occupation",
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("📋 Tong hop Scores")
        display = scores.copy()
        display["Icon"] = display["Occupation (O*NET-SOC Title)"].apply(occupation_icon)
        display["Occupation"] = display["Icon"] + " " + display["Occupation (O*NET-SOC Title)"]
        display["API"] = display["api_score"].round(1)
        display["Readiness"] = display["readiness_score"].round(1)
        display["Collab"] = display["collab_score"].round(1)

        st.dataframe(
            display[["Occupation", "API", "Readiness", "Collab"]],
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("---")

    # --- Thong ke mo ta ---
    st.subheader("📝 Cau truc du lieu")
    tab1, tab2 = st.tabs(["Tasks (O*NET)", "Worker Desires", "Expert Capability"])

    with tab1:
        stats = get_summary_stats(data["tasks"])
        st.write(f"**So task CS**: {stats['rows']}")
        st.dataframe(data["tasks"].head(5), use_container_width=True)

    with tab2:
        st.dataframe(data["desires"].head(5), use_container_width=True)

    # Hien thi du lieu chi tiet
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.caption("**Worker Desires** - Khao sat nguoi lao dong")
        st.dataframe(data["desires"].head(3), use_container_width=True)
    with col_t2:
        st.caption("**Expert Capability** - Danh gia chuyen gia")
        st.dataframe(data["capability"].head(3), use_container_width=True)


# ============================================================
# PAGE: AUTOMATION POTENTIAL
# ============================================================

def render_automation_potential(analyzer):
    """
    Trang phan tich Automation Potential Index chi tiet.
    Hien thi bieu do xu huong va phan tich da chieu.
    """
    st.title("📈 Automation Potential Index (API)")
    st.markdown("""
    **API** la chi so tong hop do luong muc do phu hop de ung dung AI Agent vao cong viec.
    Duoc tinh tu: Mong muon nguoi lao dong, Kha nang cong nghe, Do phuc tap chuyen mon, Giao tiep.
    """)

    scores = analyzer.compute_all_scores()
    sorted_scores = scores.sort_values("api_score", ascending=True)

    # Bieu do ngang
    fig = px.bar(
        sorted_scores,
        x="api_score",
        y="Occupation (O*NET-SOC Title)",
        color="api_score",
        color_continuous_scale="RdYlGn",
        text="api_score",
        labels={"api_score": "API Score (%)", "Occupation (O*NET-SOC Title)": ""},
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.add_vline(x=50, line_dash="dash", line_color="gray", annotation_text="Trung binh")
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Phan tich Desire vs Capacity
    st.subheader("🎯 Desire vs Capacity")
    gap_df = analyzer.compute_gap_analysis()
    gap_df = gap_df.dropna()
    gap_df = gap_df.sort_values("gap", ascending=True)

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        y=gap_df["Occupation (O*NET-SOC Title)"],
        x=gap_df["desire_mean"],
        name="Desire (Mong muon)",
        orientation="h",
        marker_color="#ff7f0e",
    ))
    fig2.add_trace(go.Bar(
        y=gap_df["Occupation (O*NET-SOC Title)"],
        x=gap_df["capacity_mean"],
        name="Capacity (Kha nang)",
        orientation="h",
        marker_color="#1f77b4",
    ))
    fig2.update_layout(
        title="So sanh Mong muon Tu dong hoa vs Kha nang Cong nghe",
        barmode="group",
        height=500,
        xaxis_title="Diem (1-5)",
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # Scatter plot
    st.subheader("🧩 Tuong quan Desire vs Capacity")
    fig3 = px.scatter(
        gap_df,
        x="desire_mean",
        y="capacity_mean",
        text="Occupation (O*NET-SOC Title)",
        size="gap",
        color="gap",
        color_continuous_scale="RdYlBu_r",
        labels={
            "desire_mean": "Desire (1-5)",
            "capacity_mean": "Capacity (1-5)",
            "gap": "Gap",
        },
    )
    fig3.add_hline(y=3, line_dash="dash", line_color="gray")
    fig3.add_vline(x=3, line_dash="dash", line_color="gray")
    fig3.update_traces(textposition="top center")
    fig3.update_layout(height=500)
    st.plotly_chart(fig3, use_container_width=True)


# ============================================================
# PAGE: CHI TIET OCCUPATION
# ============================================================

def render_occupation_detail(data, analyzer):
    """
    Trang chi tiet cho tung Occupation trong CS.
    Hien thi:
      - Thong tin co ban
      - Top tasks co the tu dong hoa
      - AI Agent recommendation
    """
    st.title("💼 Chi tiet Occupation")

    occ_list = CS_OCCUPATIONS
    occ = st.selectbox("Chon Occupation:", occ_list)

    if occ:
        icon = occupation_icon(occ)
        st.markdown(f"## {icon} {occ}")

        # Lay scores
        scores = analyzer.compute_all_scores()
        row = scores[scores["Occupation (O*NET-SOC Title)"] == occ]

        if not row.empty:
            r = row.iloc[0]
            col1, col2, col3 = st.columns(3)
            col1.metric("API Score", f"{r['api_score']:.1f}%")
            col2.metric("Readiness", f"{r['readiness_score']:.1f}%")
            col3.metric("Collab Score", f"{r['collab_score']:.1f}%")

        st.markdown("---")

        # Top tasks cho automation
        st.subheader("🎯 Top tasks co the tu dong hoa bang AI Agent")
        top_tasks = analyzer.get_top_tasks_for_automation(occ, top_n=8)

        if not top_tasks.empty:
            display_cols = [c for c in ["Task", "desire", "capacity", "total_score"]
                           if c in top_tasks.columns]
            st.dataframe(top_tasks[display_cols], use_container_width=True, hide_index=True)
        else:
            st.info(f"Chua co du lieu task chi tiet cho {occ}")

        st.markdown("---")

        # AI Agent recommendation
        st.subheader("🤖 AI Agent Khuyen nghi")
        engine = get_engine(analyzer)
        agents, explanation = engine.get_agents_for_occupation(occ)
        plan = engine.recommend_implementation_plan(occ)

        st.info(explanation)

        cols = st.columns(3)
        categories = [
            ("🟢 Ngan han (1-3 thang)", plan["short_term"]),
            ("🟡 Trung han (3-6 thang)", plan["medium_term"]),
            ("🔴 Dai han (6-12 thang)", plan["long_term"]),
        ]
        for i, (cat_name, agent_list) in enumerate(categories):
            with cols[i]:
                st.markdown(f"**{cat_name}**")
                if agent_list:
                    for a in agent_list:
                        with st.expander(f"{a.icon} **{a.name}**"):
                            st.caption(a.description)
                            st.markdown("**Kha nang:**")
                            for cap in a.capabilities:
                                st.markdown(f"- {cap}")
                            st.markdown(f"**Cong nghe:** {', '.join(a.tech_stack)}")
                else:
                    st.markdown("*Khong co*")

        st.markdown(f"**Tong Impact uoc tinh:** ~{plan['total_impact']}% tu dong hoa")

        # Danh muc task detail tu workbank
        st.markdown("---")
        st.subheader("📋 Task detail tu WorkBank")
        occ_tasks = data["tasks"][data["tasks"]["Occupation (O*NET-SOC Title)"] == occ]
        if not occ_tasks.empty:
            st.dataframe(
                occ_tasks[["Task", "Category", "Frequency", "Importance"]].head(10),
                use_container_width=True,
                hide_index=True,
            )


# ============================================================
# PAGE: KHUYEN NGHI AI AGENT
# ============================================================

def render_recommendations(analyzer):
    """
    Trang khuyen nghi AI Agent chi tiet cho tung occupation.
    Gioi thieu danh muc agent va mapping.
    """
    st.title("🤖 Khuyen nghi AI Agent")

    # Gioi thieu cac loai Agent
    st.markdown("### 📚 Danh muc AI Agent")
    st.markdown("Co **8 loai AI Agent** duoc phan loai dua tren kha nang va muc do phuc tap.")

    agent_cols = st.columns(4)
    for i, (agent_id, agent) in enumerate(ALL_AGENTS.items()):
        col = agent_cols[i % 4]
        with col:
            with st.expander(f"{agent.icon} **{agent.name}**", expanded=(i < 4)):
                st.caption(agent.description)
                st.markdown("**Kha nang:**")
                for cap in agent.capabilities:
                    st.markdown(f"- {cap}")
                st.markdown(f"**Cong nghe:** {', '.join(agent.tech_stack)}")
                st.markdown(f"**Do phuc tap:** {'⭐' * agent.complexity}")

    st.markdown("---")

    # Bang recommendation tong hop
    st.subheader("📊 Bang khuyen nghi tong hop")
    engine = get_engine(analyzer)
    recommendations = engine.get_all_recommendations()

    if not recommendations.empty:
        # Them icon
        recommendations["Occupation_display"] = recommendations["Occupation"].apply(
            lambda x: f"{occupation_icon(x)} {x}"
        )

        st.dataframe(
            recommendations[["Occupation_display", "Recommended Agents", "API Score", "Readiness Score", "Priority"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Occupation_display": st.column_config.TextColumn("Occupation"),
            },
        )

    st.markdown("---")

    # Implementation plan cho tung agent type
    st.subheader("📋 Ke hoach trien khai")
    st.markdown("""
    **Quy trinh trien khai AI Agent khuyen nghi:**
    1. **Phan tich hien trang** - Danh gia quy trinh hien tai, xac dinh task phu hop
    2. **Chon Agent** - Chon loai agent phu hop voi tung task
    3. **Pilot** - Trien khai thu voi quy mo nho (1-2 agent)
    4. **Danh gia** - Do luong hieu qua (thoi gian, chi phi, sai sot)
    5. **Mo rong** - Nhan rong sang cac task khac
    """)

    # Bieu do phan phoi
    st.markdown("---")
    st.subheader("📈 Phan bo khuyen nghi theo Occupation")
    if not recommendations.empty:
        priority_counts = recommendations["Priority"].value_counts()
        fig = px.pie(
            values=priority_counts.values,
            names=priority_counts.index,
            title="Ty le Uu tien (Cao/Trung binh/Thap)",
            color=priority_counts.index,
            color_discrete_map={"Cao": "#2ca02c", "Trung binh": "#ffbb78", "Thap": "#d62728"},
        )
        st.plotly_chart(fig, use_container_width=True)


# ============================================================
# PAGE: GAP ANALYSIS
# ============================================================

def render_gap_analysis(analyzer):
    """
    Trang phan tich Gap - Khoang cach giua mong muon va kha nang.
    Gap > 0: Worker muon tu dong hoa nhieu hon so voi kha nang CN.
    Gap < 0: CN co the lam duoc nhieu hon mong muon.
    """
    st.title("📊 Gap Analysis")
    st.markdown("""
    **Phan tich khoang cach (Gap)** giua:
    - **Desire**: Mong muon tu dong hoa tu nguoi lao dong (1-5)
    - **Capacity**: Danh gia cua chuyen gia ve kha nang cong nghe (1-5)

    *Gap duong = Nguoi lao dong muon AI nhieu hon kha nang hien co*
    *Gap am = Cong nghe san sang nhung nguoi lao dong chua muon*
    """)

    gap_df = analyzer.compute_gap_analysis()
    gap_df = gap_df.dropna(subset=["gap"])
    gap_df = gap_df.sort_values("gap", ascending=True)

    # Bieu do GAP
    colors = gap_df["gap"].apply(
        lambda x: COLORS["danger"] if x > 0.5 else (COLORS["success"] if x < -0.5 else COLORS["gray"])
    )

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=gap_df["Occupation (O*NET-SOC Title)"],
        x=gap_df["gap"],
        orientation="h",
        marker_color=colors,
        text=gap_df["gap"].round(2),
        textposition="outside",
    ))
    fig.add_vline(x=0, line_width=2, line_color="black")
    fig.update_layout(
        title="Gap giua Mong muon va Kha nang",
        xaxis_title="Gap (Desire - Capacity)",
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Interpretation
    st.markdown("---")
    st.subheader("📝 Phan tich")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🔴 Gap > 0.5 (Can uu tien)")
        high_gap = gap_df[gap_df["gap"] > 0.5]
        if not high_gap.empty:
            for _, r in high_gap.iterrows():
                st.markdown(f"- **{r['Occupation (O*NET-SOC Title)']}**: Gap = {r['gap']:.2f}")
                st.markdown(f"  - Desire: {r['desire_mean']:.2f}, Capacity: {r['capacity_mean']:.2f}")
                st.markdown(f"  - => **Uu tien cao**: Can phat trien AI Agent de dap ung nhu cau")
        else:
            st.markdown("*Khong co*")

    with col2:
        st.markdown("#### 🟢 Gap < -0.5 (Thua nang luc)")
        low_gap = gap_df[gap_df["gap"] < -0.5]
        if not low_gap.empty:
            for _, r in low_gap.iterrows():
                st.markdown(f"- **{r['Occupation (O*NET-SOC Title)']}**: Gap = {r['gap']:.2f}")
                st.markdown(f"  - Desire: {r['desire_mean']:.2f}, Capacity: {r['capacity_mean']:.2f}")
                st.markdown(f"  - => Can tang cuong dao tao, nhan thuc ve AI")
        else:
            st.markdown("*Khong co*")


# ============================================================
# PAGE: SO SANH
# ============================================================

def render_comparison(analyzer):
    """
    Trang so sanh nhieu occupation cung luc.
    """
    st.title("⚖️ So sanh Occupations")

    occs = st.multiselect(
        "Chon 2-4 Occupation de so sanh:",
        CS_OCCUPATIONS,
        default=CS_OCCUPATIONS[:4],
    )

    if len(occs) >= 2:
        scores = analyzer.compute_all_scores()
        compare = scores[scores["Occupation (O*NET-SOC Title)"].isin(occs)]

        if not compare.empty:
            # Radar chart
            st.subheader("🕸 Bieu do Radar")
            categories = ["API Score", "Readiness", "Collab"]
            fig = go.Figure()
            for _, row in compare.iterrows():
                values = [row["api_score"], row["readiness_score"], row["collab_score"]]
                fig.add_trace(go.Scatterpolar(
                    r=values + [values[0]],
                    theta=categories + [categories[0]],
                    name=row["Occupation (O*NET-SOC Title)"],
                    fill="toself",
                ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                height=500,
            )
            st.plotly_chart(fig, use_container_width=True)

            # Bang so sanh
            st.subheader("📋 Bang so sanh")
            display = compare[[
                "Occupation (O*NET-SOC Title)",
                "api_score", "desire_mean", "capacity_mean",
                "gap", "readiness_score", "collab_score",
            ]].round(2)
            display.columns = [
                "Occupation", "API (%)", "Desire", "Capacity",
                "Gap", "Readiness (%)", "Collab (%)",
            ]
            st.dataframe(display, use_container_width=True, hide_index=True)

    else:
        st.warning("Vui long chon it nhat 2 Occupation de so sanh.")


# ============================================================
# PAGE: VE PROJECT
# ============================================================

def render_about():
    """Trang thong tin ve project."""
    st.title("ℹ️ Ve project")

    st.markdown("""
    ## 🤖 AI Agent trong Khoa hoc May tinh

    **Project nay** phan tich du lieu tu **WorkBank Dataset** de dua ra khuyen nghi ve
    ung dung AI Agent trong linh vuc Khoa hoc May tinh (Computer Science).

    ### 📊 Nguon du lieu
    - **WorkBank**: Khao sat tu 1000+ nguoi lao dong ve nhu cau tu dong hoa
    - **O*NET**: Co so du lieu chuan ve mo ta cong viec tai Hoa Ky
    - **Expert Rating**: Danh gia tu chuyen gia ve kha nang cong nghe

    ### 🏗️ Kien truc project
    ```
    workbank1/
    ├── ai_agent_cs/
    │   ├── app.py                 # Streamlit UI chinh
    │   ├── data_loader.py         # Load & tien xu ly du lieu
    │   ├── analysis.py            # Phan tich chi so API, Gap, v.v.
    │   ├── recommendations.py     # Engine khuyen nghi AI Agent
    │   ├── utils.py               # Ham tien ich
    │   ├── requirements.txt       # Dependencies
    │   └── setup.ps1              # Script setup & push GitHub
    ├── *.csv                      # WorkBank raw data
    ```

    ### 🚀 Cong nghe
    - **Streamlit**: Web app framework
    - **Pandas + NumPy**: Xu ly du lieu
    - **Plotly**: Bieu do tuong tac
    - **scikit-learn**: Phan tich (future)

    ### 📝 Tac gia
    - AI Agent CS Analysis - 2026
    """)

    st.markdown("---")

    # Huong dan push github
    st.subheader("📤 Huong dan push len GitHub")
    with st.expander("Xem huong dan chi tiet"):
        st.code("""
# Buoc 1: Khoi tao git repo
cd workbank1/ai_agent_cs
git init
git add .
git commit -m "Initial: AI Agent CS Analysis with Streamlit"

# Buoc 2: Tao repo tren GitHub (https://github.com/new)
# Ten: ai-agent-cs-analysis

# Buoc 3: Push code
git branch -M main
git remote add origin https://github.com/<USERNAME>/ai-agent-cs-analysis.git
git push -u origin main

# Buoc 4: Chay Streamlit
pip install -r requirements.txt
streamlit run app.py
        """, language="bash")


# ============================================================
# MAIN
# ============================================================

def main():
    """
    Ham chinh - Dieu huong cac trang cua Streamlit app.
    """
    # Load data
    try:
        data = load_data()
        analyzer = get_analyzer(data)
    except Exception as e:
        st.error(f"Loi load du lieu: {e}")
        st.warning("Kiem tra lai duong dan den file CSV hoac chay tu thu dung.")
        st.stop()

    # Render sidebar & lay page selection
    page = render_sidebar()

    # Dieu huong trang
    if page == "🏠 Tong quan":
        render_dashboard(data, analyzer)
    elif page == "📈 Automation Potential":
        render_automation_potential(analyzer)
    elif page == "💼 Chi tiet Occupation":
        render_occupation_detail(data, analyzer)
    elif page == "🤖 Khuyen nghi AI Agent":
        render_recommendations(analyzer)
    elif page == "📊 Gap Analysis":
        render_gap_analysis(analyzer)
    elif page == "⚖️ So sanh":
        render_comparison(analyzer)
    elif page == "ℹ️ Ve project":
        render_about()


# ============================================================
# Entry point
# ============================================================
if __name__ == "__main__":
    main()
