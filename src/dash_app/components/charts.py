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

from src.shared.theme import apply_chart_theme

RFM_COLUMNS = ["Customer ID", "Country", "Recency", "Frequency", "Monetary", "RFM_Score", "Segment"]


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
        .resample("MS")["Sales"].sum().reset_index()
    )
    fig = px.line(monthly, x="Order Date", y="Sales", markers=True)
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


def build_forecast_figure(orders_filtered: pd.DataFrame) -> tuple:
    """Trả về (figure, caption). Cần >= 3 tháng dữ liệu."""
    monthly = (
        orders_filtered.set_index("Order Date")
        .resample("MS")["Sales"].sum().reset_index()
    )
    if len(monthly) < 3:
        return None, None
    monthly["t"] = np.arange(len(monthly))
    model = LinearRegression().fit(monthly[["t"]], monthly["Sales"])
    future_t = np.arange(len(monthly), len(monthly) + 3)
    future_dates = pd.date_range(
        monthly["Order Date"].max() + pd.DateOffset(months=1), periods=3, freq="MS")
    future_sales = model.predict(future_t.reshape(-1, 1))
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["Order Date"], y=monthly["Sales"],
        mode="lines+markers", name="Thực tế"))
    fig.add_trace(go.Scatter(
        x=future_dates, y=future_sales,
        mode="lines+markers", name="Dự báo", line=dict(dash="dash")))
    apply_chart_theme(fig)
    caption = (
        f"Xu hướng trung bình: {model.coef_[0]:+,.0f} đồng/tháng "
        f"(hồi quy tuyến tính trên {len(monthly)} tháng, dự báo 3 tháng tiếp theo)."
    )
    return fig, caption
