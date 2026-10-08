# Nguồn dữ liệu

Nguồn đầu vào được lưu trong `data/raw/`. Mọi bảng processed được tái tạo bằng `python scripts/clean_data.py`.	

## Fact bán hàng

| Nguồn                                                                                                     | Khoảng thời gian | Tình trạng/giới hạn                                                                                                                                                                                                                                                                                                                                                                                 |
| ---------------------------------------------------------------------------------------------------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Global Superstore                                                                                          | 2012–2015         | Nguồn đa quốc gia đang có; xem chi tiết kiểm tra EDA tại[members/eda.md](./members/eda.md).                                                                                                                                                                                                                                                                                                      |
| Superstore 2015–2018                                                                                      | 2015–2018         | Nguồn Mỹ, dùng để bổ sung giai đoạn 2016–2018.                                                                                                                                                                                                                                                                                                                                                 |
| [Kaggle: Global Electronics Retail](https://www.kaggle.com/datasets/faheem113141/global-electronics-retail) | 2019–2020         | License Kaggle công bố: MIT. File phát hành`SAC Retailer Dataset.xlsx`; bản kiểm tra có 20.281 dòng, 29 cột, 137 quốc gia và có đủ 10 trường nghiệp vụ cần cho pipeline. Tuy nhiên trang dataset không dẫn nguồn giao dịch gốc; provenance chưa được xác minh. Xem như dữ liệu demo/unverified, không trình bày như số liệu giao dịch thực đã kiểm toán. |
| Superstore 2021–2024                                                                                      | 2021–2024         | Nguồn Mỹ/Canada đang có; xem chi tiết kiểm tra EDA tại[members/eda.md](./members/eda.md).                                                                                                                                                                                                                                                                                                         |

### Kiểm tra nguồn Kaggle 2019–2020

- Tệp gốc: `data/raw/global_electronics_retail_2019_2020.xlsx`; bản CSV dùng cho pipeline: `data/raw/global_electronics_retail_2019_2020.csv`. CSV chỉ chuẩn hóa ngày Excel sang `YYYY-MM-DD`, không thay đổi các trường nghiệp vụ.
- Dải ngày quan sát được: 2019-01-02 đến 2020-12-31; 8.963 dòng thuộc 2019 và 11.318 dòng thuộc 2020.
- Bản tải kiểm tra có 1.541 Customer ID, 9.257 Order ID, 3 Category và 10 Sub-Category; các trường nghiệp vụ không thiếu, Sales không âm và Quantity dương.
- Pipeline giữ đủ 20.281 dòng sau chuẩn hóa; không có bản ghi trùng hoàn toàn theo 10 trường nghiệp vụ.
- Có 5.016 dòng Profit âm; giữ nguyên theo quy tắc pipeline.
- Cột `Data Source` đánh dấu các dòng nguồn này là `Kaggle Global Electronics Retail (demo, unverified)`. Dashboard có bộ lọc nguồn và cảnh báo để có thể tách nguồn này khỏi các nguồn khác.
- Bản dữ liệu được tải từ trang Kaggle ngày 2026-10-04. License MIT là license hiển thị trên Kaggle; cần giữ attribution và không suy diễn provenance mà trang nguồn không cung cấp.

Các số liệu trong bảng này mô tả nội dung tệp đã tải để kiểm tra, không xác nhận tính xác thực của giao dịch hay tính đại diện của các quốc gia. Khi trích dẫn trong báo cáo, phải ghi rõ nguồn Kaggle và trạng thái demo/unverified.
