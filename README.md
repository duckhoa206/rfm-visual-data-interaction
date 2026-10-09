# Dashboard phân tích bán hàng và khách hàng RFM

Đồ án xây dựng Dashboard tương tác cho dữ liệu bán hàng. Người dùng có thể xem doanh thu, lợi nhuận, khu vực bán hàng, phân khúc khách hàng và dự báo doanh thu.

## Chức năng chính

- **Tổng quan:** KPI, doanh thu theo danh mục, xu hướng theo tháng và hiệu suất quản lý.
- **Địa lý:** bản đồ doanh thu, treemap và heatmap theo khu vực/danh mục.
- **Phân khúc RFM:** phân loại khách hàng theo lần mua gần nhất, số lần mua và số tiền đã chi.
- **Dự báo:** dự báo 3 năm, 5 năm hoặc 10 năm theo các kịch bản cơ sở, lạc quan và thận trọng.
- **Walmart:** phân tích doanh số theo tuần, ngày lễ, cửa hàng và biến kinh tế.
- **BigMart:** phân tích sản phẩm, giá bán, trưng bày và loại cửa hàng.

## Dữ liệu

Dashboard sử dụng ba nhóm dữ liệu:

1. Dữ liệu đơn hàng Superstore giai đoạn 2012–2024.
2. Dữ liệu Walmart theo cửa hàng và tuần.
3. Dữ liệu sản phẩm và điểm bán BigMart.

Dữ liệu được làm sạch và lưu trong `data/processed/`. Thông tin nguồn và giới hạn dữ liệu xem tại [docs/data_sources.md](docs/data_sources.md).

## Công nghệ

- Python
- Dash và dash-bootstrap-components
- Pandas, NumPy
- Plotly
- Scikit-learn

## Cài đặt và chạy

```cmd
py -3.12 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python scripts\clean_data.py
python src\dash_app\app.py
```

Mở địa chỉ `http://127.0.0.1:8050` trên trình duyệt.

## Cấu trúc thư mục

```text
data/raw/          Dữ liệu gốc và thông tin nguồn
data/processed/    Dữ liệu đã làm sạch cho Dashboard
scripts/           Lệnh xử lý dữ liệu
src/dash_app/      Giao diện và các trang Dashboard
src/shared/        Logic dùng chung: làm sạch, RFM, dự báo
assets/             CSS và hình ảnh giao diện
docs/               Tài liệu nguồn dữ liệu và phân công
```

## Phân công

- **Phạm Đức Khoa:** giao diện và Dashboard.
- **Phạm Quốc Duy:** RFM, insight và dự báo.
- **Nguyễn Văn Xuân An:** dữ liệu và EDA.

## Lưu ý

- Nguồn Kaggle Global Electronics Retail 2019–2020 chưa xác minh được nguồn giao dịch gốc, nên chỉ dùng như dữ liệu tham khảo/demo.
- File `forecast_output.html` là kết quả tạo thêm khi chạy thử mô hình, không phải file cần thiết để chạy Dashboard.
