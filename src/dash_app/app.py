"""Khung Hub-and-Spoke: sidebar trái liền khối (thương hiệu + điều hướng)
+ cột nội dung (bộ lọc gọn + trang).

Chạy:  python src/dash_app/app.py   →  http://127.0.0.1:8050
"""

import os
from pathlib import Path
import sys

import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.dash_app.components import filters, sidebar
from src.dash_app.shared_data import FILTER_OPTIONS, ORDERS, RFM

app = Dash(
    __name__,
    use_pages=True,
    pages_folder=str(ROOT_DIR / "src" / "dash_app" / "pages"),
    external_stylesheets=[
        dbc.themes.FLATLY,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css",
    ],
    title="Phân tích bán lẻ RFM | HCMUTE",
    assets_folder=str(ROOT_DIR / "assets"),
)
server = app.server
app.layout = dbc.Container(
    [
        dcc.Location(id="url"),
        dcc.Store(id="sidebar-store", data=False),
        html.Div(
            [
                # Trái: thương hiệu + điều hướng liền một khối
                sidebar.layout(),
                # Phải: bộ lọc gọn + nội dung trang
                html.Div(
                    [
                        dbc.Card(
                            dbc.CardBody([
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            [
                                                                html.H2(
                                                                    "Bộ lọc",
                                                                    className="section-title",
                                                                ),
                                                                html.Span(
                                                                    "Mặc định",
                                                                    id="filter-active-count",
                                                                    className="filter-count-badge",
                                                                ),
                                                            ],
                                                            className="filter-title-row",
                                                        ),
                                                        html.P(
                                                            "Tinh chỉnh phạm vi phân tích theo khu vực, thời gian và phân khúc",
                                                            className="filter-subtitle",
                                                        ),
                                                    ],
                                                ),
                                            ],
                                            className="filter-title-wrap",
                                        ),
                                        html.Div(
                                            [
                                                html.Span(
                                                    [
                                                        "Đơn hàng: ",
                                                        html.B("—", id="scope-orders"),
                                                    ],
                                                    className="scope-pill",
                                                ),
                                                html.Span(
                                                    [
                                                        "Khách hàng: ",
                                                        html.B("—", id="scope-customers"),
                                                    ],
                                                    className="scope-pill",
                                                ),
                                                html.Span(
                                                    [
                                                        "Dòng SP: ",
                                                        html.B("—", id="scope-lines"),
                                                    ],
                                                    className="scope-pill",
                                                ),
                                                html.Button(
                                                    "Đặt lại",
                                                    id="filter-reset",
                                                    n_clicks=0,
                                                    className="filter-reset",
                                                    title="Xóa mọi điều kiện lọc",
                                                ),
                                            ],
                                            className="scope-panel",
                                        ),
                                    ],
                                    className="section-head filter-head",
                                ),
                                filters.layout(FILTER_OPTIONS),
                            ]),
                            className="section-card filter-card",
                        ),
                        html.Main(dash.page_container, id="page-content", className="content"),
                    ],
                    className="main-column",
                ),
            ],
            className="app-shell",
        ),
    ],
    fluid=True,
    className="app-container",
)

filters.register_callbacks(app, ORDERS, RFM)

if __name__ == "__main__":
    app.run(debug=os.getenv("DASH_DEBUG", "0") == "1", port=8050)
