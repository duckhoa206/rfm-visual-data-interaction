"""Trang phụ: phân khúc khách hàng RFM (1 dropdown chọn 1 trong 3 biểu đồ)."""

import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html, no_update, register_page

from src.dash_app.components.charts import blank_figure, build_rfm_figure
from src.dash_app.config import PAGE_META
from src.dash_app.shared_data import ORDERS, RFM
from src.shared import data_service

register_page(__name__, **PAGE_META["rfm"])

RFM_OPTIONS = [
    {"label": "Tỷ trọng phân khúc", "value": "pie"},
    {"label": "Tần suất × Chi tiêu", "value": "scatter"},
    {"label": "Phân phối chi tiêu", "value": "box"},
]


def layout() -> html.Div:
    return html.Div([
        dbc.Card(dbc.CardBody([
            html.H4("Phân khúc khách hàng RFM", className="page-title"),
            dcc.Dropdown(
                id="rfm-chart-select", options=RFM_OPTIONS,
                value="pie", clearable=False),
            dbc.Alert(id="rfm-alert", color="warning", is_open=False),
            dcc.Graph(id="rfm-chart", config={"displaylogo": False}, style={"height": 480}),
        ]), className="section-card"),
    ])


@callback(
    Output("rfm-chart", "figure"),
    Output("rfm-alert", "children"),
    Output("rfm-alert", "is_open"),
    Input("filter-store", "data"),
    Input("rfm-chart-select", "value"),
)
def _update(store, chart):
    if not store:
        return no_update, no_update, no_update
    _, rfm_f = data_service.apply_filters(
        ORDERS, RFM, regions=store.get("regions"), countries=store.get("countries"),
        start_date=store.get("start"), end_date=store.get("end"),
        segments=store.get("segments"))
    if rfm_f.empty:
        return blank_figure(), "Không có khách hàng nào khớp với bộ lọc.", True
    return build_rfm_figure(chart or "pie", rfm_f), "", False
