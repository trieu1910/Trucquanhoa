# Sơ đồ luồng chức năng — AI Agent CS Analyzer

## 1. Sơ đồ tổng quát

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        WORKBANK DATASET (4 CSV)                        │
│                                                                         │
│  task_statement   domain_worker   domain_worker   expert_rated         │
│  _with_metadata   _desires        _metadata       _technological       │
│  (2131 dong)      (5731 dong)     (1500 dong)     _capability          │
│                                                   (2057 dong)          │
└─────────────────────────┬───────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     load_data()  [app.py:78]                            │
│                                                                         │
│  ┌─ read("task...csv") ──► loc 14 CS jobs ──► tasks (150 dong)        │
│  ├─ read("desires.csv") ──► loc 14 CS jobs ──► desires (1002 dong)    │
│  ├─ read("workers.csv") ──► loc 14 CS jobs ──► workers (247 dong)     │
│  └─ read("expert.csv") ──► loc 14 CS jobs ──► expert (321 dong)       │
│                                                                         │
│  @st.cache_data: luu cache 1h, khong load lai khi refresh              │
└─────────────────────────┬───────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     calc_scores()  [app.py:120]                         │
│  Xử lý: groupby("Occupation") + mean() cho từng chỉ số                 │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ ĐẦU VÀO (từ desires + expert)                                    │   │
│  │                                                                   │   │
│  │  d = desires["Automation Desire Rating"]       (mong muon)       │   │
│  │  c = expert["Automation Capacity Rating"]      (kha nang CN)     │   │
│  │  u = expert["Involved Uncertainty"]           (do bat dinh)      │   │
│  │  e = expert["Domain Expertise Requirement"]   (yeu cau chuyen mon)│   │
│  │  i = expert["Interpersonal Comm Requirement"] (yeu cau giao tiep)│   │
│  │  a = desires["Human Agency Scale Rating"]     (muc do giu nguoi) │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                          │                                               │
│                          ▼                                               │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ TÍNH TOÁN                                                         │   │
│  │                                                                   │   │
│  │  API = desire*0.4 + capacity*0.4                                 │   │
│  │        + (6-expertise)*0.1 + (6-interpersonal)*0.1               │   │
│  │  API = ((API-1)/4*100).clip(0,100)  ──► 0..100%                  │   │
│  │                                                                   │   │
│  │  Readiness = (capacity + (6-uncertainty)) / 2                     │   │
│  │  Readiness = ((Readiness-1)/4*100).clip(0,100)  ──► 0..100%      │   │
│  │                                                                   │   │
│  │  Collab = agency*0.6 + 0.4                                       │   │
│  │  Collab = ((Collab-1)/4*100).clip(0,100)     ──► 0..100%         │   │
│  │                                                                   │   │
│  │  Gap = desire - capacity                   ──► -4..+4            │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                          │                                               │
│                          ▼                                               │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ ĐẦU RA: DataFrame index=Occupation, gom 14 dong                 │   │
│  │  Columns: desire, capacity, api, readiness, collab, gap          │   │
│  │  Sort: api DESC (cao nhat → thap nhat)                          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     top_tasks(occ, data, n)  [app.py:150]               │
│  Chỉ chạy khi người dùng chọn 1 occupation cụ thể (trang Chi tiết)     │
│                                                                         │
│  ┌─ Loc desires theo occ ──► groupby("Task ID")["Desire"].mean()      │
│  ├─ Loc expert theo occ  ──► groupby("Task ID")["Capacity"].mean()    │
│  ├─ Join 2 bang theo Task ID                                           │
│  ├─ score = desire*0.5 + capacity*0.5                                 │
│  ├─ Sort score DESC, lay top n                                         │
│  └─ Merge voi tasks["Task"] de lay mo ta                               │
│                                                                         │
│  Kết quả: DataFrame [Task, score] - ví dụ:                             │
│    "Investigate whether networks..."  → 4.20                           │
│    "Compile and write documentation"  → 4.15                           │
└─────────────────────────┬───────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│               RECS (Recommendation Mapping)  [app.py:62]               │
│  Danh sách có sẵn: 14 occupation → [3 agent_id, lý do]                │
│                                                                         │
│  Ví dụ:                                                                 │
│    "Computer Programmers"                                              │
│      └─► ["copilot", "code", "rpa"]                                    │
│      └─► "Code + RPA la chinh"                                         │
│                                                                         │
│    "Information Security Analysts"                                     │
│      └─► ["security", "monitor", "analytic"]                           │
│      └─► "Bao mat la chinh"                                            │
└─────────────────────────┬───────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│               8 LOẠI AI AGENT  [app.py:41]                             │
│                                                                         │
│  ┌──────────┬───────────┬──────────────────┬────────┐                  │
│  │ ID       │ Icon      │ Mô tả            │ Level  │                  │
│  ├──────────┼───────────┼──────────────────┼────────┤                  │
│  │ code     │ ⚡        │ Sinh code tự động │ 1-thấp │                  │
│  │ rpa      │ 🤖       │ RPA nhập liệu     │ 1-thấp │                  │
│  │ monitor  │ 📡       │ Giám sát hệ thống  │ 1-thấp │                  │
│  │ analytic │ 📊       │ Phân tích dữ liệu  │ 2-tb   │                  │
│  │ security │ 🔒       │ Bảo mật           │ 2-tb   │                  │
│  │ copilot  │ 👨‍💻    │ Trợ lý AI         │ 2-tb   │                  │
│  │ autonomous│ 🧠      │ Tự động hoàn toàn  │ 3-cao  │                  │
│  │ collab   │ 🤝       │ Hợp tác người-AI  │ 3-cao  │                  │
│  └──────────┴───────────┴──────────────────┴────────┘                  │
└─────────────────────────┬───────────────────────────────────────────────┘
                          │
                          ▼
┌═════════════════════════════════════════════════════════════════════════┐
║                    STREAMLIT UI (4 trang)                              ║
║                                                                         ║
║  ┌──────────────────────────────────────────────────────────────────┐  ║
║  │ TRANG 1: DASHBOARD  [page_dashboard()]                           │  ║
║  │                                                                   │  ║
║  │  sidebar() ──► chon "📊 Dashboard"                               │  ║
║  │       │                                                           │  ║
║  │       ▼                                                           │  ║
║  │  calc_scores(data) ──► scores                                    │  ║
║  │       │                                                           │  ║
║  │       ├──► 4 metric cards (so luong, API TB, Top, Readiness TB)  │  ║
║  │       ├──► Bar chart: API score 14 nghe (mau RdYlGn)             │  ║
║  │       └──► Bang: API, Readiness, Collab, Gap                     │  ║
║  └──────────────────────────────────────────────────────────────────┘  ║
║                                                                         ║
║  ┌──────────────────────────────────────────────────────────────────┐  ║
║  │ TRANG 2: CHI TIET  [page_detail()]                               │  ║
║  │                                                                   │  ║
║  │  sidebar() ──► chon "💼 Chi tiet"                                │  ║
║  │       │                                                           │  ║
║  │       ▼                                                           │  ║
║  │  selectbox("Chon nghe") ──► occ                                  │  ║
║  │       │                                                           │  ║
║  │       ├──► calc_scores() ──► 3 metric: API, Readiness, Collab   │  ║
║  │       ├──► top_tasks(occ)  ──► bang "Top task"                  │  ║
║  │       └──► RECS[occ] ──► AGENTS[agent_id]                       │  ║
║  │              │                                                    │  ║
║  │              └──► Hien thi agent: icon, ten, mo ta, cong nghe   │  ║
║  └──────────────────────────────────────────────────────────────────┘  ║
║                                                                         ║
║  ┌──────────────────────────────────────────────────────────────────┐  ║
║  │ TRANG 3: KHUYEN NGHI  [page_recommend()]                         │  ║
║  │                                                                   │  ║
║  │  sidebar() ──► chon "🤖 Khuyen nghi"                             │  ║
║  │       │                                                           │  ║
║  │       ▼                                                           │  ║
║  │  calc_scores(data) ──► scores                                    │  ║
║  │       │                                                           │  ║
║  │       ├──► Danh muc 8 Agent (expander)                           │  ║
║  │       ├──► Tao bang: [Occupation, Agent, API, Priority]          │  ║
║  │       │      priority: Cao(API>55) / TB(API>40) / Thap          │  ║
║  │       └──► Pie chart: phan bo Cao/TB/Thap                       │  ║
║  └──────────────────────────────────────────────────────────────────┘  ║
║                                                                         ║
║  ┌──────────────────────────────────────────────────────────────────┐  ║
║  │ TRANG 4: SO SANH  [page_compare()]                               │  ║
║  │                                                                   │  ║
║  │  sidebar() ──► chon "📈 So sanh"                                 │  ║
║  │       │                                                           │  ║
║  │       ▼                                                           │  ║
║  │  multiselect(CS_JOBS) ──► chon (2-4 nghe)                        │  ║
║  │       │                                                           │  ║
║  │       ├──► Radar chart: API + Readiness + Collab                 │  ║
║  │       └──► Group bar: Desire vs Capacity                         │  ║
║  └──────────────────────────────────────────────────────────────────┘  ║
║                                                                         ║
║  ┌──────────────────────────────────────────────────────────────────┐  ║
║  │ MAIN()  [app.py:400]                                             │  ║
║  │                                                                   │  ║
║  │  1. load_data()           ──► neu loi → st.error + stop          │  ║
║  │  2. sidebar()             ──► page = ten trang                   │  ║
║  │  3. pages[page](data)     ──► goi ham tuong ung                  │  ║
║  └──────────────────────────────────────────────────────────────────┘  ║
║                                                                         ║
╚═════════════════════════════════════════════════════════════════════════╝
```

---

## 2. Sơ đồ luồng dữ liệu chi tiết

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│  tasks   │   │ desires  │   │ workers  │   │  expert  │
│ (2131→150)│   │(5731→1002)│   │(1500→247)│   │(2057→321)│
└────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘
     │              │              │              │
     │              ▼              │              ▼
     │       ┌──────────┐          │       ┌──────────┐
     │       │ Desires  │          │       │ Capacity │
     │       │ (1-5)    │          │       │ (1-5)    │
     │       │ Agency   │          │       │ Uncert.  │
     │       │ (1-5)    │          │       │ Expert.  │
     │       │          │          │       │ Interper │
     │       └────┬─────┘          │       └────┬─────┘
     │            │                │            │
     │            ▼                │            ▼
     │       ┌──────────────────────────────────────┐
     │       │        calc_scores()                 │
     │       │                                      │
     │       │  API = d*0.4 + c*0.4                 │
     │       │        + (6-e)*0.1 + (6-i)*0.1       │
     │       │  Readiness = (c + (6-u)) / 2         │
     │       │  Collab = agency*0.6 + 0.4           │
     │       │  Gap = d - c                         │
     │       └────────────────┬─────────────────────┘
     │                        │
     │                        ▼
     │       ┌──────────────────────────────────────┐
     │       │     scores DataFrame (14 dong)       │
     │       │  index = Occupation                  │
     │       │  cols = [api, readiness, collab, gap]│
     │       └────────────────┬─────────────────────┘
     │                        │
     │                        ├──────► page_dashboard()
     │                        ├──────► page_recommend()
     │                        └──────► page_compare()
     │
     │              Khi chon 1 Occ cu the:
     ▼
┌──────────────────────────────────────┐
│      top_tasks(occ)                  │
│                                      │
│  desires[occ] + expert[occ]          │
│       │                              │
│       ▼                              │
│  groupby(Task ID)                    │
│  score = desire*0.5 + capacity*0.5   │
│  sort + top 5                        │
│  merge voi tasks["Task"]             │
│       │                              │
│       ▼                              │
│  Bang "Top task" cho nguoi dung      │
└──────────────────────────────────────┘

KET HOP VOI RECS MAPPING:

  scores[occ] + RECS[occ] + AGENTS[]
       │
       ▼
  Hien thi:
  - Ten agent (icon)
  - Mo ta
  - Cong nghe de xuat
```

---

## 3. Sơ đồ luồng quyết định khuyến nghị

```
                         BẮT ĐẦU
                           │
                           ▼
              ┌─────────────────────────┐
              │  Nguoi dung chon nghe   │
              │  tu dropdown / trang    │
              └────────────┬────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │  occ = ten nghe         │
              └────────────┬────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │  RECS[occ] co ton tai?  │
              └────────────┬────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
             YES                        NO
              │                         │
              ▼                         ▼
   ┌────────────────────┐   ┌────────────────────┐
   │ agent_ids, reason  │   │  Khong co de xuat  │
   │ = RECS[occ]        │   │  → thong bao       │
   └────────┬───────────┘   └────────────────────┘
            │
            ▼
   ┌────────────────────┐
   │  Duyet agent_ids:  │
   │  for i, aid in ... │
   └────────┬───────────┘
            │
            ▼
   ┌────────────────────────────────────┐
   │  ag = AGENTS[aid]                  │
   │  Hien thi:                         │
   │    icon + ten + mo ta + cong nghe  │
   └────────────────────────────────────┘
            │
            ▼
   ┌────────────────────┐
   │  Phan loai theo    │
   │  do phuc tap:      │
   │  level 1: ngan han │
   │  level 2: trung han│
   │  level 3: dai han  │
   └────────┬───────────┘
            │
            ▼
   ┌────────────────────┐
   │  Api score > 55?   │
   └────────┬───────────┘
            │
   ┌────────┴────────┐
   │                 │
  YES                NO
   │                 │
   ▼                 ▼
  "Cao"        API > 40?
                │     │
              YES     NO
               │      │
               ▼      ▼
             "TB"   "Thap"
```

---

## 4. Sơ đồ kiến trúc project

```
workbank1/
│
├── ai_agent_cs/                    # Thư mục chính của project
│   │
│   ├── app.py                      # TOÀN BỘ CODE (421 dòng)
│   │   │
│   │   ├── [1-16]   Import + cấu hình
│   │   ├── [18-37]  CS_JOBS: 14 ngành
│   │   ├── [39-57]  AGENTS: 8 loại AI Agent
│   │   ├── [59-75]  RECS: mapping ngành→agent
│   │   ├── [77-112] load_data(): đọc 4 CSV
│   │   ├── [114-141] calc_scores(): tính API/Readiness/Gap
│   │   ├── [143-172] top_tasks(): top task cho 1 ngành
│   │   ├── [174-182] sidebar(): menu điều hướng
│   │   ├── [184-210] page_dashboard(): trang tổng quan
│   │   ├── [212-249] page_detail(): trang chi tiết
│   │   ├── [251-283] page_recommend(): trang khuyến nghị
│   │   ├── [285-318] page_compare(): trang so sánh
│   │   └── [320-346] main(): khởi động app
│   │
│   ├── requirements.txt            # 4 thư viện
│   ├── README.md                   # Tài liệu
│   └── FLOWCHART.md                # File này
│
├── task_statement_with_metadata.csv
├── domain_worker_desires.csv
├── domain_worker_metadata.csv
└── expert_rated_technological_capability.csv
```

---

## 5. Luồng sự kiện người dùng

```
NGƯỜI DÙNG                    STREAMLIT                     DATA
    │                             │                           │
    │  streamlit run app.py       │                           │
    │────────────────────────────►│                           │
    │                             │                           │
    │                             │  load_data()              │
    │                             │──────────────────────────►│
    │                             │◄──────────────────────────│
    │                             │  (cache 1h)               │
    │                             │                           │
    │  ◄─── Mở trình duyệt ────►  │                           │
    │                             │                           │
    │  Chọn "Dashboard"           │                           │
    │────────────────────────────►│                           │
    │                             │  calc_scores(data)        │
    │                             │  Vẽ bar chart + metric    │
    │◄────────────────────────────│                           │
    │                             │                           │
    │  Chọn "Chi tiết"            │                           │
    │────────────────────────────►│                           │
    │                             │  Selectbox(CS_JOBS)       │
    │◄──── chọn dropdown ────────│                           │
    │                             │                           │
    │  Chọn "Computer Programmer" │                           │
    │────────────────────────────►│                           │
    │                             │  calc_scores → 3 metric   │
    │                             │  top_tasks(occ) → 5 task  │
    │                             │  RECS[occ] → agent info   │
    │◄────────────────────────────│                           │
    │                             │                           │
    │  Chọn "Khuyến nghị"         │                           │
    │────────────────────────────►│                           │
    │                             │  calc_scores              │
    │                             │  Duyệt RECS + AGENTS      │
    │                             │  Vẽ pie chart             │
    │◄────────────────────────────│                           │
    │                             │                           │
    │  Chọn "So sánh"             │                           │
    │────────────────────────────►│                           │
    │                             │  multiselect(CS_JOBS)     │
    │◄─── chọn 2-4 ngành ───────│                           │
    │                             │  calc_scores              │
    │                             │  Vẽ radar + group bar     │
    │◄────────────────────────────│                           │
```

---

## 6. Chú thích

| Ký hiệu | Ý nghĩa |
|---------|---------|
| `┌───┐` | Khối bắt đầu/kết thúc |
| `──►` | Luồng dữ liệu / xử lý |
| `◄──►` | Tương tác hai chiều |
| `...→n` | Số dòng dữ liệu trước→sau khi lọc |
| `[app.py:xxx]` | Số dòng code tương ứng |
| `@st.cache_data` | Hàm có cache trong Streamlit |
