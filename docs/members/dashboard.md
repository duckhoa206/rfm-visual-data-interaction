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
src/dash_app/config.py         PAGE_META: thêm/xóa/đổi tên/đổi thứ tự trang ở 1 chỗ
src/dash_app/shared_data.py    ORDERS/RFM/FILTER_OPTIONS tải 1 lần, mọi trang import
src/dash_app/pages/overview.py Trang chính /: KPI + bar/line + bảng RFM (gộp, không tiêu đề thừa)
src/dash_app/pages/geo.py      Trang phụ /geo: choropleth / treemap / heatmap (chọn 1)
src/dash_app/pages/rfm.py      Trang phụ /rfm: pie / scatter / box (chọn 1)
src/dash_app/pages/forecast.py Trang phụ /forecast: thực tế + dự báo 3 tháng
src/dash_app/components/       header.py, sidebar.py, filters.py, charts.py
assets/style.css               Style duy nhất của dashboard
```

Mỗi trang đăng ký bằng `dash.register_page(__name__, **PAGE_META["<key>"])`. Bộ lọc ở header lưu vào `dcc.Store(id="filter-store")`; mọi trang đọc store này nên chuyển trang không reset. Không đọc trực tiếp file trong `data/raw/` từ bất kỳ trang nào.

## Input và output

### Input

- Fact duy nhất `data/processed/cleaned_data.csv` (UNION 2012–2024, schema 10 cột) qua `shared_data.py`; RFM tính 1 lần bằng `src/shared/rfm_utils.py`.
- `data_service.apply_filters()`: dữ liệu sau filter khu vực, quốc gia, thời gian và segment.

### Output hiện có (10 visual)

- [x] Trang chính: 4 thẻ KPI, bar doanh thu theo danh mục, line xu hướng theo tháng, bảng chi tiết RFM (sort/filter native).
- [x] Trang địa lý: choropleth theo quốc gia, treemap Region/Country/Category, heatmap Region × Category.
- [x] Trang RFM: pie tỷ trọng segment, scatter Frequency–Monetary, box phân phối Monetary.
- [x] Trang dự báo: line thực tế + dự báo 3 tháng (Linear Regression) kèm chú thích xu hướng/tháng.
- [x] Trạng thái rỗng cho mọi biểu đồ + panel phạm vi (số đơn/khách sau filter).

## Việc cần hoàn thiện

- [ ] Thêm visual thứ 11 cho trang dự báo để không lặp line chart (gợi ý: top 10 sản phẩm horizontal bar hoặc histogram giá trị đơn hàng).
- [ ] Cân nhắc drill-down/cross-filtering nếu phù hợp tiến độ.
- [ ] Tích hợp và kiểm tra hiển thị khi nhận metric/insight chính thức từ Insight & Forecast.

## Quy tắc tích hợp

- Chỉ đọc dữ liệu đã làm sạch qua `shared_data.py`; không tự quy ước schema khác trong trang.
- Không viết lại công thức RFM hoặc thuật toán dự báo trong trang; biểu đồ mới phải gọi hàm trong `components/charts.py`.
- Khi thêm biểu đồ, xử lý DataFrame rỗng và giữ dark theme qua `apply_chart_theme()`.
- Thống nhất với Data/Insight trước khi đổi cách hiển thị khi schema thay đổi; không giả định mọi tính năng vẫn áp dụng được.
- Mỗi thay đổi nên có commit riêng, ví dụ: `feat(dashboard): thêm biểu đồ top sản phẩm`.
