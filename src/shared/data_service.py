"""Dịch vụ dữ liệu thuần pandas dùng chung cho Streamlit và Dash.

QUAN TRỌNG: file này KHÔNG được import streamlit hay dash.
Mọi logic đọc/lọc dữ liệu chỉ nằm ở đây; callbacks Dash gọi trực tiếp các hàm này.

Nguồn duy nhất: data/processed/cleaned_data.csv (do scripts/clean_data.py sinh ra).
"""

from functools import lru_cache
from pathlib import Path

import pandas as pd

from src.shared.data_cleaning import DATA_SOURCE_COLUMN, REQUIRED_COLUMNS
from src.shared.rfm_utils import build_rfm_table

ROOT_DIR = Path(__file__).resolve().parents[2]

CLEAN_DATA_PATH = ROOT_DIR / "data" / "processed" / "cleaned_data.csv"


def _read_orders_uncached() -> pd.DataFrame:
    if not CLEAN_DATA_PATH.exists() or CLEAN_DATA_PATH.stat().st_size == 0:
        raise FileNotFoundError(
            "Chưa có dữ liệu đã làm sạch. Hãy chạy: "
            "python scripts/clean_data.py"
        )

    df = pd.read_csv(CLEAN_DATA_PATH, parse_dates=["Order Date"])
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing_columns:
        raise ValueError(
            "Dữ liệu processed thiếu các cột bắt buộc: "
            + ", ".join(missing_columns)
        )
    if DATA_SOURCE_COLUMN not in df.columns:
        raise ValueError(
            f"Dữ liệu processed thiếu cột provenance {DATA_SOURCE_COLUMN!r}. "
            "Hãy chạy lại: python scripts/clean_data.py"
        )
    return df


@lru_cache(maxsize=1)
def load_orders() -> pd.DataFrame:
    """Đọc bảng đơn hàng đã làm sạch (cache trong RAM)."""
    return _read_orders_uncached()


@lru_cache(maxsize=1)
def load_rfm() -> pd.DataFrame:
    """Bảng RFM đầy đủ điểm số + segment (tính 1 lần duy nhất)."""
    return build_rfm_table(load_orders())


def clear_cache() -> None:
    """Xóa cache khi cleaned_data.csv được tạo lại (dùng trong test/dev)."""
    load_orders.cache_clear()
    load_rfm.cache_clear()


def get_filter_options(
    orders: pd.DataFrame, rfm: pd.DataFrame
) -> dict:
    """Trả về options cho filter bar dùng chung."""
    options = {
        "regions": sorted(orders["Region"].unique()),
        "countries": sorted(orders["Country"].unique()),
        "date_min": orders["Order Date"].min(),
        "date_max": orders["Order Date"].max(),
        "segments": sorted(rfm["Segment"].unique()),
    }
    if DATA_SOURCE_COLUMN in orders.columns:
        options["data_sources"] = sorted(
            orders[DATA_SOURCE_COLUMN].dropna().unique()
        )
    return options


def get_countries_for_regions(
    orders: pd.DataFrame,
    regions: list,
    data_sources: list | None = None,
) -> list:
    """Drill-down: quốc gia thuộc các khu vực đã chọn (dùng cho callback Region→Country)."""
    matching_orders = orders[orders["Region"].isin(regions)]
    if data_sources is not None and DATA_SOURCE_COLUMN in matching_orders.columns:
        matching_orders = matching_orders[
            matching_orders[DATA_SOURCE_COLUMN].isin(data_sources)
        ]
    return sorted(matching_orders["Country"].unique())


def apply_filters(
    orders: pd.DataFrame,
    rfm: pd.DataFrame,
    regions: list | None = None,
    countries: list | None = None,
    start_date: pd.Timestamp | str | None = None,
    end_date: pd.Timestamp | str | None = None,
    segments: list | None = None,
    data_sources: list | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Lọc đơn hàng + RFM theo filter. Mọi trang dashboard đọc qua hàm này.

    None nghĩa là "chọn tất cả". Trả về (orders_filtered, rfm_filtered).
    """
    if regions is None:
        regions = sorted(orders["Region"].unique())
    if countries is None:
        countries = sorted(orders["Country"].unique())
    if start_date is None:
        start_date = orders["Order Date"].min()
    if end_date is None:
        end_date = orders["Order Date"].max()
    if segments is None:
        segments = sorted(rfm["Segment"].unique())
    if DATA_SOURCE_COLUMN in orders.columns and data_sources is None:
        data_sources = sorted(orders[DATA_SOURCE_COLUMN].dropna().unique())

    start_date, end_date = pd.Timestamp(start_date), pd.Timestamp(end_date)
    orders_filtered = orders[
        orders["Region"].isin(regions)
        & orders["Country"].isin(countries)
        & orders["Order Date"].between(start_date, end_date)
    ]
    if data_sources is not None:
        if DATA_SOURCE_COLUMN not in orders_filtered.columns:
            raise ValueError(
                f"Không thể lọc nguồn dữ liệu: thiếu cột {DATA_SOURCE_COLUMN!r}."
            )
        orders_filtered = orders_filtered[
            orders_filtered[DATA_SOURCE_COLUMN].isin(data_sources)
        ]
    customers_filtered = orders_filtered["Customer ID"].unique()
    rfm_filtered = rfm[
        rfm["Customer ID"].isin(customers_filtered)
        & rfm["Segment"].isin(segments)
    ]
    if data_sources is not None and DATA_SOURCE_COLUMN in rfm_filtered.columns:
        rfm_filtered = rfm_filtered[
            rfm_filtered[DATA_SOURCE_COLUMN].isin(data_sources)
        ]
    return orders_filtered, rfm_filtered
