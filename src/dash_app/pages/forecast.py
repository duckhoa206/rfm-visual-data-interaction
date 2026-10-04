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
            html.H4("Dự báo doanh thu & Đánh giá mô hình", className="page-title"),
            dbc.Alert(id="forecast-alert", color="warning", is_open=False),
            dcc.Graph(id="forecast-graph", config={"displaylogo": False}, style={"height": 450}),
            html.P(id="forecast-caption", className="caption fw-bold text-primary mt-2"),
            
            html.Hr(),
            html.Div([
                html.H6("📌 Giả định, Giới hạn & Lưu ý nguồn dữ liệu:", className="text-secondary fw-bold"),
                html.Ul([
                    html.Li("Mô hình Linear Regression giả định doanh thu biến thiên tuyến tính theo thời gian; chưa nắm bắt được yếu tố mùa vụ (Q4 cao điểm)."),
                    html.Li("Đánh giá mô hình (MAE, RMSE) được thực hiện trên 3 tháng có giao dịch gần nhất bằng phương pháp time-based split."),
                    html.Li("Nguồn dữ liệu Kaggle 2019–2020 (nếu có trong bộ lọc) là dữ liệu thử nghiệm chưa xác minh độc lập; kết quả dự báo đóng vai trò baseline tham khảo xu hướng ngắn hạn.")
                ], className="small text-muted mb-0")
            ], className="mt-3 p-3 bg-light rounded")
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
        segments=store.get("segments"),
        data_sources=store.get("data_sources"))
    if orders_f.empty:
        return blank_figure(), "", "Không có dữ liệu khớp với bộ lọc.", True
    fig, caption = build_forecast_figure(orders_f)
    if fig is None:
        return (blank_figure(), "",
                caption or "Cần ít nhất 5 tháng dữ liệu để huấn luyện và kiểm thử. Hãy mở rộng khoảng thời gian ở bộ lọc.", True)
    return fig, caption, "", False