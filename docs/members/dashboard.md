# Phân công Dashboard

**Phụ trách:** Phạm Đức Khoa

## Công việc

- Xây dựng khung Dash, header, sidebar và bộ lọc chung.
- Kết nối các trang vào `dash.page_container`.
- Giữ bộ lọc khi chuyển trang.
- Dùng các hàm chung trong `src/dash_app/components/charts.py` để tạo biểu đồ.
- Kiểm tra giao diện, kích thước và thao tác tương tác.

## Các trang hiện có

| Trang | Nội dung chính |
|---|---|
| Tổng quan | KPI, doanh thu theo danh mục, xu hướng tháng, quản lý khu vực |
| Địa lý | Bản đồ, treemap, heatmap |
| Phân khúc RFM | Tỷ trọng phân khúc, Frequency–Monetary, box plot, bảng hành động |
| Dự báo | KPI, các kịch bản, dự báo theo ngành hàng/khu vực, sản lượng và lợi nhuận |
| Walmart | Doanh số tuần, ngày lễ, biến kinh tế và cửa hàng |
| BigMart | Giá, trưng bày, sản phẩm và loại điểm bán |

## Luồng dữ liệu giao diện

```text
src/dash_app/app.py
        ↓
header + bộ lọc + sidebar
        ↓
src/dash_app/pages/
        ↓
src/dash_app/shared_data.py
```

Phần làm sạch dữ liệu, công thức RFM và mô hình dự báo nằm ở các module dùng chung; trang giao diện không tự đọc CSV riêng.

## Chạy kiểm tra

```cmd
python src\dash_app\app.py
```

Sau đó mở `http://127.0.0.1:8050` và kiểm tra từng trang, bộ lọc, nút mở rộng biểu đồ và nút đặt lại bộ lọc.
