"""Chuỗi tháng đồng nhất nguồn và hồi quy panel theo thời gian-khu vực."""

import numpy as np
import pandas as pd


def comparable_monthly_orders(orders: pd.DataFrame) -> pd.DataFrame:
    """Giữ đoạn tháng liên tục cuối cùng có cùng tập nguồn dữ liệu.

    Tháng thiếu giao dịch hoặc thay đổi tập nguồn là ranh giới chuỗi,
    không tự coi dữ liệu thiếu là doanh thu bằng 0.
    """
    frame = orders.copy()
    frame["Order Date"] = pd.to_datetime(frame["Order Date"])
    indexed = frame.set_index("Order Date")
    monthly = indexed.resample("MS").agg(Sales=("Sales", "sum"), Rows=("Sales", "size"))
    if "Data Source" in frame.columns:
        monthly["Sources"] = indexed["Data Source"].resample("MS").agg(
            lambda values: tuple(sorted(values.dropna().unique()))
        )
    else:
        monthly["Sources"] = [()] * len(monthly)
    last_sources = monthly["Sources"].iloc[-1]
    start = len(monthly) - 1
    while start > 0:
        previous = monthly.iloc[start - 1]
        if previous["Rows"] == 0 or previous["Sources"] != last_sources:
            break
        start -= 1
    return monthly.iloc[start:].reset_index()


def predict_monthly_sales(history: pd.DataFrame, dates) -> np.ndarray:
    """Ước lượng xu thế và mùa vụ cùng lúc, theo khoảng cách tháng thực.

    Chỉ dùng hiệu ứng tháng khi có ít nhất hai quan sát cho mỗi tháng.
    Không nhân doanh thu hồi quy với hệ số tháng từ các nguồn khác nhau.
    """
    origin = history["Order Date"].iloc[0]
    seasonal = history["Order Date"].dt.month.value_counts().reindex(
        range(1, 13), fill_value=0
    ).min() >= 2

    def design(values):
        values = pd.DatetimeIndex(values)
        elapsed = (values.year - origin.year) * 12 + values.month - origin.month
        columns = [np.ones(len(values)), np.asarray(elapsed, dtype=float)]
        if seasonal:
            columns.extend((values.month == month).astype(float) for month in range(2, 13))
        return np.column_stack(columns)

    coefficients = np.linalg.lstsq(
        design(history["Order Date"]), history["Sales"].to_numpy(), rcond=None
    )[0]
    return np.maximum(0, design(dates) @ coefficients)


def _regional_monthly_orders(orders: pd.DataFrame, history: pd.DataFrame) -> pd.DataFrame:
    """Tạo panel tháng-khu vực trong đúng đoạn nguồn đồng nhất của lịch sử."""
    if "Region" not in orders.columns or not orders["Region"].notna().any():
        return pd.DataFrame(columns=["Order Date", "Region", "Sales"])

    frame = orders.copy()
    frame["Order Date"] = pd.to_datetime(frame["Order Date"]).dt.to_period("M").dt.to_timestamp()
    frame = frame[frame["Order Date"].between(
        history["Order Date"].iloc[0], history["Order Date"].iloc[-1]
    )]
    sources = history["Sources"].iloc[-1]
    if sources and "Data Source" in frame.columns:
        frame = frame[frame["Data Source"].isin(sources)]

    regions = sorted(frame["Region"].dropna().unique())
    if not regions:
        return pd.DataFrame(columns=["Order Date", "Region", "Sales"])
    index = pd.MultiIndex.from_product(
        [history["Order Date"], regions], names=["Order Date", "Region"]
    )
    return (
        frame.groupby(["Order Date", "Region"])["Sales"].sum()
        .reindex(index, fill_value=0.0)
        .rename("Sales")
        .reset_index()
    )


def _predict_regional_sales(history: pd.DataFrame, dates) -> pd.DataFrame:
    """Hồi quy panel với mùa vụ, mức nền và xu thế riêng theo khu vực."""
    regions = sorted(history["Region"].unique())
    origin = history["Order Date"].min()
    seasonal = history["Order Date"].drop_duplicates().dt.month.value_counts().reindex(
        range(1, 13), fill_value=0
    ).min() >= 2

    def design(frame):
        values = pd.DatetimeIndex(frame["Order Date"])
        elapsed = np.asarray(
            (values.year - origin.year) * 12 + values.month - origin.month,
            dtype=float,
        )
        columns = []
        for region in regions:
            indicator = frame["Region"].eq(region).to_numpy(dtype=float)
            columns.extend([indicator, indicator * elapsed])
            if seasonal:
                columns.extend(
                    indicator * (values.month == month).astype(float)
                    for month in range(2, 13)
                )
        return np.column_stack(columns)

    coefficients = np.linalg.lstsq(
        design(history), history["Sales"].to_numpy(), rcond=None
    )[0]
    target = pd.MultiIndex.from_product(
        [pd.DatetimeIndex(dates), regions], names=["Order Date", "Region"]
    ).to_frame(index=False)
    target["Base"] = np.maximum(0, design(target) @ coefficients)
    return target


def make_forecast_projection(
    orders: pd.DataFrame,
    start_date=None,
    end_date=None,
    target_year: int = 2030,
    optimistic_weight: float = 0.20,
    cautious_weight: float = 0.15,
) -> dict:
    """Huấn luyện một lần, chọn cửa sổ tháng cho toàn bộ dashboard dự báo.

    Ngày bắt đầu/kết thúc chọn các tháng bao gồm hai mốc, không cắt dữ liệu
    huấn luyện. Chỉ bộ lọc chính quyết định dữ liệu lịch sử được huấn luyện.
    """
    if orders.empty:
        raise ValueError("Không có dữ liệu khớp với bộ lọc chính.")
    history = comparable_monthly_orders(orders)
    if len(history) < 12:
        raise ValueError("Cần tối thiểu 12 tháng liên tục có cùng nguồn dữ liệu để huấn luyện và kiểm thử. Hãy mở rộng bộ lọc chính.")

    first = history["Order Date"].iloc[0]
    last = history["Order Date"].iloc[-1]
    raw_start = pd.Timestamp(start_date if start_date else first)
    raw_end = pd.Timestamp(end_date if end_date else f"{target_year}-12-31")
    if pd.isna(raw_start) or pd.isna(raw_end) or raw_start > raw_end:
        raise ValueError("Thời gian bắt đầu phải nhỏ hơn hoặc bằng thời gian kết thúc.")
    start = raw_start.to_period("M").to_timestamp()
    end = raw_end.to_period("M").to_timestamp()

    test_len = min(12, max(3, len(history) // 5))
    train = history.iloc[:-test_len].copy()
    test = history.iloc[-test_len:].copy()
    regional_history = _regional_monthly_orders(orders, history)
    if regional_history.empty:
        test["Prediction"] = predict_monthly_sales(train, test["Order Date"])
    else:
        regional_train = _regional_monthly_orders(orders, train)
        regional_test = _predict_regional_sales(regional_train, test["Order Date"])
        test_predictions = regional_test.groupby("Order Date")["Base"].sum()
        test["Prediction"] = test["Order Date"].map(test_predictions)
    errors = test["Sales"] - test["Prediction"]

    dates = pd.date_range(last + pd.DateOffset(months=1), end, freq="MS")
    if regional_history.empty:
        base = predict_monthly_sales(history, dates)
        future_by_region = pd.DataFrame(columns=["Order Date", "Region", "Base"])
    else:
        future_by_region = _predict_regional_sales(regional_history, dates)
        base_by_date = future_by_region.groupby("Order Date")["Base"].sum()
        base = base_by_date.reindex(dates, fill_value=0.0).to_numpy()
    optimistic_weight = max(0.0, float(optimistic_weight))
    cautious_weight = max(0.0, min(0.95, float(cautious_weight)))
    future = pd.DataFrame({
        "Order Date": dates,
        "Base": base,
        "Optimistic": base * np.linspace(1.0, 1.0 + optimistic_weight, len(dates)),
        "Cautious": base * np.linspace(1.0, 1.0 - cautious_weight, len(dates)),
    })
    visible_history = history[history["Order Date"].between(start, end)].copy()
    visible_future = future[future["Order Date"].between(start, end)].copy()
    visible_future_by_region = future_by_region[
        future_by_region["Order Date"].between(start, end)
    ].copy()
    if visible_history.empty and visible_future.empty:
        raise ValueError(f"Khoảng đang chọn không có dữ liệu trong chuỗi đồng nhất nguồn (bắt đầu {first:%m/%Y}). Hãy chọn khoảng khác hoặc đổi bộ lọc chính.")

    amounts = pd.concat([
        visible_history[["Order Date", "Sales"]],
        visible_future[["Order Date", "Base"]].rename(columns={"Base": "Sales"}),
    ], ignore_index=True)
    final_year = amounts[amounts["Order Date"].dt.year == end.year]
    final_sales = float(final_year["Sales"].sum())
    annual_history = history.groupby(history["Order Date"].dt.year)["Sales"].agg(["sum", "size"])
    complete = annual_history[(annual_history["size"] == 12) & (annual_history.index < end.year)]
    cagr = None
    if len(final_year) == 12 and not complete.empty and not visible_future.empty:
        reference_year = int(complete.index[-1])
        reference_sales = float(complete["sum"].iloc[-1])
        if reference_sales > 0:
            cagr = ((final_sales / reference_sales) ** (1 / (end.year - reference_year)) - 1) * 100

    return {
        "start": start, "end": end,
        "optimistic_weight": optimistic_weight,
        "cautious_weight": cautious_weight,
        "history": history, "train": train, "test": test, "future": future,
        "future_by_region": future_by_region,
        "visible_history": visible_history, "visible_future": visible_future,
        "visible_future_by_region": visible_future_by_region,
        "kpis": {
            "annual_2030": final_sales,
            "cum_sales": float(amounts["Sales"].sum()),
            "cagr": cagr,
            "mae": float(np.abs(errors).mean()),
            "rmse": float(np.sqrt(np.square(errors).mean())),
            "test_months": test_len,
            "last_year": last.year, "target_year": end.year,
            "training_start": first.isoformat(),
            "sources": list(history["Sources"].iloc[-1]),
            "model_features": ["xu thế thời gian", "mùa vụ tháng", "khu vực"],
        },
    }
