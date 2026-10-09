"""Dashboard dự báo với bộ lọc năm độc lập dữ liệu huấn luyện."""

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, State, callback, ctx, dcc, html, no_update, register_page

from src.dash_app.components.charts import (
    blank_figure,
    build_category_forecast_figure,
    build_forecast_scenarios_figure,
    build_quantity_profit_forecast_figure,
    build_regional_forecast_figure,
)
from src.dash_app.config import PAGE_META
from src.dash_app.shared_data import ORDERS, RFM
from src.shared import data_service
from src.shared.forecast_model import comparable_monthly_orders, make_forecast_projection

register_page(__name__, **PAGE_META["forecast"])

DEFAULT_START_YEAR = pd.Timestamp(ORDERS["Order Date"].max()).year + 1
MAX_YEAR = max(2040, DEFAULT_START_YEAR + 10)


def _filtered_orders(store):
    store = store or {}
    orders_f, _ = data_service.apply_filters(
        ORDERS, RFM, regions=store.get("regions"), countries=store.get("countries"),
        start_date=store.get("start"), end_date=store.get("end"),
        segments=store.get("segments"), data_sources=store.get("data_sources"),
    )
    return orders_f


def _period_from_value(value, fallback):
    try:
        start, years = str(value).split(":")
        return {"start_year": int(start), "years": int(years)}
    except (ValueError, TypeError):
        return dict(fallback or {"years": 1})


def _period_choices(orders, period):
    """Khoảng năm luôn có cùng độ dài và nằm trong chuỗi nguồn đang chọn."""
    period = period or {}
    try:
        years = int(period.get("years", 1))
    except (TypeError, ValueError):
        years = 1
    if years not in (1, 3, 5, 10):
        years = 1
    state = {"start_year": DEFAULT_START_YEAR, "years": years}
    if orders.empty:
        return [], None, state

    history = comparable_monthly_orders(orders)
    minimum = history["Order Date"].iloc[0].year
    maximum = MAX_YEAR - years + 1
    default = min(history["Order Date"].iloc[-1].year + 1, maximum)
    try:
        start = int(period.get("start_year", default))
    except (ValueError, TypeError):
        start = default
    # Giá trị cũ khi đổi nguồn không được gây cảnh báo hoặc giữ dropdown rỗng.
    start = default if start < minimum else min(start, maximum)
    state["start_year"] = start
    options = [
        {"label": f"{year} – {year + years - 1}", "value": f"{year}:{years}"}
        for year in range(minimum, maximum + 1)
    ]
    return options, f"{start}:{years}", state


def _forecast_kpi(title, title_id, value_id):
    return dbc.Card(dbc.CardBody([
        html.Div(title, id=title_id, className="kpi-title"),
        html.Div("—", id=value_id, className="kpi-value"),
    ]), className="kpi-card")


def _period_labels(start, end):
    period = str(start.year) if start.year == end.year else f"{start.year}–{end.year}"
    return (
        f"Doanh thu năm {end.year}",
        f"Tổng doanh thu ({period})",
        f"Doanh thu theo năm & Kịch bản ({period})",
        f"Cơ cấu doanh thu theo ngành hàng ({period})",
        f"Doanh thu khu vực trong khoảng ({period})",
        f"Sản lượng & Lợi nhuận ({period})",
        f"Kế hoạch hành động trong giai đoạn {period}",
    )


def _strategy_rows(start, end, last_month):
    months = pd.date_range(max(start, last_month + pd.DateOffset(months=1)), end, freq="MS")
    if not len(months):
        return [html.Tr(html.Td("Khoảng đang chọn chỉ có dữ liệu lịch sử; không có giai đoạn dự phóng.", colSpan=4))]
    phases = [
        ("Tối ưu hóa & Ổn định", "Củng cố khách hàng trung thành; cân đối tồn kho và chiến dịch bán hàng theo dự báo tháng.", "Theo dõi MAE ($/tháng) và sai số tương đối; kiểm tra tồn kho thực tế."),
        ("Mở rộng & Tăng tốc", "Phân bổ nguồn lực theo doanh thu dự báo của từng ngành hàng và khu vực.", "So sánh kịch bản cơ sở, lạc quan và thận trọng trong khoảng chọn."),
        ("Bền vững & Đánh giá", "Rà soát mục tiêu cuối kỳ và điều chỉnh kế hoạch khi có dữ liệu giao dịch mới.", "Dự phòng biến động nhu cầu và chi phí; cập nhật mô hình định kỳ."),
    ]
    count = min(3, len(months))
    rows, offset = [], 0
    for index in range(count):
        length = len(months) // count + (index < len(months) % count)
        first, last = months[offset], months[offset + length - 1]
        title, action, risk = phases[index]
        rows.append(html.Tr([
            html.Td(f"{first:%m/%Y}–{last:%m/%Y}"),
            html.Td(html.Strong(title)), html.Td(action), html.Td(risk),
        ]))
        offset += length
    return rows


def layout() -> html.Div:
    options, selected, period = _period_choices(ORDERS, {"years": 1})
    return html.Div([
        dcc.Store(id="forecast-period-state", data=period),
        html.Div([
            html.H4("Dự báo Doanh thu & Kế hoạch Chiến lược", className="page-title"),
            html.P(
                "Dự báo từ giai đoạn nguồn dữ liệu đồng nhất gần nhất, kết hợp xu thế và mùa vụ tháng "
                "và phân tích đa chiều (Kịch bản, Ngành hàng, Thị trường khu vực, Nhu cầu sản lượng).",
                className="section-subtitle mb-2",
            ),
        ]),
        dbc.Card(dbc.CardBody([
            html.Div([
                html.H5("Khoảng thời gian dự báo", className="chart-title forecast-range-title"),
                html.Div([
                    html.Label("Năm bắt đầu – Năm kết thúc", htmlFor="forecast-period-select", className="filter-label"),
                    dbc.Select(id="forecast-period-select", options=options, value=selected,
                               class_name="forecast-period-select"),
                ], className="forecast-period-field"),
                html.Div([
                    html.Button("3 năm", id="forecast-range-36", n_clicks=0, className="filter-reset"),
                    html.Button("5 năm", id="forecast-range-60", n_clicks=0, className="filter-reset"),
                    html.Button("10 năm", id="forecast-range-120", n_clicks=0, className="filter-reset"),
                    html.Button("Đặt lại", id="forecast-range-reset", n_clicks=0, className="filter-reset"),
                ], className="forecast-range-actions"),
            ], className="forecast-range-toolbar"),
            html.Div([
                html.Div([
                    html.Div([html.Span("Kịch bản lạc quan"), html.Span("0–50%", className="forecast-weight-range")], className="forecast-weight-label"),
                    dcc.Slider(id="forecast-optimistic-slider", min=0, max=0.5, step=0.05, value=0.20,
                               marks={0: "0%", 0.2: "20%", 0.5: "50%"}, tooltip={"placement": "top"}),
                ], className="forecast-weight"),
                html.Div([
                    html.Div([html.Span("Kịch bản thận trọng"), html.Span("0–50%", className="forecast-weight-range")], className="forecast-weight-label"),
                    dcc.Slider(id="forecast-cautious-slider", min=0, max=0.5, step=0.05, value=0.15,
                               marks={0: "0%", 0.15: "15%", 0.5: "50%"}, tooltip={"placement": "top"}),
                ], className="forecast-weight"),
            ], className="forecast-weight-row"),
        ]), className="section-card forecast-range-card"),
        dbc.Alert(id="forecast-alert", color="warning", is_open=False, class_name="mb-3"),

        # KPI tính theo khoảng năm đang chọn.
        dbc.Row([
            dbc.Col(_forecast_kpi("Doanh thu cuối kỳ", "forecast-kpi-end-label", "forecast-kpi-2030"), xs=12, sm=6, md=3),
            dbc.Col(_forecast_kpi("Tổng doanh thu trong khoảng", "forecast-kpi-cum-label", "forecast-kpi-cum"), xs=12, sm=6, md=3),
            dbc.Col(_forecast_kpi("CAGR dự kiến", "forecast-kpi-cagr-label", "forecast-kpi-cagr"), xs=12, sm=6, md=3),
            dbc.Col(_forecast_kpi("Sai số kiểm thử MAE ($/tháng)", "forecast-kpi-mae-label", "forecast-kpi-mae"), xs=12, sm=6, md=3),
        ], className="g-2 kpi-row"),

        # Hàng 2: Biểu đồ chính Dự báo dài hạn 3 Kịch bản
        dbc.Card(dbc.CardBody([
            html.Div([
                html.Div([html.H5("Doanh thu theo năm & Kịch bản", id="forecast-main-title", className="chart-title"), html.Button([html.I(className="bi bi-arrows-fullscreen"), " Mở rộng"], id="forecast-expand-main", n_clicks=0, className="chart-expand")], className="chart-head"),
                html.P(
                    "Tổng hợp doanh thu theo năm để nhìn rõ xu hướng. Dải kịch bản mở rộng dần "
                    "đến +20% / −15% so với cơ sở; không phải khoảng tin cậy thống kê.",
                    className="section-subtitle mb-2",
                ),
            ]),
            dcc.Graph(id="forecast-graph", config={"displaylogo": False}, style={"height": 450}),
        ]), className="section-card"),

        dbc.Card(dbc.CardBody([
            html.Div([
                html.H5("Chi tiết tháng: kiểm thử và mùa vụ", className="chart-title"),
                html.Button([html.I(className="bi bi-arrows-fullscreen"), " Mở rộng"],
                            id="forecast-expand-monthly", n_clicks=0, className="chart-expand"),
            ], className="chart-head"),
            html.P("Hiển thị đúng các tháng trong bộ lọc riêng. "
                   "Dao động theo tháng phản ánh mùa vụ ước lượng; MAE được tính trên dữ liệu kiểm thử lịch sử.",
                   className="section-subtitle mb-2"),
            dcc.Graph(id="forecast-monthly-graph", config={"displaylogo": False},
                      style={"height": 450}),
        ]), className="section-card"),

        # Hàng 3: Hai biểu đồ Phân tích Danh mục & Khu vực
        dbc.Row([
            dbc.Col(
                dbc.Card(dbc.CardBody([
                    html.Div([html.H5("Cơ cấu doanh thu theo ngành hàng", id="forecast-category-title", className="chart-title"), html.Button([html.I(className="bi bi-arrows-fullscreen"), " Mở rộng"], id="forecast-expand-category", n_clicks=0, className="chart-expand")], className="chart-head"),
                    html.P(
                        "Phân bổ dự báo cơ sở theo tỷ trọng ngành hàng trong 12 tháng lịch sử gần nhất; chỉ cộng các tháng đang chọn.",
                        className="section-subtitle mb-2",
                    ),
                    dcc.Graph(id="forecast-category-graph", config={"displaylogo": False}, style={"height": 380}),
                ]), className="section-card h-100"),
                xs=12, lg=6,
            ),
            dbc.Col(
                dbc.Card(dbc.CardBody([
                    html.Div([html.H5("Doanh thu theo khu vực", id="forecast-region-title", className="chart-title"), html.Button([html.I(className="bi bi-arrows-fullscreen"), " Mở rộng"], id="forecast-expand-region", n_clicks=0, className="chart-expand")], className="chart-head"),
                    html.P(
                        "Thực tế và dự báo trong khoảng chọn; phân bổ theo tỷ trọng 12 tháng gần nhất, hiển thị tối đa 6 khu vực.",
                        className="section-subtitle mb-2",
                    ),
                    dcc.Graph(id="forecast-region-graph", config={"displaylogo": False}, style={"height": 380}),
                ]), className="section-card h-100"),
                xs=12, lg=6,
            ),
        ], className="g-2 mb-2"),

        # Hàng 4: Biểu đồ Sản lượng & Lợi nhuận
        dbc.Card(dbc.CardBody([
            html.Div([html.H5("Sản lượng & Lợi nhuận", id="forecast-qp-title", className="chart-title"), html.Button([html.I(className="bi bi-arrows-fullscreen"), " Mở rộng"], id="forecast-expand-quantity", n_clicks=0, className="chart-expand")], className="chart-head"),
            html.P(
                "Từ dự báo cơ sở và tỷ lệ sản lượng/doanh thu, lợi nhuận/doanh thu của 12 tháng lịch sử gần nhất.",
                className="section-subtitle mb-2",
            ),
            dcc.Graph(id="forecast-qp-graph", config={"displaylogo": False}, style={"height": 380}),
        ]), className="section-card"),

        # Hàng 5: Bảng Kế hoạch Chiến lược 3 Giai đoạn
        dbc.Card(dbc.CardBody([
            html.H6("Kế hoạch hành động theo khoảng chọn", id="forecast-plan-title", className="text-secondary fw-bold"),
            dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th("Giai đoạn", style={"width": "16%"}),
                        html.Th("Trọng tâm Chiến lược", style={"width": "22%"}),
                        html.Th("Hành động Nghiệp vụ Cụ thể", style={"width": "42%"}),
                        html.Th("Chỉ tiêu Quản trị Rủi ro", style={"width": "20%"}),
                    ])
                ]),
                html.Tbody(id="forecast-plan-body")
            ], bordered=True, hover=True, responsive=True, size="sm", className="mt-2 small"),

            html.Hr(),
            html.Div([
                html.H6("📌 Phương pháp luận & Lưu ý nguồn dữ liệu:", className="text-secondary fw-bold"),
                html.Ul([
                    html.Li("Huấn luyện trên đoạn tháng liên tục cuối cùng có cùng tập nguồn. Xu thế và hiệu ứng tháng được ước lượng cùng lúc; chỉ dùng mùa vụ khi có ít nhất 2 quan sát cho mỗi tháng."),
                    html.Li("Các biểu đồ và KPI dùng cùng dự báo cơ sở, cùng khoảng năm. Ngành hàng/khu vực giữ tỷ trọng gần nhất; sản lượng/lợi nhuận giữ tỷ lệ gần nhất. Đây là giả định phân bổ, không phải mô hình riêng cho từng nhóm."),
                    html.Li("Bộ lọc riêng lấy từ tháng 1 năm bắt đầu đến hết tháng 12 năm kết thúc; không cắt dữ liệu huấn luyện. MAE không đổi nếu chỉ đổi khoảng xem."),
                    html.Li("Đánh giá mô hình kiểm thử độc lập (Time-based Split) trên các tháng gần nhất để cung cấp chỉ số MAE và RMSE trung thực, khách quan."),
                    html.Li("Nguồn dữ liệu Kaggle 2019–2020 (nếu chọn trong bộ lọc) là tập dữ liệu thử nghiệm có quy mô lớn; khi cần phân tích xu hướng thị trường chuẩn hóa, người dùng nên chọn nguồn Superstore qua bộ lọc nguồn ở thanh điều hướng.")
                ], className="small text-muted mb-0")
            ], className="mt-2 p-3 bg-light rounded")
        ]), className="section-card"),
        dbc.Modal([dbc.ModalHeader(dbc.ModalTitle(id="forecast-modal-title")), dbc.ModalBody(dcc.Graph(id="forecast-modal-graph", config={"displaylogo": False}, style={"height": "72vh"}))], id="forecast-chart-modal", is_open=False, size="xl", centered=True),
    ])


@callback(
    Output("forecast-graph", "figure"),
    Output("forecast-monthly-graph", "figure"),
    Output("forecast-category-graph", "figure"),
    Output("forecast-region-graph", "figure"),
    Output("forecast-qp-graph", "figure"),
    Output("forecast-alert", "children"),
    Output("forecast-alert", "is_open"),
    Output("forecast-kpi-2030", "children"),
    Output("forecast-kpi-cum", "children"),
    Output("forecast-kpi-cagr", "children"),
    Output("forecast-kpi-mae", "children"),
    Output("forecast-kpi-end-label", "children"),
    Output("forecast-kpi-cum-label", "children"),
    Output("forecast-main-title", "children"),
    Output("forecast-category-title", "children"),
    Output("forecast-region-title", "children"),
    Output("forecast-qp-title", "children"),
    Output("forecast-plan-title", "children"),
    Output("forecast-plan-body", "children"),
    Input("filter-store", "data"),
    Input("forecast-period-state", "data"),
    Input("forecast-optimistic-slider", "value"),
    Input("forecast-cautious-slider", "value"),
)
def _update(store, period, optimistic_weight, cautious_weight):
    if not store:
        return (no_update,) * 19

    orders_f = _filtered_orders(store)
    _, _, period = _period_choices(orders_f, period)
    start = pd.Timestamp(period["start_year"], 1, 1)
    end = pd.Timestamp(period["start_year"] + period["years"] - 1, 12, 31)
    labels = _period_labels(start, end)

    blank = blank_figure()
    try:
        projection = make_forecast_projection(
            orders_f,
            start,
            end,
            optimistic_weight=optimistic_weight if optimistic_weight is not None else 0.20,
            cautious_weight=cautious_weight if cautious_weight is not None else 0.15,
        )
    except ValueError as error:
        return (
            blank, blank, blank, blank, blank,
            str(error), True, "—", "—", "—", "—",
        ) + labels + ([],)

    fig_main, _, kpis = build_forecast_scenarios_figure(orders_f, projection=projection)
    fig_monthly, _, _ = build_forecast_scenarios_figure(orders_f, granularity="month", projection=projection)
    fig_cat = build_category_forecast_figure(orders_f, projection=projection)
    fig_reg = build_regional_forecast_figure(orders_f, projection=projection)
    fig_qp = build_quantity_profit_forecast_figure(orders_f, projection=projection)

    # Format KPI values
    val_end = f"${kpis.get('annual_2030', 0):,.0f}"
    val_cum = f"${kpis.get('cum_sales', 0):,.0f}"
    cagr_val = kpis.get("cagr", 0.0)
    val_cagr = f"{cagr_val:+.1f}%/năm" if cagr_val is not None else "—"
    mae_val = kpis.get("mae", 0.0)
    val_mae = f"${mae_val:,.0f}"

    return (
        fig_main, fig_monthly, fig_cat, fig_reg, fig_qp,
        "", False,
        val_end, val_cum, val_cagr, val_mae
    ) + labels + (
        _strategy_rows(start, end, projection["history"]["Order Date"].iloc[-1]),
    )


@callback(
    Output("forecast-period-select", "options"),
    Output("forecast-period-select", "value"),
    Output("forecast-period-select", "disabled"),
    Output("forecast-period-state", "data"),
    Output("forecast-range-36", "className"),
    Output("forecast-range-60", "className"),
    Output("forecast-range-120", "className"),
    Input("filter-store", "data"),
    Input("forecast-period-select", "value"),
    Input("forecast-range-36", "n_clicks"),
    Input("forecast-range-60", "n_clicks"),
    Input("forecast-range-120", "n_clicks"),
    Input("forecast-range-reset", "n_clicks"),
    State("forecast-period-state", "data"),
)
def _sync_period(store, value, _three_years, _five_years, _ten_years, _reset, period):
    period = _period_from_value(value, period)
    if ctx.triggered_id == "forecast-range-reset":
        period = {"years": 1}
    else:
        years = {"forecast-range-36": 3, "forecast-range-60": 5, "forecast-range-120": 10}
        if ctx.triggered_id in years:
            period["years"] = years[ctx.triggered_id]
    options, selected, period = _period_choices(_filtered_orders(store), period)
    classes = tuple("filter-reset is-active" if period["years"] == years else "filter-reset"
                    for years in (3, 5, 10))
    return options, selected, not bool(options), period, *classes


@callback(
    Output("forecast-chart-modal", "is_open"), Output("forecast-modal-title", "children"), Output("forecast-modal-graph", "figure"),
    Input("forecast-expand-main", "n_clicks"), Input("forecast-expand-monthly", "n_clicks"), Input("forecast-expand-category", "n_clicks"), Input("forecast-expand-region", "n_clicks"), Input("forecast-expand-quantity", "n_clicks"), Input("forecast-chart-modal", "is_open"),
    State("forecast-graph", "figure"), State("forecast-monthly-graph", "figure"), State("forecast-category-graph", "figure"), State("forecast-region-graph", "figure"), State("forecast-qp-graph", "figure"), prevent_initial_call=True,
)
def _toggle_modal(_main, _monthly, _category, _region, _quantity, _open, main_fig, monthly_fig, category_fig, region_fig, quantity_fig):
    if ctx.triggered_id == "forecast-chart-modal":
        return False, no_update, no_update
    charts = {
        "forecast-expand-main": ("Dự báo doanh thu dài hạn", main_fig),
        "forecast-expand-monthly": ("Chi tiết kiểm thử và mùa vụ tháng", monthly_fig),
        "forecast-expand-category": ("Dự báo cơ cấu doanh thu theo ngành hàng", category_fig),
        "forecast-expand-region": ("Dự báo tăng trưởng doanh thu theo khu vực", region_fig),
        "forecast-expand-quantity": ("Dự báo sản lượng và lợi nhuận", quantity_fig),
    }
    title, figure = charts[ctx.triggered_id]
    return True, title, figure
