"""Sidebar dọc kiểu Climate Lab: icon + tên mục, highlight trang đang chọn,
nút thu gọn/mở rộng. Mục tự sinh từ dash.page_registry (sắp xếp theo order)."""

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, html


def layout() -> html.Aside:
    pages = sorted(
        dash.page_registry.values(), key=lambda p: p.get("order", 99))
    links = [
        dbc.NavLink(
            [html.Span(p.get("icon", "•"), className="sidebar-icon"),
             html.Span(p["name"], className="sidebar-label")],
            href=p["path"], active="exact", className="sidebar-link",
        )
        for p in pages
    ]
    return html.Aside(
        [
            html.Button("☰", id="sidebar-toggle", className="sidebar-toggle",
                        title="Thu gọn / mở rộng"),
            dbc.Nav(links, vertical=True, pills=True, className="sidebar-nav"),
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
