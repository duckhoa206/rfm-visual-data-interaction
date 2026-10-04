# Nguồn dữ liệu thô (data/raw) — đa quốc gia, đa brand

Đáp ứng: hệ thống siêu thị đa quốc gia, ≥3 bảng, tổng ≫ 5.000 samples.

## Bảng đơn hàng (fact cho dashboard)

| File | Nguồn tải trực tiếp | Nội dung |
|---|---|---|
| `global_superstore_orders.csv` (51.290 dòng, 24 cột) | https://github.com/itsmecevi/global-superstore (Global Superstore.xlsx → sheet Orders) | Đơn hàng 2012–2015, **165 quốc gia**, 5 markets, 23 regions, 17.415 khách |
| `superstore_2015_2018.csv` (9.994 dòng — **cào thêm 2026-10-01 để lấp 2016-2018**) | https://github.com/larryt2003/Superstore-Sales-Dataset-2015-2018 (`Superstore_clean.csv`) | Đơn hàng 2015-01-03 → 2018-12-30, Mỹ, cùng họ schema (cột `Sales`/`Profit` dính khoảng trắng, pipeline đã strip); kiểm tra 0 trùng Order ID và 0 trùng key giao dịch với Global → UNION an toàn |
| `superstore_2021_2024.csv` (10.194 dòng, 22 cột) — **GẦN 2026 NHẤT** | https://github.com/venunelaturi/Super-store-Sales-Data-Analysis (`Sample - Superstore.csv`) | Đơn hàng 2021-01-03 → 2024-12-30, Mỹ (9.994) + Canada (200), 804 khách |
| `global_superstore_people.csv` (24 dòng) | như Global Superstore (sheet People) | Nhân sự phụ trách theo Region (JOIN key) |

Ghi chú cào thêm (2026-10-01): đã thử nhưng LOẠI các nguồn sau —
`An-j96/SuperstoreData` (trùng ~60% giao dịch với file 2015-2018, chỉ khác năm → double-count),
`mahfuzmee-eng/global-sales-dataset` (bảng 100k engineered features, thiếu Category/Region nên không map được schema 10 cột),
Kaggle Global E-Commerce/Electronics (cần auth), Scribd 2020 (PDF).
Khoảng trống còn lại **2019–2020** hiện không có nguồn tương thích tải trực tiếp.

## Bảng bổ trợ (làm sạch + JOIN minh hoạ, khác grain nên không UNION vào fact)

| File | Nguồn tải trực tiếp | Nội dung |
|---|---|---|
| `walmart_stores.csv` (45 dòng) | https://huggingface.co/datasets/large-traversaal/Walmart-sales | 45 siêu thị Walmart (Mỹ): loại hình, diện tích |
| `walmart_features.csv` (8.190 dòng) | như trên | Theo store/tuần + nhiệt độ, nhiên liệu, markdown, CPI, thất nghiệp (2010-02-05 → 2013-07-26) |
| `walmart_train.csv` (421.570 dòng — **đã tải lại bản full 12,8MB** ngày 2026-10-01, bản trước bị cắt cụt 11.173 dòng) | như trên (`train.csv`) | Doanh số theo store/dept/tuần (2010-02-05 → 2012-10-26) |
| `bigmart_train.csv` (8.523 dòng — đã tải đủ) | https://raw.githubusercontent.com/BalaMungala/BigMart/master/Train.csv | Sản phẩm × cửa hàng Big Mart Ấn Độ (không có cột thời gian, chỉ năm mở cửa hàng 1985–2009) |

Lệnh tải lại khi cần (chạy tại gốc repo):

```cmd
curl.exe -L -o data\raw\superstore_2015_2018.csv "https://raw.githubusercontent.com/larryt2003/Superstore-Sales-Dataset-2015-2018/main/Superstore_clean.csv"
curl.exe -L -o data\raw\superstore_2021_2024.csv "https://raw.githubusercontent.com/venunelaturi/Super-store-Sales-Data-Analysis/main/Sample%20-%20Superstore.csv"
curl.exe -L -o data\raw\walmart_train.csv "https://huggingface.co/datasets/large-traversaal/Walmart-sales/resolve/main/train.csv"
curl.exe -L -o data\raw\bigmart_train.csv "https://raw.githubusercontent.com/BalaMungala/BigMart/master/Train.csv"
```

## Kết quả pipeline (2026-10-01): `python scripts/clean_data.py`

- `cleaned_data.csv`: **71.391 dòng, schema 10 cột không đổi**, 2012-01-01 → 2024-12-30
  (UNION 3 nguồn 51.280 + 9.994 + 10.194, khử 77 trùng lặp liên nguồn;
  165 quốc gia, 18.223 khách, 0 null). Phủ liên tục 2012–2018 và 2021–2024,
  chỉ còn trống 2019–2020 (không nội suy thêm để giữ trung thực).
- `orders_enriched.csv`: UNION LEFT JOIN People ON Region → thêm cột `Manager`
  (20.501/71.391 dòng null 28,7%: Region `Canada` + 4 Region Mỹ `Central/East/South/West`
  của 2 nguồn Mỹ không có trong People — giữ đơn hàng, không loại bỏ).
- `walmart_weekly_enriched.csv`: 421.570 dòng = train LEFT JOIN features
  ON (Store, Date) + LEFT JOIN stores ON Store (star-join, giữ toàn bộ doanh số).
- `bigmart_cleaned.csv`: 8.523 dòng, 0 null (Fat_Content chuẩn hoá 2 giá trị,
  Visibility 0 → impute theo Item, Weight null → impute theo Item,
  Size null → mode theo Outlet_Type, thêm `Outlet_Age` mốc 2013).
- `rfm_customers.csv`: 18.223 khách (R/F/M, score, Segment, Country/Region, Manager)
  để Insight EDA segment không cần chạy lại code.
- `monthly_sales.csv`: 156 tháng (Sales/Profit/Orders/Customers; tháng 2019–2020 = 0
  đúng bản chất lỗ dữ liệu) để train/test forecast theo thời gian.
- EDA ghi nhận và giữ nguyên (không xoá bản ghi thật): Profit âm (đơn lỗ),
  Weekly_Sales âm (hoàn tiền), Markdown/CPI null (đặc thù thu thập).

> Lưu ý: biểu đồ và dự báo trên dashboard vẽ từ `cleaned_data.csv`
> (UNION dọc các bảng đơn hàng). Các file JOIN ngang (`orders_enriched`,
> `walmart_weekly_enriched`, `bigmart_cleaned`) là kết quả minh hoạ đã xuất
> ra `data/processed/`, hiện chưa nối vào visual.
