"""Trang chính: KPI và biểu đồ tổng quan hiệu suất bán hàng."""

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, ctx, dcc, html, no_update, register_page

from src.dash_app.components.charts import (
    blank_figure,
    build_bar_category,
    build_line_monthly,
    build_manager_performance,
    kpi_card,
)
from src.dash_app.config import PAGE_META
from src.dash_app.shared_data import ORDERS, RFM
from src.shared import data_service

register_page(__name__, **PAGE_META["overview"])


def layout() -> html.Div:
    return html.Div([
        html.H4("Tổng quan hiệu suất bán hàng", className="page-title"),
        # KPI: 4 thẻ 1 hàng trên desktop, 2x2 trên mobile
        dbc.Row([
            dbc.Col(kpi_card("Tổng doanh thu", "kpi-sales"), xs=6, md=3),
            dbc.Col(kpi_card("Tổng lợi nhuận", "kpi-profit"), xs=6, md=3),
            dbc.Col(kpi_card("Số đơn hàng", "kpi-orders"), xs=6, md=3),
            dbc.Col(kpi_card("Số khách hàng", "kpi-customers"), xs=6, md=3),
        ], class_name="g-2 kpi-row"),
        dbc.Alert(id="overview-alert", color="warning", is_open=False, class_name="mb-2"),
        # 2 biểu đồ cạnh nhau, mỗi chart 1 card riêng
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(dbc.CardBody([
                        html.Div([html.H5("Doanh thu theo danh mục", className="chart-title"), html.Button([html.I(className="bi bi-arrows-fullscreen"), " Mở rộng"], id="overview-expand-category", n_clicks=0, className="chart-expand")], className="chart-head"),
                        dcc.Graph(id="bar-cat", config={"displaylogo": False}, style={"height": 340}),
                    ]), className="section-card h-100"),
                    xs=12, md=6,
                ),
                dbc.Col(
                    dbc.Card(dbc.CardBody([
                        html.Div([html.H5("Xu hướng doanh thu theo tháng", className="chart-title"), html.Button([html.I(className="bi bi-arrows-fullscreen"), " Mở rộng"], id="overview-expand-month", n_clicks=0, className="chart-expand")], className="chart-head"),
                        dcc.Graph(id="line-month", config={"displaylogo": False}, style={"height": 340}),
                    ]), className="section-card h-100"),
                    xs=12, md=6,
                ),
            ],
            class_name="g-2 mb-2",
        ),
        # Biểu đồ hiệu suất Quản lý khu vực (từ bảng People)
        dbc.Card(dbc.CardBody([
            html.Div([html.H5("Hiệu suất Quản lý Khu vực (Regional Manager Performance)", className="chart-title"), html.Button([html.I(className="bi bi-arrows-fullscreen"), " Mở rộng"], id="overview-expand-manager", n_clicks=0, className="chart-expand")], className="chart-head"),
            html.P("So sánh Doanh thu ($) và Lợi nhuận ($) của từng Quản lý phụ trách vùng thị trường (nguồn People nối vào Đơn hàng)",
                   className="section-subtitle mb-2"),
            dcc.Graph(id="bar-manager", config={"displaylogo": False}, style={"height": 360}),
        ]), className="section-card mb-2"),
        dbc.Modal([dbc.ModalHeader(dbc.ModalTitle(id="overview-modal-title")), dbc.ModalBody(dcc.Graph(id="overview-modal-graph", config={"displaylogo": False}, style={"height": "72vh"}))], id="overview-chart-modal", is_open=False, size="xl", centered=True),
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
    Output("bar-manager", "figure"),
    Output("overview-alert", "children"),
    Output("overview-alert", "is_open"),
    Input("filter-store", "data"),
)
def _update_overview(store):
    if not store:
        return no_update, no_update, no_update, no_update, no_update
    orders_f, _ = data_service.apply_filters(
        ORDERS, RFM, regions=store.get("regions"), countries=store.get("countries"),
        start_date=store.get("start"), end_date=store.get("end"),
        segments=store.get("segments"),
        data_sources=store.get("data_sources"))
    if orders_f.empty:
        return blank_figure(), blank_figure(), blank_figure(), "Không có dữ liệu khớp với bộ lọc.", True
    return (
        build_bar_category(orders_f),
        build_line_monthly(orders_f),
        build_manager_performance(orders_f),
        "",
        False,
    )


@callback(
    Output("overview-chart-modal", "is_open"), Output("overview-modal-title", "children"), Output("overview-modal-graph", "figure"),
    Input("overview-expand-category", "n_clicks"), Input("overview-expand-month", "n_clicks"), Input("overview-expand-manager", "n_clicks"), Input("overview-chart-modal", "is_open"),
    State("bar-cat", "figure"), State("line-month", "figure"), State("bar-manager", "figure"), prevent_initial_call=True,
)
def _toggle_modal(_category, _month, _manager, _open, category_fig, month_fig, manager_fig):
    if ctx.triggered_id == "overview-chart-modal":
        return False, no_update, no_update
    charts = {"overview-expand-category": ("Doanh thu theo danh mục", category_fig), "overview-expand-month": ("Xu hướng doanh thu theo tháng", month_fig), "overview-expand-manager": ("Hiệu suất quản lý khu vực", manager_fig)}
    title, figure = charts[ctx.triggered_id]
    return True, title, figure
