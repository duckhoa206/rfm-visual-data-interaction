# Phân công Data Pipeline + EDA

**Phụ trách:** Nguyễn Văn Xuân An
**Mục tiêu:** thu thập, kiểm tra (EDA) và làm sạch dữ liệu bán hàng để tạo nguồn đáng tin cậy cho dashboard và RFM. Quy tắc nhóm: **không commit/push file dữ liệu lên origin** — data trao đổi qua link Drive (xem README mục “Quy tắc dữ liệu”).

## Phạm vi sở hữu

```text
data/raw/                         Dữ liệu nguồn (chi tiết từng file: data/raw/SOURCES.md)
data/processed/                   Output pipeline; dashboard chỉ đọc từ đây
data/processed/cleaned_data.csv   UNION 3 nguồn, 71.391 dòng, schema 10 cột, 2012→2024
scripts/clean_data.py             Điểm chạy full pipeline: làm sạch + JOIN
src/shared/data_cleaning.py       Quy tắc làm sạch, EDA đã chốt và hàm JOIN
src/dash_app/shared_data.py       Loader duy nhất dashboard dùng (không đọc raw)
```

Luồng bàn giao: `data/raw/*.csv → scripts/clean_data.py → data/processed/*.csv → dashboard`. `cleaned_data.csv` tái tạo được, không sửa tay. Sau khi đổi dataset phải chạy lại pipeline và báo Dashboard/Insight trước khi bàn giao.

## Quá trình cào dữ liệu (2026-10-01)

Xuất phát: Global Superstore 2012–2015 (cũ) + 2 file từng rớt mạng (`walmart_train.csv` bị cắt cụt 11.173 dòng, `bigmart_train.csv` đủ).

1. Tải bù `walmart_train.csv` bản full 12,8MB từ HuggingFace (`large-traversaal/Walmart-sales`) → đủ 421.570 dòng, hết lỗi dòng cuối.
2. Tìm nguồn gần 2026 nhất mà vẫn RFM được: chốt `superstore_2021_2024.csv` (GitHub venunelaturi, 10.194 dòng, 2021-01-03 → 2024-12-30). Các nguồn 2025 (Đức) và 2026 (Ấn Độ) bị loại vì đơn quốc gia và/hoặc thiếu Customer ID.
3. Lấp lỗ 2016–2020: thử `An-j96/SuperstoreData` (trùng ~60% giao dịch với file dưới → loại, tránh double-count), `global-sales-100k` (thiếu Category/Region → loại), Kaggle (cần auth), Scribd (PDF) → chốt `superstore_2015_2018.csv` (GitHub larryt2003, 9.994 dòng, 2015–2018, 0 trùng Order ID/key với Global).
4. Kết quả: phủ liên tục 2012–2018 + 2021–2024; chỉ còn trống 2019–2020 (không nội suy, giữ trung thực).

## Kết quả EDA (số liệu đã chốt)

| Bảng | Quy mô / phủ thời gian | Phát hiện chính | Xử lý |
|---|---|---|---|
| Global Orders | 51.290 dòng, 24 cột, 2012–2015, 165 nước, 17.415 khách | `Postal Code` null 41.296; 0 trùng; Sales<0: 0; Qty≤0: 0 | Bỏ cột ngoài schema; giữ Profit âm (đơn lỗ thật) |
| Superstore 2015–2018 | 9.994 dòng, 2015–2018, Mỹ | Tên cột `Sales`/`Profit` dính khoảng trắng; 0 trùng với Global | Strip tên cột rồi UNION |
| Superstore 2021–2024 | 10.194 dòng, 2021–2024, Mỹ + Canada 200 dòng, 804 khách | 0 null/trùng; Discount 0–0,8; Profit âm 1.901 dòng | Giữ đơn lỗ; alias `Country/Region` → `Country` |
| Walmart train | 421.570 dòng, 2010–2012, 45 stores × 81 depts | 1.285 `Weekly_Sales` âm (hoàn tiền) | Giữ nguyên, ghi chú |
| Walmart features | 8.190 = 45×182 tuần, tới 07/2013 | Markdown null ~50%, CPI/Unemployment null 585 (tuần 2013 ngoài train) | Giữ null; sau JOIN còn 0 null |
| BigMart | 8.523 dòng, không có cột thời gian | `Item_Weight` null 1.463; `Outlet_Size` null 2.410; `Fat_Content` 5 biến thể; `Visibility` = 0 có 526 dòng | Chuẩn hoá 2 giá trị; Visibility 0 → impute theo Item; Weight → impute theo Item; Size → mode theo Outlet_Type; thêm `Outlet_Age` (mốc 2013) → 0 null |
| People | 24 dòng Region → người phụ trách | Tên dính ký tự thay thế encoding (giữ nguyên); khớp 22/23 Region Global | LEFT JOIN, giữ đơn không khớp |

## JOIN và output pipeline

- `cleaned_data.csv` (71.391): UNION 3 nguồn đơn hàng (51.280 + 9.994 + 10.194, khử 77 trùng liên nguồn), schema 10 cột không đổi, 0 null.
- `orders_enriched.csv` (71.391): UNION LEFT JOIN People ON Region → thêm `Manager`; null 28,7% (Region `Canada` + `Central/East/South/West` của 2 nguồn Mỹ không có trong People).
- `walmart_weekly_enriched.csv` (421.570): train LEFT JOIN features ON (Store, Date) + LEFT JOIN stores (star-join).
- `bigmart_cleaned.csv` (8.523) + `people_cleaned.csv` + 3 file Walmart đã chuẩn hoá.

> Biểu đồ/dự báo trên dashboard vẽ từ `cleaned_data.csv`. Các file JOIN ngang là kết quả minh hoạ đã xuất, hiện chưa nối vào visual.

## Kế hoạch bảng bàn giao cho thành viên

| Bảng | Nội dung | Giao cho | Trạng thái |
|---|---|---|---|
| `cleaned_data.csv` | Fact 71.391 dòng, schema 10 cột | Khoa (dashboard), Duy (RFM/forecast input) | ✅ Xong |
| `orders_enriched.csv` | UNION + `Manager` (LEFT JOIN People) | Khoa (thêm cột Manager vào bảng RFM), Duy (insight theo người phụ trách) | ✅ File xong, ⏳ chờ nối vào bảng hiển thị |
| `rfm_customers.csv` | 18.223 khách: R/F/M, score, Segment, Country/Region, Manager | Duy (EDA segment, không cần chạy lại code) | ✅ Xong |
| `monthly_sales.csv` | 156 tháng: Sales/Profit/Orders/Customers (tháng 2019–2020 = 0, đúng bản chất lỗ dữ liệu) | Duy (train/test forecast theo thời gian) | ✅ Xong |
| `walmart_weekly_enriched.csv` | 421.570 dòng store/dept/tuần + features + stores | Duy (forecast theo tuần, phân tích holiday/markdown) | ✅ Xong |
| `bigmart_cleaned.csv` | 8.523 dòng Item×Outlet + `Outlet_Age` | Duy (insight sản phẩm/cửa hàng) | ✅ Xong |
| `people_cleaned.csv`, `walmart_*_cleaned.csv` | Bảng dimension đã chuẩn hoá | Dùng chung khi cần tra cứu | ✅ Xong |

Quy tắc bảng mới: tên file nói rõ grain (khách/tháng/tuần), không merge các grain khác nhau vào một bảng, mọi bảng đều tái tạo bằng `scripts/clean_data.py`.

## Schema đầu ra bắt buộc (hợp đồng tích hợp)

```text
Order ID, Order Date, Customer ID, Country, Region,
Category, Sub-Category, Sales, Quantity, Profit
```

Quy ước: `Order Date` parse được; `Sales`/`Quantity`/`Profit` là số, Profit được phép âm; `Sales >= 0`, `Quantity > 0`; một `Order ID` có thể nhiều dòng sản phẩm nên không xoá trùng chỉ theo `Order ID`. Dataset nguồn chỉ cần ánh xạ được về schema này qua `COLUMN_ALIASES`; thiếu trường không suy dẫn được thì thống nhất giảm tính năng, không tự điền giá trị giả.

## Lệnh sử dụng

```cmd
python scripts\clean_data.py
```

(Tái tạo toàn bộ output. Lệnh tải lại từng file raw xem `data/raw/SOURCES.md`.)

## Tiêu chí hoàn thành

- [x] Dataset ≥ 5.000 dòng/nhiều bảng, có nguồn trích dẫn (`SOURCES.md`).
- [x] EDA + quy tắc làm sạch/JOIN đã chốt (bảng trên).
- [x] Pipeline tái tạo 1 lệnh, dashboard đọc được dữ liệu mới.
- [ ] Lập data dictionary chi tiết từng cột cho báo cáo đồ án.
- [ ] Vẽ biểu đồ EDA bằng Matplotlib/Seaborn lưu vào báo cáo.
