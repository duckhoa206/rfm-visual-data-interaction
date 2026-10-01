# Phân tích hiệu suất bán hàng và phân khúc khách hàng (RFM)

Đồ án **Tương tác dữ liệu trực quan** trong lĩnh vực bán lẻ. Dự án xây dựng dashboard tương tác để theo dõi hiệu suất bán hàng của hệ thống siêu thị đa quốc gia, phân tích hành vi khách hàng theo mô hình RFM và minh hoạ xu hướng doanh thu.

## Mục tiêu

- Theo dõi doanh thu, lợi nhuận và số đơn hàng theo thời gian, danh mục và khu vực.
- Phân tích phân bố doanh thu theo địa lý bằng bản đồ tương tác.
- Phân khúc khách hàng bằng **RFM**: Recency, Frequency và Monetary.
- Hỗ trợ nhận diện nhóm khách hàng giá trị cao, khách hàng mới và nhóm có nguy cơ rời bỏ.
- Dự báo doanh thu ngắn hạn bằng mô hình Linear Regression (phiên bản demo).

## Công nghệ sử dụng

- Python 3.12+, Dash + dash-bootstrap-components
- Pandas, NumPy: xử lý dữ liệu
- Plotly: biểu đồ và bản đồ tương tác
- Scikit-learn: mô hình dự báo

## Bảng phân công

| Thành viên | MSSV | Hướng dẫn | Phụ trách |
| --- | --- | --- | --- |
| Phạm Đức Khoa | 24149170 | [dashboard](docs/members/dashboard.md) | Dashboard Hub-and-Spoke, liên kết các phần |
| Phạm Quốc Duy | 24133008 | [insight_forecast](docs/members/insight_forecast.md) | RFM, insight, dự báo |
| Nguyễn Văn Xuân An | 24133002 | [data](docs/members/data.md) | Data pipeline, EDA |


## Cấu trúc dự án

```text
rfm-visual-data-interaction/
├── data/
│   ├── raw/                 # Dữ liệu đầu vào (xem data/raw/SOURCES.md)
│   └── processed/
│       ├── cleaned_data.csv # Fact duy nhất dashboard đọc (UNION 2012–2024)
│       ├── orders_enriched.csv, walmart_weekly_enriched.csv,
│       ├── bigmart_cleaned.csv, people_cleaned.csv,  # Bảng JOIN minh hoạ
│       └── rfm_customers.csv, monthly_sales.csv      # Bảng giao Insight & Forecast
├── scripts/
│   └── clean_data.py        # Full pipeline: làm sạch + JOIN toàn bộ bảng
├── src/
│   ├── dash_app/
│   │   ├── app.py           # Khung chung: header (logo + bộ lọc) + sidebar + page_container
│   │   ├── config.py        # Bảng PAGE_META: thêm/xóa/đổi tên/đổi thứ tự trang ở 1 chỗ
│   │   ├── shared_data.py   # ORDERS/RFM/FILTER_OPTIONS tải 1 lần, mọi trang import
│   │   ├── pages/           # overview.py (/) + geo.py, rfm.py, forecast.py
│   │   └── components/      # header.py, sidebar.py, filters.py, charts.py
│   └── shared/              # data_cleaning, data_service, rfm_utils, theme
├── assets/
│   └── style.css            # Toàn bộ màu sắc/font/kích thước sửa ở 1 nơi
├── docs/
│   └── members/             # dashboard.md (Khoa), data.md (An), insight_forecast.md (Duy)
├── requirements.txt
└── README.md
```

## Luồng dữ liệu

```text
data/raw/*.csv → scripts/clean_data.py → data/processed/*.csv → Dash dashboard
```

- Fact chính: `global_superstore_orders.csv` (2012–2015) UNION
  `superstore_2015_2018.csv` (2015–2018, lấp 2016-2018) UNION
  `superstore_2021_2024.csv` (2021–2024, gần 2026 nhất) → `cleaned_data.csv`
  (71.391 dòng, schema 10 cột, 2012-01-01 → 2024-12-30, chỉ còn trống 2019–2020).
- JOIN minh hoạ: đơn hàng LEFT JOIN People theo Region (`orders_enriched.csv`);
  Walmart train LEFT JOIN features theo (Store, Date) + LEFT JOIN stores
  (`walmart_weekly_enriched.csv`); BigMart làm sạch đơn bảng (`bigmart_cleaned.csv`).
- Chi tiết nguồn, EDA và tỷ lệ khớp JOIN xem `data/raw/SOURCES.md`.

Dashboard chỉ đọc `data/processed/cleaned_data.csv` (qua `src/dash_app/shared_data.py`), không đọc trực tiếp `data/raw/`. Khi thay dữ liệu thật và schema vẫn đúng hợp đồng dữ liệu, chỉ cần chạy lại pipeline. Nếu schema khác dữ liệu mẫu, cần cập nhật pipeline/các phần liên quan trước khi làm mới dashboard.

`data/processed/` là thư mục output trung gian và là nguồn dữ liệu duy nhất được bàn giao cho Dashboard, RFM và Forecast. Không sửa trực tiếp `cleaned_data.csv`; mọi thay đổi phải bắt đầu từ file trong `data/raw/` và được tạo lại bằng pipeline.

## Cài đặt và chạy dự án

Cài đặt môi trường ảo của Python cho dự án:
Thực hiện tại thư mục gốc của dự án (chạy 1 lần).

```cmd
py -3.12 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```
Lấy dữ liệu từ link Drive (mục “Quy tắc dữ liệu”), giải nén đúng cấu trúc `data/`,
làm sạch toàn bộ (UNION + JOIN) và chạy dashboard Hub-and-Spoke:

```cmd
python scripts\clean_data.py
python src\dash_app\app.py
```

Mở địa chỉ Local URL mà Dash hiển thị, thường là `http://127.0.0.1:8050`.

## Sử dụng dữ liệu

1. Đặt file CSV nguồn vào thư mục `data/raw/` (và ghi nguồn vào `data/raw/SOURCES.md`).
2. Chạy pipeline làm sạch + JOIN toàn bộ bảng, ví dụ:

```cmd
python scripts\clean_data.py
```

3. Làm mới dashboard. File `data/processed/cleaned_data.csv` sẽ được cập nhật và là nguồn duy nhất dashboard sử dụng (qua `src/dash_app/shared_data.py`).

Dataset nguồn không bắt buộc phải có đúng tên hoặc đúng thứ tự các cột của dữ liệu mẫu. Pipeline cần ánh xạ được các trường tương đương về schema đầu ra: `Order ID`, `Order Date`, `Customer ID`, `Country`, `Region`, `Category`, `Sub-Category`, `Sales`, `Quantity`, `Profit`. Đây là schema mà các hàm làm sạch, RFM, bộ lọc và biểu đồ hiện đang sử dụng sau khi chuẩn hoá. Nếu dataset thật thiếu trường, khác kiểu dữ liệu hoặc thay đổi ý nghĩa, hãy cập nhật `COLUMN_ALIASES`/pipeline và kiểm tra các phần liên quan; không tự tạo giá trị giả để giữ dashboard chạy.

## Các trang dashboard (Hub-and-Spoke)

Header cố định dùng chung mọi trang: khung logo + khung bộ lọc (lưu vào `dcc.Store`,
chuyển trang không reset). Sidebar dọc bên trái (icon + tên, highlight trang hiện tại,
nút ☰ thu gọn/mở rộng), nội dung bên phải:

- **Tổng quan** (`/`): KPI doanh thu/lợi nhuận/đơn hàng/khách hàng, doanh thu theo
  danh mục, xu hướng theo tháng và bảng chi tiết RFM (gộp, không tiêu đề thừa).
- **Phân tích địa lý** (`/geo`): bản đồ choropleth / treemap / heatmap (chọn 1).
- **Phân khúc RFM** (`/rfm`): tỷ trọng phân khúc / scatter Frequency–Monetary / box plot.
- **Dự báo** (`/forecast`): doanh thu thực tế + dự báo 3 tháng (hồi quy tuyến tính).

Tất cả trang dùng chung bộ lọc khu vực, quốc gia, thời gian và phân khúc RFM.

## Cách thêm một trang mới

1. Copy `src/dash_app/pages/geo.py` thành file mới trong `src/dash_app/pages/`.
2. Thêm 1 dòng vào `PAGE_META` trong `src/dash_app/config.py` (`path`, `name`, `icon`, `order`).
3. Trong file mới, đổi `register_page(__name__, **PAGE_META["<key-mới>"])` và viết `layout()` từ hàm có sẵn trong `src/dash_app/components/charts.py`.
4. Nếu cần biểu đồ mới, thêm hàm dựng vào `charts.py` (đừng code figure trong trang) rồi import vào trang.
5. Chạy `python src\dash_app\app.py`, mở trang mới trên sidebar và kiểm tra bộ lọc chung còn giữ nguyên khi chuyển trang.

## Quy tắc dữ liệu (bắt buộc)

- **Không commit/push bất kỳ file dữ liệu nào lên origin** (`data/` đã bị ignore toàn bộ).
- Dữ liệu `data/raw/` và `data/processed/` được các thành viên trao đổi với nhau
  **qua link Google Drive** (link Drive sẽ cập nhật tại đây):
  - 👉 Drive data: _(TODO: dán link Drive dùng chung tại đây)_
- Thành viên mới: tải data từ Drive về đúng cấu trúc `data/raw/`, `data/processed/`,
  sau đó chạy `python scripts\clean_data.py` để tái tạo và kiểm tra pipeline.

## Quy ước làm việc nhóm

- Không commit thư mục `.venv/`, cache Python hoặc file dữ liệu nhạy cảm/lớn.
- Không tính lại RFM trong `src/dash_app/pages/`; dùng `RFM` từ `src/dash_app/shared_data.py` (tính 1 lần bằng `src/shared/rfm_utils.py`) và hàm dựng hình trong `src/dash_app/components/charts.py`.
- Mỗi thay đổi chức năng nên được thực hiện có commit riêng, có mô tả rõ ràng.
- Cập nhật tài liệu nhiệm vụ tương ứng trong `docs/members/` khi mở rộng dashboard.

> Thông tin phân công chi tiết được cập nhật trong thư mục `docs/members/`.
