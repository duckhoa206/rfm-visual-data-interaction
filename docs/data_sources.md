# Nguồn dữ liệu

Dữ liệu gốc nằm trong `data/raw/`. Dữ liệu sau khi làm sạch nằm trong `data/processed/`. Có thể tạo lại dữ liệu bằng lệnh:

```cmd
python scripts\clean_data.py
```

## Các nguồn dùng cho Dashboard

| Nguồn | Thời gian | Mục đích |
|---|---:|---|
| Global Superstore | 2012–2015 | Đơn hàng bán lẻ quốc tế |
| Superstore | 2015–2018 | Bổ sung dữ liệu bán hàng |
| Global Electronics Retail trên Kaggle | 2019–2020 | Dữ liệu tham khảo/demo |
| Superstore | 2021–2024 | Dữ liệu bán hàng Mỹ và Canada |
| Walmart | Theo tuần | Doanh số, cửa hàng và biến kinh tế |
| BigMart | Không có thời gian | Sản phẩm và điểm bán FMCG |

## Giới hạn dữ liệu

Nguồn Kaggle 2019–2020 có đủ các cột cần cho Dashboard nhưng chưa xác minh được nguồn giao dịch gốc. Vì vậy, không nên trình bày nguồn này như số liệu thực tế đã được kiểm toán.

Trong Dashboard, nguồn này được đánh dấu là `demo, unverified`. Khi cần phân tích số liệu đáng tin cậy hơn, nên ưu tiên các nguồn Superstore.

## Quy tắc sử dụng

- Không sửa trực tiếp các file trong `data/processed/`; hãy chạy lại pipeline.
- Khi thêm nguồn mới, cần ghi tên nguồn, thời gian, giấy phép và giới hạn dữ liệu.
- Các nguồn Walmart và BigMart khác loại dữ liệu với bảng đơn hàng nên được phân tích ở trang riêng, không gộp vào bảng bán hàng chính.
