# Phân công Dashboard Hub-and-Spoke (Dash)

**Phụ trách:** Phạm Đức Khoa
**Mục tiêu:** khung Hub-and-Spoke (sidebar + nhiều trang), header dùng chung (logo + bộ lọc), tích hợp đầu ra do phần Data và Insight & Forecast bàn giao. Chạy: `python src\dash_app\app.py` → `http://127.0.0.1:8050`.

## Phạm vi phụ trách

- Khung chung trong `src/dash_app/app.py`: hàng header (logo + bộ lọc) + sidebar + `dash.page_container`.
- Sidebar tự sinh từ `dash.page_registry` (`src/dash_app/components/sidebar.py`): icon + tên mục, highlight trang hiện tại, nút ☰ thu gọn/mở rộng.
- 4 trang trong `src/dash_app/pages/`, mỗi trang tự chứa `layout()` + callback, chỉ đọc dữ liệu qua `src/dash_app/shared_data.py`.
- Hàm dựng biểu đồ/KPI dùng chung trong `src/dash_app/components/charts.py`; toàn bộ màu/font/kích thước trong `assets/style.css`.
- Không sở hữu logic làm sạch dữ liệu, công thức RFM hay thuật toán dự báo.

## Kiến trúc cần tuân thủ

```text
src/dash_app/app.py            Khung chung: header + sidebar + page_container
src/dash_app/config.py         PAGE_META: cấu hình 6 trang (overview, geo, rfm, forecast, walmart, bigmart)
src/dash_app/shared_data.py    ORDERS/RFM/WALMART/BIGMART tải tập trung có cache, mọi trang import
src/dash_app/pages/overview.py Trang chính /: KPI + bar danh mục + line tháng + bar Manager + bảng RFM
src/dash_app/pages/geo.py      Trang phụ /geo: choropleth map + treemap phân cấp + heatmap
src/dash_app/pages/rfm.py      Trang phụ /rfm: scatter F×M + pie tỷ trọng + box phân phối + bảng hành động
src/dash_app/pages/forecast.py Trang phụ /forecast: KPI 2030 + 3 kịch bản + cơ cấu Category/Region + Sản lượng/Lợi nhuận
src/dash_app/pages/walmart.py  Trang chuyên đề /walmart: KPI + tương quan vĩ mô + holiday lift + store size + markdown
src/dash_app/pages/bigmart.py  Trang chuyên đề /bigmart: KPI + giá MRP vs sales + outlet tier + category MRP + visibility
src/dash_app/components/       sidebar.py, filters.py, charts.py
assets/style.css               Style duy nhất của dashboard
```

Mỗi trang đăng ký bằng `dash.register_page(__name__, **PAGE_META["<key>"])`. Bộ lọc ở header lưu vào `dcc.Store(id="filter-store")`; các trang bán lẻ đọc store này nên chuyển trang không reset. Bộ lọc gồm khu vực, quốc gia, thời gian, segment và `Data Source`; nguồn Kaggle 2019–2020 có cảnh báo provenance demo/unverified. Các trang chuyên đề Walmart và BigMart có bộ lọc cục bộ theo phân loại và cấp đô thị.

## Input và output

### Input (3 Mô hình Nghiệp vụ Trung tâm)

- **Core 1 - Bán lẻ Đa kênh & RFM:** `data/processed/orders_enriched.csv` (UNION 2012–2024 LEFT JOIN People để có cột `Manager`), kèm `rfm_customers.csv` tải trực tiếp với cache RAM; lọc qua `data_service.apply_filters()`.
- **Core 2 - Chuỗi Siêu thị & Vĩ mô:** `data/processed/walmart_weekly_enriched.csv` (Star-schema 421.570 dòng kết nối tuần bán với biến vĩ mô, khuyến mãi và đặc trưng siêu thị).
- **Core 3 - Trưng bày & Điểm bán FMCG:** `data/processed/bigmart_cleaned.csv` (8.523 mặt hàng đã chuẩn hóa thuộc tính và phân loại điểm bán).

### Output hoàn thiện (20 visuals trực quan, đa chiều)

- [x] **Trang Tổng quan (5 visual):** 4 thẻ KPI điều hành, Bar doanh thu theo danh mục, Line xu hướng theo tháng, Bar kép Hiệu suất Quản lý khu vực (Manager Performance), Bảng dữ liệu RFM chi tiết.
- [x] **Trang Địa lý (3 visual):** Choropleth bản đồ thế giới, Treemap phân cấp 3 tầng (Region → Country → Category), Heatmap ma trận Khu vực × Danh mục.
- [x] **Trang Phân khúc RFM (3 visual + bảng hành động):** Donut chart tỷ trọng 6 segment, Scatter bong bóng Frequency × Monetary (kèm hover Manager), Box plot phân phối Monetary, Bảng khuyến nghị hành động CRM.
- [x] **Trang Dự báo Chiến lược 2030 (5 visual + kịch bản):** 4 thẻ KPI dự phóng, Line đa kịch bản (Cơ sở, Lạc quan, Thận trọng) kèm dải tin cậy và điểm kiểm thử Test MAE/RMSE, Stacked bar dự phóng theo Danh mục, Grouped bar so sánh Khu vực trọng điểm, Dual-axis bar/line Nhu cầu Sản lượng & Lợi nhuận ròng.
- [x] **Trang Chuỗi Siêu thị Walmart (4 visual + KPI):** 4 thẻ KPI chuỗi, Correlation Heatmap ma trận vĩ mô (Xăng, CPI, Thất nghiệp, Nhiệt độ), Grouped Bar đo lường sức bật ngày lễ (Holiday Lift theo Loại A/B/C), Scatter Bubble quy mô Diện tích (sqft) vs Doanh số tuần, Bar quy mô 5 chương trình chiết khấu MarkDown 1–5.
- [x] **Trang Trưng bày Hàng hóa BigMart (4 visual + KPI):** 4 thẻ KPI điểm bán, Scatter tương quan Giá niêm yết (Item_MRP) vs Doanh số, Grouped Bar hiệu quả theo Cấp đô thị (Tier 1–3) và loại hình cửa hàng, Box plot phổ giá theo Nhóm hàng FMCG, Scatter bóc tách nghịch lý Trưng bày quầy kệ (Item_Visibility vs Sales).

## Đánh giá hoàn thiện nhiệm vụ

- [x] Đã nâng cấp toàn diện visual cho trang dự báo với kịch bản dài hạn 2030 và phân tích mùa vụ.
- [x] Đã kết nối cột `Manager` từ People vào trang Tổng quan để hiển thị hiệu suất lãnh đạo vùng.
- [x] Đã khai thác 100% dữ liệu đã nối (Walmart Star-Schema và BigMart Merchandising) thành 2 trang chuyên đề trực quan.
- [x] Đã tối ưu hiệu năng tải dữ liệu thông qua cơ chế đọc trực tiếp bảng RFM cache và LRU cache.
