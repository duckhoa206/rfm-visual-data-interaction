"""Sidebar trái liền khối: thương hiệu HCMUTE + điều hướng icon + label,
highlight trang đang chọn, nút thu gọn/mở rộng.
Khi rút gọn chỉ hiện icon (có tooltip tên trang).
Mục tự sinh từ dash.page_registry (sắp xếp theo order)."""

import base64
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, html

ROOT_DIR = Path(__file__).resolve().parents[3]
LOGO_PATH = ROOT_DIR / "assets" / "Logo HCM-UTE.png"
FALLBACK_LOGO_PATH = ROOT_DIR / "assets" / "hcmute-sidebar-brand.png"

# Icon Bootstrap (chuẩn, không phải AI) cho từng trang, map theo path.
ICONS = {
    "/": "bi-speedometer2",
    "/geo": "bi-map",
    "/rfm": "bi-people",
    "/forecast": "bi-graph-up-arrow",
    "/walmart": "bi-shop",
    "/bigmart": "bi-box-seam",
    "/data": "bi-table",
}


def _logo_src() -> str:
    logo = LOGO_PATH if LOGO_PATH.exists() else FALLBACK_LOGO_PATH
    return "data:image/png;base64," + base64.b64encode(logo.read_bytes()).decode("ascii")


def layout() -> html.Aside:
    pages = sorted(
        dash.page_registry.values(), key=lambda p: p.get("order", 99))
    links = [
        html.Div(
            dbc.NavLink(
                [
                    html.I(className=f"bi {ICONS.get(p['path'], 'bi-circle')} sidebar-ico"),
                    html.Span(p["name"], className="sidebar-label"),
                ],
                href=p["path"], active="exact", className="sidebar-link",
            ),
            title=p["name"],
            className="sidebar-link-wrap",
        )
        for p in pages
    ]
    return html.Aside(
        [
            html.Div(
                [
                    html.Img(src=_logo_src(), alt="HCMUTE", className="sidebar-logo"),
                    html.Div(
                        [
                            html.P("HCMUTE", className="sidebar-school"),
                            html.P(
                                "Phân tích bán lẻ & RFM",
                                className="sidebar-title",
                            ),
                        ],
                        className="sidebar-brand-copy",
                    ),
                ],
                className="sidebar-brand",
            ),
            html.Hr(className="sidebar-divider"),
            dbc.Nav(links, vertical=True, pills=True, className="sidebar-nav"),
            html.Button("☰", id="sidebar-toggle", className="sidebar-toggle",
                        title="Thu gọn / mở rộng"),
        ],
        id="sidebar", className="sidebar",
    )


@callback(
    Output("sidebar", "className"),
    Output("sidebar-store", "data"),
    Input("sidebar-toggle", "n_clicks"),
    State("sidebar-store", "data"),
    prevent_initial_call=True,
)
def _toggle(n_clicks, collapsed):
    collapsed = not bool(collapsed)
    return ("sidebar collapsed" if collapsed else "sidebar"), collapsed
