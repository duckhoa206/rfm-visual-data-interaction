# Phân công Insight, RFM và Forecast

**Phụ trách: Phạm Quốc Duy**
**Mục tiêu:** biến dữ liệu sạch thành các phân khúc khách hàng, insight kinh doanh và dự báo doanh thu có đánh giá rõ ràng.

## Phạm vi sở hữu

```text
src/shared/rfm_utils.py            Công thức RFM, score và segment (duy nhất)
src/dash_app/components/charts.py  build_rfm_figure() + build_forecast_figure() dùng chung
src/dash_app/pages/rfm.py          Trang /rfm (pie / scatter / box)
src/dash_app/pages/forecast.py     Trang /forecast (thực tế + dự báo 3 tháng)
docs/members/insight_forecast.md   Theo dõi giả định, metric và insight
```

Input đơn hàng luôn đi qua `src/dash_app/shared_data.py`, đọc từ `data/processed/cleaned_data.csv` (UNION 2012–2024, 71.391 dòng). Không thay đổi cách làm sạch trong `data_cleaning.py` nếu chưa trao đổi với Data. Không chỉnh khung sidebar/filter chung nếu chưa trao đổi với Dashboard. Nếu dataset thiếu, đổi tên, đổi kiểu hoặc đổi ý nghĩa trường, phối hợp với Data và Dashboard kiểm tra/cập nhật logic RFM, insight và forecast liên quan.

## Phần nền tảng đã có

- [X] `rfm_utils.py` tính Recency, Frequency, Monetary theo `Customer ID`.
- [X] Có R/F/M score 1–5 và các segment: Champions, Loyal Customers, New Customers, At Risk, Lost, Need Attention.
- [X] Trang RFM đã hiển thị tỷ trọng segment, scatter Frequency–Monetary, box plot và bảng chi tiết.
- [X] Trang dự báo có Linear Regression demo, dự báo doanh thu ba tháng tiếp theo.

## Danh mục biểu đồ đã làm (10 visual, dữ liệu 2012–2024)

| Trang                 | Biểu đồ                                                                                                       | Nguồn                                         |
| --------------------- | ---------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| Tổng quan`/`       | Bar doanh thu theo danh mục; line xu hướng theo tháng; bảng RFM                                             | `build_bar_category`, `build_line_monthly` |
| Địa lý`/geo`     | Choropleth theo quốc gia; treemap Region/Country/Category; heatmap Region × Category                           | `build_geo_figure`                           |
| RFM`/rfm`           | Pie tỷ trọng segment; scatter Frequency–Monetary (size = Monetary); box phân phối Monetary                  | `build_rfm_figure`                           |
| Dự báo`/forecast` | Line thực tế + dự báo 3 tháng (Linear Regression trên chỉ số tháng`t`), chú thích xu hướng/tháng | `build_forecast_figure`                      |

RFM hiện tại: snapshot = ngày đơn hàng mới nhất (2024-12-30) + 1 ngày; 18.223 khách hàng; Recency tính bằng ngày, Frequency = số Order ID, Monetary = tổng Sales.

## Việc cần hoàn thiện: RFM và insight

- [ ] Xác nhận định nghĩa nghiệp vụ của Recency, Frequency, Monetary và ngày snapshot với nhóm.
- [ ] Kiểm thử RFM trên dữ liệu mới (71.391 dòng); xử lý trường hợp nhiều giá trị Recency trùng khiến `qcut` không tạo đủ nhóm.
- [ ] Viết mô tả và hành động đề xuất cho từng segment.
- [ ] Tạo các insight có bằng chứng: xu hướng doanh thu 2012–2024 (lưu ý lỗ 2019–2020), khu vực/danh mục nổi bật, nhóm khách hàng giá trị cao và nhóm rủi ro.
- [ ] Mỗi insight cần có: quan sát dữ liệu, diễn giải ngắn và khuyến nghị hành động.

## Việc cần hoàn thiện: Forecast

- [ ] Tách logic trong `build_forecast_figure()` sang `src/shared/forecasting.py` (chuẩn bị chuỗi tháng, train, evaluate, predict); page chỉ hiển thị kết quả.
- [ ] Tổng hợp doanh thu theo tháng, xử lý tháng bị thiếu (đặc biệt quanh 2019–2020) và xác định horizon dự báo.
- [ ] Chia train/test theo thời gian, không chia ngẫu nhiên.
- [ ] Đánh giá mô hình bằng ít nhất MAE và RMSE; MAPE nếu doanh thu không bằng 0.
- [ ] So sánh Linear Regression với baseline đơn giản, ví dụ doanh thu tháng gần nhất hoặc trung bình trượt.
- [ ] Hiển thị actual, prediction trên tập test, future forecast và metric trên dashboard.
- [ ] Sửa cảnh báo feature name bằng cách dự đoán với DataFrame có cột `t`.
- [ ] Ghi rõ giả định và giới hạn của mô hình; không diễn giải forecast hiện tại như kết quả chính thức (mô hình tuyến tính đơn biến, chưa tách yếu tố mùa vụ).

## Hợp đồng bàn giao cho Dashboard

- Data bàn giao file `data/processed/cleaned_data.csv` theo schema đầu ra đã chuẩn hoá.
- Nếu một trường cần cho RFM/forecast không có trong dataset nguồn, không tự tạo giá trị giả. Phải thống nhất cách suy dẫn có căn cứ hoặc ghi rõ tính năng/phân tích nào không áp dụng được.
- Hàm RFM trả về tối thiểu: `Customer ID`, `Recency`, `Frequency`, `Monetary`, `R_score`, `F_score`, `M_score`, `RFM_Score`, `Segment`.
- Hàm forecast cần trả về dữ liệu theo tháng cho actual/test prediction/future prediction và dictionary metric.
- Gửi nội dung insight ngắn, có thể hiển thị dưới biểu đồ: tiêu đề, phát hiện, khuyến nghị.

Khi thay đổi schema đầu vào hoặc cách chuẩn hoá, phải kiểm tra lại `data_cleaning.py`, `shared_data.py`, `rfm_utils.py`, phần forecast và các biểu đồ/page phụ thuộc trước khi xác nhận bàn giao.

## Tiêu chí hoàn thành

- RFM ổn định khi chạy với dữ liệu mới và segment có mô tả nghiệp vụ.
- Forecast có time-based validation, metric và biểu đồ dễ đối chiếu.
- Có danh sách insight/kết luận đủ để sử dụng trong dashboard và phần trình bày đồ án.
