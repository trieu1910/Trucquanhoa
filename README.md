# 🤖 AI Agent trong Khoa học Máy tính

**Phân tích & Khuyến nghị ứng dụng AI Agent** dựa trên dữ liệu WorkBank.
Công cụ: **Streamlit + Pandas + Plotly**.

---

## 1. Tổng quan

WorkBank là bộ khảo sát từ **1000+ người lao động** về nhu cầu tự động hóa công việc,
kết hợp với **đánh giá chuyên gia** về khả năng công nghệ.

Project này tập trung vào **14 ngành nghề Computer Science (CS)**, phân tích:

- **Mong muốn** của người lao động: họ có muốn AI làm thay không?
- **Khả năng** công nghệ: chuyên gia đánh giá mức độ sẵn sàng
- **Khoảng cách (Gap)**: giữa mong muốn và thực tế
- **Khuyến nghị AI Agent**: loại agent nào phù hợp nhất

---

## 2. 14 ngành CS được phân tích

| # | Ngành | Mô tả |
|---|-------|-------|
| 1 | Web Administrators | Quản trị web |
| 2 | Web Developers | Phát triển web |
| 3 | Network/Systems Administrators | Quản trị mạng & hệ thống |
| 4 | Software QA Analysts | Kiểm thử phần mềm |
| 5 | Computer User Support Specialists | Hỗ trợ người dùng |
| 6 | Computer Programmers | Lập trình viên |
| 7 | Computer Network Support Specialists | Hỗ trợ mạng |
| 8 | Database Administrators | Quản trị cơ sở dữ liệu |
| 9 | Computer/Information Research Scientists | Nghiên cứu khoa học máy tính |
| 10 | Computer Systems Analysts | Phân tích hệ thống |
| 11 | Information Security Analysts | Phân tích bảo mật |
| 12 | Computer Systems Engineers/Architects | Kiến trúc sư hệ thống |
| 13 | Computer/Information Systems Managers | Quản lý hệ thống thông tin |
| 14 | Information Technology Project Managers | Quản lý dự án CNTT |

---

## 3. Phương pháp tính điểm

### 3.1 API - Automation Potential Index

**Công thức:**
```
API = (Desire × 0.4) + (Capacity × 0.4) + (6 − Expertise) × 0.1 + (6 − Interpersonal) × 0.1
```
- **Desire**: Mong muốn tự động hóa từ người lao động (1-5)
- **Capacity**: Khả năng công nghệ (1-5)
- **Expertise**: Mức độ yêu cầu chuyên môn (1-5, càng cao càng khó tự động)
- **Interpersonal**: Mức độ yêu cầu giao tiếp (1-5, càng cao càng khó tự động)

API được chuẩn hóa về thang **0-100%**.

### 3.2 Readiness Score

Đo lường mức độ sẵn sàng của công nghệ:
```
Readiness = (Capacity + (6 − Uncertainty)) / 2
```
- **Uncertainty**: Mức độ bất định trong công việc

### 3.3 Gap Analysis

```
Gap = Desire − Capacity
```

| Gap | Ý nghĩa |
|-----|---------|
| **> 0.5** | Người lao động muốn AI nhiều hơn khả năng hiện tại → **Cần ưu tiên phát triển** |
| **< -0.5** | Công nghệ sẵn sàng nhưng người lao động chưa muốn → **Cần nâng cao nhận thức** |
| **~ 0** | Cân bằng giữa mong muốn và khả năng |

---

## 4. Kết quả phân tích

### 4.1 Bảng xếp hạng API

| Hạng | Ngành | API (%) | Readiness (%) | Gap |
|------|-------|---------|---------------|-----|
| 🥇 | Web Administrators | **70.2** | 78.5 | -0.6 |
| 🥈 | Web Developers | **64.3** | 80.3 | -1.0 |
| 🥉 | Network/Systems Administrators | **62.7** | 63.0 | +0.2 |
| 4 | Software QA Analysts | **61.8** | 72.0 | -0.5 |
| 5 | Computer User Support | **61.5** | 73.7 | -0.9 |
| 6 | Computer Programmers | **60.4** | 72.0 | -0.9 |
| 7 | Computer Network Support | **57.5** | 70.1 | -1.0 |
| 8 | Database Administrators | **56.4** | 70.8 | -1.3 |
| 9 | Computer/Information Research Scientists | **53.6** | 45.8 | +1.2 |
| 10 | Computer Systems Analysts | **52.0** | 65.9 | -0.8 |
| 11 | Information Security Analysts | **51.6** | 46.6 | +0.2 |
| 12 | Computer Systems Engineers/Architects | **51.4** | 56.0 | +0.2 |
| 13 | Computer/Information Systems Managers | **50.7** | 55.6 | +0.8 |
| 14 | IT Project Managers | **41.1** | 43.2 | +0.3 |

### 4.2 Nhận xét chính

**Nhóm có tiềm năng cao (API > 60%):**
- Web Administrators, Web Developers, Network/Systems Admins, QA Analysts, User Support, Programmers
- Đặc điểm: công việc có quy trình rõ ràng, lặp lại, ít bất định
- Phù hợp: **RPA, Code Generation, Monitoring Agents**

**Nhóm có Gap dương (thiếu hụt công nghệ):**
- Computer/Information Research Scientists (+1.2): mong muốn AI cao nhưng công nghệ chưa theo kịp
- IT Managers (+0.3), Systems Managers (+0.8): quản lý muốn AI hỗ trợ nhưng chuyên gia đánh giá thấp

**Nhóm có Gap âm (công nghệ vượt nhu cầu):**
- Database Administrators (-1.3): công nghệ sẵn sàng nhưng chưa được tận dụng
- Web Developers (-1.0), Network Support (-1.0): tương tự

---

## 5. 8 loại AI Agent

| Agent | Icon | Mô tả | Độ phức tạp |
|-------|------|-------|-------------|
| **Code Agent** | ⚡ | Sinh code, sửa lỗi, refactor tự động | Thấp |
| **RPA Agent** | 🤖 | Tự động hóa nhập liệu, xử lý form | Thấp |
| **Monitor Agent** | 📡 | Giám sát hệ thống, cảnh báo bất thường | Thấp |
| **Analytic Agent** | 📊 | Phân tích data, phát hiện pattern | Trung bình |
| **Security Agent** | 🔒 | Phát hiện xâm nhập, kiểm tra bảo mật | Trung bình |
| **Copilot Agent** | 👨‍💻 | Trợ lý AI realtime cho developer | Trung bình |
| **Auto Agent** | 🧠 | Tự quyết định & thực thi không cần người | Cao |
| **Collab Agent** | 🤝 | Hợp tác người-AI, chia task, học từ feedback | Cao |

---

## 6. Khuyến nghị cụ thể

### 6.1 Lập trình viên (Programmers)
**Agent đề xuất:** Copilot → Code Agent → RPA
- Copilot hỗ trợ viết code realtime
- Code Agent tự động sinh test, documentation
- RPA xử lý nhập liệu, deploy tự động

### 6.2 Kiểm thử phần mềm (QA)
**Agent đề xuất:** Code Agent → RPA → Analytic Agent
- Tự động sinh test case
- Tự động chạy regression test
- Phân tích bug reports, phát hiện xu hướng lỗi

### 6.3 Quản trị hệ thống (SysAdmins)
**Agent đề xuất:** Monitor → RPA → Security Agent
- Giám sát server 24/7
- Tự động backup, patch
- Phát hiện xâm nhập

### 6.4 An ninh mạng (Security Analysts)
**Agent đề xuất:** Security Agent → Monitor → Analytic Agent
- Quét lỗ hổng tự động
- Phân tích log bảo mật
- Cảnh báo tấn công realtime

### 6.5 Quản lý dự án CNTT (IT PM)
**Agent đề xuất:** Analytic Agent → Collab Agent → Monitor Agent
- Phân tích tiến độ, rủi ro
- Tracking milestone tự động
- Tạo báo cáo thông minh

---

## 7. Hướng dẫn sử dụng

### Yêu cầu
- Python 3.9+
- Git

### Cài đặt & chạy
```bash
cd ai_agent_cs
pip install streamlit pandas numpy plotly
streamlit run app.py
```

### Các trang trong app
| Trang | Chức năng |
|-------|-----------|
| **Dashboard** | Tổng quan API, Readiness, Gap cho 14 ngành |
| **Chi tiết** | Xem từng ngành: top task, agent đề xuất |
| **Khuyến nghị** | Danh sách agent gợi ý cho mọi ngành |
| **So sánh** | So sánh 2-4 ngành cạnh nhau |

---

## 8. Cấu trúc project

```
workbank1/
├── ai_agent_cs/
│   ├── app.py           # 287 dòng - toàn bộ ứng dụng
│   ├── requirements.txt # 4 thư viện
│   └── README.md        # File này
├── task_statement_with_metadata.csv  # O*NET tasks
├── domain_worker_desires.csv         # Khảo sát người lao động
├── domain_worker_metadata.csv        # Thông tin nhân khẩu
└── expert_rated_technological_capability.csv  # Đánh giá chuyên gia
```

---

## 9. Dataset WorkBank

WorkBank bao gồm **4 file CSV**:

1. **task_statement_with_metadata.csv** (2131 dòng)
   - Mô tả công việc chuẩn O*NET
   - Mỗi task có: tần suất, tầm quan trọng, kỹ năng yêu cầu

2. **domain_worker_desires.csv** (5731 dòng)
   - Khảo sát người lao động (2025)
   - Hỏi về mong muốn tự động hóa cho từng task
   - Thang điểm 1-5: 1 = không muốn, 5 = rất muốn
   - Kèm lý do: repetitive, stress, human error, scale...

3. **domain_worker_metadata.csv** (1500 dòng)
   - Thông tin nhân khẩu: tuổi, giới tính, thu nhập, học vấn
   - Thái độ với AI, mức độ sử dụng LLM trong công việc

4. **expert_rated_technological_capability.csv** (2057 dòng)
   - Chuyên gia đánh giá khả năng tự động hóa của công nghệ hiện tại
   - Thang 1-5 cho từng task

---

## 10. Kết luận

**Phát hiện chính:**

1. **6/14 ngành CS có API > 60%** - sẵn sàng cho AI Agent ngay
2. **Web Administrators dẫn đầu** (70.2%) - đơn giản, quy trình rõ
3. **IT Project Managers thấp nhất** (41.1%) - phức tạp, nhiều giao tiếp
4. **Database Administrators có gap âm lớn nhất** (-1.3) - công nghệ vượt nhu cầu
5. **Research Scientists có gap dương lớn nhất** (+1.2) - cần phát triển thêm

**Chiến lược triển khai:**

| Giai đoạn | Thời gian | Hành động |
|-----------|-----------|-----------|
| Ngắn hạn | 1-3 tháng | RPA + Monitor Agent cho task đơn giản |
| Trung hạn | 3-6 tháng | Copilot + Analytic Agent cho task phức tạp |
| Dài hạn | 6-12 tháng | Auto Agent + Collab Agent cho tự động hóa toàn diện |

---

*Project phân tích dựa trên WorkBank Dataset (2025) - 14 ngành Khoa học Máy tính*
*Công cụ: Streamlit + Pandas + Plotly*
