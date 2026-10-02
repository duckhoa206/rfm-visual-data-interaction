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

## Kế hoạch dự báo

- [ ] Chọn mục tiêu dự báo: doanh thu tổng, doanh thu theo quốc gia/khu vực, hoặc nhu cầu từng thị trường. Dùng `Sales` làm giá trị doanh thu và `Quantity` làm đại diện nhu cầu; tổng hợp theo tháng và theo thị trường từ dữ liệu trong `data/processed/`.
- [ ] Dùng `monthly_sales.csv` cho dự báo doanh thu tổng; dùng `cleaned_data.csv` để tổng hợp theo Country/Region. Nếu phân tích theo châu lục, bổ sung mapping Country → Continent có nguồn và quy tắc rõ ràng.
- [ ] Chia dữ liệu theo thời gian: train trên giai đoạn 2012–2018, test trên 2021–2024. Không dùng các tháng 2019–2020 đang được điền 0 như doanh thu thực để train hoặc đánh giá. (Lưu ý: Cập nhật khi được cào thêm dữ liệu trong các năm bị trống)
- [ ] Đánh giá dự báo trên 2021–2024 bằng MAE và RMSE; tạo biểu đồ đối chiếu doanh thu thực tế với dự báo trong giai đoạn test.
- [ ] Sau khi chọn mô hình và cấu hình, huấn luyện lại trên toàn bộ dữ liệu thực có sẵn (2012–2018 và 2021–2024), loại trừ các tháng 2019–2020 được điền 0; dự báo doanh thu/nhu cầu cho 2025–2050 và nêu rõ giả định/giới hạn của dự báo dài hạn. (Lưu ý: Cập nhật khi được cào thêm dữ liệu trong các năm bị trống)
- [ ] Bàn giao cho Dashboard các biểu đồ: thực tế so với dự báo 2021–2024; dự báo 2025–2050; và biểu đồ theo quốc gia/khu vực/châu lục nếu mục tiêu thị trường được chọn.
