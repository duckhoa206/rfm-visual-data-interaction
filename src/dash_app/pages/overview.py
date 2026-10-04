"""Trang chính: KPI + 2 biểu đồ tổng quan + bảng RFM (gộp, bỏ tiêu đề thừa)."""

import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dash_table, dcc, html, no_update, register_page

from src.dash_app.components.charts import (
    RFM_COLUMNS,
    blank_figure,
    build_bar_category,
    build_line_monthly,
    kpi_card,
)
from src.dash_app.config import PAGE_META
from src.dash_app.shared_data import ORDERS, RFM
from src.shared import data_service

register_page(__name__, **PAGE_META["overview"])


def layout() -> html.Div:
    return html.Div([
        dbc.Row([
            dbc.Col(kpi_card("Tổng doanh thu", "kpi-sales"), md=6),
            dbc.Col(kpi_card("Tổng lợi nhuận", "kpi-profit"), md=6),
            dbc.Col(kpi_card("Số đơn hàng", "kpi-orders"), md=6),
            dbc.Col(kpi_card("Số khách hàng", "kpi-customers"), md=6),
        ], class_name="g-2 kpi-row"),
        dbc.Card(dbc.CardBody([
            html.H5("Doanh thu theo danh mục", className="chart-title"),
            dcc.Graph(id="bar-cat", config={"displaylogo": False}, style={"height": 300}),
            html.H5("Xu hướng doanh thu theo tháng", className="chart-title"),
            dcc.Graph(id="line-month", config={"displaylogo": False}, style={"height": 300}),
            dbc.Alert(id="overview-alert", color="warning", is_open=False),
        ]), className="section-card"),
        html.Div([
            html.H5("Chi tiết khách hàng RFM", className="chart-title"),
            dash_table.DataTable(
                id="rfm-table",
                columns=[{"name": c, "id": c} for c in RFM_COLUMNS],
                page_size=10, sort_action="native", filter_action="native",
                style_table={"overflowX": "auto"},
                style_header={"backgroundColor": "#18253A", "color": "#E8EEF8", "fontWeight": "bold"},
                style_cell={"backgroundColor": "#111C2E", "color": "#E8EEF8", "border": "1px solid #253753"},
            ),
        ], className="section-card"),
    ])


@callback(
    Output("kpi-sales", "children"),
    Output("kpi-profit", "children"),
    Output("kpi-orders", "children"),
    Output("kpi-customers", "children"),
    Input("filter-store", "data"),
)
def _update_kpis(store):
    if not store:
        return no_update, no_update, no_update, no_update
    orders_f, rfm_f = data_service.apply_filters(
        ORDERS, RFM, regions=store.get("regions"), countries=store.get("countries"),
        start_date=store.get("start"), end_date=store.get("end"),
        segments=store.get("segments"),
        data_sources=store.get("data_sources"))
    return (
        f"${orders_f['Sales'].sum():,.0f}",
        f"${orders_f['Profit'].sum():,.0f}",
        f"{orders_f['Order ID'].nunique():,}",
        f"{rfm_f['Customer ID'].nunique():,}",
    )


@callback(
    Output("bar-cat", "figure"),
    Output("line-month", "figure"),
    Output("overview-alert", "children"),
    Output("overview-alert", "is_open"),
    Input("filter-store", "data"),
)
def _update_overview(store):
    if not store:
        return no_update, no_update, no_update, no_update
    orders_f, _ = data_service.apply_filters(
        ORDERS, RFM, regions=store.get("regions"), countries=store.get("countries"),
        start_date=store.get("start"), end_date=store.get("end"),
        segments=store.get("segments"),
        data_sources=store.get("data_sources"))
    if orders_f.empty:
        return blank_figure(), blank_figure(), "Không có dữ liệu khớp với bộ lọc.", True
    return build_bar_category(orders_f), build_line_monthly(orders_f), "", False


@callback(Output("rfm-table", "data"), Input("filter-store", "data"))
def _update_table(store):
    if not store:
        return no_update
    _, rfm_f = data_service.apply_filters(
        ORDERS, RFM, regions=store.get("regions"), countries=store.get("countries"),
        start_date=store.get("start"), end_date=store.get("end"),
        segments=store.get("segments"),
        data_sources=store.get("data_sources"))
    return rfm_f[RFM_COLUMNS].to_dict("records")
