"""Module phân tích & dự báo chuỗi thời gian doanh thu dài hạn đến năm 2030."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error


def load_and_prepare_monthly(filepath: str = "data/processed/monthly_sales.csv") -> pd.DataFrame:
    """Đọc dữ liệu doanh thu theo tháng và tạo trục thời gian t."""
    df = pd.read_csv(filepath)
    df["Month"] = pd.to_datetime(df["Month"])
    df = df.groupby("Month", as_index=False).agg({"Sales": "sum", "Profit": "sum", "Orders": "sum"})
    df = df.sort_values("Month").reset_index(drop=True)
    df["t"] = np.arange(len(df))
    return df


def train_and_evaluate(df: pd.DataFrame, test_months: int = 12, target_year: int = 2030):
    """
    Huấn luyện mô hình chuỗi thời gian kết hợp Trend + Seasonality,
    kiểm thử trên các tháng gần nhất và dự báo dài hạn đến năm 2030.
    """
    last_date = df["Month"].iloc[-1]
    end_date = pd.Timestamp(f"{target_year}-12-01")
    if end_date <= last_date:
        end_date = last_date + pd.DateOffset(years=5)

    future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), end=end_date, freq="MS")
    n_future = len(future_dates)

    test_len = min(test_months, max(3, len(df) // 5))
    train_df = df.iloc[:-test_len].copy()
    test_df = df.iloc[-test_len:].copy()

    # Mùa vụ tháng
    m_factors = train_df.groupby(train_df["Month"].dt.month)["Sales"].mean()
    m_overall = train_df["Sales"].mean() if train_df["Sales"].mean() > 0 else 1.0
    season_dict = (m_factors / m_overall).to_dict()

    slope, intercept = np.polyfit(train_df["t"].values, train_df["Sales"].values, 1)
    test_factors = np.array([season_dict.get(m, 1.0) for m in test_df["Month"].dt.month])
    pred_test = np.maximum(0, (intercept + slope * test_df["t"].values) * test_factors)

    # Baseline Naive
    naive_pred = [train_df["Sales"].iloc[-1]] + list(test_df["Sales"].iloc[:-1])

    def calc_metrics(y_true, y_pred):
        mae = float(mean_absolute_error(y_true, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
        mape = float(mean_absolute_percentage_error(y_true, y_pred) * 100)
        return {"MAE": mae, "RMSE": rmse, "MAPE_%": mape}

    metrics = {
        "Trend_Seasonality": calc_metrics(test_df["Sales"], pred_test),
        "Baseline_Naive": calc_metrics(test_df["Sales"], naive_pred),
    }

    # Huấn luyện trên toàn bộ dữ liệu
    all_slope, all_intercept = np.polyfit(df["t"].values, df["Sales"].values, 1)
    all_factors = df.groupby(df["Month"].dt.month)["Sales"].mean()
    all_overall = df["Sales"].mean() if df["Sales"].mean() > 0 else 1.0
    all_season_dict = (all_factors / all_overall).to_dict()

    first_date = df["Month"].iloc[0]
    future_t = np.array((future_dates.year - first_date.year) * 12 + future_dates.month - first_date.month)
    future_factors = np.array([all_season_dict.get(m, 1.0) for m in future_dates.month])

    base_forecast = np.maximum(0, (all_intercept + all_slope * future_t) * future_factors)
    opt_forecast = base_forecast * np.linspace(1.02, 1.25, n_future)
    pess_forecast = base_forecast * np.linspace(0.98, 0.80, n_future)

    future_df = pd.DataFrame({
        "Month": future_dates,
        "base_forecast": base_forecast,
        "opt_forecast": opt_forecast,
        "pess_forecast": pess_forecast,
        "t": future_t,
    })

    test_df_copy = test_df.copy()
    test_df_copy["pred_model"] = pred_test
    test_df_copy["pred_naive"] = naive_pred

    return {
        "train": train_df,
        "test": test_df_copy,
        "future": future_df,
        "metrics": metrics,
        "target_year": target_year,
    }


def create_forecast_figure(results: dict) -> go.Figure:
    """Tạo biểu đồ Plotly gồm thực tế, so sánh test và 3 kịch bản dự báo tương lai đến 2030."""
    train_df = results["train"]
    test_df = results["test"]
    future_df = results["future"]
    target_year = results.get("target_year", 2030)

    fig = go.Figure()

    # 1. Doanh thu thực tế (Train)
    fig.add_trace(go.Scatter(
        x=train_df["Month"], y=train_df["Sales"],
        mode="lines", name="Lịch sử (Train)",
        line=dict(color="#0284C7", width=2),
    ))

    # 2. Doanh thu thực tế (Test)
    fig.add_trace(go.Scatter(
        x=test_df["Month"], y=test_df["Sales"],
        mode="lines+markers", name=f"Thực tế (Test {len(test_df)} tháng)",
        line=dict(color="#059669", width=2.5),
    ))

    # 3. Dự đoán trên tập Test
    fig.add_trace(go.Scatter(
        x=test_df["Month"], y=test_df["pred_model"],
        mode="lines", name="Dự đoán Đối chiếu (Test)",
        line=dict(color="#D97706", width=2, dash="dash"),
    ))

    connect_dates = [train_df["Month"].iloc[-1] if test_df.empty else test_df["Month"].iloc[-1]] + list(future_df["Month"])
    last_val = train_df["Sales"].iloc[-1] if test_df.empty else test_df["Sales"].iloc[-1]
    connect_pess = [last_val] + list(future_df["pess_forecast"])
    connect_opt = [last_val] + list(future_df["opt_forecast"])
    connect_base = [last_val] + list(future_df["base_forecast"])

    # 4. Kịch bản Thận trọng
    fig.add_trace(go.Scatter(
        x=connect_dates, y=connect_pess,
        mode="lines", name="Kịch bản Thận trọng (-15%)",
        line=dict(color="#EF4444", width=1.5, dash="dash"),
    ))

    # 5. Kịch bản Lạc quan
    fig.add_trace(go.Scatter(
        x=connect_dates, y=connect_opt,
        mode="lines", name="Kịch bản Lạc quan (+20%)",
        line=dict(color="#10B981", width=1.5, dash="dash"),
        fill="tonexty", fillcolor="rgba(2, 132, 199, 0.08)",
    ))

    # 6. Kịch bản Cơ sở
    fig.add_trace(go.Scatter(
        x=connect_dates, y=connect_base,
        mode="lines", name=f"Kịch bản Cơ sở (Đến {target_year})",
        line=dict(color="#0B3B82", width=3),
    ))

    fig.update_layout(
        title=f"Biểu đồ Dự báo Doanh thu Dài hạn & 3 Kịch bản Tăng trưởng Đến Năm {target_year}",
        xaxis_title="Thời gian (Tháng)",
        yaxis_title="Doanh thu ($)",
        hovermode="x unified",
        template="plotly_white",
        yaxis=dict(tickformat="$,.0f"),
    )
    return fig