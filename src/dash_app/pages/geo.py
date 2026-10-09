"""Trang phụ: phân tích địa lý (dashboard 3 biểu đồ, không dropdown)."""

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, ctx, dcc, html, no_update, register_page

from src.dash_app.components.charts import blank_figure, build_geo_figure
from src.dash_app.config import PAGE_META
from src.dash_app.shared_data import ORDERS, RFM
from src.shared import data_service

register_page(__name__, **PAGE_META["geo"])


def layout() -> html.Div:
    return html.Div([
        html.H4("Phân tích", className="page-title"),
        dbc.Alert(id="geo-alert", color="warning", is_open=False, class_name="mb-2"),
        # Hàng 1: bản đồ cần full-width (rộng để thấy các quốc gia)
        dbc.Card(dbc.CardBody([
            html.Div([html.H5("Bản đồ doanh thu theo quốc gia", className="chart-title"), html.Button([html.I(className="bi bi-arrows-fullscreen"), " Mở rộng"], id="geo-expand-map", n_clicks=0, className="chart-expand")], className="chart-head"),
            html.P("Màu đậm = doanh thu cao, hover để xem số liệu từng nước",
                  className="section-subtitle mb-2"),
            dcc.Graph(id="geo-choropleth", config={"displaylogo": False},
                      style={"height": 480}),
        ]), className="section-card"),
        # Hàng 2: treemap cần rộng hơn (7) + heatmap gọn (5)
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(dbc.CardBody([
                        html.Div([html.H5("Cơ cấu Quốc gia / Danh mục", className="chart-title"), html.Button([html.I(className="bi bi-arrows-fullscreen"), " Mở rộng"], id="geo-expand-treemap", n_clicks=0, className="chart-expand")], className="chart-head"),
                        html.P("Ô to = doanh thu lớn, lồng 3 cấp Khu vực → Quốc gia → Danh mục",
                              className="section-subtitle mb-2"),
                        dcc.Graph(id="geo-treemap", config={"displaylogo": False},
                                  style={"height": 420}),
                    ]), className="section-card h-100"),
                    xs=12, lg=7,
                ),
                dbc.Col(
                    dbc.Card(dbc.CardBody([
                        html.Div([html.H5("Doanh thu Khu vực × Danh mục", className="chart-title"), html.Button([html.I(className="bi bi-arrows-fullscreen"), " Mở rộng"], id="geo-expand-heatmap", n_clicks=0, className="chart-expand")], className="chart-head"),
                        html.P("Ma trận màu — hàng là khu vực, cột là danh mục",
                              className="section-subtitle mb-2"),
                        dcc.Graph(id="geo-heatmap", config={"displaylogo": False},
                                  style={"height": 420}),
                    ]), className="section-card h-100"),
                    xs=12, lg=5,
                ),
            ],
            class_name="g-2",
        ),
        dbc.Modal([dbc.ModalHeader(dbc.ModalTitle(id="geo-modal-title")), dbc.ModalBody(dcc.Graph(id="geo-modal-graph", config={"displaylogo": False}, style={"height": "72vh"}))], id="geo-chart-modal", is_open=False, size="xl", centered=True, scrollable=True),
    ])


@callback(
    Output("geo-choropleth", "figure"),
    Output("geo-treemap", "figure"),
    Output("geo-heatmap", "figure"),
    Output("geo-alert", "children"),
    Output("geo-alert", "is_open"),
    Input("filter-store", "data"),
)
def _update(store):
    if not store:
        return no_update, no_update, no_update, no_update, no_update
    orders_f, _ = data_service.apply_filters(
        ORDERS, RFM, regions=store.get("regions"), countries=store.get("countries"),
        start_date=store.get("start"), end_date=store.get("end"),
        segments=store.get("segments"),
        data_sources=store.get("data_sources"))
    if orders_f.empty:
        blank = blank_figure()
        return blank, blank, blank, "Không có dữ liệu khớp với bộ lọc.", True
    return (
        build_geo_figure("choropleth", orders_f),
        build_geo_figure("treemap", orders_f),
        build_geo_figure("heatmap", orders_f),
        "", False,
    )


@callback(
    Output("geo-chart-modal", "is_open"), Output("geo-modal-title", "children"), Output("geo-modal-graph", "figure"),
    Input("geo-expand-map", "n_clicks"), Input("geo-expand-treemap", "n_clicks"), Input("geo-expand-heatmap", "n_clicks"), Input("geo-chart-modal", "is_open"),
    State("geo-choropleth", "figure"), State("geo-treemap", "figure"), State("geo-heatmap", "figure"), prevent_initial_call=True,
)
def _toggle_modal(_map, _tree, _heat, _open, map_fig, tree_fig, heat_fig):
    if ctx.triggered_id == "geo-chart-modal":
        return False, no_update, no_update
    charts = {"geo-expand-map": ("Bản đồ doanh thu theo quốc gia", map_fig), "geo-expand-treemap": ("Cơ cấu quốc gia / danh mục", tree_fig), "geo-expand-heatmap": ("Doanh thu khu vực × danh mục", heat_fig)}
    title, figure = charts[ctx.triggered_id]
    return True, title, figure
