"""
Logic tính RFM DÙNG CHUNG cho toàn bộ dashboard.

QUAN TRỌNG: đây là file duy nhất được phép chứa công thức tính RFM.
Mọi trang trong src/dash_app/pages/ chỉ được GỌI các hàm ở đây (qua
src/dash_app/shared_data.py), không được tự viết lại công thức riêng
-> tránh lệch số liệu giữa các trang.
"""

import pandas as pd


def compute_rfm(orders_df: pd.DataFrame, snapshot_date: pd.Timestamp | None = None) -> pd.DataFrame:
    """
    Tính Recency, Frequency, Monetary theo Customer ID, hoặc theo cặp
    Customer ID × Data Source khi bảng có provenance.

    orders_df cần có các cột: 'Customer ID', 'Order Date', 'Order ID', 'Sales'
    snapshot_date: ngày mốc để tính Recency, mặc định = ngày đơn hàng gần nhất + 1 ngày
    """
    df = orders_df.copy()
    df["Order Date"] = pd.to_datetime(df["Order Date"])

    if snapshot_date is None:
        snapshot_date = df["Order Date"].max() + pd.Timedelta(days=1)

    group_columns = ["Customer ID"]
    if "Data Source" in df.columns:
        group_columns.append("Data Source")

    rfm = df.groupby(group_columns).agg(
        Recency=("Order Date", lambda x: (snapshot_date - x.max()).days),
        Frequency=("Order ID", "nunique"),
        Monetary=("Sales", "sum"),
    ).reset_index()

    # Gắn vị trí phổ biến nhất trong đúng customer/source cohort.
    locations = (
        df.groupby(group_columns)
        .agg(
            Country=("Country", lambda values: values.mode().iloc[0]),
            Region=("Region", lambda values: values.mode().iloc[0]),
        )
        .reset_index()
    )
    rfm = rfm.merge(locations, on=group_columns, how="left")

    rfm["Monetary"] = rfm["Monetary"].round(2)
    return rfm


def score_rfm(rfm_df: pd.DataFrame) -> pd.DataFrame:
    """
    Chia mỗi trục R, F, M thành 5 nhóm (1-5) bằng qcut, rồi gán nhãn Segment.
    Recency: số ngày CÀNG NHỎ càng tốt -> điểm 5 = gần đây nhất.
    Frequency, Monetary: giá trị CÀNG LỚN càng tốt -> điểm 5 = cao nhất.
    """
    df = rfm_df.copy()

    df["R_score"] = pd.qcut(df["Recency"], 5, labels=[5, 4, 3, 2, 1], duplicates="drop").astype(int)
    df["F_score"] = pd.qcut(df["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5], duplicates="drop").astype(int)
    df["M_score"] = pd.qcut(df["Monetary"], 5, labels=[1, 2, 3, 4, 5], duplicates="drop").astype(int)

    df["RFM_Score"] = df["R_score"].astype(str) + df["F_score"].astype(str) + df["M_score"].astype(str)
    df["Segment"] = df.apply(_assign_segment, axis=1)
    return df


def _assign_segment(row) -> str:
    r, f, m = row["R_score"], row["F_score"], row["M_score"]
    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    if r >= 3 and f >= 3:
        return "Loyal Customers"
    if r >= 4 and f <= 2:
        return "New Customers"
    if r <= 2 and f >= 3:
        return "At Risk"
    if r <= 2 and f <= 2 and m <= 2:
        return "Lost"
    return "Need Attention"


def build_rfm_table(orders_df: pd.DataFrame) -> pd.DataFrame:
    """Hàm tiện ích: gọi 1 lần là ra bảng RFM đầy đủ điểm số + segment."""
    rfm = compute_rfm(orders_df)
    rfm = score_rfm(rfm)
    return rfm
