"""Hàm dựng biểu đồ + thẻ KPI dùng chung cho mọi trang.

Đổi style một lần ở đây (hoặc assets/style.css) là áp dụng toàn bộ.
Các trang chỉ gọi hàm, không tự code figure.
"""

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html

from src.shared.theme import apply_chart_theme
from src.dash_app.components.forecast_charts import (
    build_category_forecast_figure,
    build_forecast_scenarios_figure,
    build_quantity_profit_forecast_figure,
    build_regional_forecast_figure,
)

RFM_COLUMNS = [
    "Customer ID", "Data Source", "Country", "Recency", "Frequency",
    "Monetary", "RFM_Score", "Segment",
]


def kpi_card(title: str, value_id: str) -> dbc.Card:
    return dbc.Card(
        dbc.CardBody([
            html.Div(title, className="kpi-title"),
            html.Div("—", id=value_id, className="kpi-value"),
        ]),
        className="kpi-card",
    )


def blank_figure() -> go.Figure:
    return go.Figure()


def build_bar_category(orders_filtered: pd.DataFrame) -> go.Figure:
    by_cat = orders_filtered.groupby("Category", as_index=False)["Sales"].sum()
    fig = px.bar(by_cat, x="Category", y="Sales", color="Category")
    apply_chart_theme(fig)
    # Màu đã mã hóa ngay trên trục X → ẩn legend thừa, xoay nhãn cho khỏi đè.
    fig.update_layout(showlegend=False, margin=dict(l=12, r=12, t=16, b=84))
    fig.update_xaxes(tickangle=-15, automargin=True)
    fig.update_yaxes(tickformat=",.0f")
    return fig


def build_line_monthly(orders_filtered: pd.DataFrame) -> go.Figure:
    monthly = (
        orders_filtered.set_index("Order Date")
        .resample("MS")
        .agg(Sales=("Sales", "sum"), Rows=("Sales", "size"))
        .reset_index()
    )
    monthly.loc[monthly["Rows"] == 0, "Sales"] = np.nan
    fig = px.line(monthly, x="Order Date", y="Sales", markers=True)
    fig.update_traces(connectgaps=False)
    fig.update_traces(line=dict(width=3))
    apply_chart_theme(fig)
    # Chỉ 1 đường duy nhất → ẩn legend cho thoáng.
    fig.update_layout(showlegend=False, margin=dict(l=12, r=12, t=16, b=48))
    fig.update_yaxes(tickformat=",.0f")
    return fig


def build_geo_figure(chart: str, orders_filtered: pd.DataFrame) -> go.Figure:
    if chart == "treemap":
        fig = px.treemap(
            orders_filtered, path=["Region", "Country", "Category"], values="Sales")
        apply_chart_theme(fig)
        # Nhãn đã nằm trong từng ô → ẩn legend.
        fig.update_layout(showlegend=False, margin=dict(l=12, r=12, t=16, b=24))
        return fig
    elif chart == "heatmap":
        pivot = orders_filtered.pivot_table(
            index="Region", columns="Category", values="Sales",
            aggfunc="sum", fill_value=0)
        # Nhiều khu vực làm heatmap bị ép thành dải rất hẹp nếu giữ ô vuông
        # và in số trên từng ô. Dùng ô co giãn theo khung + hover để đọc chi tiết.
        fig = px.imshow(pivot, aspect="auto", color_continuous_scale="Oranges")
        apply_chart_theme(fig)
        fig.update_traces(
            hovertemplate="Khu vực: %{y}<br>Danh mục: %{x}<br>Doanh thu: %{z:,.0f}<extra></extra>",
            xgap=2,
            ygap=2,
        )
        fig.update_layout(
            showlegend=False, margin=dict(l=12, r=12, t=16, b=48),
            coloraxis_colorbar=dict(title="Doanh thu", thickness=12, len=0.75),
        )
        fig.update_xaxes(tickangle=0, automargin=True, side="bottom")
        fig.update_yaxes(automargin=True)
        return fig
    else:
        by_country = orders_filtered.groupby("Country", as_index=False)["Sales"].sum()
        fig = px.choropleth(
            by_country, locations="Country", locationmode="country names",
            color="Sales", color_continuous_scale="YlOrRd", hover_name="Country", hover_data={"Sales": ":,.0f"})
        apply_chart_theme(fig)
        fig.update_layout(
            showlegend=False, margin=dict(l=4, r=4, t=16, b=24),
            coloraxis_colorbar=dict(title="Doanh thu", thickness=16, len=0.72, tickformat=",.2s"),
            geo=dict(showframe=False, showcoastlines=True, coastlinecolor="#94A3B8", showcountries=True, countrycolor="#CBD5E1", showland=True, landcolor="#F8FAFC", showocean=True, oceancolor="#E0F2FE", projection_type="natural earth"),
        )
        fig.update_geos(fitbounds="locations", visible=True)
        return fig


def build_rfm_figure(chart: str, rfm_filtered: pd.DataFrame) -> go.Figure:
    if chart == "scatter":
        fig = px.scatter(
            rfm_filtered, x="Frequency", y="Monetary", color="Segment",
            size="Monetary", hover_data=["Customer ID", "Recency"])
        apply_chart_theme(fig)
        # Bong bóng mờ + giới hạn size để bớt đè nhau; legend đáy giữa.
        fig.update_traces(marker=dict(opacity=0.65, line=dict(width=0)), selector=dict(mode="markers"))
        fig.update_traces(marker=dict(sizeref=2.0 * rfm_filtered["Monetary"].max() / (18 ** 2)) if not rfm_filtered.empty else {})
        fig.update_layout(legend_title_text="Phân khúc")
        fig.update_yaxes(tickformat=",.0f")
        return fig
    elif chart == "box":
        fig = px.box(rfm_filtered, x="Segment", y="Monetary", color="Segment")
        apply_chart_theme(fig)
        # Trục X đã là tên nhóm → ẩn legend trùng lặp.
        fig.update_layout(showlegend=False, margin=dict(l=12, r=12, t=16, b=96))
        fig.update_xaxes(tickangle=-15, automargin=True)
        fig.update_yaxes(tickformat=",.0f")
        return fig
    else:
        seg_count = rfm_filtered["Segment"].value_counts().reset_index()
        seg_count.columns = ["Segment", "Count"]
        fig = px.pie(seg_count, names="Segment", values="Count", hole=0.4)
        apply_chart_theme(fig)
        # % nằm trong lát cắt, tên nhóm xuống legend đáy — hết chồng chữ.
        fig.update_traces(
            textinfo="percent", textposition="inside",
            textfont_size=11, insidetextorientation="radial",
            texttemplate="%{percent:.1%}",
            hovertemplate="%{label}<br>%{value:,} khách (%{percent})<extra></extra>",
            marker=dict(line=dict(color="#FFFFFF", width=2)),
            sort=False,
        )
        fig.update_layout(margin=dict(l=12, r=12, t=16, b=96))
        return fig


def build_forecast_figure(orders_filtered: pd.DataFrame, test_months: int = 3, forecast_months: int = 3) -> tuple:
    """Wrapper tương thích ngược với API cũ."""
    fig, caption, _ = build_forecast_scenarios_figure(orders_filtered, target_year=2030)
    return fig, caption


def build_manager_performance(orders_filtered: pd.DataFrame) -> go.Figure:
    """Biểu đồ hiệu suất Quản lý khu vực (từ bảng People JOIN vào orders)."""
    if orders_filtered.empty or "Manager" not in orders_filtered.columns:
        return blank_figure()
    df_mgr = orders_filtered.dropna(subset=["Manager"])
    if df_mgr.empty:
        return blank_figure()
    summary = df_mgr.groupby("Manager", as_index=False).agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
    ).sort_values("Sales", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=summary["Manager"], x=summary["Sales"],
        orientation="h", name="Doanh thu ($)",
        marker=dict(color="#0284C7"),
        hovertemplate="%{y}<br>Doanh thu: $%{x:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        y=summary["Manager"], x=summary["Profit"],
        orientation="h", name="Lợi nhuận ($)",
        marker=dict(color="#10B981"),
        hovertemplate="%{y}<br>Lợi nhuận: $%{x:,.0f}<extra></extra>",
    ))
    apply_chart_theme(fig)
    fig.update_layout(
        barmode="group",
        hovermode="y unified",
        margin=dict(l=12, r=12, t=16, b=48),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(tickformat="$,.0f")
    return fig


def build_walmart_correlation(walmart_df: pd.DataFrame) -> go.Figure:
    """Ma trận tương quan giữa Doanh số tuần và các biến kinh tế vĩ mô."""
    if walmart_df.empty:
        return blank_figure()
    cols = ["Weekly_Sales", "Temperature", "Fuel_Price", "CPI", "Unemployment", "Size"]
    cols_present = [c for c in cols if c in walmart_df.columns]
    if len(cols_present) < 2:
        return blank_figure()

    corr = walmart_df[cols_present].corr().round(2)
    labels_vi = {
        "Weekly_Sales": "Doanh số tuần",
        "Temperature": "Nhiệt độ",
        "Fuel_Price": "Giá xăng",
        "CPI": "Chỉ số CPI",
        "Unemployment": "Thất nghiệp",
        "Size": "Diện tích cửa hàng",
    }
    x_labels = [labels_vi.get(c, c) for c in corr.columns]
    y_labels = [labels_vi.get(c, c) for c in corr.index]

    fig = px.imshow(
        corr.values,
        x=x_labels, y=y_labels,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
    )
    apply_chart_theme(fig)
    fig.update_layout(
        margin=dict(l=12, r=12, t=16, b=64),
            coloraxis_colorbar=dict(title="Mức tương quan", thickness=12, len=0.8),
    )
    fig.update_xaxes(tickangle=-15, automargin=True)
    return fig


def build_walmart_holiday_impact(walmart_df: pd.DataFrame) -> go.Figure:
    """So sánh doanh số tuần bình thường vs tuần lễ hội (Holiday Uplift) theo Loại siêu thị."""
    if walmart_df.empty or "Type" not in walmart_df.columns or "IsHoliday" not in walmart_df.columns:
        return blank_figure()

    df_agg = walmart_df.groupby(["Type", "IsHoliday"], as_index=False)["Weekly_Sales"].mean()
    df_agg["Loại cửa hàng"] = df_agg["Type"].map(
        {"A": "Loại A", "B": "Loại B", "C": "Loại C"}
    ).fillna(df_agg["Type"])
    df_agg["Dịp lễ"] = df_agg["IsHoliday"].map({True: "Tuần lễ", False: "Tuần thường"})

    fig = px.bar(
        df_agg, x="Loại cửa hàng", y="Weekly_Sales", color="Dịp lễ",
        barmode="group",
        color_discrete_map={"Tuần lễ": "#F59E0B", "Tuần thường": "#0284C7"},
        labels={"Loại cửa hàng": "Loại siêu thị", "Weekly_Sales": "Doanh số trung bình/tuần ($)"},
    )
    apply_chart_theme(fig)
    fig.update_layout(
        hovermode="x unified",
        margin=dict(l=12, r=12, t=16, b=48),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_yaxes(tickformat="$,.0f")
    return fig


def build_walmart_store_types(walmart_df: pd.DataFrame) -> go.Figure:
    """Mối quan hệ giữa Diện tích (Size sqft), Doanh số trung bình tuần và Loại siêu thị A/B/C."""
    if walmart_df.empty or "Store" not in walmart_df.columns:
        return blank_figure()

    store_summary = walmart_df.groupby(["Store", "Type"], as_index=False).agg(
        Size=("Size", "mean"),
        Weekly_Sales=("Weekly_Sales", "mean"),
    )
    store_summary["Loại cửa hàng"] = store_summary["Type"].map(
        {"A": "Loại A", "B": "Loại B", "C": "Loại C"}
    ).fillna(store_summary["Type"])
    fig = px.scatter(
        store_summary, x="Size", y="Weekly_Sales", color="Loại cửa hàng",
        size="Weekly_Sales",
        hover_name="Store",
        labels={"Size": "Diện tích cửa hàng (sq ft)", "Weekly_Sales": "Doanh số trung bình/tuần ($)", "Loại cửa hàng": "Loại cửa hàng"},
        color_discrete_sequence=["#0284C7", "#10B981", "#8B5CF6"],
        size_max=18,
    )
    apply_chart_theme(fig)
    fig.update_layout(
        hovermode="closest",
        margin=dict(l=12, r=12, t=16, b=72),
        legend=dict(title="Loại cửa hàng", orientation="h", yanchor="bottom", y=-0.24, xanchor="center", x=0.5),
    )
    fig.update_xaxes(tickformat=",.0f")
    fig.update_yaxes(tickformat="$,.0f")
    return fig


def build_walmart_markdown_impact(walmart_df: pd.DataFrame) -> go.Figure:
    """Tổng ngân sách và quy mô 5 chương trình khuyến mãi MarkDown 1-5."""
    if walmart_df.empty:
        return blank_figure()
    md_cols = [f"MarkDown{i}" for i in range(1, 6) if f"MarkDown{i}" in walmart_df.columns]
    if not md_cols:
        return blank_figure()

    md_totals = walmart_df[md_cols].sum().reset_index()
    md_totals.columns = ["Chương trình", "Tổng giá trị giảm giá"]
    md_totals["Chương trình"] = md_totals["Chương trình"].str.replace(
        "MarkDown", "Chương trình ", regex=False
    )

    fig = px.bar(
        md_totals, x="Chương trình", y="Tổng giá trị giảm giá",
        color="Chương trình",
        color_discrete_sequence=["#38BDF8", "#0284C7", "#059669", "#D97706", "#EF4444"],
    )
    apply_chart_theme(fig)
    fig.update_layout(
        showlegend=False,
        margin=dict(l=12, r=12, t=16, b=48),
    )
    fig.update_xaxes(title="Chương trình giảm giá")
    fig.update_yaxes(title="Tổng giá trị giảm giá ($)", tickformat="$,.0f")
    return fig


def build_bigmart_mrp_vs_sales(bigmart_df: pd.DataFrame) -> go.Figure:
    """Tương quan mạnh mẽ giữa Giá niêm yết (Item_MRP) và Doanh số bán ra (Item_Outlet_Sales)."""
    if bigmart_df.empty:
        return blank_figure()
    sample_df = bigmart_df.sample(n=min(1200, len(bigmart_df)), random_state=42)
    fig = px.scatter(
        sample_df, x="Item_MRP", y="Item_Outlet_Sales",
        color="Outlet_Type",
        opacity=0.65,
        labels={"Item_MRP": "Giá Niêm yết Tối đa ($)", "Item_Outlet_Sales": "Doanh số Bán ra ($)", "Outlet_Type": "Loại điểm bán"},
    )
    apply_chart_theme(fig)
    fig.update_layout(
        hovermode="closest",
        margin=dict(l=12, r=12, t=16, b=48),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(tickformat="$,.0f")
    fig.update_yaxes(tickformat="$,.0f")
    return fig


def build_bigmart_outlet_performance(bigmart_df: pd.DataFrame) -> go.Figure:
    """So sánh doanh số trung bình theo Cấp bậc đô thị (Tier 1-3) và Loại hình điểm bán."""
    if bigmart_df.empty:
        return blank_figure()
    agg = bigmart_df.groupby(["Outlet_Location_Type", "Outlet_Type"], as_index=False)["Item_Outlet_Sales"].mean()
    fig = px.bar(
        agg, x="Outlet_Location_Type", y="Item_Outlet_Sales", color="Outlet_Type",
        barmode="group",
        labels={"Outlet_Location_Type": "Cấp bậc Đô thị", "Item_Outlet_Sales": "Doanh số TB / Mặt hàng ($)", "Outlet_Type": "Loại siêu thị"},
    )
    apply_chart_theme(fig)
    fig.update_layout(
        hovermode="x unified",
        margin=dict(l=12, r=12, t=16, b=48),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_yaxes(tickformat="$,.0f")
    return fig


def build_bigmart_category_sales(bigmart_df: pd.DataFrame) -> go.Figure:
    """Phân bổ Giá niêm yết (MRP) theo từng Nhóm ngành hàng FMCG (Item_Type)."""
    if bigmart_df.empty:
        return blank_figure()
    fig = px.box(
        bigmart_df, x="Item_Type", y="Item_MRP", color="Item_Type",
        labels={"Item_Type": "Nhóm ngành hàng", "Item_MRP": "Giá Niêm yết ($)"},
    )
    apply_chart_theme(fig)
    fig.update_layout(
        showlegend=False,
        margin=dict(l=12, r=12, t=16, b=84),
    )
    fig.update_xaxes(tickangle=-30, automargin=True)
    fig.update_yaxes(tickformat="$,.0f")
    return fig


def build_bigmart_visibility_sales(bigmart_df: pd.DataFrame) -> go.Figure:
    """Độ hiển thị quầy kệ (Item_Visibility) vs Doanh số bán lẻ."""
    if bigmart_df.empty:
        return blank_figure()
    sample_df = bigmart_df.sample(n=min(1200, len(bigmart_df)), random_state=42)
    fig = px.scatter(
        sample_df, x="Item_Visibility", y="Item_Outlet_Sales",
        color="Outlet_Size",
        opacity=0.6,
        labels={"Item_Visibility": "Tỷ lệ Hiển thị Quầy kệ (%)", "Item_Outlet_Sales": "Doanh số Bán ra ($)", "Outlet_Size": "Quy mô Siêu thị"},
    )
    apply_chart_theme(fig)
    fig.update_layout(
        hovermode="closest",
        margin=dict(l=12, r=12, t=16, b=48),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(tickformat=".1%")
    fig.update_yaxes(tickformat="$,.0f")
    return fig
