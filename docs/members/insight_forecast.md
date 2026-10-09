# Phân công Insight, RFM và Dự báo Dài hạn (Forecast đến 2030)

**Phụ trách:** Phạm Quốc Duy (MSSV: 24133008)  
**Mục tiêu:** Huấn luyện và đánh giá mô hình dự báo doanh thu dài hạn đến năm 2030 từ dữ liệu đã chuẩn hóa; gắn nhãn phân khúc RFM theo từng nguồn dữ liệu; bàn giao hệ thống biểu đồ đa chiều và insight nghiệp vụ chiến lược cho Dashboard.

---

## 1. Phạm vi sở hữu & Hiện trạng hoàn thành

- [x] `src/shared/rfm_utils.py`: Công thức tính RFM (Recency, Frequency, Monetary), chấm điểm 1–5 bằng `rank(method="first")` và gán nhãn 6 segment. Cohort phân tách rõ theo `Customer ID × Data Source`.
- [x] `src/dash_app/components/charts.py`: Xây dựng bộ hàm trực quan hóa dự báo dài hạn đến 2030:
  - `build_forecast_scenarios_figure()`: Chuỗi thời gian kết hợp Trend + Mùa vụ 12 tháng, 3 kịch bản tăng trưởng (Cơ sở, Lạc quan +20%, Thận trọng -15%) và dải tin cậy.
  - `build_category_forecast_figure()`: Stacked Bar cơ cấu doanh thu theo Category tới 2030.
  - `build_regional_forecast_figure()`: Grouped Bar so sánh doanh thu hiện tại vs mục tiêu 2030 của các khu vực trọng điểm.
  - `build_quantity_profit_forecast_figure()`: Combo Bar-Line sản lượng tiêu thụ (Quantity) & lợi nhuận dự phóng (Profit).
- [x] `src/dash_app/pages/rfm.py`: Trang phân khúc khách hàng (Dropdown/Grid chuyển đổi Pie / Scatter / Box plot kèm bảng hành động đề xuất chi tiết).
- [x] `src/dash_app/pages/forecast.py`: Dashboard dự báo dài hạn hoàn chỉnh với 4 thẻ KPI mục tiêu 2030, 4 cụm biểu đồ đa chiều và bảng lộ trình chiến lược 3 giai đoạn.
- [x] `src/shared/forecasting.py`: Module xử lý dự báo độc lập và tự động xuất file HTML tương tác (`forecast_output.html`).
- [x] `docs/members/insight_forecast.md`: Tài liệu nghiệm thu, nhật ký thực nghiệm, giả định và khuyến nghị chiến lược.

---

## 2. Kết quả Thực nghiệm & Đánh giá Mô hình Dự báo

### A. Phương pháp thực nghiệm
- **Chuỗi thời gian:** Tổng hợp doanh thu theo tháng từ `data/processed/cleaned_data.csv` (156 tháng từ 2012 đến 2024).
- **Phân chia dữ liệu:** Time-based Split — sử dụng 12 tháng gần nhất làm tập kiểm thử (Test Horizon).
- **Thuật toán cốt lõi:** 
  - **Thành phần Xu thế (Trend):** Hồi quy tuyến tính bậc 1 trên trục thời gian $t$.
  - **Thành phần Mùa vụ (Seasonality):** Chỉ số mùa vụ chuẩn hóa 12 tháng (Monthly Seasonality Index $S_m = \bar{Y}_m / \bar{Y}$), phản ánh chính xác các đợt bùng nổ mua sắm Quý 4 (đặc biệt là tháng 11).
  - **Dự phóng tương lai:** 72 tháng (từ tháng 01/2025 đến tháng 12/2030).

### B. Chỉ số sai số thực nghiệm trên tập Test
- **Mô hình Xu thế + Mùa vụ:**
  - Sai số MAE và RMSE phản ánh biên độ biến động tự nhiên của chuỗi bán lẻ.
  - Đảm bảo bắt kịp các tháng cao điểm cuối năm thay vì một đường thẳng cố định.
- **Baseline Naive:** Sai số ngắn hạn 1 tháng thấp hơn nhờ bám sát giá trị tháng liền kề, nhưng không thể sử dụng để hoạch định dài hạn 5–6 năm.

---

## 3. Ba Kịch bản Tăng trưởng Hướng tới Năm 2030

| Kịch bản | Giả định thị trường | Tỷ lệ tăng trưởng | Mục tiêu Doanh thu Năm 2030 |
| :--- | :--- | :--- | :--- |
| **Kịch bản Cơ sở (Base Case)** | Duy trì xu thế tăng trưởng lịch sử và tính chu kỳ mùa vụ hiện tại. | CAGR bình quân ~8% - 12%/năm | Đạt mốc doanh thu ổn định, cân bằng giữa đầu tư và bảo toàn vốn. |
| **Kịch bản Lạc quan (Optimistic)** | Mở rộng thị phần quốc tế, đẩy mạnh nhóm ngành Technology và tối ưu chiến dịch khách hàng VIP. | Biên tăng trưởng +15% đến +25% so với Base | Tối đa hóa công suất bán hàng, mở rộng quy mô toàn cầu. |
| **Kịch bản Thận trọng (Pessimistic)** | Lạm phát, sức mua suy giảm, gián đoạn chuỗi cung ứng logistics. | Biên tăng trưởng -15% đến -20% so với Base | Bảo toàn dòng tiền, kiểm soát chặt chẽ hàng tồn kho và chi phí vận hành. |

---

## 4. Kế hoạch Hành động Chiến lược 3 Giai đoạn (2025–2030)

### Giai đoạn 1 (2025 – 2026: Ngắn hạn) — Tối ưu hóa & Ổn định
- **Trọng tâm:** Củng cố nhóm khách hàng *Champions* & *Loyal Customers*; số hóa quy trình quản trị kho theo dự báo sản lượng tháng; chủ động ứng phó đỉnh điểm mua sắm Quý 4.
- **Chỉ tiêu:** Kiểm soát sai số dự báo MAE < 15%; duy trì mức tồn kho an toàn 45 ngày.

### Giai đoạn 2 (2027 – 2028: Trung hạn) — Mở rộng & Tăng tốc
- **Trọng tâm:** Đẩy mạnh ngân sách marketing tại các Region có tốc độ tăng trưởng (CAGR) cao nhất; mở rộng danh mục Technology và các gói combo sản phẩm biên lợi nhuận cao.
- **Chỉ tiêu:** Theo sát Kịch bản Lạc quan với mức tăng trưởng +20%/năm; duy trì tỷ suất lợi nhuận ròng > 12%.

### Giai đoạn 3 (2029 – 2030: Dài hạn) — Bứt phá & Bền vững
- **Trọng tâm:** Hoàn thành mốc doanh thu mục tiêu năm 2030; tự động hóa hoàn toàn chuỗi cung ứng logistics; chuyển đổi mô hình phân phối đa kênh.
- **Chỉ tiêu:** Chuẩn bị quỹ dự phòng rủi ro 10% doanh thu theo Kịch bản Thận trọng để ứng phó với chu kỳ suy thoái kinh tế vĩ mô.

---

## 5. Insight Nghiệp vụ RFM & Khuyến nghị Phân khúc

- **Nhóm Champions (R: 4-5, F: 4-5, M: 4-5):** Khách hàng VIP, đóng góp doanh thu lớn nhất. Cung cấp đặc quyền cá nhân hóa, chăm sóc riêng và trải nghiệm sản phẩm mới sớm.
- **Nhóm Loyal Customers (R: 3-5, F: 3-5, M linh hoạt):** Mua sắm đều đặn. Triển khai chương trình tích điểm hội viên, ưu đãi theo combo (upselling/cross-selling).
- **Nhóm New Customers (R: 4-5, F: 1-2, M linh hoạt):** Khách hàng mới. Tặng voucher cho đơn hàng thứ 2 trong vòng 14 ngày để kích thích chuyển đổi thành khách hàng thường xuyên.
- **Nhóm Need Attention (Điểm trung bình R: 3, F: 2-3):** Dấu hiệu chững lại. Gợi ý lại các danh mục hàng họ từng mua kèm khuyến mãi có thời hạn ngắn.
- **Nhóm At Risk (R: 1-2, F: 3-5, M cao):** Khách quen lâu ngày chưa quay lại. Kích hoạt chiến dịch Email Automation cá nhân hóa, gửi khảo sát phản hồi dịch vụ.
- **Nhóm Lost (R: 1-2, F: 1-2, M: 1-2):** Đã rời bỏ hoàn toàn. Giảm thiểu chi phí tiếp thị trực tiếp; chỉ tiếp cận qua các chiến dịch đại lễ lớn.