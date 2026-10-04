# Phân công Insight, RFM và Forecast

**Phụ trách: Phạm Quốc Duy**
**Mục tiêu:** huấn luyện và đánh giá mô hình dự báo doanh thu hoặc nhu cầu thị trường từ dữ liệu đã xử lý; bàn giao các biểu đồ dự báo để đưa lên dashboard.

## Phạm vi sở hữu

```text
src/shared/rfm_utils.py            Công thức RFM, score và segment (duy nhất)
src/dash_app/components/charts.py  build_rfm_figure() + build_forecast_figure() dùng chung
src/dash_app/pages/rfm.py          Trang /rfm (pie / scatter / box)
src/dash_app/pages/forecast.py     Trang /forecast (thực tế + dự báo 3 tháng)
docs/members/insight_forecast.md   Theo dõi giả định, metric và insight
```

Input đơn hàng luôn đi qua `src/dash_app/shared_data.py`, đọc từ `data/processed/cleaned_data.csv` (UNION 2012–2024, có `Data Source`). Nguồn Kaggle 2019–2020 chưa xác minh provenance; dùng bộ lọc nguồn để tách khỏi các nguồn khác và nêu giới hạn khi báo cáo. Không thay đổi cách làm sạch trong `data_cleaning.py` nếu chưa trao đổi với Data. Không chỉnh khung sidebar/filter chung nếu chưa trao đổi với Dashboard. Nếu dataset thiếu, đổi tên, đổi kiểu hoặc đổi ý nghĩa trường, phối hợp với Data và Dashboard kiểm tra/cập nhật logic RFM, insight và forecast liên quan.

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
| Dự báo`/forecast` | Line thực tế + dự báo 3 tháng (Linear Regression trên chỉ số tháng lịch; bỏ qua tháng không có giao dịch) | `build_forecast_figure` |

RFM: snapshot = ngày đơn hàng mới nhất + 1 ngày; Recency tính bằng ngày, Frequency = số Order ID, Monetary = tổng Sales. Khi có `Data Source`, cohort RFM được tính riêng theo Customer ID × nguồn để tránh trộn khách giữa các nguồn.

## Kế hoạch dự báo

- [ ] Chọn mục tiêu dự báo: doanh thu tổng, doanh thu theo quốc gia/khu vực, hoặc nhu cầu từng thị trường. Dùng `Sales` làm giá trị doanh thu và `Quantity` làm đại diện nhu cầu; tổng hợp theo tháng và theo thị trường từ dữ liệu trong `data/processed/`.
- [ ] Dùng `monthly_sales.csv` cho dự báo doanh thu tổng; file này có grain Data Source × Month và chỉ chứa các tháng có giao dịch, không tự điền doanh thu 0. Dùng `cleaned_data.csv` để tổng hợp theo Country/Region. Nếu phân tích theo châu lục, bổ sung mapping Country → Continent có nguồn và quy tắc rõ ràng.
- [ ] Chia dữ liệu theo thời gian: train/test và báo cáo kết quả theo nguồn. Nếu mục tiêu là đánh giá dự báo trên dữ liệu đã kiểm chứng, loại trừ hoặc đánh giá riêng nguồn Kaggle demo/unverified 2019–2020.
- [ ] Đánh giá dự báo trên 2021–2024 bằng MAE và RMSE; tạo biểu đồ đối chiếu doanh thu thực tế với dự báo trong giai đoạn test.
- [ ] Sau khi chọn mô hình và cấu hình, huấn luyện trên nguồn phù hợp với mục tiêu; không gộp nguồn demo/unverified như dữ liệu lịch sử thực nếu chưa có xác minh độc lập. Nêu rõ giả định và giới hạn của dự báo.
- [ ] Bàn giao cho Dashboard các biểu đồ: thực tế so với dự báo 2021–2024; dự báo 2025–2050; và biểu đồ theo quốc gia/khu vực/châu lục nếu mục tiêu thị trường được chọn.
