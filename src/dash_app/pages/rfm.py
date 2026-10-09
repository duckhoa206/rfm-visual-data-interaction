"""Trang phụ: phân khúc khách hàng RFM (dashboard 3 biểu đồ + hành động đề xuất)."""

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, ctx, dcc, html, no_update, register_page

from src.dash_app.components.charts import blank_figure, build_rfm_figure
from src.dash_app.config import PAGE_META
from src.dash_app.shared_data import ORDERS, RFM
from src.shared import data_service

register_page(__name__, **PAGE_META["rfm"])


def layout() -> html.Div:
    return html.Div([
        html.H4("Phân khúc khách hàng RFM", className="page-title"),
        dbc.Alert(id="rfm-alert", color="warning", is_open=False, class_name="mb-2"),
        # Hàng 1: Scatter cần rộng (8) + Pie gọn (4)
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(dbc.CardBody([
                        html.Div([html.H5("Tần suất × Chi tiêu", className="chart-title"), html.Button([html.I(className="bi bi-arrows-fullscreen"), " Mở rộng"], id="rfm-expand-scatter", n_clicks=0, className="chart-expand")], className="chart-head"),
                        dcc.Graph(id="rfm-scatter", config={"displaylogo": False},
                                  style={"height": 400}),
                    ]), className="section-card h-100"),
                    xs=12, lg=8,
                ),
                dbc.Col(
                    dbc.Card(dbc.CardBody([
                        html.Div([html.H5("Tỷ trọng phân khúc", className="chart-title"), html.Button([html.I(className="bi bi-arrows-fullscreen"), " Mở rộng"], id="rfm-expand-pie", n_clicks=0, className="chart-expand")], className="chart-head"),
                        dcc.Graph(id="rfm-pie", config={"displaylogo": False},
                                  style={"height": 400}),
                    ]), className="section-card h-100"),
                    xs=12, lg=4,
                ),
            ],
            class_name="g-2 mb-2",
        ),
        # Hàng 2: Box full-width (cần ngang để so sánh phân phối)
        dbc.Card(dbc.CardBody([
            html.Div([html.H5("Phân phối chi tiêu theo phân khúc", className="chart-title"), html.Button([html.I(className="bi bi-arrows-fullscreen"), " Mở rộng"], id="rfm-expand-box", n_clicks=0, className="chart-expand")], className="chart-head"),
            dcc.Graph(id="rfm-box", config={"displaylogo": False},
                      style={"height": 360}),
        ]), className="section-card"),
        dbc.Modal([dbc.ModalHeader(dbc.ModalTitle(id="rfm-modal-title")), dbc.ModalBody(dcc.Graph(id="rfm-modal-graph", config={"displaylogo": False}, style={"height": "72vh"}))], id="rfm-chart-modal", is_open=False, size="xl", centered=True),
    ])


@callback(
    Output("rfm-scatter", "figure"),
    Output("rfm-pie", "figure"),
    Output("rfm-box", "figure"),
    Output("rfm-alert", "children"),
    Output("rfm-alert", "is_open"),
    Input("filter-store", "data"),
)
def _update(store):
    if not store:
        return no_update, no_update, no_update, no_update, no_update
    _, rfm_f = data_service.apply_filters(
        ORDERS, RFM, regions=store.get("regions"), countries=store.get("countries"),
        start_date=store.get("start"), end_date=store.get("end"),
        segments=store.get("segments"),
        data_sources=store.get("data_sources"))
    if rfm_f.empty:
        blank = blank_figure()
        return blank, blank, blank, "Không có khách hàng nào khớp với bộ lọc.", True
    return (
        build_rfm_figure("scatter", rfm_f),
        build_rfm_figure("pie", rfm_f),
        build_rfm_figure("box", rfm_f),
        "", False,
    )


@callback(
    Output("rfm-chart-modal", "is_open"), Output("rfm-modal-title", "children"), Output("rfm-modal-graph", "figure"),
    Input("rfm-expand-scatter", "n_clicks"), Input("rfm-expand-pie", "n_clicks"), Input("rfm-expand-box", "n_clicks"), Input("rfm-chart-modal", "is_open"),
    State("rfm-scatter", "figure"), State("rfm-pie", "figure"), State("rfm-box", "figure"), prevent_initial_call=True,
)
def _toggle_modal(_scatter, _pie, _box, _open, scatter_fig, pie_fig, box_fig):
    if ctx.triggered_id == "rfm-chart-modal":
        return False, no_update, no_update
    charts = {"rfm-expand-scatter": ("Tần suất × chi tiêu", scatter_fig), "rfm-expand-pie": ("Tỷ trọng phân khúc", pie_fig), "rfm-expand-box": ("Phân phối chi tiêu theo phân khúc", box_fig)}
    title, figure = charts[ctx.triggered_id]
    return True, title, figure
