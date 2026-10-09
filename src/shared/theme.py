"""Theme dùng chung cho Streamlit và Dash (không phụ thuộc framework UI).

Copy palette COLORS + apply_chart_theme() từ src/shared/ui.py,
loại bỏ mọi import streamlit để Dash dùng được.
"""

import plotly.graph_objects as go

COLORS = {
    "background": "#F1F5F9",
    "surface": "#FFFFFF",
    "surface_alt": "#EAF0F7",
    "text": "#0F172A",
    "muted": "#64748B",
    "primary": "#0284C7",
    "secondary": "#7C5CFC",
    "success": "#059669",
    "warning": "#D97706",
    "danger": "#DC2626",
    "slate": "#64748B",
}


def apply_chart_theme(fig: go.Figure) -> go.Figure:
    """Palette nền sáng + legend đáy giữa (không đè lên biểu đồ).

    Mọi legend nằm dưới vùng vẽ (y < 0) nên không bao giờ chồng title/chart,
    kể cả khi có 6 mục như phân khúc RFM.
    """
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="'Segoe UI', -apple-system, Roboto, 'Helvetica Neue', Arial, sans-serif", color=COLORS["text"]),
        colorway=[
            COLORS["primary"], "#0EA5E9", COLORS["success"],
            COLORS["warning"], COLORS["danger"], COLORS["secondary"],
        ],
        margin=dict(l=12, r=12, t=16, b=72),
        legend=dict(
            orientation="h",
            yanchor="top", y=-0.18,
            xanchor="center", x=0.5,
            font=dict(size=11, color=COLORS["muted"]),
            itemwidth=30,
            tracegroupgap=10,
            title=None,
        ),
        hoverlabel=dict(bgcolor="#FFFFFF", font_color=COLORS["text"]),
        uniformtext=dict(minsize=9, mode="hide"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="#CBD5E1")
    fig.update_yaxes(gridcolor="#E2E8F0", zeroline=False)
    return fig
