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
| Nguyễn Văn Xuân An | 24133002 | [eda](docs/members/eda.md) | Data pipeline, EDA |


## Cấu trúc dự án

```text
rfm-visual-data-interaction/
├── data/
│   ├── raw/                 # Dữ liệu đầu vào (xem docs/data_sources.md)
│   └── processed/
│       ├── orders_enriched.csv         # Core 1: Đơn hàng UNION 4 nguồn + LEFT JOIN People (Manager)
│       ├── walmart_weekly_enriched.csv # Core 2: Star-Schema kết nối chuỗi siêu thị và biến vĩ mô
│       ├── bigmart_cleaned.csv         # Core 3: Merchandising 8.523 mặt hàng và phân loại điểm bán
│       ├── rfm_customers.csv           # Cache điểm số và phân khúc RFM khách hàng
│       └── monthly_sales.csv           # Chuỗi thời gian tổng hợp phục vụ dự báo
├── scripts/
│   └── clean_data.py        # Full pipeline: làm sạch + JOIN toàn bộ bảng
├── src/
│   ├── dash_app/
│   │   ├── app.py           # Khung chung: header (logo + bộ lọc) + sidebar + page_container
│   │   ├── config.py        # Bảng PAGE_META: cấu hình 6 trang dashboard
│   │   ├── shared_data.py   # ORDERS/RFM/WALMART/BIGMART tải 1 lần tập trung có cache
│   │   ├── pages/           # overview.py, geo.py, rfm.py, forecast.py, walmart.py, bigmart.py
│   │   └── components/      # sidebar.py, filters.py, charts.py
│   └── shared/              # data_cleaning, data_service, rfm_utils, theme, forecasting
├── assets/
│   └── style.css            # Toàn bộ màu sắc/font/kích thước sửa ở 1 nơi
├── docs/
│   ├── data_sources.md      # Nguồn dữ liệu, license và giới hạn
│   └── members/             # dashboard.md (Khoa), eda.md (An), insight_forecast.md (Duy)
├── requirements.txt
└── README.md
```

## Luồng dữ liệu & 3 Mô hình Trung tâm

```text
data/raw/*.csv → scripts/clean_data.py → 3 Core Datamarts (data/processed/) → Dash Dashboard (6 Trang)
```

- **Mô hình 1 (Bán lẻ Đa kênh & RFM):** UNION 4 nguồn Superstore (2012–2024) LEFT JOIN People theo Region → `orders_enriched.csv` (có cột `Manager`), phục vụ các trang *Tổng quan*, *Địa lý*, *Phân khúc RFM* và *Dự báo chiến lược 2030*.
- **Mô hình 2 (Chuỗi Siêu thị & Kinh tế Vĩ mô):** Walmart train LEFT JOIN features theo (Store, Date) + LEFT JOIN stores → `walmart_weekly_enriched.csv` (421.570 dòng), phục vụ trang *Chuỗi siêu thị Walmart*.
- **Mô hình 3 (Trưng bày & Điểm bán FMCG):** 8.523 mặt hàng chuẩn hóa thuộc tính và phân loại điểm bán → `bigmart_cleaned.csv`, phục vụ trang *Trưng bày FMCG BigMart*.

Dashboard tải dữ liệu tập trung qua `src/dash_app/shared_data.py` kết hợp caching RAM thông minh, không đọc trực tiếp file từ `data/raw/`. Mọi dữ liệu đã xử lý đều có thể tái tạo hoàn toàn bằng một câu lệnh `python scripts/clean_data.py`.

## Cài đặt và chạy dự án

Cài đặt môi trường ảo của Python cho dự án:
Thực hiện tại thư mục gốc của dự án (chạy 1 lần).

```cmd
py -3.12 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```
Dữ liệu đầu vào và các bảng đã xử lý được lưu riêng trong `data/` và quản lý cùng
mã nguồn trên GitHub. Chạy pipeline để tái tạo dữ liệu processed, sau đó chạy
dashboard Hub-and-Spoke:

```cmd
python scripts\clean_data.py
python src\dash_app\app.py
```

Mở địa chỉ Local URL mà Dash hiển thị, thường là `http://127.0.0.1:8050`.

## Sử dụng dữ liệu

1. Đặt file dữ liệu nguồn vào `data/raw/` (và ghi nguồn/license/giới hạn vào `docs/data_sources.md`).
2. Chạy pipeline làm sạch + JOIN toàn bộ bảng, ví dụ:

```cmd
python scripts\clean_data.py
```

3. Làm mới dashboard. File `data/processed/cleaned_data.csv` sẽ được cập nhật và là nguồn duy nhất dashboard sử dụng (qua `src/dash_app/shared_data.py`).

Dataset nguồn không bắt buộc phải có đúng tên hoặc đúng thứ tự các cột của dữ liệu mẫu. Pipeline ánh xạ schema nghiệp vụ gồm `Order ID`, `Order Date`, `Customer ID`, `Country`, `Region`, `Category`, `Sub-Category`, `Sales`, `Quantity`, `Profit`, đồng thời gắn `Data Source` làm provenance. Nếu dataset thiếu trường hoặc thay đổi ý nghĩa, hãy cập nhật pipeline/các phần liên quan; không tự tạo giá trị để giữ dashboard chạy.

## Các trang dashboard (Hub-and-Spoke)

Header cố định dùng chung mọi trang: khung logo + khung bộ lọc (lưu vào `dcc.Store`,
chuyển trang không reset). Sidebar dọc bên trái (icon + tên, highlight trang hiện tại,
nút ☰ thu gọn/mở rộng), nội dung bên phải:

- **Tổng quan** (`/`): KPI doanh thu/lợi nhuận/đơn hàng/khách hàng, doanh thu theo
  danh mục, xu hướng theo tháng và bảng chi tiết RFM (gộp, không tiêu đề thừa).
- **Phân tích địa lý** (`/geo`): bản đồ choropleth / treemap / heatmap (chọn 1).
- **Phân khúc RFM** (`/rfm`): tỷ trọng phân khúc / scatter Frequency–Monetary / box plot.
- **Dự báo** (`/forecast`): doanh thu thực tế + dự báo 3 tháng (hồi quy tuyến tính).

Tất cả trang dùng chung bộ lọc khu vực, quốc gia, thời gian, phân khúc RFM và nguồn dữ liệu.

## Cách thêm một trang mới

1. Copy `src/dash_app/pages/geo.py` thành file mới trong `src/dash_app/pages/`.
2. Thêm 1 dòng vào `PAGE_META` trong `src/dash_app/config.py` (`path`, `name`, `icon`, `order`).
3. Trong file mới, đổi `register_page(__name__, **PAGE_META["<key-mới>"])` và viết `layout()` từ hàm có sẵn trong `src/dash_app/components/charts.py`.
4. Nếu cần biểu đồ mới, thêm hàm dựng vào `charts.py` (đừng code figure trong trang) rồi import vào trang.
5. Chạy `python src\dash_app\app.py`, mở trang mới trên sidebar và kiểm tra bộ lọc chung còn giữ nguyên khi chuyển trang.

## Quy tắc dữ liệu (bắt buộc)

- Dữ liệu được tách trong `data/raw/` (nguồn) và `data/processed/` (đầu ra pipeline),
  có thể thêm và chia sẻ trực tiếp cùng repository trên GitHub; không cần Google Drive.
- Khi thêm dữ liệu, kiểm tra quyền/license và ghi nguồn, giới hạn sử dụng tại
  `docs/data_sources.md`. Mỗi file GitHub thông thường phải nhỏ hơn 100 MB.
- Thành viên mới clone repository là có dữ liệu; chạy
  `python scripts\clean_data.py` để tái tạo và kiểm tra các bảng processed.

## Quy ước làm việc nhóm

- Không commit thư mục `.venv/`, cache Python hoặc dữ liệu nhạy cảm; dùng Git LFS
  hoặc kho lưu trữ phù hợp nếu một file vượt giới hạn GitHub.
- Không tính lại RFM trong `src/dash_app/pages/`; dùng `RFM` từ `src/dash_app/shared_data.py` (tính 1 lần bằng `src/shared/rfm_utils.py`) và hàm dựng hình trong `src/dash_app/components/charts.py`.
- Mỗi thay đổi chức năng nên được thực hiện có commit riêng, có mô tả rõ ràng.
- Cập nhật tài liệu nhiệm vụ tương ứng trong `docs/members/` khi mở rộng dashboard.

> Thông tin phân công chi tiết được cập nhật trong thư mục `docs/members/`.
