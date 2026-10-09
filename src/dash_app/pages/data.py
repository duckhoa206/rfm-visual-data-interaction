"""Trang Dữ liệu: chi tiết khách hàng RFM theo bộ lọc chung."""

import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dash_table, html, no_update, register_page

from src.dash_app.components.charts import RFM_COLUMNS
from src.dash_app.config import PAGE_META
from src.dash_app.shared_data import ORDERS, RFM
from src.shared import data_service

register_page(__name__, **PAGE_META["data"])


def layout() -> html.Div:
    return html.Div([
        html.H4("Dữ liệu", className="page-title"),
        dbc.Card(dbc.CardBody([
            html.H5("Chi tiết khách hàng RFM", className="chart-title"),
            dash_table.DataTable(
                id="rfm-table",
                columns=[
                    {"name": c, "id": c, "type": "numeric",
                     "format": {"specifier": ",.0f"}}
                    if c in ("Recency", "Frequency", "Monetary", "RFM_Score")
                    else {"name": c, "id": c}
                    for c in RFM_COLUMNS
                ],
                page_action="native",
                page_size=10,
                sort_action="native",
                sort_mode="single",
                filter_action="none",
                fixed_rows={"headers": True},
                style_table={
                    "overflowX": "auto", "overflowY": "auto",
                    "maxHeight": "420px", "border": "none",
                },
                style_header={
                    "backgroundColor": "#F8FAFC", "color": "#475569",
                    "fontWeight": "700", "fontSize": "11px",
                    "textTransform": "uppercase", "letterSpacing": ".04em",
                    "padding": "10px 12px",
                    "border": "none", "borderBottom": "2px solid #E2E8F0",
                    "whiteSpace": "nowrap",
                },
                style_cell={
                    "backgroundColor": "#FFFFFF", "color": "#0F172A",
                    "fontSize": "13px", "padding": "9px 12px",
                    "border": "none", "borderBottom": "1px solid #F1F5F9",
                    "whiteSpace": "nowrap", "textAlign": "left",
                    "fontFamily": '"Segoe UI", -apple-system, Roboto, Arial, sans-serif',
                },
                style_cell_conditional=[
                    {"if": {"column_id": c}, "textAlign": "right",
                     "fontVariantNumeric": "tabular-nums"}
                    for c in ("Recency", "Frequency", "Monetary", "RFM_Score")
                ] + [
                    {"if": {"column_id": "Customer ID"},
                     "fontWeight": "600", "color": "#0C4A6E"},
                    {"if": {"column_id": "Segment"}, "fontWeight": "600"},
                ],
                style_data_conditional=[
                    {"if": {"row_index": "odd"},
                     "backgroundColor": "#F8FAFC"},
                ],
            ),
        ]), className="section-card"),
    ])


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
