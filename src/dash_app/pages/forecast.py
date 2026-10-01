"""Trang phụ: dự báo doanh thu 3 tháng (hồi quy tuyến tính)."""

import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html, no_update, register_page

from src.dash_app.components.charts import blank_figure, build_forecast_figure
from src.dash_app.config import PAGE_META
from src.dash_app.shared_data import ORDERS, RFM
from src.shared import data_service

register_page(__name__, **PAGE_META["forecast"])


def layout() -> html.Div:
    return html.Div([
        dbc.Card(dbc.CardBody([
            html.H4("Dự báo doanh thu", className="page-title"),
            dbc.Alert(id="forecast-alert", color="info", is_open=False),
            dcc.Graph(id="forecast-graph", config={"displaylogo": False}, style={"height": 360}),
            html.P(id="forecast-caption", className="caption"),
        ]), className="section-card"),
    ])


@callback(
    Output("forecast-graph", "figure"),
    Output("forecast-caption", "children"),
    Output("forecast-alert", "children"),
    Output("forecast-alert", "is_open"),
    Input("filter-store", "data"),
)
def _update(store):
    if not store:
        return no_update, no_update, no_update, no_update
    orders_f, _ = data_service.apply_filters(
        ORDERS, RFM, regions=store.get("regions"), countries=store.get("countries"),
        start_date=store.get("start"), end_date=store.get("end"),
        segments=store.get("segments"))
    if orders_f.empty:
        return blank_figure(), "", "Không có dữ liệu khớp với bộ lọc.", True
    fig, caption = build_forecast_figure(orders_f)
    if fig is None:
        return (blank_figure(), "",
                "Cần ít nhất 3 tháng dữ liệu. Hãy mở rộng khoảng thời gian ở bộ lọc.", True)
    return fig, caption, "", False
