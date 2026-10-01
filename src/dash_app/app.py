"""Khung Hub-and-Spoke: header cố định (logo + bộ lọc) + sidebar + nội dung trang.

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

from src.dash_app.components import filters, header, sidebar
from src.dash_app.shared_data import FILTER_OPTIONS, ORDERS, RFM

app = Dash(
    __name__,
    use_pages=True,
    pages_folder=str(ROOT_DIR / "src" / "dash_app" / "pages"),
    external_stylesheets=[dbc.themes.DARKLY],
    title="Phân tích bán lẻ RFM | HCMUTE",
    assets_folder=str(ROOT_DIR / "assets"),
)
app.layout = dbc.Container(
    [
        dcc.Location(id="url"),
        dcc.Store(id="sidebar-store", data=False),
        dbc.Row(
            [
                dbc.Col(header.layout(), md=6),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H2("Bộ lọc", className="section-title"),
                            filters.layout(FILTER_OPTIONS),
                        ]),
                        className="section-card",
                    ),
                    md=6,
                ),
            ],
            class_name="g-2",
        ),
        html.Div(
            [
                sidebar.layout(),
                html.Main(dash.page_container, id="page-content", className="content"),
            ],
            className="body-row",
        ),
    ],
    fluid=True,
    className="app-container",
)

filters.register_callbacks(app, ORDERS, RFM)

if __name__ == "__main__":
    app.run(debug=os.getenv("DASH_DEBUG", "0") == "1", port=8050)
