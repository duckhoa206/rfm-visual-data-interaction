"""Filter bar sticky: Region → Country (drill-down) + Date + Segment + scope panel."""

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, dcc, html, no_update

from src.shared import data_service


def _initial_store(options: dict) -> dict:
    return {
        "regions": options["regions"],
        "countries": options["countries"],
        "start": pd.Timestamp(options["date_min"]).date().isoformat(),
        "end": pd.Timestamp(options["date_max"]).date().isoformat(),
        "segments": options["segments"],
        "data_sources": options["data_sources"],
    }


def layout(options: dict) -> html.Div:
    """Thanh filter dính trên cùng khi cuộn. Store chỉ lưu params (không lưu DataFrame)."""
    date_min = pd.Timestamp(options["date_min"]).date()
    date_max = pd.Timestamp(options["date_max"]).date()
    return html.Div(
        [
            dcc.Store(id="filter-store", data=_initial_store(options)),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Khu vực", className="filter-label"),
                            dcc.Dropdown(
                                id="region-dd",
                                options=options["regions"],
                                value=options["regions"],
                                multi=True,
                                placeholder="Chọn khu vực...",
                            ),
                        ],
                        md=3,
                    ),
                    dbc.Col(
                        [
                            html.Label("Quốc gia (drill-down)", className="filter-label"),
                            dcc.Dropdown(
                                id="country-dd",
                                options=options["countries"],
                                value=options["countries"],
                                multi=True,
                                placeholder="Chọn quốc gia...",
                            ),
                        ],
                        md=3,
                    ),
                    dbc.Col(
                        [
                            html.Label("Khoảng thời gian", className="filter-label"),
                            dcc.DatePickerRange(
                                id="date-range",
                                min_date_allowed=date_min,
                                max_date_allowed=date_max,
                                start_date=date_min,
                                end_date=date_max,
                                display_format="DD/MM/YYYY",
                            ),
                        ],
                        md=3,
                    ),
                    dbc.Col(
                        [
                            html.Label("Phân khúc khách hàng (RFM)", className="filter-label"),
                            dcc.Dropdown(
                                id="segment-dd",
                                options=options["segments"],
                                value=options["segments"],
                                multi=True,
                                placeholder="Chọn phân khúc...",
                            ),
                        ],
                        md=3,
                    ),
                    dbc.Col(
                        [
                            html.Label("Nguồn dữ liệu", className="filter-label"),
                            dcc.Dropdown(
                                id="data-source-dd",
                                options=options["data_sources"],
                                value=options["data_sources"],
                                multi=True,
                                placeholder="Chọn nguồn...",
                            ),
                        ],
                        md=3,
                    ),
                ],
                class_name="g-2",
            ),
            html.Div(
                [
                    html.Span("PHẠM VI PHÂN TÍCH", className="scope-caption"),
                    html.Span(["Đơn hàng: ", html.B(id="scope-orders")], className="scope-item"),
                    html.Span(["Khách hàng: ", html.B(id="scope-customers")], className="scope-item"),
                ],
                className="scope-panel",
            ),
        ],
        className="filter-bar",
        id="filters",
    )


def register_callbacks(app, orders: pd.DataFrame, rfm: pd.DataFrame) -> None:
    """CB-FILTER-1 drill-down Region→Country, CB-FILTER-2 lưu store, CB-SCOPE đếm phạm vi."""

    @app.callback(
        Output("country-dd", "options"),
        Output("country-dd", "value"),
        Input("region-dd", "value"),
        Input("data-source-dd", "value"),
        prevent_initial_call=True,
    )
    def _drill_down_countries(regions, data_sources):
        # Đổi Region thì reset Country về all (spec FR-03): tránh kẹt subset cũ
        # khiến chọn lại Region mà dataset không khôi phục (bug review Phase 4).
        if not regions:
            return [], []
        countries = data_service.get_countries_for_regions(
            orders, regions, data_sources=data_sources
        )
        return countries, countries

    @app.callback(
        Output("filter-store", "data"),
        Input("region-dd", "value"),
        Input("country-dd", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("segment-dd", "value"),
        Input("data-source-dd", "value"),
    )
    def _save_store(regions, countries, start, end, segments, data_sources):
        return {
            "regions": regions,
            "countries": countries,
            "start": start,
            "end": end,
            "segments": segments,
            "data_sources": data_sources,
        }

    @app.callback(
        Output("scope-orders", "children"),
        Output("scope-customers", "children"),
        Input("filter-store", "data"),
    )
    def _update_scope(store):
        if not store:
            return no_update, no_update
        orders_f, rfm_f = data_service.apply_filters(
            orders,
            rfm,
            regions=store.get("regions"),
            countries=store.get("countries"),
            start_date=store.get("start"),
            end_date=store.get("end"),
            segments=store.get("segments"),
            data_sources=store.get("data_sources"),
        )
        return f"{len(orders_f):,}", f"{rfm_f['Customer ID'].nunique():,}"
