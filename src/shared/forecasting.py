import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error

def load_and_prepare_monthly(filepath: str = "data/processed/monthly_sales.csv") -> pd.DataFrame:
    """Đọc dữ liệu doanh thu theo tháng và tạo trục thời gian t."""
    df = pd.read_csv(filepath)
    df["Month"] = pd.to_datetime(df["Month"])
    df = df.sort_values("Month").reset_index(drop=True)
    df["t"] = np.arange(len(df))
    return df

def train_and_evaluate(df: pd.DataFrame, test_months: int = 3, forecast_horizon: int = 3):
    """
    Huấn luyện mô hình, kiểm thử 3 tháng cuối và dự báo horizon tháng tiếp theo.
    """
    train_df = df.iloc[:-test_months].copy()
    test_df = df.iloc[-test_months:].copy()

    # Huấn luyện trên Train
    model = LinearRegression()
    model.fit(train_df[["t"]], train_df["Sales"])
    test_df["pred_linear"] = model.predict(test_df[["t"]])

    # Baseline Naive (lấy doanh thu tháng liền kề trước đó)
    naive_pred = [train_df["Sales"].iloc[-1]] + list(test_df["Sales"].iloc[:-1])
    test_df["pred_naive"] = naive_pred

    # Tính metrics
    def calc_metrics(y_true, y_pred):
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mape = mean_absolute_percentage_error(y_true, y_pred) * 100
        return {"MAE": mae, "RMSE": rmse, "MAPE_%": mape}

    metrics = {
        "Linear Regression": calc_metrics(test_df["Sales"], test_df["pred_linear"]),
        "Baseline Naive": calc_metrics(test_df["Sales"], naive_pred)
    }

    # Huấn luyện trên toàn bộ dữ liệu để dự báo tương lai
    full_model = LinearRegression()
    full_model.fit(df[["t"]], df["Sales"])

    last_t = df["t"].iloc[-1]
    last_date = df["Month"].iloc[-1]

    future_t = np.arange(last_t + 1, last_t + 1 + forecast_horizon)
    future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=forecast_horizon, freq="MS")
    future_pred = full_model.predict(pd.DataFrame({"t": future_t}))

    future_df = pd.DataFrame({
        "Month": future_dates,
        "forecast": future_pred,
        "t": future_t
    })

    return {
        "train": train_df,
        "test": test_df,
        "future": future_df,
        "metrics": metrics
    }

def create_forecast_figure(results: dict) -> go.Figure:
    """Tạo biểu đồ Plotly gồm thực tế, so sánh test và dự báo tương lai."""
    train_df = results["train"]
    test_df = results["test"]
    future_df = results["future"]

    fig = go.Figure()

    # 1. Doanh thu thực tế (Train)
    fig.add_trace(go.Scatter(
        x=train_df["Month"], y=train_df["Sales"],
        mode="lines+markers", name="Thực tế (Train)",
        line=dict(color="#1f77b4", width=2)
    ))

    # 2. Doanh thu thực tế (Test)
    fig.add_trace(go.Scatter(
        x=test_df["Month"], y=test_df["Sales"],
        mode="lines+markers", name="Thực tế (Test)",
        line=dict(color="#2ca02c", width=2)
    ))

    # 3. Dự đoán trên tập Test
    fig.add_trace(go.Scatter(
        x=test_df["Month"], y=test_df["pred_linear"],
        mode="lines+markers", name="Dự đoán trên Test (Linear)",
        line=dict(color="#ff7f0e", width=2, dash="dash")
    ))

    # 4. Dự báo tương lai
    connect_dates = [train_df["Month"].iloc[-1] if test_df.empty else test_df["Month"].iloc[-1]] + list(future_df["Month"])
    connect_vals = [train_df["Sales"].iloc[-1] if test_df.empty else test_df["Sales"].iloc[-1]] + list(future_df["forecast"])

    fig.add_trace(go.Scatter(
        x=connect_dates, y=connect_vals,
        mode="lines+markers", name="Dự báo 3 tháng tới",
        line=dict(color="#d62728", width=2.5, dash="dot")
    ))

    fig.update_layout(
        title="Biểu đồ Dự báo Doanh thu & So sánh Dự đoán với Thực tế",
        xaxis_title="Thời gian (Tháng)",
        yaxis_title="Doanh thu ($)",
        hovermode="x unified",
        template="plotly_white"
    )
    return fig