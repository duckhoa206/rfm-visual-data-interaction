"""Trang chuyên đề: Phân tích Trưng bày Hàng hóa & Điểm bán FMCG (BigMart)."""

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, ctx, dcc, html, no_update, register_page

from src.dash_app.components.charts import (
    blank_figure,
    build_bigmart_category_sales,
    build_bigmart_mrp_vs_sales,
    build_bigmart_outlet_performance,
    build_bigmart_visibility_sales,
    kpi_card,
)
from src.dash_app.config import PAGE_META
from src.dash_app.shared_data import BIGMART

register_page(__name__, **PAGE_META["bigmart"])


def layout() -> html.Div:
    tier_options = [{"label": "Tất cả cấp bậc đô thị", "value": "ALL"}] + [
        {"label": f"Khu vực Đô thị {t}", "value": t}
        for t in (sorted(BIGMART["Outlet_Location_Type"].dropna().unique()) if not BIGMART.empty else ["Tier 1", "Tier 2", "Tier 3"])
    ]

    return html.Div([
        html.Div([
            html.H4("Trưng bày Hàng hóa & Điểm bán FMCG (BigMart)", className="page-title"),
            html.P(
                "Phân tích nghệ thuật trưng bày quầy kệ (Item Visibility), cơ cấu định giá niêm yết (Item MRP) "
                "và hiệu quả phân phối theo tầng đô thị (Tier 1–3) trên 8.523 mặt hàng bán lẻ.",
                className="section-subtitle mb-2",
            ),
        ]),

        # Bộ lọc nội bộ cho trang BigMart
        dbc.Card(dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Lọc theo Cấp bậc Đô thị (Tier):", className="filter-label fw-bold small text-secondary"),
                    dcc.Dropdown(
                        id="bigmart-tier-filter",
                        options=tier_options,
                        value="ALL",
                        clearable=False,
                        className="pro-dropdown",
                    ),
                ], xs=12, md=4),
                dbc.Col([
                    html.Div([
                        html.Span("Mô hình dữ liệu: ", className="text-muted small"),
                        html.B("Product Merchandising Mart", className="small text-primary"),
                        html.Span(" (8.523 sản phẩm × Đặc tính hàng hoá × Cấu trúc Điểm bán)", className="text-muted small"),
                    ], className="mt-4 pt-1"),
                ], xs=12, md=8),
            ], class_name="align-items-center"),
        ]), className="section-card mb-2 p-2"),

        # Hàng KPI
        dbc.Row([
            dbc.Col(kpi_card("Tổng Doanh số Điểm bán", "bigmart-kpi-sales"), xs=12, sm=6, md=3),
            dbc.Col(kpi_card("Số Mặt hàng Quan sát", "bigmart-kpi-items"), xs=12, sm=6, md=3),
            dbc.Col(kpi_card("Doanh số TB / Mặt hàng", "bigmart-kpi-avg"), xs=12, sm=6, md=3),
            dbc.Col(kpi_card("Giá Niêm yết (MRP) Bình quân", "bigmart-kpi-mrp"), xs=12, sm=6, md=3),
        ], className="g-2 kpi-row mb-2"),

        # Hàng 1: Giá niêm yết vs Doanh số + Hiệu quả theo Cấp đô thị
        dbc.Row([
            dbc.Col(
                dbc.Card(dbc.CardBody([
                    html.Div([html.H5("Tương quan Giá Niêm yết (MRP) vs Doanh số Bán ra", className="chart-title"), html.Button([html.I(className="bi bi-arrows-fullscreen"), " Mở rộng"], id="bigmart-expand-mrp", n_clicks=0, className="chart-expand")], className="chart-head"),
                    html.P("Mối tương quan dương mạnh (r = 0.57) giữa giá niêm yết và doanh số thực tế",
                           className="section-subtitle mb-2"),
                    dcc.Graph(id="bigmart-mrp-graph", config={"displaylogo": False}, style={"height": 380}),
                ]), className="section-card h-100"),
                xs=12, lg=6,
            ),
            dbc.Col(
                dbc.Card(dbc.CardBody([
                    html.Div([html.H5("Hiệu quả Doanh thu theo Cấp Đô thị & Loại Siêu thị", className="chart-title"), html.Button([html.I(className="bi bi-arrows-fullscreen"), " Mở rộng"], id="bigmart-expand-outlet", n_clicks=0, className="chart-expand")], className="chart-head"),
                    html.P("Doanh số trung bình tại các khu vực Tier 1, 2, 3 phân bổ theo mô hình điểm bán",
                           className="section-subtitle mb-2"),
                    dcc.Graph(id="bigmart-outlet-graph", config={"displaylogo": False}, style={"height": 380}),
                ]), className="section-card h-100"),
                xs=12, lg=6,
            ),
        ], className="g-2 mb-2"),

        # Hàng 2: Phân bổ MRP theo Nhóm hàng + Nghịch lý Độ hiển thị quầy kệ
        dbc.Row([
            dbc.Col(
                dbc.Card(dbc.CardBody([
                    html.Div([html.H5("Phổ Giá Niêm yết (MRP) theo Nhóm Hàng hóa FMCG", className="chart-title"), html.Button([html.I(className="bi bi-arrows-fullscreen"), " Mở rộng"], id="bigmart-expand-category", n_clicks=0, className="chart-expand")], className="chart-head"),
                    html.P("Phân phối mức giá tối đa giữa các danh mục đồ ăn, thức uống, hoá mỹ phẩm",
                           className="section-subtitle mb-2"),
                    dcc.Graph(id="bigmart-cat-graph", config={"displaylogo": False}, style={"height": 380}),
                ]), className="section-card h-100"),
                xs=12, lg=6,
            ),
            dbc.Col(
                dbc.Card(dbc.CardBody([
                    html.Div([html.H5("Độ Hiển thị Quầy kệ (Visibility) vs Doanh số", className="chart-title"), html.Button([html.I(className="bi bi-arrows-fullscreen"), " Mở rộng"], id="bigmart-expand-visibility", n_clicks=0, className="chart-expand")], className="chart-head"),
                    html.P("Kiểm chứng giả thuyết: Hàng xếp quầy rộng có thực sự bán chạy hơn không?",
                           className="section-subtitle mb-2"),
                    dcc.Graph(id="bigmart-vis-graph", config={"displaylogo": False}, style={"height": 380}),
                ]), className="section-card h-100"),
                xs=12, lg=6,
            ),
        ], className="g-2 mb-2"),

        # Bảng Insight Nghiệp vụ
        dbc.Card(dbc.CardBody([
            html.H6("💡 Insight Nghiệp vụ Trưng bày & Phân phối BigMart:", className="text-secondary fw-bold"),
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
                        html.Td(html.Strong("Sức mạnh của Giá niêm yết (MRP)")),
                        html.Td("Giá niêm yết Item_MRP có tương quan dương mạnh nhất với doanh số (r = 0.57). Các mặt hàng giá trị cao tạo ra phần lớn doanh thu cho cửa hàng."),
                        html.Td("Chiến lược kinh doanh nên ưu tiên bảo vệ nguồn cung các mặt hàng cận cao cấp (Premium FMCG) thay vì chỉ tập trung sản phẩm giá rẻ."),
                    ]),
                    html.Tr([
                        html.Td(html.Strong("Nghịch lý Trưng bày (Visibility Paradox)")),
                        html.Td("Tỷ lệ hiển thị Item_Visibility có tương quan âm nhẹ (-0.13) với doanh số. Sản phẩm bán chạy thường chia sẻ diện tích quầy kệ hẹp; trong khi hàng chậm bán thường được bày rộng để kích cầu."),
                        html.Td("Không lãng phí không gian quầy kệ chính cho sản phẩm ế; cần luân chuyển diện tích trưng bày theo tốc độ quay vòng tồn kho thực tế."),
                    ]),
                    html.Tr([
                        html.Td(html.Strong("Tiềm năng Thị trường Ngoại ô (Tier 2 & 3)")),
                        html.Td("Doanh số trung bình tại Tier 2 ($2,324) và Tier 3 ($2,280) cao hơn hẳn Tier 1 ($1,877) nhờ sự hiện diện của các đại siêu thị Supermarket Type 3."),
                        html.Td("Mở rộng mạng lưới đại siêu thị ra các vùng đô thị vệ tinh Tier 2/Tier 3 thay vì cạnh tranh gay gắt tại trung tâm lõi Tier 1."),
                    ]),
                ])
            ], bordered=True, hover=True, responsive=True, size="sm", className="mt-2 small"),
        ]), className="section-card"),
        dbc.Modal([dbc.ModalHeader(dbc.ModalTitle(id="bigmart-modal-title")), dbc.ModalBody(dcc.Graph(id="bigmart-modal-graph", config={"displaylogo": False}, style={"height": "72vh"}))], id="bigmart-chart-modal", is_open=False, size="xl", centered=True),
    ])


@callback(
    Output("bigmart-mrp-graph", "figure"),
    Output("bigmart-outlet-graph", "figure"),
    Output("bigmart-cat-graph", "figure"),
    Output("bigmart-vis-graph", "figure"),
    Output("bigmart-kpi-sales", "children"),
    Output("bigmart-kpi-items", "children"),
    Output("bigmart-kpi-avg", "children"),
    Output("bigmart-kpi-mrp", "children"),
    Input("bigmart-tier-filter", "value"),
)
def _update_bigmart(selected_tier):
    if BIGMART.empty:
        blank = blank_figure()
        return blank, blank, blank, blank, "—", "—", "—", "—"

    df = BIGMART if selected_tier in ("ALL", None) else BIGMART[BIGMART["Outlet_Location_Type"] == selected_tier]
    if df.empty:
        blank = blank_figure()
        return blank, blank, blank, blank, "—", "—", "—", "—"

    total_sales = df["Item_Outlet_Sales"].sum()
    n_items = len(df)
    avg_sales = df["Item_Outlet_Sales"].mean()
    avg_mrp = df["Item_MRP"].mean()

    return (
        build_bigmart_mrp_vs_sales(df),
        build_bigmart_outlet_performance(df),
        build_bigmart_category_sales(df),
        build_bigmart_visibility_sales(df),
        f"${total_sales:,.0f}",
        f"{n_items:,} mặt hàng",
        f"${avg_sales:,.0f}",
        f"${avg_mrp:,.1f}",
    )


@callback(
    Output("bigmart-chart-modal", "is_open"), Output("bigmart-modal-title", "children"), Output("bigmart-modal-graph", "figure"),
    Input("bigmart-expand-mrp", "n_clicks"), Input("bigmart-expand-outlet", "n_clicks"), Input("bigmart-expand-category", "n_clicks"), Input("bigmart-expand-visibility", "n_clicks"), Input("bigmart-chart-modal", "is_open"),
    State("bigmart-mrp-graph", "figure"), State("bigmart-outlet-graph", "figure"), State("bigmart-cat-graph", "figure"), State("bigmart-vis-graph", "figure"), prevent_initial_call=True,
)
def _toggle_modal(_mrp, _outlet, _category, _visibility, _open, mrp_fig, outlet_fig, category_fig, visibility_fig):
    if ctx.triggered_id == "bigmart-chart-modal":
        return False, no_update, no_update
    charts = {"bigmart-expand-mrp": ("Tương quan giá niêm yết và doanh số", mrp_fig), "bigmart-expand-outlet": ("Hiệu quả doanh thu theo điểm bán", outlet_fig), "bigmart-expand-category": ("Phổ giá niêm yết theo nhóm hàng", category_fig), "bigmart-expand-visibility": ("Độ hiển thị quầy kệ và doanh số", visibility_fig)}
    title, figure = charts[ctx.triggered_id]
    return True, title, figure
