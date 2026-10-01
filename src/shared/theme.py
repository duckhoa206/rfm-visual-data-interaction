"""Theme dùng chung cho Streamlit và Dash (không phụ thuộc framework UI).

Copy palette COLORS + apply_chart_theme() từ src/shared/ui.py,
loại bỏ mọi import streamlit để Dash dùng được.
"""

import plotly.graph_objects as go

COLORS = {
    "background": "#0B1220",
    "surface": "#111C2E",
    "surface_alt": "#18253A",
    "text": "#E8EEF8",
    "muted": "#94A3B8",
    "primary": "#39B6FF",
    "secondary": "#7C5CFC",
    "success": "#35D39E",
    "warning": "#F7B955",
    "danger": "#FF718B",
}


def apply_chart_theme(fig: go.Figure) -> go.Figure:
    """Áp dụng palette và typography chung cho mọi biểu đồ Plotly."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Arial, sans-serif", color=COLORS["text"]),
        colorway=[COLORS["primary"], COLORS["secondary"], COLORS["success"], COLORS["warning"], COLORS["danger"]],
        margin=dict(l=12, r=12, t=24, b=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hoverlabel=dict(bgcolor="#18253A", font_color=COLORS["text"]),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="#2B3C57")
    fig.update_yaxes(gridcolor="#23334B", zeroline=False)
    return fig
