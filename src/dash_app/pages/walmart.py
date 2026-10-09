"""Trang chuyên đề: Phân tích Chuỗi siêu thị Walmart & Kinh tế Vĩ mô."""

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, ctx, dcc, html, no_update, register_page

from src.dash_app.components.charts import (
    blank_figure,
    build_walmart_correlation,
    build_walmart_holiday_impact,
    build_walmart_markdown_impact,
    build_walmart_store_types,
    kpi_card,
)
from src.dash_app.config import PAGE_META
from src.dash_app.shared_data import WALMART

register_page(__name__, **PAGE_META["walmart"])


def layout() -> html.Div:
    type_options = [{"label": "Tất cả loại siêu thị", "value": "ALL"}] + [
        {"label": f"Loại {t}", "value": t}
        for t in (sorted(WALMART["Type"].dropna().unique()) if not WALMART.empty else ["A", "B", "C"])
    ]

    return html.Div([
        html.Div([
            html.H4("Phân tích chuỗi siêu thị Walmart", className="page-title"),
            html.P(
                "So sánh doanh số tuần với giá xăng, mức giá chung, tỷ lệ thất nghiệp, giảm giá và tuần lễ.",
                className="section-subtitle mb-2",
            ),
        ]),

        # Bộ lọc nội bộ cho trang Walmart
        dbc.Card(dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Loại siêu thị", className="filter-label fw-bold small text-secondary"),
                    dcc.Dropdown(
                        id="walmart-type-filter",
                        options=type_options,
                        value="ALL",
                        clearable=False,
                        className="pro-dropdown",
                    ),
                ], xs=12, md=4),
                dbc.Col([
                    html.Div([
                        html.Span("Dữ liệu: doanh số tuần, yếu tố kinh tế và thông tin cửa hàng", className="text-muted small"),
                    ], className="mt-4 pt-1"),
                ], xs=12, md=8),
            ], class_name="align-items-center"),
        ]), className="section-card mb-2 p-2"),

        # Hàng KPI
        dbc.Row([
            dbc.Col(kpi_card("Tổng doanh số tuần", "walmart-kpi-sales"), xs=12, sm=6, md=3),
            dbc.Col(kpi_card("Số siêu thị", "walmart-kpi-stores"), xs=12, sm=6, md=3),
            dbc.Col(kpi_card("Doanh số trung bình/tuần", "walmart-kpi-avg"), xs=12, sm=6, md=3),
            dbc.Col(kpi_card("Tăng doanh số tuần lễ", "walmart-kpi-lift"), xs=12, sm=6, md=3),
        ], className="g-2 kpi-row mb-2"),

        # Hàng 1: Ma trận Tương quan Vĩ mô + Hiệu ứng Dịp lễ
        dbc.Row([
            dbc.Col(
                dbc.Card(dbc.CardBody([
                    html.Div([html.H5("Mối liên hệ giữa doanh số và các yếu tố", className="chart-title"), html.Button([html.I(className="bi bi-arrows-fullscreen"), " Mở rộng"], id="walmart-expand-corr", n_clicks=0, className="chart-expand")], className="chart-head"),
                    html.P("Màu đậm cho thấy mối liên hệ mạnh hơn giữa các chỉ số.",
                           className="section-subtitle mb-2"),
                    dcc.Graph(id="walmart-corr-graph", config={"displaylogo": False}, style={"height": 380}),
                ]), className="section-card h-100"),
                xs=12, lg=6,
            ),
            dbc.Col(
                dbc.Card(dbc.CardBody([
                    html.Div([html.H5("Doanh số: tuần thường và tuần lễ", className="chart-title"), html.Button([html.I(className="bi bi-arrows-fullscreen"), " Mở rộng"], id="walmart-expand-holiday", n_clicks=0, className="chart-expand")], className="chart-head"),
                    html.P("So sánh doanh số trung bình giữa tuần thường và tuần lễ.",
                           className="section-subtitle mb-2"),
                    dcc.Graph(id="walmart-holiday-graph", config={"displaylogo": False}, style={"height": 380}),
                ]), className="section-card h-100"),
                xs=12, lg=6,
            ),
        ], className="g-2 mb-2"),

        # Hàng 2: Quy mô Cửa hàng + Khuyến mãi Markdown
        dbc.Row([
            dbc.Col(
                dbc.Card(dbc.CardBody([
                    html.Div([html.H5("Diện tích cửa hàng và doanh số", className="chart-title"), html.Button([html.I(className="bi bi-arrows-fullscreen"), " Mở rộng"], id="walmart-expand-store", n_clicks=0, className="chart-expand")], className="chart-head"),
                    html.P("Mỗi điểm là một siêu thị; màu thể hiện loại cửa hàng.",
                           className="section-subtitle mb-2"),
                    dcc.Graph(id="walmart-store-graph", config={"displaylogo": False}, style={"height": 380}),
                ]), className="section-card h-100"),
                xs=12, lg=6,
            ),
            dbc.Col(
                dbc.Card(dbc.CardBody([
                    html.Div([html.H5("Giá trị giảm giá theo chương trình", className="chart-title"), html.Button([html.I(className="bi bi-arrows-fullscreen"), " Mở rộng"], id="walmart-expand-markdown", n_clicks=0, className="chart-expand")], className="chart-head"),
                    html.P("Tổng giá trị giảm giá của 5 chương trình.",
                           className="section-subtitle mb-2"),
                    dcc.Graph(id="walmart-markdown-graph", config={"displaylogo": False}, style={"height": 380}),
                ]), className="section-card h-100"),
                xs=12, lg=6,
            ),
        ], className="g-2 mb-2"),

        # Bảng Insight Nghiệp vụ
        dbc.Card(dbc.CardBody([
            html.H6("💡 Insight Nghiệp vụ Chuỗi bán lẻ Walmart:", className="text-secondary fw-bold"),
            dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th("Chủ đề phân tích", style={"width": "22%"}),
                        html.Th("Phát hiện từ Dữ liệu thực tế", style={"width": "43%"}),
                        html.Th("Hành động / Khuyến nghị Quản trị", style={"width": "35%"}),
                    ])
                ]),
                html.Tbody([
                    html.Tr([
                        html.Td(html.Strong("Yếu tố Kinh tế Vĩ mô")),
                        html.Td("Tương quan giữa Giá xăng / CPI / Thất nghiệp với Doanh số rất thấp (-0.02 đến -0.03). Tiêu dùng tại siêu thị tổng hợp là nhu cầu thiết yếu ít co giãn."),
                        html.Td("Không cần cắt giảm ngân sách hàng hóa khi xăng tăng; tập trung duy trì giá ổn định cho nhóm nhu yếu phẩm."),
                    ]),
                    html.Tr([
                        html.Td(html.Strong("Hiệu ứng Ngày lễ (Holiday Lift)")),
                        html.Td("Siêu thị Loại A và B ghi nhận doanh thu tăng vọt từ 6.5% – 9.8% trong các tuần lễ hội (Thanksgiving, Christmas). Loại C ít biến động."),
                        html.Td("Tập trung nhân lực và bổ sung tồn kho trước 3 tuần cho các đại siêu thị Loại A; không dồn vốn dư thừa vào Loại C."),
                    ]),
                    html.Tr([
                        html.Td(html.Strong("Quy mô & Loại hình")),
                        html.Td("Diện tích cửa hàng (Size) có tương quan dương mạnh nhất với doanh số (r = 0.24). Siêu thị Loại A đạt năng suất vượt trội."),
                        html.Td("Tối ưu hóa layout trưng bày tại các mặt bằng lớn để khai thác tối đa doanh số trên mỗi foot vuông (sqft)."),
                    ]),
                ])
            ], bordered=True, hover=True, responsive=True, size="sm", className="mt-2 small"),
        ]), className="section-card"),
        dbc.Modal([dbc.ModalHeader(dbc.ModalTitle(id="walmart-modal-title")), dbc.ModalBody(dcc.Graph(id="walmart-modal-graph", config={"displaylogo": False}, style={"height": "72vh"}))], id="walmart-chart-modal", is_open=False, size="xl", centered=True),
    ])


@callback(
    Output("walmart-corr-graph", "figure"),
    Output("walmart-holiday-graph", "figure"),
    Output("walmart-store-graph", "figure"),
    Output("walmart-markdown-graph", "figure"),
    Output("walmart-kpi-sales", "children"),
    Output("walmart-kpi-stores", "children"),
    Output("walmart-kpi-avg", "children"),
    Output("walmart-kpi-lift", "children"),
    Input("walmart-type-filter", "value"),
)
def _update_walmart(selected_type):
    if WALMART.empty:
        blank = blank_figure()
        return blank, blank, blank, blank, "—", "—", "—", "—"

    df = WALMART if selected_type in ("ALL", None) else WALMART[WALMART["Type"] == selected_type]
    if df.empty:
        blank = blank_figure()
        return blank, blank, blank, blank, "—", "—", "—", "—"

    # Tính KPIs
    total_sales = df["Weekly_Sales"].sum()
    n_stores = df["Store"].nunique()
    avg_sales = df["Weekly_Sales"].mean()

    # Tính Holiday Lift
    hol_sales = df[df["IsHoliday"] == True]["Weekly_Sales"].mean()
    non_hol_sales = df[df["IsHoliday"] == False]["Weekly_Sales"].mean()
    lift_pct = ((hol_sales / non_hol_sales) - 1.0) * 100 if non_hol_sales > 0 else 0.0

    return (
        build_walmart_correlation(df),
        build_walmart_holiday_impact(df),
        build_walmart_store_types(df),
        build_walmart_markdown_impact(df),
        f"${total_sales:,.0f}",
        f"{n_stores} siêu thị",
        f"${avg_sales:,.0f} / tuần",
        f"{lift_pct:+.1f}%",
    )


@callback(
    Output("walmart-chart-modal", "is_open"), Output("walmart-modal-title", "children"), Output("walmart-modal-graph", "figure"),
    Input("walmart-expand-corr", "n_clicks"), Input("walmart-expand-holiday", "n_clicks"), Input("walmart-expand-store", "n_clicks"), Input("walmart-expand-markdown", "n_clicks"), Input("walmart-chart-modal", "is_open"),
    State("walmart-corr-graph", "figure"), State("walmart-holiday-graph", "figure"), State("walmart-store-graph", "figure"), State("walmart-markdown-graph", "figure"), prevent_initial_call=True,
)
def _toggle_modal(_corr, _holiday, _store, _markdown, _open, corr_fig, holiday_fig, store_fig, markdown_fig):
    if ctx.triggered_id == "walmart-chart-modal":
        return False, no_update, no_update
    charts = {"walmart-expand-corr": ("Mối liên hệ giữa doanh số và các yếu tố", corr_fig), "walmart-expand-holiday": ("Doanh số: tuần thường và tuần lễ", holiday_fig), "walmart-expand-store": ("Diện tích cửa hàng và doanh số", store_fig), "walmart-expand-markdown": ("Giá trị giảm giá theo chương trình", markdown_fig)}
    title, figure = charts[ctx.triggered_id]
    return True, title, figure
