"""Trang phụ: phân khúc khách hàng RFM (1 dropdown chọn 1 trong 3 biểu đồ + hành động đề xuất)."""

import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html, no_update, register_page

from src.dash_app.components.charts import blank_figure, build_rfm_figure
from src.dash_app.config import PAGE_META
from src.dash_app.shared_data import ORDERS, RFM
from src.shared import data_service

register_page(__name__, **PAGE_META["rfm"])

RFM_OPTIONS = [
    {"label": "Tỷ trọng phân khúc (Pie Chart)", "value": "pie"},
    {"label": "Tần suất × Chi tiêu (Scatter F-M)", "value": "scatter"},
    {"label": "Phân phối chi tiêu (Box Plot)", "value": "box"},
]


def layout() -> html.Div:
    return html.Div([
        dbc.Card(dbc.CardBody([
            html.H4("Phân khúc khách hàng RFM", className="page-title"),
            dcc.Dropdown(
                id="rfm-chart-select", options=RFM_OPTIONS,
                value="pie", clearable=False, className="mb-3"),
            dbc.Alert(id="rfm-alert", color="warning", is_open=False),
            dcc.Graph(id="rfm-chart", config={"displaylogo": False}, style={"height": 480}),
            
            html.Hr(),
            html.H6("📋 Hướng dẫn nghiệp vụ & Hành động đề xuất cho từng Phân khúc:", className="text-secondary fw-bold mt-3"),
            dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th("Phân khúc", style={"width": "18%"}),
                        html.Th("Đặc điểm RFM", style={"width": "22%"}),
                        html.Th("Ý nghĩa nghiệp vụ & Khuyến nghị hành động", style={"width": "60%"})
                    ])
                ]),
                html.Tbody([
                    html.Tr([
                        html.Td(html.Span("Champions", className="badge bg-success")),
                        html.Td("R: 4-5 | F: 4-5 | M: 4-5"),
                        html.Td("Nhóm khách hàng VIP, trung thành và chi tiêu nhiều nhất. Hành động: Cung cấp đặc quyền thành viên VIP, ưu đãi trải nghiệm sớm sản phẩm mới.")
                    ]),
                    html.Tr([
                        html.Td(html.Span("Loyal Customers", className="badge bg-primary")),
                        html.Td("R: 3-5 | F: 3-5 | M linh hoạt"),
                        html.Td("Mua sắm đều đặn, phản hồi tốt. Hành động: Giới thiệu các chương trình tích điểm, khuyến mãi mua theo combo (cross-selling/upselling).")
                    ]),
                    html.Tr([
                        html.Td(html.Span("New Customers", className="badge bg-info text-dark")),
                        html.Td("R: 4-5 | F: 1-2 | M linh hoạt"),
                        html.Td("Khách hàng mới phát sinh đơn hàng gần đây. Hành động: Gửi email chào mừng/hướng dẫn sử dụng, tặng voucher ưu đãi cho đơn hàng thứ 2.")
                    ]),
                    html.Tr([
                        html.Td(html.Span("Need Attention", className="badge bg-secondary")),
                        html.Td("Điểm trung bình (khoảng R: 3, F: 2-3)"),
                        html.Td("Tần suất hoặc mức chi tiêu có dấu hiệu chững lại. Hành động: Gợi ý các sản phẩm liên quan đến lịch sử mua sắm kèm giảm giá có giới hạn thời gian.")
                    ]),
                    html.Tr([
                        html.Td(html.Span("At Risk", className="badge bg-warning text-dark")),
                        html.Td("R: 1-2 | F: 3-5 | M cao"),
                        html.Td("Khách hàng cũ từng mua nhiều nhưng đã lâu không quay lại. Hành động: Kích hoạt chiến dịch Remarketing, gửi khảo sát phản hồi dịch vụ.")
                    ]),
                    html.Tr([
                        html.Td(html.Span("Lost", className="badge bg-danger")),
                        html.Td("R: 1-2 | F: 1-2 | M: 1-2"),
                        html.Td("Khách hàng đã rời bỏ hoàn toàn, chi tiêu thấp. Hành động: Không ưu tiên ngân sách remarketing; chỉ tiếp cận qua các chiến dịch đại lễ lớn.")
                    ]),
                ])
            ], bordered=True, hover=True, responsive=True, size="sm", className="mt-2 small")
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
        segments=store.get("segments"),
        data_sources=store.get("data_sources"))
    if rfm_f.empty:
        return blank_figure(), "Không có khách hàng nào khớp với bộ lọc.", True
    return build_rfm_figure(chart or "pie", rfm_f), "", False