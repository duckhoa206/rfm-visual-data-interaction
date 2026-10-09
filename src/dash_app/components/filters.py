"""Thanh bộ lọc gọn với chọn nhiều + "Tất cả", drill-down Region → Country."""

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, dcc, html, no_update

from src.shared import data_service

ALL = "ALL"


def _single_options(items: list, all_label: str) -> list:
    """Options dropdown đơn: dòng "Tất cả" đầu tiên + các giá trị."""
    return [{"label": all_label, "value": ALL}] + [
        {"label": str(v), "value": v} for v in items
    ]


def _initial_store(options: dict) -> dict:
    return {
        "regions": None,
        "countries": None,
        "start": pd.Timestamp(options["date_min"]).date().isoformat(),
        "end": pd.Timestamp(options["date_max"]).date().isoformat(),
        "segments": None,
        "data_sources": None,
    }


def _field(label: str, control) -> html.Div:
    """1 ô lọc: label text + control cao 40px."""
    return html.Div(
        [
            html.Label(label, className="filter-label"),
            html.Div(control, className="filter-control"),
        ],
        className="filter-field",
    )


def layout(options: dict) -> html.Div:
    """Grid 5 control: 2+3+3+2+2 = 12 cột, gọn 1 hàng trên desktop."""
    date_min = pd.Timestamp(options["date_min"]).date()
    date_max = pd.Timestamp(options["date_max"]).date()
    return html.Div(
        [
            dcc.Store(id="filter-store", data=_initial_store(options)),
            dbc.Row(
                [
                    dbc.Col(
                        _field(
                            "Khu vực",
                            dcc.Dropdown(
                                id="region-dd",
                                options=_single_options(options["regions"], "Tất cả khu vực"),
                                value=[ALL],
                                multi=True,
                                clearable=False,
                                searchable=True,
                                closeOnSelect=False,
                                labels={"select_all": "Select All", "deselect_all": "Deselect All", "clear_selection": "Clear selection"},
                                placeholder="Chọn khu vực…",
                                className="pro-dropdown",
                            ),
                        ),
                        xs=12, sm=6, lg=2, class_name="filter-col",
                    ),
                    dbc.Col(
                        _field(
                            "Quốc gia",
                            dcc.Dropdown(
                                id="country-dd",
                                options=_single_options(options["countries"], "Tất cả quốc gia"),
                                value=[ALL],
                                multi=True,
                                clearable=False,
                                searchable=True,
                                closeOnSelect=False,
                                labels={"select_all": "Select All", "deselect_all": "Deselect All", "clear_selection": "Clear selection"},
                                placeholder="Tìm quốc gia…",
                                className="pro-dropdown",
                            ),
                        ),
                        xs=12, sm=6, lg=3, class_name="filter-col",
                    ),
                    dbc.Col(
                        _field(
                            "Khoảng thời gian",
                            dcc.DatePickerRange(
                                id="date-range",
                                min_date_allowed=date_min,
                                max_date_allowed=date_max,
                                start_date=date_min,
                                end_date=date_max,
                                display_format="DD/MM/YYYY",
                                className="pro-date",
                                start_date_placeholder_text="Từ ngày",
                                end_date_placeholder_text="Đến ngày",
                            ),
                        ),
                        xs=12, sm=6, lg=3, class_name="filter-col",
                    ),
                    dbc.Col(
                        _field(
                            "Phân khúc RFM",
                            dcc.Dropdown(
                                id="segment-dd",
                                options=_single_options(options["segments"], "Tất cả phân khúc"),
                                value=[ALL],
                                multi=True,
                                clearable=False,
                                searchable=True,
                                closeOnSelect=False,
                                labels={"select_all": "Select All", "deselect_all": "Deselect All", "clear_selection": "Clear selection"},
                                placeholder="Chọn phân khúc…",
                                className="pro-dropdown",
                            ),
                        ),
                        xs=12, sm=6, lg=2, class_name="filter-col",
                    ),
                    dbc.Col(
                        _field(
                            "Nguồn dữ liệu",
                            dcc.Dropdown(
                                id="data-source-dd",
                                options=_single_options(options["data_sources"], "Tất cả nguồn"),
                                value=[ALL],
                                multi=True,
                                clearable=False,
                                searchable=True,
                                closeOnSelect=False,
                                labels={"select_all": "Select All", "deselect_all": "Deselect All", "clear_selection": "Clear selection"},
                                placeholder="Chọn nguồn…",
                                className="pro-dropdown",
                            ),
                        ),
                        xs=12, sm=6, lg=2, class_name="filter-col",
                    ),
                ],
                class_name="g-2 filter-row",
            ),
        ],
        className="filter-bar",
        id="filters",
    )


def _as_list(value) -> list | None:
    """Chuẩn hóa dropdown multi: rỗng hoặc có ALL nghĩa là không giới hạn."""
    if value is None or value == ALL or (isinstance(value, list) and (not value or ALL in value)):
        return None
    return value if isinstance(value, list) else [value]


def register_callbacks(app, orders: pd.DataFrame, rfm: pd.DataFrame) -> None:
    @app.callback(
        Output("region-dd", "value", allow_duplicate=True),
        Output("country-dd", "value", allow_duplicate=True),
        Output("segment-dd", "value", allow_duplicate=True),
        Output("data-source-dd", "value", allow_duplicate=True),
        Input("region-dd", "value"),
        Input("country-dd", "value"),
        Input("segment-dd", "value"),
        Input("data-source-dd", "value"),
        prevent_initial_call=True,
    )
    def _normalize_multi_values(region, country, segment, data_source):
        """Giữ option ALL độc quyền khi người dùng chọn nhiều mục."""
        values = [region, country, segment, data_source]
        normalized = []
        changed = False
        for value in values:
            if isinstance(value, list) and ALL in value and len(value) > 1:
                normalized.append([ALL])
                changed = True
            else:
                normalized.append(no_update)
        return tuple(normalized) if changed else (no_update, no_update, no_update, no_update)

    """CB-FILTER-1 drill-down Region→Country, CB-FILTER-2 lưu store,
    CB-FILTER-3 reset, CB-SCOPE đếm phạm vi + badge đang lọc."""

    @app.callback(
        Output("country-dd", "options", allow_duplicate=True),
        Output("country-dd", "value", allow_duplicate=True),
        Input("region-dd", "value"),
        Input("data-source-dd", "value"),
        prevent_initial_call=True,
    )
    def _drill_down_countries(region, data_source):
        # Đổi Region thì reset Country về "Tất cả" (tránh kẹt subset cũ).
        regions = _as_list(region)
        data_sources = _as_list(data_source)
        countries = data_service.get_countries_for_regions(
            orders, regions or sorted(orders["Region"].unique()),
            data_sources=data_sources,
        )
        return _single_options(countries, "Tất cả quốc gia"), [ALL]

    @app.callback(
        Output("filter-store", "data"),
        Input("region-dd", "value"),
        Input("country-dd", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("segment-dd", "value"),
        Input("data-source-dd", "value"),
    )
    def _save_store(region, country, start, end, segment, data_source):
        return {
            "regions": _as_list(region),
            "countries": _as_list(country),
            "start": start,
            "end": end,
            "segments": _as_list(segment),
            "data_sources": _as_list(data_source),
        }

    @app.callback(
        Output("region-dd", "value", allow_duplicate=True),
        Output("country-dd", "value", allow_duplicate=True),
        Output("segment-dd", "value", allow_duplicate=True),
        Output("data-source-dd", "value", allow_duplicate=True),
        Output("date-range", "start_date", allow_duplicate=True),
        Output("date-range", "end_date", allow_duplicate=True),
        Input("filter-reset", "n_clicks"),
        prevent_initial_call=True,
    )
    def _reset_filters(_n):
        date_min = pd.Timestamp(orders["Order Date"].min()).date().isoformat()
        date_max = pd.Timestamp(orders["Order Date"].max()).date().isoformat()
        return [ALL], [ALL], [ALL], [ALL], date_min, date_max

    @app.callback(
        Output("scope-orders", "children"),
        Output("scope-customers", "children"),
        Output("scope-lines", "children"),
        Output("filter-active-count", "children"),
        Output("filter-active-count", "className"),
        Input("filter-store", "data"),
    )
    def _update_scope(store):
        if not store:
            return no_update, no_update, no_update, no_update, no_update
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
        # Đếm số chiều đang lọc (không tính ngày mặc định full-range).
        full_start = pd.Timestamp(orders["Order Date"].min()).date().isoformat()
        full_end = pd.Timestamp(orders["Order Date"].max()).date().isoformat()
        active = sum([
            bool(store.get("regions")),
            bool(store.get("countries")),
            bool(store.get("segments")),
            bool(store.get("data_sources")),
            bool(store.get("start") != full_start or store.get("end") != full_end),
        ])
        badge = "Mặc định" if active == 0 else f"{active} đang lọc"
        cls = "filter-count-badge" + ("" if active == 0 else " is-active")
        return (
            f"{orders_f['Order ID'].nunique():,}",
            f"{rfm_f['Customer ID'].nunique():,}",
            f"{len(orders_f):,}",
            badge,
            cls,
        )
