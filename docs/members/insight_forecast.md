# Phân công Insight, RFM và Forecast

**Phụ trách:** Phạm Quốc Duy (MSSV: 24133008)  
**Mục tiêu:** Huấn luyện và đánh giá mô hình dự báo doanh thu từ dữ liệu đã chuẩn hóa; gắn nhãn phân khúc RFM theo từng nguồn dữ liệu; bàn giao biểu đồ và insight nghiệp vụ cho Dashboard.

1. Phạm vi sở hữu & Hiện trạng hoàn thành
[x] src/shared/rfm_utils.py: Công thức tính RFM (Recency, Frequency, Monetary), chấm điểm 1–5 bằng rank(method="first") và gán nhãn 6 segment. Cohort phân tách rõ theo Customer ID × Data Source.

[x] src/dash_app/components/charts.py: Đã nâng cấp build_rfm_figure() và build_forecast_figure() (tích hợp time-based train/test split, tính MAE/RMSE và dự báo 3 tháng).

[x] src/dash_app/pages/rfm.py: Trang phân khúc khách hàng (Dropdown chuyển đổi Pie / Scatter / Box plot kèm bảng hành động đề xuất chi tiết).

[x] src/dash_app/pages/forecast.py: Trang dự báo doanh thu (hiển thị đối chiếu thực tế vs dự báo, caption tự động MAE/RMSE và ghi chú giới hạn mô hình).

[x] docs/members/insight_forecast.md: Tài liệu nghiệm thu, nhật ký thực nghiệm và insight nghiệp vụ.

2. Kết quả Đánh giá Mô hình Dự báo (Linear Regression)
A. Phương pháp thực nghiệm
Chuỗi thời gian: Tổng hợp doanh thu theo tháng từ data/processed/monthly_sales.csv (chỉ xét các tháng có phát sinh đơn hàng thực tế).
Phân chia dữ liệu: Time-based Split — sử dụng 3 tháng có giao dịch gần nhất làm tập kiểm thử (Test Horizon).
Biến độc lập: Trục thời gian số học t = 0, 1, 2, ... tính từ mốc tháng đầu tiên của chuỗi.
B. Chỉ số sai số thực nghiệm trên tập Test
MAE (Mean Absolute Error): ~184,402

RMSE (Root Mean Squared Error): ~185,103

Baseline Naive: Sai số ngắn hạn đạt mức thấp hơn (~24,283) do mô hình Naive bám sát giá trị tháng liền kề trước đó.

3. Giả định và Giới hạn Mô hình
Giả định xu thế tuyến tính: Mô hình Linear Regression giả định doanh thu biến thiên tuyến tính theo thời gian.

Hạn chế mùa vụ (Seasonality): Doanh thu bán lẻ có tính biến động và bùng nổ rất mạnh vào Quý 4 hàng năm (mùa mua sắm, lễ hội). Mô hình hồi quy đường thẳng chưa nắm bắt được tính chu kỳ này, dẫn đến sai số kiểm thử còn cao.

Giới hạn nguồn dữ liệu: Nguồn Kaggle 2019–2020 là dữ liệu thử nghiệm chưa xác minh độc lập (unverified provenance), cần tách riêng qua bộ lọc nguồn khi phân tích; kết quả từ Linear Regression đóng vai trò baseline tham khảo xu hướng nền, không dùng làm dự báo kinh doanh chính thức.

4. Insight Nghiệp vụ RFM & Khuyến nghị Hành động
**Nhóm Champions**
Đặc điểm RFM: R đạt 4-5, F đạt 4-5, M đạt 4-5.

Quan sát dữ liệu: Chiếm tỷ trọng doanh thu cao nhất toàn hệ thống dù số lượng khách không chiếm đa số.

Hành động đề xuất: Cung cấp dịch vụ chăm sóc VIP riêng biệt, ưu tiên trải nghiệm sớm sản phẩm mới.

**Nhóm Loyal Customers**
Đặc điểm RFM: R đạt 3-5, F đạt 3-5, M linh hoạt.

Quan sát dữ liệu: Khách hàng mua sắm đều đặn, tần suất ổn định qua các năm.

Hành động đề xuất: Triển khai các gói khuyến mãi combo (cross-selling, upselling), xây dựng chương trình tích điểm hội viên.

**Nhóm New Customers**
Đặc điểm RFM: R đạt 4-5, F đạt 1-2, M linh hoạt.

Quan sát dữ liệu: Khách hàng mới phát sinh giao dịch trong thời gian gần đây.

Hành động đề xuất: Gửi email cảm ơn, tặng mã giảm giá cho đơn hàng thứ 2 trong vòng 14 ngày để gia tăng tỷ lệ quay lại.

**Nhóm Need Attention**
Đặc điểm RFM: Điểm trung bình (khoảng R: 3, F: 2-3).

Quan sát dữ liệu: Tần suất mua sắm hoặc mức chi tiêu có dấu hiệu chững lại.

Hành động đề xuất: Gợi ý lại các danh mục hàng họ từng mua kèm ưu đãi có giới hạn thời gian.

**Nhóm At Risk**
Đặc điểm RFM: R đạt 1-2, F đạt 3-5, M cao.

Quan sát dữ liệu: Khách quen trước đây nhưng đã lâu không phát sinh đơn hàng mới (Recency quá 90 ngày).

Hành động đề xuất: Kích hoạt chiến dịch Email Automation cá nhân hóa, gửi khảo sát tìm hiểu lý do khách ngừng mua sắm.

**Nhóm Lost**
Đặc điểm RFM: R đạt 1-2, F đạt 1-2, M đạt 1-2.

Quan sát dữ liệu: Khách hàng đã rời bỏ hoàn toàn, đóng góp giá trị thấp.

Hành động đề xuất: Giảm thiểu chi phí tiếp thị trực tiếp; chỉ tiếp cận lại vào các đợt khuyến mãi xả kho hoặc đại lễ lớn trong năm.