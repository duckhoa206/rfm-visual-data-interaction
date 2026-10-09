# Phân công Dữ liệu và EDA

**Phụ trách:** Nguyễn Văn Xuân An

## Công việc

- Kiểm tra nguồn dữ liệu và giấy phép sử dụng.
- Làm sạch tên cột, ngày tháng, giá trị thiếu và dữ liệu trùng.
- Chuẩn hóa các cột cần cho Dashboard.
- Tạo các bảng trong `data/processed/`.
- Kiểm tra số dòng, khoảng thời gian và các cột bắt buộc.

## Luồng xử lý

```text
data/raw/ → scripts/clean_data.py → data/processed/ → Dashboard
```

Dashboard đọc dữ liệu đã xử lý, không đọc trực tiếp từng file trong `data/raw/`.

## Các bảng chính

| Bảng | Nội dung |
|---|---|
| `orders_enriched.csv` | Đơn hàng bán lẻ, có thêm nguồn dữ liệu và quản lý khu vực |
| `rfm_customers.csv` | Điểm RFM và phân khúc khách hàng |
| `monthly_sales.csv` | Doanh thu tổng hợp theo tháng |
| `walmart_weekly_enriched.csv` | Doanh số Walmart theo tuần đã nối thông tin cửa hàng và kinh tế |
| `bigmart_cleaned.csv` | Sản phẩm và điểm bán BigMart đã chuẩn hóa |

## Lệnh sử dụng

```cmd
python scripts\clean_data.py
```

Không sửa tay các file đầu ra. Nếu thay đổi nguồn hoặc cách làm sạch, cần chạy lại pipeline và kiểm tra Dashboard.
