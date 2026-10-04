"""Hàm dựng biểu đồ + thẻ KPI dùng chung cho mọi trang.

Đổi style một lần ở đây (hoặc assets/style.css) là áp dụng toàn bộ.
Các trang chỉ gọi hàm, không tự code figure.
"""

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

from src.shared.theme import apply_chart_theme

RFM_COLUMNS = [
    "Customer ID", "Data Source", "Country", "Recency", "Frequency",
    "Monetary", "RFM_Score", "Segment",
]


def kpi_card(title: str, value_id: str) -> dbc.Card:
    return dbc.Card(
        dbc.CardBody([
            html.Div(title, className="kpi-title"),
            html.Div("—", id=value_id, className="kpi-value"),
        ]),
        className="kpi-card",
    )


def blank_figure() -> go.Figure:
    return go.Figure()


def build_bar_category(orders_filtered: pd.DataFrame) -> go.Figure:
    by_cat = orders_filtered.groupby("Category", as_index=False)["Sales"].sum()
    fig = px.bar(by_cat, x="Category", y="Sales", color="Category")
    return apply_chart_theme(fig)


def build_line_monthly(orders_filtered: pd.DataFrame) -> go.Figure:
    monthly = (
        orders_filtered.set_index("Order Date")
        .resample("MS")
        .agg(Sales=("Sales", "sum"), Rows=("Sales", "size"))
        .reset_index()
    )
    monthly.loc[monthly["Rows"] == 0, "Sales"] = np.nan
    fig = px.line(monthly, x="Order Date", y="Sales", markers=True)
    fig.update_traces(connectgaps=False)
    fig.update_traces(line=dict(width=3))
    return apply_chart_theme(fig)


def build_geo_figure(chart: str, orders_filtered: pd.DataFrame) -> go.Figure:
    if chart == "treemap":
        fig = px.treemap(
            orders_filtered, path=["Region", "Country", "Category"], values="Sales")
    elif chart == "heatmap":
        pivot = orders_filtered.pivot_table(
            index="Region", columns="Category", values="Sales",
            aggfunc="sum", fill_value=0)
        fig = px.imshow(pivot, text_auto=".0f", color_continuous_scale="Oranges")
    else:
        by_country = orders_filtered.groupby("Country", as_index=False)["Sales"].sum()
        fig = px.choropleth(
            by_country, locations="Country", locationmode="country names",
            color="Sales", color_continuous_scale="Blues")
    return apply_chart_theme(fig)


def build_rfm_figure(chart: str, rfm_filtered: pd.DataFrame) -> go.Figure:
    if chart == "scatter":
        fig = px.scatter(
            rfm_filtered, x="Frequency", y="Monetary", color="Segment",
            size="Monetary", hover_data=["Customer ID", "Recency"])
    elif chart == "box":
        fig = px.box(rfm_filtered, x="Segment", y="Monetary", color="Segment")
    else:
        seg_count = rfm_filtered["Segment"].value_counts().reset_index()
        seg_count.columns = ["Segment", "Count"]
        fig = px.pie(seg_count, names="Segment", values="Count", hole=0.4)
    return apply_chart_theme(fig)


def build_forecast_figure(orders_filtered: pd.DataFrame, test_months: int = 3, forecast_months: int = 3) -> tuple:
    """
    Trả về (figure, caption).
    - Chuỗi thời gian: tháng có giao dịch (bỏ qua tháng trống).
    - Phân chia Train/Test theo thời gian để đánh giá (MAE, RMSE).
    - Huấn luyện trên toàn bộ dữ liệu để dự báo tương lai.
    """
    if orders_filtered.empty:
        return None, None

    orders_df = orders_filtered.copy()
    orders_df["Order Date"] = pd.to_datetime(orders_df["Order Date"])

    monthly = (
        orders_df.set_index("Order Date")
        .resample("MS")
        .agg(Sales=("Sales", "sum"), Rows=("Sales", "size"))
        .reset_index()
    )
    monthly = monthly[monthly["Rows"] > 0].reset_index(drop=True)

    # Cần tối thiểu dữ liệu train + test
    if len(monthly) < (test_months + 2):
        return None, "Không đủ dữ liệu tháng để huấn luyện và kiểm thử mô hình (cần tối thiểu 5 tháng)."

    # Trục thời gian số học t (tính theo khoảng cách tháng so với tháng đầu tiên)
    first_month = monthly["Order Date"].iloc[0]
    monthly["t"] = (
        (monthly["Order Date"].dt.year - first_month.year) * 12
        + monthly["Order Date"].dt.month
        - first_month.month
    )

    # 1. Phân chia Train / Test theo thời gian
    train_df = monthly.iloc[:-test_months].copy()
    test_df = monthly.iloc[-test_months:].copy()

    # Huấn luyện mô hình đánh giá trên tập Train
    eval_model = LinearRegression().fit(train_df[["t"]], train_df["Sales"])
    test_df["pred_sales"] = eval_model.predict(test_df[["t"]])

    # Đánh giá độ chính xác
    mae = mean_absolute_error(test_df["Sales"], test_df["pred_sales"])
    rmse = np.sqrt(mean_squared_error(test_df["Sales"], test_df["pred_sales"]))

    # 2. Huấn luyện mô hình trên toàn bộ chuỗi để dự báo tương lai
    full_model = LinearRegression().fit(monthly[["t"]], monthly["Sales"])

    last_t = monthly["t"].iloc[-1]
    future_t = np.arange(last_t + 1, last_t + 1 + forecast_months)
    future_dates = pd.date_range(
        monthly["Order Date"].max() + pd.DateOffset(months=1),
        periods=forecast_months,
        freq="MS"
    )
    future_sales = full_model.predict(pd.DataFrame({"t": future_t}))

    # 3. Dựng biểu đồ trực quan
    fig = go.Figure()

    # Thực tế Train
    fig.add_trace(go.Scatter(
        x=train_df["Order Date"], y=train_df["Sales"],
        mode="lines+markers", name="Thực tế (Huấn luyện)",
        line=dict(color="#1f77b4", width=2)
    ))

    # Thực tế Test
    fig.add_trace(go.Scatter(
        x=test_df["Order Date"], y=test_df["Sales"],
        mode="lines+markers", name=f"Thực tế (Kiểm thử {test_months} tháng)",
        line=dict(color="#2ca02c", width=2)
    ))

    # Đường đối chiếu dự đoán trên tập Test
    fig.add_trace(go.Scatter(
        x=test_df["Order Date"], y=test_df["pred_sales"],
        mode="lines+markers", name="Dự đoán đối chiếu (Test)",
        line=dict(color="#ff7f0e", width=2, dash="dash")
    ))

    # Đường dự báo tương lai
    connect_dates = [monthly["Order Date"].iloc[-1]] + list(future_dates)
    connect_sales = [monthly["Sales"].iloc[-1]] + list(future_sales)

    fig.add_trace(go.Scatter(
        x=connect_dates, y=connect_sales,
        mode="lines+markers", name=f"Dự báo {forecast_months} tháng tới",
        line=dict(color="#d62728", width=2.5, dash="dot")
    ))

    apply_chart_theme(fig)
    fig.update_layout(
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    caption = (
        f"Đánh giá kiểm thử ({test_months} tháng gần nhất): MAE = {mae:,.0f} | RMSE = {rmse:,.0f}. "
        f"Xu hướng dài hạn: {full_model.coef_[0]:+,.0f} doanh thu/tháng "
        f"(hồi quy tuyến tính trên {len(monthly)} tháng có giao dịch)."
    )

    return fig, caption