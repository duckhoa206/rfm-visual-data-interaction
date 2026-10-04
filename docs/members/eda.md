# Phân công Data Pipeline + EDA

**Phụ trách:** Nguyễn Văn Xuân An
**Mục tiêu:** thu thập, kiểm tra (EDA) và làm sạch dữ liệu bán hàng để tạo nguồn đáng tin cậy cho dashboard và RFM. Quy tắc nhóm: **không commit/push file dữ liệu lên origin** — data trao đổi qua link Drive (xem README mục “Quy tắc dữ liệu”).

## Phạm vi sở hữu

```text
data/raw/                         Dữ liệu nguồn (chi tiết: docs/data_sources.md)
data/processed/                   Output pipeline; dashboard chỉ đọc từ đây
data/processed/cleaned_data.csv   UNION 4 nguồn, 10 cột nghiệp vụ + Data Source, 2012→2024
scripts/clean_data.py             Điểm chạy full pipeline: làm sạch + JOIN
src/shared/data_cleaning.py       Quy tắc làm sạch, EDA đã chốt và hàm JOIN
src/dash_app/shared_data.py       Loader duy nhất dashboard dùng (không đọc raw)
```

Luồng bàn giao: `data/raw/*.csv → scripts/clean_data.py → data/processed/*.csv → dashboard`. `cleaned_data.csv` tái tạo được, không sửa tay; cột `Data Source` ghi nguồn từng dòng để có thể lọc riêng. Sau khi đổi dataset phải chạy lại pipeline và báo Dashboard/Insight trước khi bàn giao.

## Quá trình cào dữ liệu (2026-10-01)

Xuất phát: Global Superstore 2012–2015 (cũ) + 2 file từng rớt mạng (`walmart_train.csv` bị cắt cụt 11.173 dòng, `bigmart_train.csv` đủ).

1. Tải bù `walmart_train.csv` bản full 12,8MB từ HuggingFace (`large-traversaal/Walmart-sales`) → đủ 421.570 dòng, hết lỗi dòng cuối.
2. Tìm nguồn gần 2026 nhất mà vẫn RFM được: chốt `superstore_2021_2024.csv` (GitHub venunelaturi, 10.194 dòng, 2021-01-03 → 2024-12-30). Các nguồn 2025 (Đức) và 2026 (Ấn Độ) bị loại vì đơn quốc gia và/hoặc thiếu Customer ID.
3. Lấp lỗ 2016–2020: thử `An-j96/SuperstoreData` (trùng ~60% giao dịch với file dưới → loại, tránh double-count), `global-sales-100k` (thiếu Category/Region → loại), Kaggle (cần auth), Scribd (PDF) → chốt `superstore_2015_2018.csv` (GitHub larryt2003, 9.994 dòng, 2015–2018, 0 trùng Order ID/key với Global).
4. Kết quả ban đầu: phủ 2012–2018 + 2021–2024; chưa có nguồn tương thích cho 2019–2020.
5. Ứng viên bổ sung 2019–2020: [Kaggle Global Electronics Retail](https://www.kaggle.com/datasets/faheem113141/global-electronics-retail), license MIT hiển thị trên Kaggle. Đã kiểm tra file 20.281 dòng, 29 cột, 137 quốc gia, 1.541 Customer ID, ngày 2019-01-02 → 2020-12-31; schema đủ 10 trường nghiệp vụ. Trang Kaggle không nêu nguồn giao dịch gốc nên gắn nhãn `demo, unverified`, không xem là số liệu thực đã xác minh. Chi tiết tại [data_sources.md](../data_sources.md).

## Kết quả EDA (số liệu đã chốt)

| Bảng                 | Quy mô / phủ thời gian                                    | Phát hiện chính                                                                                                     | Xử lý                                                                                                                                                         |
| --------------------- | ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Global Orders         | 51.290 dòng, 24 cột, 2012–2015, 165 nước, 17.415 khách | `Postal Code` null 41.296; 0 trùng; Sales<0: 0; Qty≤0: 0                                                           | Bỏ cột ngoài schema; giữ Profit âm (đơn lỗ thật)                                                                                                       |
| Superstore 2015–2018 | 9.994 dòng, 2015–2018, Mỹ                                 | Tên cột`Sales`/`Profit` dính khoảng trắng; 0 trùng với Global                                               | Strip tên cột rồi UNION                                                                                                                                      |
| Superstore 2021–2024 | 10.194 dòng, 2021–2024, Mỹ + Canada 200 dòng, 804 khách | 0 null/trùng; Discount 0–0,8; Profit âm 1.901 dòng                                                                 | Giữ đơn lỗ; alias`Country/Region` → `Country`                                                                                                          |
| Kaggle Global Electronics Retail | 20.281 dòng, 2019–2020, 137 quốc gia, 1.541 khách | 0 thiếu trường schema; 5.016 Profit âm; trang Kaggle không dẫn nguồn giao dịch gốc | Giữ Profit âm; đánh dấu `Data Source` là demo/unverified, không khẳng định tính xác thực |
| Walmart train         | 421.570 dòng, 2010–2012, 45 stores × 81 depts             | 1.285`Weekly_Sales` âm (hoàn tiền)                                                                                | Giữ nguyên, ghi chú                                                                                                                                          |
| Walmart features      | 8.190 = 45×182 tuần, tới 07/2013                          | Markdown null ~50%, CPI/Unemployment null 585 (tuần 2013 ngoài train)                                                | Giữ null; sau JOIN còn 0 null                                                                                                                                 |
| BigMart               | 8.523 dòng, không có cột thời gian                      | `Item_Weight` null 1.463; `Outlet_Size` null 2.410; `Fat_Content` 5 biến thể; `Visibility` = 0 có 526 dòng | Chuẩn hoá 2 giá trị; Visibility 0 → impute theo Item; Weight → impute theo Item; Size → mode theo Outlet_Type; thêm`Outlet_Age` (mốc 2013) → 0 null |
| People                | 24 dòng Region → người phụ trách                       | Tên dính ký tự thay thế encoding (giữ nguyên); khớp 22/23 Region Global                                        | LEFT JOIN, giữ đơn không khớp                                                                                                                              |

## JOIN và output pipeline

- `cleaned_data.csv`: 91.681 dòng = 51.280 Global + 9.928 Superstore 2015–2018 + 20.281 Kaggle demo + 10.192 Superstore 2021–2024; 10 cột nghiệp vụ + `Data Source`. UNION chỉ bỏ trùng khi toàn bộ 10 trường nghiệp vụ giống nhau.
- `orders_enriched.csv` (91.681): UNION LEFT JOIN People ON Region → thêm `Manager`; null khi Region không khớp People vẫn được giữ.
- `walmart_weekly_enriched.csv` (421.570): train LEFT JOIN features ON (Store, Date) + LEFT JOIN stores (star-join).
- `bigmart_cleaned.csv` (8.523) + `people_cleaned.csv` + 3 file Walmart đã chuẩn hoá.

> Biểu đồ/dự báo trên dashboard vẽ từ `cleaned_data.csv`. Các file JOIN ngang là kết quả minh hoạ đã xuất, hiện chưa nối vào visual.

## Các file trong `data/processed/`

| File                             | Nội dung / mục đích                                                                                                                                                                                  |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `cleaned_data.csv`             | Fact dashboard đọc; 91.681 dòng, schema nghiệp vụ 10 cột + `Data Source` để truy nguồn và lọc riêng nguồn demo.                               |
| `orders_enriched.csv`          | Các đơn hàng đã nối thêm`Manager` từ People theo `Region`. Manager có thể null khi Region không khớp; vẫn giữ các đơn đó.                                                        |
| `rfm_customers.csv`            | Bảng RFM 20.553 cohort khách-nguồn có thêm `Data Source`; mỗi Customer ID được tính trong cohort nguồn tương ứng để tránh trộn chỉ số khách giữa nguồn demo và các nguồn khác.                       |
| `monthly_sales.csv`            | Tổng hợp theo `Data Source` × `Month` gồm Sales, Profit, số đơn và số khách; chỉ có tháng thực sự có giao dịch, không tự tạo tháng 0. Khi báo cáo/dự báo cần ghi rõ giới hạn provenance của nguồn Kaggle demo. |
| `people_cleaned.csv`           | Bảng tra cứu`Person` theo `Region`, đã chuẩn hoá; làm dimension để nối người phụ trách vào đơn hàng/RFM.                                                                           |
| `walmart_train_cleaned.csv`    | Doanh số Walmart theo Store × Dept × tuần (`Date`), 421.570 dòng. Có giữ `Weekly_Sales` âm vì có thể là hoàn tiền/điều chỉnh.                                                       |
| `walmart_features_cleaned.csv` | Đặc trưng Walmart theo Store × tuần, gồm thời tiết, giá nhiên liệu, markdown, CPI, thất nghiệp và ngày lễ. Các giá trị thiếu đặc thù được giữ lại.                           |
| `walmart_stores_cleaned.csv`   | Dimension cửa hàng Walmart: 45 cửa hàng với mã`Store`, loại `Type` và quy mô `Size`.                                                                                                      |
| `walmart_weekly_enriched.csv`  | Bảng Walmart đã nối doanh số train với features theo (Store, Date), rồi nối thông tin stores theo Store; dùng phân tích/dự báo doanh số tuần.                                            |
| `bigmart_cleaned.csv`          | Dữ liệu BigMart theo Item × Outlet, 8.523 dòng; đã chuẩn hoá và xử lý giá trị thiếu, có thêm`Outlet_Age`. Dùng phân tích sản phẩm/cửa hàng.                                     |

Các file `_cleaned` là dữ liệu nguồn đã chuẩn hoá; file `_enriched` đã nối thêm bảng liên quan; RFM và doanh thu tháng là các bảng tổng hợp theo grain riêng. Các output được tái tạo bằng `scripts/clean_data.py`, không sửa tay.

## Schema đầu ra bắt buộc (hợp đồng tích hợp)

```text
Order ID, Order Date, Customer ID, Country, Region,
Category, Sub-Category, Sales, Quantity, Profit, Data Source
```

10 cột đầu là schema nghiệp vụ; `Data Source` là metadata provenance do pipeline gắn, không phải giá trị suy diễn từ dữ liệu. Quy ước: `Order Date` parse được; `Sales`/`Quantity`/`Profit` là số, Profit được phép âm; `Sales >= 0`, `Quantity > 0`; một `Order ID` có thể nhiều dòng sản phẩm nên không xoá trùng chỉ theo `Order ID`. Dataset nguồn chỉ cần ánh xạ được về schema nghiệp vụ qua `COLUMN_ALIASES`; thiếu trường không suy dẫn được thì thống nhất giảm tính năng, không tự điền giá trị giả.

## Lệnh sử dụng

```cmd
python scripts\clean_data.py
```

(Tái tạo toàn bộ output. Nguồn, license và giới hạn xem [data_sources.md](../data_sources.md).)

## Tiêu chí hoàn thành

- [X] Dataset ≥ 5.000 dòng/nhiều bảng, có nguồn/license/giới hạn trong [data_sources.md](../data_sources.md).
- [X] EDA + quy tắc làm sạch/JOIN đã chốt (bảng trên).
- [X] Pipeline tái tạo 1 lệnh, dashboard đọc được dữ liệu mới.
- [X] Tìm, kiểm tra schema/độ phủ và tích hợp ứng viên đa quốc gia cho 2019–2020; provenance chưa xác minh nên dữ liệu được gắn nhãn demo/unverified và cảnh báo trên dashboard.
