"""Pipeline làm sạch + kết nối toàn bộ dữ liệu thô cho dashboard.

Fact chính (dashboard đọc duy nhất file này):
  data/raw/global_superstore_orders.csv (2012-2015, 165 quốc gia)
  + data/raw/superstore_2015_2018.csv (2015-2018, Mỹ — lấp 2016-2018)
  + data/raw/global_electronics_retail_2019_2020.csv (Kaggle, demo/unverified)
  + data/raw/superstore_2021_2024.csv (2021-2024, Mỹ/Canada — gần 2026 nhất)
  UNION → data/processed/cleaned_data.csv (10 cột nghiệp vụ + Data Source).
  Cột Data Source cho phép truy vết/tách cohort; nguồn Kaggle được cảnh báo trên dashboard.

Bảng phụ (làm sạch + join minh hoạ, không phá pipeline cũ):
  people_cleaned.csv, walmart_*_cleaned.csv, walmart_weekly_enriched.csv
  (train LEFT JOIN features ON Store,Date + LEFT JOIN stores),
  bigmart_cleaned.csv, orders_enriched.csv (UNION LEFT JOIN people ON Region).

Chạy:  python scripts/clean_data.py
"""

import argparse
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.shared.data_cleaning import (
    build_monthly_sales,
    build_orders_union,
    build_rfm_export,
    clean_bigmart,
    clean_orders,
    clean_people,
    clean_walmart_features,
    clean_walmart_stores,
    clean_walmart_train,
    join_orders_people,
    join_walmart_weekly,
)

RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"

CLEAN_DATA_PATH = PROCESSED_DIR / "cleaned_data.csv"


def run_pipeline() -> dict:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Fact đơn hàng: UNION bốn nguồn có nhãn provenance.
    orders_global = clean_orders(
        RAW_DIR / "global_superstore_orders.csv",
        PROCESSED_DIR / "_tmp_global.csv",
        source_name="Global Superstore (2012-2015)",
    )
    orders_mid = clean_orders(
        RAW_DIR / "superstore_2015_2018.csv",
        PROCESSED_DIR / "_tmp_mid.csv",
        source_name="Superstore (2015-2018)",
    )
    orders_demo = clean_orders(
        RAW_DIR / "global_electronics_retail_2019_2020.csv",
        PROCESSED_DIR / "_tmp_demo.csv",
        source_name="Kaggle Global Electronics Retail (demo, unverified)",
    )
    orders_recent = clean_orders(
        RAW_DIR / "superstore_2021_2024.csv",
        PROCESSED_DIR / "_tmp_recent.csv",
        source_name="Superstore (2021-2024)",
    )
    orders_union = build_orders_union(
        [orders_global, orders_mid, orders_demo, orders_recent]
    )
    orders_union.to_csv(CLEAN_DATA_PATH, index=False)

    # 2. People (JOIN key Region).
    people = clean_people(
        RAW_DIR / "global_superstore_people.csv",
        PROCESSED_DIR / "people_cleaned.csv",
    )
    orders_enriched = join_orders_people(orders_union, people)
    orders_enriched.to_csv(PROCESSED_DIR / "orders_enriched.csv", index=False)

    # 3. Walmart star-schema.
    stores = clean_walmart_stores(
        RAW_DIR / "walmart_stores.csv", PROCESSED_DIR / "walmart_stores_cleaned.csv")
    features = clean_walmart_features(
        RAW_DIR / "walmart_features.csv", PROCESSED_DIR / "walmart_features_cleaned.csv")
    train = clean_walmart_train(
        RAW_DIR / "walmart_train.csv", PROCESSED_DIR / "walmart_train_cleaned.csv")
    walmart_enriched = join_walmart_weekly(train, features, stores)
    walmart_enriched.to_csv(PROCESSED_DIR / "walmart_weekly_enriched.csv", index=False)

    # 4. BigMart (đơn bảng, không join ngoài).
    bigmart = clean_bigmart(
        RAW_DIR / "bigmart_train.csv", PROCESSED_DIR / "bigmart_cleaned.csv")

    # 5. Bảng giao cho Insight & Forecast: RFM kèm Manager + chuỗi tháng.
    rfm_export = build_rfm_export(orders_union, people)
    rfm_export.to_csv(PROCESSED_DIR / "rfm_customers.csv", index=False)
    monthly = build_monthly_sales(orders_union)
    monthly.to_csv(PROCESSED_DIR / "monthly_sales.csv", index=False)

    for tmp in ["_tmp_global.csv", "_tmp_mid.csv", "_tmp_demo.csv", "_tmp_recent.csv"]:
        tmp_path = PROCESSED_DIR / tmp
        if tmp_path.exists():
            tmp_path.unlink()

    return {
        "cleaned_data": len(orders_union),
        "people_cleaned": len(people),
        "orders_enriched": len(orders_enriched),
        "walmart_stores_cleaned": len(stores),
        "walmart_features_cleaned": len(features),
        "walmart_train_cleaned": len(train),
        "walmart_weekly_enriched": len(walmart_enriched),
        "bigmart": len(bigmart),
        "bigmart_cleaned": len(bigmart),
        "rfm_customers": len(rfm_export),
        "monthly_sales": len(monthly),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lam sach + join toan bo du lieu.")
    parser.add_argument(
        "raw_file", nargs="?", default=None,
        help="(Tuong thich cu) CSV raw don le; bo qua de chay full pipeline.",
    )
    args = parser.parse_args()

    if args.raw_file:
        raw_path = Path(args.raw_file)
        if not raw_path.is_absolute():
            raw_path = ROOT_DIR / raw_path
        cleaned = clean_orders(raw_path, CLEAN_DATA_PATH)
        print(f"Da lam sach {len(cleaned):,} dong: {raw_path} -> {CLEAN_DATA_PATH}")
    else:
        stats = run_pipeline()
        file_reports = [
            ("cleaned_data.csv", "global_superstore_orders.csv + superstore_2015_2018.csv + global_electronics_retail_2019_2020.csv + superstore_2021_2024.csv (UNION)"),
            ("people_cleaned.csv", "global_superstore_people.csv"),
            ("orders_enriched.csv", "cleaned_data (UNION) LEFT JOIN people_cleaned ON Region"),
            ("walmart_stores_cleaned.csv", "walmart_stores.csv"),
            ("walmart_features_cleaned.csv", "walmart_features.csv"),
            ("walmart_train_cleaned.csv", "walmart_train.csv"),
            ("walmart_weekly_enriched.csv", "walmart_train LEFT JOIN features ON Store,Date + LEFT JOIN stores"),
            ("bigmart_cleaned.csv", "bigmart_train.csv"),
            ("rfm_customers.csv", "cleaned_data + people (build_rfm_export)"),
            ("monthly_sales.csv", "cleaned_data (build_monthly_sales)"),
        ]
        stat_key_by_file = {
            "cleaned_data.csv": "cleaned_data",
            "people_cleaned.csv": "people_cleaned",
            "orders_enriched.csv": "orders_enriched",
            "walmart_stores_cleaned.csv": "walmart_stores_cleaned",
            "walmart_features_cleaned.csv": "walmart_features_cleaned",
            "walmart_train_cleaned.csv": "walmart_train_cleaned",
            "walmart_weekly_enriched.csv": "walmart_weekly_enriched",
            "bigmart_cleaned.csv": "bigmart_cleaned",
            "rfm_customers.csv": "rfm_customers",
            "monthly_sales.csv": "monthly_sales",
        }
        print(f"Hoan tat pipeline, thu muc dich: {PROCESSED_DIR}")
        for filename, source_desc in file_reports:
            count = stats.get(stat_key_by_file[filename], 0)
            print(f"Da lam sach {count:,} dong: {source_desc} -> {PROCESSED_DIR / filename}")
