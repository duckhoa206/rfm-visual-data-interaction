"""Trang chính: KPI và biểu đồ tổng quan hiệu suất bán hàng."""

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, ctx, dcc, html, no_update, register_page

from src.dash_app.components.charts import (
    blank_figure,
    build_bar_category,
    build_line_monthly,
    build_region_performance,
    kpi_card,
)
from src.dash_app.config import PAGE_META
from src.dash_app.shared_data import ORDERS, RFM
from src.shared import data_service

register_page(__name__, **PAGE_META["overview"])


def layout() -> html.Div:
    return html.Div([
        dcc.Store(id="overview-selection", data={"categories": [], "region": None}),
        html.H4("Tổng quan hiệu suất bán hàng", className="page-title"),
        dbc.Row([
            dbc.Col(kpi_card("Tổng doanh thu", "kpi-sales"), xs=6, md=3),
            dbc.Col(kpi_card("Tổng lợi nhuận", "kpi-profit"), xs=6, md=3),
            dbc.Col(kpi_card("Số đơn hàng", "kpi-orders"), xs=6, md=3),
            dbc.Col(kpi_card("Số khách hàng", "kpi-customers"), xs=6, md=3),
        ], class_name="g-2 kpi-row"),
        dbc.Alert(id="overview-alert", color="warning", is_open=False, class_name="mb-2"),
        html.Div([
            html.Span(
                "Nhấp vào cột danh mục hoặc khu vực để liên kết các biểu đồ.",
                id="overview-selection-label",
            ),
            html.Button(
                "Xóa lựa chọn",
                id="overview-selection-reset",
                n_clicks=0,
                disabled=True,
                className="filter-reset",
            ),
        ], className="overview-selection-bar"),
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
        dbc.Card(dbc.CardBody([
            html.Div([html.H5("Doanh thu và lợi nhuận theo khu vực (tối đa 12)", className="chart-title"), html.Button([html.I(className="bi bi-arrows-fullscreen"), " Mở rộng"], id="overview-expand-region", n_clicks=0, className="chart-expand")], className="chart-head"),
            html.P("Nhấp vào khu vực để xem cơ cấu danh mục và xu hướng doanh thu tương ứng.",
                   className="section-subtitle mb-2"),
            dcc.Graph(id="bar-region", config={"displaylogo": False}, style={"height": 360}),
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
    Output("bar-region", "figure"),
    Output("overview-alert", "children"),
    Output("overview-alert", "is_open"),
    Output("overview-selection", "data"),
    Output("overview-selection-label", "children"),
    Output("overview-selection-reset", "disabled"),
    Input("filter-store", "data"),
    Input("bar-cat", "clickData"),
    Input("bar-region", "clickData"),
    Input("overview-selection-reset", "n_clicks"),
    State("overview-selection", "data"),
)
def _update_overview(store, category_click, region_click, _reset, selection):
    if not store:
        return (no_update,) * 8
    orders_f, _ = data_service.apply_filters(
        ORDERS, RFM, regions=store.get("regions"), countries=store.get("countries"),
        start_date=store.get("start"), end_date=store.get("end"),
        segments=store.get("segments"),
        data_sources=store.get("data_sources"))
    if orders_f.empty:
        empty_selection = {"categories": [], "region": None}
        return (
            blank_figure(), blank_figure(), blank_figure(),
            "Không có dữ liệu khớp với bộ lọc.", True,
            empty_selection,
            "Nhấp vào cột danh mục hoặc khu vực để liên kết các biểu đồ.",
            True,
        )

    selection = dict(selection or {})
    categories = list(selection.get("categories") or [])
    region = selection.get("region")
    trigger = ctx.triggered_id
    if trigger in ("filter-store", "overview-selection-reset"):
        categories, region = [], None
    elif trigger == "bar-cat" and category_click:
        clicked = category_click.get("points", [{}])[0].get("x")
        if clicked in set(orders_f["Category"].dropna()):
            categories.remove(clicked) if clicked in categories else categories.append(clicked)
    elif trigger == "bar-region" and region_click:
        clicked = region_click.get("points", [{}])[0].get("y")
        if clicked in set(orders_f["Region"].dropna()):
            region = None if clicked == region else clicked

    valid_categories = set(orders_f["Category"].dropna())
    categories = [category for category in categories if category in valid_categories]
    if region not in set(orders_f["Region"].dropna()):
        region = None

    category_scope = orders_f if region is None else orders_f[orders_f["Region"] == region]
    categories = [
        category for category in categories
        if category in set(category_scope["Category"].dropna())
    ]
    line_scope = category_scope
    if categories:
        line_scope = line_scope[line_scope["Category"].isin(categories)]
    region_scope = orders_f
    if categories:
        region_scope = region_scope[region_scope["Category"].isin(categories)]

    labels = []
    if region:
        labels.append(f"Khu vực: {region}")
    if categories:
        labels.append(f"Danh mục: {', '.join(categories)}")
    label = " | ".join(labels) if labels else "Nhấp vào cột danh mục hoặc khu vực để liên kết các biểu đồ."
    selection = {"categories": categories, "region": region}
    return (
        build_bar_category(category_scope, selected_categories=categories),
        build_line_monthly(line_scope, categories=categories),
        build_region_performance(region_scope, selected_region=region),
        "",
        False,
        selection,
        label,
        not bool(categories or region),
    )


@callback(
    Output("overview-chart-modal", "is_open"), Output("overview-modal-title", "children"), Output("overview-modal-graph", "figure"),
    Input("overview-expand-category", "n_clicks"), Input("overview-expand-month", "n_clicks"), Input("overview-expand-region", "n_clicks"), Input("overview-chart-modal", "is_open"),
    State("bar-cat", "figure"), State("line-month", "figure"), State("bar-region", "figure"), prevent_initial_call=True,
)
def _toggle_modal(_category, _month, _region, _open, category_fig, month_fig, region_fig):
    if ctx.triggered_id == "overview-chart-modal":
        return False, no_update, no_update
    charts = {"overview-expand-category": ("Doanh thu theo danh mục", category_fig), "overview-expand-month": ("Xu hướng doanh thu theo tháng", month_fig), "overview-expand-region": ("Doanh thu và lợi nhuận theo khu vực", region_fig)}
    title, figure = charts[ctx.triggered_id]
    return True, title, figure
