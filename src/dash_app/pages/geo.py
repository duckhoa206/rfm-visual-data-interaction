"""Trang phụ: phân tích địa lý (1 dropdown chọn 1 trong 3 biểu đồ)."""

import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html, no_update, register_page

from src.dash_app.components.charts import blank_figure, build_geo_figure
from src.dash_app.config import PAGE_META
from src.dash_app.shared_data import ORDERS, RFM
from src.shared import data_service

register_page(__name__, **PAGE_META["geo"])

GEO_OPTIONS = [
    {"label": "Bản đồ theo quốc gia", "value": "choropleth"},
    {"label": "Cơ cấu Quốc gia / Danh mục", "value": "treemap"},
    {"label": "Doanh thu Khu vực × Danh mục", "value": "heatmap"},
]


def layout() -> html.Div:
    return html.Div([
        dbc.Card(dbc.CardBody([
            html.H4("Phân tích địa lý", className="page-title"),
            dcc.Dropdown(
                id="geo-chart-select", options=GEO_OPTIONS,
                value="choropleth", clearable=False),
            dbc.Alert(id="geo-alert", color="warning", is_open=False),
            dcc.Graph(id="geo-chart", config={"displaylogo": False}, style={"height": 480}),
        ]), className="section-card"),
    ])


@callback(
    Output("geo-chart", "figure"),
    Output("geo-alert", "children"),
    Output("geo-alert", "is_open"),
    Input("filter-store", "data"),
    Input("geo-chart-select", "value"),
)
def _update(store, chart):
    if not store:
        return no_update, no_update, no_update
    orders_f, _ = data_service.apply_filters(
        ORDERS, RFM, regions=store.get("regions"), countries=store.get("countries"),
        start_date=store.get("start"), end_date=store.get("end"),
        segments=store.get("segments"),
        data_sources=store.get("data_sources"))
    if orders_f.empty:
        return blank_figure(), "Không có dữ liệu khớp với bộ lọc.", True
    return build_geo_figure(chart or "choropleth", orders_f), "", False
