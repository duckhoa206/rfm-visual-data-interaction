"""Khung logo trường (nửa trái hàng đầu, theo layout.pdf)."""

import base64
from pathlib import Path

import dash_bootstrap_components as dbc
from dash import html

ROOT_DIR = Path(__file__).resolve().parents[3]
LOGO_PATH = ROOT_DIR / "assets" / "Logo HCM-UTE.png"
FALLBACK_LOGO_PATH = ROOT_DIR / "assets" / "hcmute-sidebar-brand.png"


def _logo_src() -> str:
    logo = LOGO_PATH if LOGO_PATH.exists() else FALLBACK_LOGO_PATH
    return "data:image/png;base64," + base64.b64encode(logo.read_bytes()).decode("ascii")


def layout() -> html.Header:
    """Khung logo + tên trường + tên đề tài (không nav, theo layout.pdf)."""
    return html.Header(
        dbc.Row(
            [
                dbc.Col(
                    html.Img(src=_logo_src(), alt="HCMUTE", className="header-logo"),
                    width="auto",
                ),
                dbc.Col(
                    html.Div(
                        [
                            html.P("TRƯỜNG ĐẠI HỌC", className="brand-university"),
                            html.P(
                                "CÔNG NGHỆ KỸ THUẬT TP. HỒ CHÍ MINH",
                                className="brand-school",
                            ),
                            html.Hr(className="brand-divider"),
                            html.P(
                                "HCMC University of Technology and Engineering",
                                className="brand-english",
                            ),
                            html.P(
                                "PHÂN TÍCH HIỆU SUẤT BÁN HÀNG VÀ PHÂN KHÚC KHÁCH HÀNG (RFM)",
                                className="brand-title",
                            ),
                        ],
                        className="header-brand-copy",
                    ),
                ),
            ],
            class_name="g-0 align-items-center",
        ),
        className="app-header",
        id="top",
    )
