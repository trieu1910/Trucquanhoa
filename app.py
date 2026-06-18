# -*- coding: utf-8 -*-
"""
AI Agent CS Analyzer
====================
Phân tích & khuyến nghị AI Agent trong Khoa học Máy tính
Dùng Streamlit + WorkBank data

SƠ ĐỒ LUỒNG:
  WorkBank (4 CSV)
       │
       ▼
  load_data() ──► lọc 14 ngành CS
       │
       ▼
  calc_scores() ──► API | Readiness | Gap | Collab
       │
       ├──► page_dashboard()   : Tổng quan
       ├──► page_detail()      : 1 ngành + top_tasks() + agent
       ├──► page_recommend()   : Bảng khuyến nghị
       └──► page_compare()     : So sánh nhiều ngành

Chạy: pip install streamlit pandas plotly && streamlit run app.py
"""

# === Thư viện ===
import streamlit as st      # Tạo web app
import pandas as pd         # Xử lý dữ liệu bảng
import numpy as np          # Tính toán số
import plotly.express as px     # Vẽ biểu đồ nhanh
import plotly.graph_objects as go  # Vẽ biểu đồ tùy chỉnh
from pathlib import Path    # Xử lý đường dẫn file

# === Cài đặt trang web: title, icon, chế độ rộng ===
st.set_page_config(page_title="AI Agent CS", page_icon="🤖", layout="wide")

# === DANH SÁCH 14 NGÀNH TRONG LĨNH VỰC KHOA HỌC MÁY TÍNH ===
# Đây là các ngành được lọc từ WorkBank dataset
# Mỗi ngành có mã O*NET-SOC riêng
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

# === ĐỊNH NGHĨA 8 LOẠI AI AGENT ===
# Mỗi agent có: tên, icon, mô tả, công nghệ, độ phức tạp (1=thấp, 3=cao)
# Đây là những agent phổ biến nhất trong CS hiện nay
AGENTS = {
    "code": {"name": "Code Agent", "icon": "⚡", "desc": "Sinh code, sửa lỗi, refactor tự động",
             "tech": "GPT-4, Copilot, Codeium, Tree-sitter", "level": 1},
    "rpa": {"name": "RPA Agent", "icon": "🤖", "desc": "Tự động hóa nhập liệu, xử lý form, lập lịch",
            "tech": "Selenium, PyAutoGUI, UiPath", "level": 1},
    "monitor": {"name": "Monitor Agent", "icon": "📡", "desc": "Giám sát hệ thống, cảnh báo bất thường",
                "tech": "Prometheus, Grafana, ELK", "level": 1},
    "analytic": {"name": "Analytic Agent", "icon": "📊", "desc": "Phân tích data, phát hiện pattern, dự báo",
                 "tech": "Pandas, sklearn, LangChain, TensorFlow", "level": 2},
    "security": {"name": "Security Agent", "icon": "🔒", "desc": "Phát hiện xâm nhập, kiểm tra bảo mật",
                 "tech": "Wazuh, Splunk, ML models", "level": 2},
    "copilot": {"name": "Copilot Agent", "icon": "👨‍💻", "desc": "Trợ lý AI realtime cho developer",
                "tech": "GitHub Copilot, Cursor, OpenAPI", "level": 2},
    "autonomous": {"name": "Auto Agent", "icon": "🧠", "desc": "Tự quyết định & thực thi không cần người",
                   "tech": "AutoGPT, CrewAI, RL", "level": 3},
    "collab": {"name": "Collab Agent", "icon": "🤝", "desc": "Hợp tác người-AI, chia task, học từ feedback",
               "tech": "AutoGen, RAG, Copilot Studio", "level": 3},
}

# === MAP: MỖI NGÀNH → AGENT KHUYẾN NGHỊ ===
# Mỗi ngành gồm: (danh sách agent_id, lý do)
# Được xây dựng từ phân tích WorkBank + đặc thù từng ngành
RECS = {
    "Computer Programmers": (["copilot", "code", "rpa"], "Code + RPA là chính"),
    "Computer Systems Analysts": (["analytic", "collab", "code"], "Cần phân tích nhiều"),
    "Computer Systems Engineers/Architects": (["collab", "analytic", "security"], "Thiết kế + Bảo mật"),
    "Computer Network Support Specialists": (["monitor", "rpa", "autonomous"], "Giám sát là chính"),
    "Computer User Support Specialists": (["copilot", "rpa", "monitor"], "Hỗ trợ người dùng"),
    "Computer and Information Research Scientists": (["analytic", "autonomous", "collab"], "Nghiên cứu"),
    "Computer and Information Systems Managers": (["analytic", "monitor", "collab"], "Quản lý tổng thể"),
    "Software Quality Assurance Analysts and Testers": (["code", "rpa", "analytic"], "Test automation"),
    "Web Developers": (["copilot", "code", "monitor"], "Web dev + deploy"),
    "Database Administrators": (["monitor", "rpa", "autonomous"], "Backup + giám sát"),
    "Network and Computer Systems Administrators": (["monitor", "rpa", "security"], "Admin + security"),
    "Information Security Analysts": (["security", "monitor", "analytic"], "Bảo mật là chính"),
    "Information Technology Project Managers": (["analytic", "collab", "monitor"], "Quản lý dự án"),
    "Web Administrators": (["monitor", "rpa", "security"], "Web admin"),
}


# ============================================================
# PHẦN 1: LOAD DỮ LIỆU TỪ FILE CSV
# ============================================================

@st.cache_data
def load_data():
    """
    Đọc 4 file CSV từ thư mục workbank1/ (cấp trên).
    Chỉ lấy những dòng thuộc 14 ngành CS.
    Kết quả được cache để khỏi đọc lại khi refresh.
    """
    # Đi lên 1 cấp: từ ai_agent_cs/ → workbank1/
    base = Path(__file__).resolve().parent.parent

    # Hàm đọc 1 file và lọc ngành CS
    def read(name):
        df = pd.read_csv(base / name, encoding="utf-8", low_memory=False)
        return df[df["Occupation (O*NET-SOC Title)"].isin(CS_JOBS)].copy()

    # Trả về 4 bảng dữ liệu
    return {
        "tasks": read("task_statement_with_metadata.csv"),   # Mô tả công việc từ O*NET
        "desires": read("domain_worker_desires.csv"),         # Khảo sát mong muốn tự động hóa
        "workers": read("domain_worker_metadata.csv"),         # Thông tin người tham gia
        "expert": read("expert_rated_technological_capability.csv"),  # Đánh giá chuyên gia
    }


# ============================================================
# PHẦN 2: TÍNH TOÁN CHỈ SỐ
# ============================================================

def calc_scores(data):
    """
    Tính 4 chỉ số chính cho từng ngành:
      - API: Tiềm năng tự động hóa (0-100%)
      - Readiness: Mức độ sẵn sàng của công nghệ (0-100%)
      - Collab: Mức độ phù hợp cho hợp tác người-AI (0-100%)
      - Gap: Chênh lệch Desire - Capacity (âm/dương)

    Cách tính:
      1. Gom 4 bảng dữ liệu theo Occupation
      2. Tính trung bình cho từng chỉ số
      3. Áp dụng công thức đã định nghĩa
    """
    # Bước 1: Gom nhóm và tính trung bình cho từng ngành
    d = data["desires"].groupby("Occupation (O*NET-SOC Title)")["Automation Desire Rating"].mean()
    c = data["expert"].groupby("Occupation (O*NET-SOC Title)")["Automation Capacity Rating"].mean()
    u = data["expert"].groupby("Occupation (O*NET-SOC Title)")["Involved Uncertainty"].mean()
    e = data["expert"].groupby("Occupation (O*NET-SOC Title)")["Domain Expertise Requirement"].mean()
    i = data["expert"].groupby("Occupation (O*NET-SOC Title)")["Interpersonal Communication Requirement"].mean()
    a = data["desires"].groupby("Occupation (O*NET-SOC Title)")["Human Agency Scale Rating"].mean()

    # Bước 2: Gom vào 1 bảng
    df = pd.DataFrame({"desire": d, "capacity": c, "uncertainty": u,
                       "expertise": e, "interpersonal": i, "agency": a})

    # Bước 3: Tính API - trọng số: Desire 40%, Capacity 40%, chuyên môn 10%, giao tiếp 10%
    df["api"] = (df["desire"]*0.4 + df["capacity"]*0.4
                 + (6-df["expertise"])*0.1 + (6-df["interpersonal"])*0.1)
    df["api"] = ((df["api"]-1)/4*100).clip(0, 100)  # Chuẩn hóa về 0-100%

    # Bước 4: Tính Readiness - công nghệ sẵn sàng = f(Capacity, Uncertainty)
    df["readiness"] = ((df["capacity"] + (6-df["uncertainty"]))/2)
    df["readiness"] = ((df["readiness"]-1)/4*100).clip(0, 100)

    # Bước 5: Tính Collab - mức độ phù hợp cho người + AI
    df["collab"] = df["agency"]*0.6 + 0.4
    df["collab"] = ((df["collab"]-1)/4*100).clip(0, 100)

    # Bước 6: Tính Gap = Desire - Capacity (dương = thiếu, âm = thừa)
    df["gap"] = df["desire"] - df["capacity"]

    # Sắp xếp: ngành có API cao nhất lên đầu
    return df.sort_values("api", ascending=False)


def top_tasks(occ, data, n=5):
    """
    Tìm n task có tiềm năng tự động hóa cao nhất
    cho một ngành cụ thể.
    Điểm = (Desire + Capacity) / 2, mỗi yếu tố 50%.

    Args:
        occ: Tên ngành (vd: "Computer Programmers")
        data: Dict 4 bảng dữ liệu
        n: Số lượng task muốn lấy

    Returns:
        DataFrame: [Task, score]
    """
    # Lọc 3 bảng theo ngành
    d = data["desires"][data["desires"]["Occupation (O*NET-SOC Title)"] == occ]
    c = data["expert"][data["expert"]["Occupation (O*NET-SOC Title)"] == occ]
    t = data["tasks"][data["tasks"]["Occupation (O*NET-SOC Title)"] == occ]

    # Nếu không có dữ liệu → trả về rỗng
    if d.empty or c.empty:
        return pd.DataFrame()

    # Tính điểm trung bình Desire và Capacity cho từng Task ID
    desire = d.groupby("Task ID")["Automation Desire Rating"].mean().rename("desire")
    cap = c.groupby("Task ID")["Automation Capacity Rating"].mean().rename("capacity")

    # Kết hợp và tính tổng điểm
    merged = desire.to_frame().join(cap, how="outer")
    merged["score"] = merged["desire"].fillna(3)*0.5 + merged["capacity"].fillna(3)*0.5
    merged = merged.sort_values("score", ascending=False).head(n)

    # Ghép với mô tả task từ bảng tasks
    info = t[["Task ID", "Task"]].drop_duplicates("Task ID")
    merged = merged.reset_index().merge(info, on="Task ID", how="left")

    return merged[["Task", "score"]]


# ============================================================
# PHẦN 3: GIAO DIỆN NGƯỜI DÙNG (UI)
# ============================================================

def sidebar():
    """
    Tạo thanh bên trái với menu điều hướng.
    Người dùng chọn trang bằng nút radio.
    """
    with st.sidebar:
        st.markdown("# 🤖 AI Agent CS")
        # Menu chính: 4 trang
        page = st.radio("", [
            "📊 Dashboard",
            "💼 Chi tiết",
            "🤖 Khuyến nghị",
            "📈 So sánh",
        ], label_visibility="collapsed")
        st.caption("WorkBank dataset | 14 CS occupations")
    return page


# ============================================================
# PHẦN 4: CÁC TRANG
# ============================================================

def page_dashboard(data):
    """
    Trang 1 - Dashboard: Tổng quan tất cả chỉ số.
    Hiển thị:
      - 4 thẻ metric (số ngành, API TB, Top ngành, Readiness TB)
      - Biểu đồ cột API cho 14 ngành
      - Bảng chi tiết API, Readiness, Collab, Gap
    """
    st.title("📊 Tổng quan AI Agent - Khoa học Máy tính")
    scores = calc_scores(data)

    # 4 thẻ thông tin nhanh
    a, b, c, d = st.columns(4)
    a.metric("CS Occupations", len(scores))
    b.metric("API TB", f"{scores['api'].mean():.1f}%")
    c.metric("Top", f"{scores.index[0]}", help=f"API={scores['api'].iloc[0]:.1f}%")
    d.metric("Readiness TB", f"{scores['readiness'].mean():.1f}%")

    # Biểu đồ cột: API Score từng ngành, màu xanh-đỏ theo giá trị
    fig = px.bar(scores.reset_index().sort_values("api"),
                 x="api", y="Occupation (O*NET-SOC Title)",
                 color="api", color_continuous_scale="RdYlGn",
                 text_auto=".1f", labels={"api": "API %"})
    fig.update_traces(textposition="outside")
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

    # Bảng dữ liệu: hiển thị 4 cột chính
    st.subheader("📋 Tổng hợp")
    display = scores[["api", "readiness", "collab", "gap"]].round(1)
    # Thêm icon cho mỗi ngành để dễ nhìn
    display.index = [f"{e} {j}" for e, j in
                     zip(["🖥️","🔍","🏗️","🌐","💻","🔬","📊","✅","🌍","🗄️","🔧","🔒","📋","⚙️"],
                         display.index)]
    st.dataframe(display, use_container_width=True)


def page_detail(data):
    """
    Trang 2 - Chi tiết: Xem thông tin 1 ngành cụ thể.
    Người dùng chọn ngành từ dropdown.
    Hiển thị:
      - 3 chỉ số chính (API, Readiness, Collab)
      - Top 5 task có thể tự động hóa
      - AI Agent khuyến nghị + công nghệ
    """
    st.title("💼 Chi tiết Occupation")

    # Dropdown chọn ngành
    occ = st.selectbox("Chọn ngành:", CS_JOBS)

    # Hiển thị 3 chỉ số
    scores = calc_scores(data)
    if occ in scores.index:
        r = scores.loc[occ]
        col1, col2, col3 = st.columns(3)
        col1.metric("API", f"{r['api']:.1f}%")
        col2.metric("Readiness", f"{r['readiness']:.1f}%")
        col3.metric("Collab", f"{r['collab']:.1f}%")

    # Bảng top task có điểm cao nhất
    st.subheader("🎯 Top task nên ưu tiên")
    tasks = top_tasks(occ, data)
    if not tasks.empty:
        st.dataframe(tasks, use_container_width=True, hide_index=True)
    else:
        st.info("Chưa có dữ liệu")

    # Hiển thị agent khuyến nghị
    st.subheader("🤖 AI Agent đề xuất")
    if occ in RECS:
        agent_ids, reason = RECS[occ]  # Lấy từ mapping
        st.success(f"**{reason}**")
        cols = st.columns(len(agent_ids))
        for i, aid in enumerate(agent_ids):
            ag = AGENTS[aid]
            with cols[i]:
                st.markdown(f"### {ag['icon']} {ag['name']}")
                st.caption(ag["desc"])
                st.markdown(f"Công nghệ: `{ag['tech']}`")


def page_recommend(data):
    """
    Trang 3 - Khuyến nghị: Bảng tổng hợp agent cho mỗi ngành.
    Hiển thị:
      - Danh mục 8 agent (dạng expander)
      - Bảng: ngành → agent đề xuất → API → mức ưu tiên
      - Biểu đồ tròn phân bố ưu tiên
    """
    st.title("🤖 Khuyến nghị AI Agent")
    scores = calc_scores(data)

    # Expander chứa danh mục agent
    with st.expander("📚 Danh mục Agent (nhấn để xem)"):
        cols = st.columns(4)
        for i, (_, ag) in enumerate(AGENTS.items()):
            with cols[i % 4]:
                st.markdown(f"**{ag['icon']} {ag['name']}**")
                st.caption(ag["desc"])

    # Tạo bảng recommend: mỗi dòng = 1 ngành
    rows = []
    for occ in scores.index:
        if occ in RECS:
            aids, _ = RECS[occ]
            # Tạo chuỗi: icon + tên agent, cách nhau bởi ", "
            agent_str = ", ".join([AGENTS[a]["icon"] + AGENTS[a]["name"] for a in aids])
            # Xếp loại ưu tiên: Cao > 55%, TB > 40%, Thấp <= 40%
            pri = "Cao" if scores.loc[occ, "api"] > 55 else ("TB" if scores.loc[occ, "api"] > 40 else "Thấp")
            rows.append({"Occupation": occ, "Agent": agent_str,
                         "API": f"{scores.loc[occ, 'api']:.1f}%", "Priority": pri})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Biểu đồ tròn: tỉ lệ Cao / TB / Thấp
    cao = sum(1 for r in rows if r["Priority"] == "Cao")
    tb = sum(1 for r in rows if r["Priority"] == "TB")
    thap = sum(1 for r in rows if r["Priority"] == "Thấp")
    fig = px.pie(names=["Cao", "TB", "Thấp"],
                 values=[cao, tb, thap],
                 title="Mức độ ưu tiên",
                 color=["Cao", "TB", "Thấp"],
                 color_discrete_map={"Cao": "#2ca02c", "TB": "#ffbb78", "Thấp": "#d62728"})
    st.plotly_chart(fig, use_container_width=True)


def page_compare(data):
    """
    Trang 4 - So sánh: So sánh 2-4 ngành cùng lúc.
    Hiển thị:
      - Biểu đồ Radar: API, Readiness, Collab
      - Biểu đồ cột: Desire vs Capacity
    """
    st.title("📈 So sánh Occupations")
    scores = calc_scores(data)

    # Multiselect cho phép chọn nhiều ngành
    chon = st.multiselect("Chọn ngành (2-4):", CS_JOBS, default=CS_JOBS[:3])
    if len(chon) >= 2:
        df = scores.loc[chon].reset_index()

        # Radar chart: mỗi ngành là 1 hình trên cùng biểu đồ
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

        # Biểu đồ cột so sánh Desire (mong muốn) vs Capacity (khả năng)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="Desire", x=df["Occupation (O*NET-SOC Title)"], y=df["desire"]))
        fig2.add_trace(go.Bar(name="Capacity", x=df["Occupation (O*NET-SOC Title)"], y=df["capacity"]))
        fig2.update_layout(barmode="group", title="Desire vs Capacity", height=400)
        st.plotly_chart(fig2, use_container_width=True)


# ============================================================
# PHẦN 5: MAIN - KHỞI ĐỘNG APP
# ============================================================

def main():
    """
    Hàm chạy chính:
      1. Load dữ liệu (nếu lỗi → dừng lại)
      2. Hiện sidebar để chọn trang
      3. Dựa vào trang đã chọn → gọi hàm tương ứng
    """
    # Load dữ liệu, nếu lỗi thì báo và dừng
    try:
        data = load_data()
    except Exception as e:
        st.error(f"Lỗi load data: {e}")
        st.stop()

    # Hỏi người dùng muốn vào trang nào
    page = sidebar()

    # Chuyển hướng: dict mapping tên trang → hàm
    pages = {
        "📊 Dashboard": page_dashboard,
        "💼 Chi tiết": page_detail,
        "🤖 Khuyến nghị": page_recommend,
        "📈 So sánh": page_compare,
    }
    pages[page](data)


# Điểm bắt đầu khi chạy `python app.py` hoặc `streamlit run app.py`
if __name__ == "__main__":
    main()
