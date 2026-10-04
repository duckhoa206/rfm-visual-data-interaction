"""Chuẩn hoá dữ liệu đơn hàng trước khi dashboard sử dụng."""

from pathlib import Path

import pandas as pd

from src.shared.rfm_utils import build_rfm_table


REQUIRED_COLUMNS = [
    "Order ID", "Order Date", "Customer ID", "Country", "Region",
    "Category", "Sub-Category", "Sales", "Quantity", "Profit",
]
DATA_SOURCE_COLUMN = "Data Source"

# Các tên cột thường gặp trong CSV thật. Có thể bổ sung khi nhóm nhận dataset.
COLUMN_ALIASES = {
    "order id": "Order ID",
    "order_id": "Order ID",
    "order date": "Order Date",
    "order_date": "Order Date",
    "transaction_date": "Order Date",
    "customer id": "Customer ID",
    "customer_id": "Customer ID",
    "country": "Country",
    "country/region": "Country",
    "country_region": "Country",
    "region": "Region",
    "market": "Region",
    "category": "Category",
    "product category": "Category",
    "sub-category": "Sub-Category",
    "sub category": "Sub-Category",
    "sub_category": "Sub-Category",
    "sales": "Sales",
    "total_spent": "Sales",
    "total revenue": "Sales",
    "revenue": "Sales",
    "quantity": "Quantity",
    "quantity purchased": "Quantity",
    "units sold": "Quantity",
    "profit": "Profit",
}


def clean_orders(
    raw_path: Path,
    clean_path: Path,
    source_name: str = "Unspecified",
) -> pd.DataFrame:
    """Chuẩn hoá CSV raw và gắn nhãn nguồn trước khi ghi bảng sạch."""
    df = pd.read_csv(raw_path)
    df.columns = [str(column).strip() for column in df.columns]

    rename_map = {
        column: COLUMN_ALIASES[column.strip().lower()]
        for column in df.columns
        if column.strip().lower() in COLUMN_ALIASES
    }
    df = df.rename(columns=rename_map)
    # Một raw có thể chứa cả cột gốc và alias (vd Global Superstore có cả
    # "Region" và "Market"→"Region"): giữ cột đầu tiên, bỏ bản trùng sau rename.
    df = df.loc[:, ~df.columns.duplicated(keep="first")]

    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing_columns:
        raise ValueError(
            "Dữ liệu thiếu các cột bắt buộc: " + ", ".join(missing_columns)
        )

    df = df[REQUIRED_COLUMNS].copy()
    df[DATA_SOURCE_COLUMN] = source_name
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")

    for column in ["Sales", "Quantity", "Profit"]:
        # Hỗ trợ giá trị như "$1,200.50" hoặc "1,200.50".
        df[column] = pd.to_numeric(
            df[column].astype(str).str.replace(r"[^0-9.-]", "", regex=True),
            errors="coerce",
        )

    for column in ["Order ID", "Customer ID", "Country", "Region", "Category", "Sub-Category"]:
        df[column] = df[column].astype("string").str.strip()

    df = df.dropna(subset=REQUIRED_COLUMNS).drop_duplicates()
    df = df[(df["Sales"] >= 0) & (df["Quantity"] > 0)]
    df = df.sort_values("Order Date").reset_index(drop=True)

    clean_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(clean_path, index=False)
    return df


def _normalize_bool(series: pd.Series) -> pd.Series:
    """Chuẩn hoá cột boolean từ nhiều kiểu (True/False, TRUE/FALSE, 1/0)."""
    return (
        series.astype(str).str.strip().str.lower().map(
            {"true": True, "1": True, "false": False, "0": False}
        )
    )


def clean_people(raw_path: Path, clean_path: Path) -> pd.DataFrame:
    """Làm sạch bảng nhân sự phụ trách theo Region (sheet People).

    EDA: 24 dòng, 0 null sau strip, tên có ký tự thay thế do khác encoding
    gốc (giữ nguyên, chỉ strip). Output: Person, Region.
    """
    df = pd.read_csv(raw_path, encoding="utf-8-sig")
    df.columns = [str(c).strip() for c in df.columns]
    for col in ["Person", "Region"]:
        df[col] = df[col].astype("string").str.strip()
    df = df.dropna(subset=["Person", "Region"]).drop_duplicates().reset_index(drop=True)
    clean_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(clean_path, index=False)
    return df


def clean_walmart_stores(raw_path: Path, clean_path: Path) -> pd.DataFrame:
    """45 siêu thị: Store (int), Type (A/B/C), Size (sqft). Không null."""
    df = pd.read_csv(raw_path)
    df.columns = [str(c).strip() for c in df.columns]
    df["Store"] = pd.to_numeric(df["Store"], errors="coerce").astype("Int64")
    df["Type"] = df["Type"].astype("string").str.strip()
    df["Size"] = pd.to_numeric(df["Size"], errors="coerce").astype("Int64")
    df = df.dropna().drop_duplicates(subset=["Store"]).sort_values("Store").reset_index(drop=True)
    clean_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(clean_path, index=False)
    return df


def clean_walmart_features(raw_path: Path, clean_path: Path) -> pd.DataFrame:
    """8190 dòng Store×tuần (2010-2013). Giữ null Markdown/CPI/Unemployment
    (đặc thù thu thập), chỉ chuẩn hoá kiểu + sort. Không drop null để giữ grain."""
    df = pd.read_csv(raw_path)
    df.columns = [str(c).strip() for c in df.columns]
    df["Store"] = pd.to_numeric(df["Store"], errors="coerce").astype("Int64")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for col in ["Temperature", "Fuel_Price", "MarkDown1", "MarkDown2",
                "MarkDown3", "MarkDown4", "MarkDown5", "CPI", "Unemployment"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "IsHoliday" in df.columns:
        df["IsHoliday"] = _normalize_bool(df["IsHoliday"])
    df = df.dropna(subset=["Store", "Date"]).drop_duplicates(
        subset=["Store", "Date"]).sort_values(["Store", "Date"]).reset_index(drop=True)
    clean_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(clean_path, index=False)
    return df


def clean_walmart_train(raw_path: Path, clean_path: Path) -> pd.DataFrame:
    """421.570 dòng Store×Dept×tuần (2010-2012). Giữ Weekly_Sales âm
    (hoàn tiền/điều chỉnh), không loại bỏ để giữ tổng đúng."""
    df = pd.read_csv(raw_path)
    df.columns = [str(c).strip() for c in df.columns]
    df["Store"] = pd.to_numeric(df["Store"], errors="coerce").astype("Int64")
    df["Dept"] = pd.to_numeric(df["Dept"], errors="coerce").astype("Int64")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Weekly_Sales"] = pd.to_numeric(df["Weekly_Sales"], errors="coerce")
    if "IsHoliday" in df.columns:
        df["IsHoliday"] = _normalize_bool(df["IsHoliday"])
    df = df.dropna(subset=["Store", "Dept", "Date", "Weekly_Sales"]).drop_duplicates(
        subset=["Store", "Dept", "Date"]).sort_values(
        ["Store", "Dept", "Date"]).reset_index(drop=True)
    clean_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(clean_path, index=False)
    return df


FAT_CONTENT_MAP = {
    "lf": "Low Fat", "low fat": "Low Fat",
    "reg": "Regular", "regular": "Regular",
}


def clean_bigmart(raw_path: Path, clean_path: Path) -> pd.DataFrame:
    """8523 dòng Item×Outlet. Chuẩn hoá Fat_Content, Visibility 0→NaN rồi
    impute theo Item, Weight null impute theo Item, Size null impute theo
    Outlet_Type mode, thêm Outlet_Age (mốc 2013)."""
    df = pd.read_csv(raw_path)
    df.columns = [str(c).strip() for c in df.columns]

    df["Item_Fat_Content"] = (
        df["Item_Fat_Content"].astype("string").str.strip().str.lower()
        .map(FAT_CONTENT_MAP).fillna(
            df["Item_Fat_Content"].astype("string").str.strip().str.title()
        )
    )
    df["Item_Fat_Content"] = df["Item_Fat_Content"].replace(
        {"Low fat": "Low Fat", "Regular": "Regular"}
    )

    for col in ["Item_Weight", "Item_Visibility", "Item_MRP", "Item_Outlet_Sales"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df.loc[df["Item_Visibility"] == 0, "Item_Visibility"] = pd.NA
    df["Item_Visibility"] = df.groupby("Item_Identifier")["Item_Visibility"].transform(
        lambda s: s.fillna(s.mean()))
    df["Item_Visibility"] = df["Item_Visibility"].fillna(df["Item_Visibility"].mean())

    df["Item_Weight"] = df.groupby("Item_Identifier")["Item_Weight"].transform(
        lambda s: s.fillna(s.mean()))
    df["Item_Weight"] = df["Item_Weight"].fillna(df["Item_Weight"].median())

    outlet_size_mode = df.groupby("Outlet_Type")["Outlet_Size"].agg(
        lambda s: s.mode().iloc[0] if s.notna().any() else pd.NA)
    df["Outlet_Size"] = df.apply(
        lambda r: outlet_size_mode.get(r["Outlet_Type"], pd.NA)
        if pd.isna(r["Outlet_Size"]) else r["Outlet_Size"], axis=1)

    df["Outlet_Establishment_Year"] = pd.to_numeric(
        df["Outlet_Establishment_Year"], errors="coerce").astype("Int64")
    df["Outlet_Age"] = (2013 - df["Outlet_Establishment_Year"]).astype("Int64")

    for col in ["Item_Identifier", "Item_Type", "Outlet_Identifier",
                "Outlet_Size", "Outlet_Location_Type", "Outlet_Type"]:
        df[col] = df[col].astype("string").str.strip()

    df = df.dropna(subset=["Item_Identifier", "Outlet_Identifier",
                           "Item_Outlet_Sales"]).drop_duplicates().reset_index(drop=True)
    clean_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(clean_path, index=False)
    return df


def build_orders_union(dfs: list) -> pd.DataFrame:
    """UNION các bảng đơn hàng, giữ nhãn provenance ngoài schema nghiệp vụ."""
    tagged_dfs = []
    for frame in dfs:
        tagged = frame.copy()
        if DATA_SOURCE_COLUMN not in tagged.columns:
            tagged[DATA_SOURCE_COLUMN] = "Unspecified"
        tagged[DATA_SOURCE_COLUMN] = tagged[DATA_SOURCE_COLUMN].fillna("Unspecified")
        tagged_dfs.append(tagged[REQUIRED_COLUMNS + [DATA_SOURCE_COLUMN]])

    union_df = pd.concat(tagged_dfs, ignore_index=True)
    union_df["Order Date"] = pd.to_datetime(union_df["Order Date"], errors="coerce")
    union_df = union_df.dropna(subset=REQUIRED_COLUMNS).drop_duplicates(
        subset=REQUIRED_COLUMNS)
    return union_df.sort_values("Order Date").reset_index(drop=True)


def join_orders_people(orders: pd.DataFrame, people: pd.DataFrame) -> pd.DataFrame:
    """LEFT JOIN đơn hàng với người phụ trách theo Region.

    Ghi chú khớp: 22/23 Region Global khớp; Region 'Canada' (Global) và
    4 Region Mỹ ('Central/East/South/West' của nguồn 2021-2024) không có trong
    People → Person null (giữ đơn hàng, không loại bỏ)."""
    return orders.merge(people.rename(columns={"Person": "Manager"}),
                        on="Region", how="left")


def join_walmart_weekly(train: pd.DataFrame, features: pd.DataFrame,
                        stores: pd.DataFrame) -> pd.DataFrame:
    """Star-join Walmart: train LEFT features ON (Store, Date),
    rồi LEFT stores ON Store. Giữ toàn bộ doanh số train."""
    enriched = train.merge(features, on=["Store", "Date"],
                           how="left", suffixes=("", "_feat"))
    if "IsHoliday_feat" in enriched.columns:
        enriched["IsHoliday"] = enriched["IsHoliday"].fillna(
            enriched["IsHoliday_feat"])
        enriched = enriched.drop(columns=["IsHoliday_feat"])
    return enriched.merge(stores, on="Store", how="left")


def build_rfm_export(orders: pd.DataFrame, people: pd.DataFrame) -> pd.DataFrame:
    """Bảng RFM kèm Manager (JOIN People ON Region) để Insight EDA segment
    mà không cần chạy lại code. Snapshot = ngày đơn mới nhất + 1 ngày."""
    rfm = build_rfm_table(orders)
    managers = people.rename(columns={"Person": "Manager"})
    return rfm.merge(managers, on="Region", how="left")


def build_monthly_sales(orders: pd.DataFrame) -> pd.DataFrame:
    """Tổng hợp theo tháng và nguồn, không tạo tháng rỗng như doanh thu 0."""
    df = orders.copy()
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Month"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()
    group_columns = ["Month"]
    if DATA_SOURCE_COLUMN in df.columns:
        group_columns.insert(0, DATA_SOURCE_COLUMN)
    monthly = df.groupby(group_columns, as_index=False, dropna=False).agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique"),
        Customers=("Customer ID", "nunique"),
    )
    return monthly.sort_values(group_columns).reset_index(drop=True)
