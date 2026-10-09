"""Biểu đồ dự báo dùng chung một cửa sổ tháng và một kết quả mô hình."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.shared.forecast_model import make_forecast_projection
from src.shared.theme import apply_chart_theme


def _resolve(orders, target_year, projection):
    return projection if projection is not None else make_forecast_projection(orders, target_year=target_year)


def _finish(fig, projection, monthly=False):
    apply_chart_theme(fig)
    fig.update_layout(
        hovermode="x unified", margin=dict(l=12, r=12, t=32, b=126),
        legend=dict(y=-0.22),
    )
    start, end = projection["start"], projection["end"]
    if monthly:
        months = (end.year - start.year) * 12 + end.month - start.month + 1
        fig.update_xaxes(title="Tháng", tickformat="%m/%Y",
                         dtick="M1" if months <= 12 else "M3" if months <= 36 else "M12",
                         range=[start - pd.Timedelta(days=10), end + pd.offsets.MonthEnd(1)])
    else:
        fig.update_xaxes(title="Năm", dtick=1, range=[start.year - 0.4, end.year + 0.4])
    fig.update_yaxes(tickformat="$,.0f", automargin=True)
    return fig


def build_forecast_scenarios_figure(orders_filtered, target_year=2030, granularity="year", projection=None):
    """Tổng doanh thu theo năm hoặc chi tiết tháng trong khoảng đang chọn."""
    try:
        p = _resolve(orders_filtered, target_year, projection)
    except ValueError as error:
        return go.Figure(), str(error), {}
    history, future = p["visible_history"], p["visible_future"]
    fig = go.Figure()
    monthly = granularity == "month"
    if monthly:
        for frame, name, color in [
            (p["train"], "Thực tế huấn luyện", "#0284C7"),
            (p["test"], "Thực tế kiểm thử", "#059669"),
        ]:
            visible = frame[frame["Order Date"].between(p["start"], p["end"])]
            if not visible.empty:
                fig.add_trace(go.Scatter(x=visible["Order Date"], y=visible["Sales"],
                                        mode="lines+markers", name=name,
                                        line=dict(color=color, width=2),
                                        hovertemplate="%{x|%m/%Y}: $%{y:,.0f}<extra>%{fullData.name}</extra>"))
        test = p["test"][p["test"]["Order Date"].between(p["start"], p["end"])]
        if not test.empty:
            fig.add_trace(go.Scatter(x=test["Order Date"], y=test["Prediction"],
                                    mode="lines", name="Dự đoán kiểm thử",
                                    line=dict(color="#D97706", width=2, dash="dash")))
        x = list(future["Order Date"])
        values = {column: list(future[column]) for column in ("Cautious", "Optimistic", "Base")}
        # Chỉ nối khi điểm thực tế cuối cùng cũng nằm trong khoảng chọn.
        if not history.empty and not future.empty and history["Order Date"].iloc[-1] == p["history"]["Order Date"].iloc[-1]:
            x.insert(0, history["Order Date"].iloc[-1])
            for y in values.values():
                y.insert(0, float(history["Sales"].iloc[-1]))
    else:
        actual = history.groupby(history["Order Date"].dt.year)["Sales"].agg(["sum", "size"])
        if not actual.empty:
            fig.add_trace(go.Scatter(x=actual.index, y=actual["sum"], mode="lines+markers",
                                    name="Thực tế trong khoảng", line=dict(color="#0284C7", width=2),
                                    customdata=actual["size"],
                                    hovertemplate="%{x}: $%{y:,.0f}<br>%{customdata} tháng trong khoảng chọn<extra>Thực tế</extra>"))
        yearly = future.groupby(future["Order Date"].dt.year)[["Cautious", "Optimistic", "Base"]].sum()
        # Năm có cả tháng thực tế và dự báo: cộng hai phần trong cửa sổ.
        yearly = yearly.add(actual["sum"].reindex(yearly.index, fill_value=0), axis=0)
        x = list(yearly.index)
        values = {column: list(yearly[column]) for column in ("Cautious", "Optimistic", "Base")}
        if not actual.empty and x and actual.index[-1] < x[0] and actual["size"].iloc[-1] == 12:
            x.insert(0, int(actual.index[-1]))
            for y in values.values():
                y.insert(0, float(actual["sum"].iloc[-1]))

    if not future.empty:
        optimistic_pct = round(float(p.get("optimistic_weight", 0.20)) * 100)
        cautious_pct = round(float(p.get("cautious_weight", 0.15)) * 100)
        for column, name, color in [
            ("Cautious", f"Thận trọng (tới −{cautious_pct}%)", "#EF4444"),
            ("Optimistic", f"Lạc quan (tới +{optimistic_pct}%)", "#10B981"),
            ("Base", "Dự báo cơ sở", "#0B3B82"),
        ]:
            fig.add_trace(go.Scatter(
                x=x, y=values[column], mode="lines" if monthly else "lines+markers", name=name,
                line=dict(color=color, width=3 if column == "Base" else 1.5,
                          dash="solid" if column == "Base" else "dash"),
                fill="tonexty" if column == "Optimistic" else None, fillcolor="rgba(2,132,199,.08)",
                hovertemplate=("%{x|%m/%Y}" if monthly else "%{x}") + ": $%{y:,.0f}<extra>%{fullData.name}</extra>",
            ))
        boundary = future["Order Date"].iloc[0] if monthly else int(future["Order Date"].dt.year.iloc[0]) - 0.4
        right = p["end"] + pd.offsets.MonthEnd(1) if monthly else p["end"].year + 0.4
        fig.add_vrect(x0=boundary, x1=right, fillcolor="#E0F2FE", opacity=0.25, line_width=0, layer="below")
        # Không đặt annotation tại mép nếu cửa sổ chỉ có dự báo.
        if not history.empty:
            fig.add_vline(x=boundary, line_width=1, line_dash="dot", line_color="#94A3B8",
                          annotation_text="Dự phóng", annotation_position="top right",
                          annotation_font=dict(size=10, color="#64748B"))
    _finish(fig, p, monthly=monthly)
    fig.update_yaxes(title="Doanh thu tháng ($)" if monthly else "Doanh thu các tháng được chọn, theo năm ($)")
    kpis = p["kpis"]
    first, last = p["history"]["Order Date"].iloc[[0, -1]]
    caption = (
        f"Đang xem {p['start']:%m/%Y}–{p['end']:%m/%Y}. "
        f"Nguồn huấn luyện: {', '.join(kpis['sources']) or 'dữ liệu đang lọc'}; {first:%m/%Y}–{last:%m/%Y}. "
        f"Kiểm thử {kpis['test_months']} tháng cuối: MAE = ${kpis['mae']:,.0f}/tháng | RMSE = ${kpis['rmse']:,.0f}/tháng. "
        "Dải màu là kịch bản giả định, không phải khoảng tin cậy thống kê."
    )
    return fig, caption, kpis


def _orders_scope(orders, projection):
    """Dòng đơn hàng thuộc cùng đoạn lịch sử dùng để huấn luyện."""
    frame = orders.copy()
    frame["Month"] = pd.to_datetime(frame["Order Date"]).dt.to_period("M").dt.to_timestamp()
    history = projection["history"]
    frame = frame[frame["Month"].between(history["Order Date"].iloc[0], history["Order Date"].iloc[-1])]
    sources = projection["kpis"]["sources"]
    if sources and "Data Source" in frame.columns:
        frame = frame[frame["Data Source"].isin(sources)]
    return frame


def _recent_orders(frame, projection):
    last = projection["history"]["Order Date"].iloc[-1]
    return frame[frame["Month"] >= last - pd.DateOffset(months=11)]


def build_category_forecast_figure(orders_filtered, target_year=2030, projection=None):
    try:
        p = _resolve(orders_filtered, target_year, projection)
    except ValueError:
        return go.Figure()
    scope = _orders_scope(orders_filtered, p)
    recent = _recent_orders(scope, p).groupby("Category")["Sales"].sum()
    shares = recent / recent.sum() if recent.sum() > 0 else recent * 0
    visible = scope[scope["Month"].between(p["start"], p["end"])]
    rows = [{"Năm": int(year), "Danh mục": category, "Doanh thu": float(sales), "Loại": "Thực tế"}
            for (year, category), sales in visible.groupby([visible["Month"].dt.year, "Category"])["Sales"].sum().items()]
    for year, sales in p["visible_future"].groupby(p["visible_future"]["Order Date"].dt.year)["Base"].sum().items():
        rows.extend({"Năm": int(year), "Danh mục": category, "Doanh thu": float(sales * share), "Loại": "Dự báo"}
                    for category, share in shares.items())
    if not rows:
        return go.Figure()
    fig = px.bar(pd.DataFrame(rows), x="Năm", y="Doanh thu", color="Danh mục",
                 custom_data=["Loại"], barmode="stack",
                 color_discrete_sequence=["#0284C7", "#0EA5E9", "#059669", "#D97706", "#7C5CFC", "#E11D48"])
    fig.update_traces(hovertemplate="%{x}: $%{y:,.0f}<br>%{customdata[0]}<extra>%{fullData.name}</extra>")
    return _finish(fig, p)


def build_regional_forecast_figure(orders_filtered, target_year=2030, projection=None):
    try:
        p = _resolve(orders_filtered, target_year, projection)
    except ValueError:
        return go.Figure()
    scope = _orders_scope(orders_filtered, p)
    recent = _recent_orders(scope, p).groupby("Region")["Sales"].sum()
    top = recent.nlargest(6).index
    shares = recent / recent.sum() if recent.sum() > 0 else recent * 0
    actual = scope[scope["Month"].between(p["start"], p["end"])].groupby("Region")["Sales"].sum()
    predicted = float(p["visible_future"]["Base"].sum())
    rows = []
    for region in top:
        if not p["visible_history"].empty:
            rows.append({"Khu vực": region, "Loại": "Thực tế trong khoảng", "Doanh thu": float(actual.get(region, 0))})
        if not p["visible_future"].empty:
            rows.append({"Khu vực": region, "Loại": "Dự báo trong khoảng", "Doanh thu": float(predicted * shares[region])})
    if not rows:
        return go.Figure()
    fig = px.bar(pd.DataFrame(rows), x="Khu vực", y="Doanh thu", color="Loại", barmode="group",
                 color_discrete_map={"Thực tế trong khoảng": "#94A3B8", "Dự báo trong khoảng": "#0284C7"})
    _finish(fig, p)
    # Trục X là khu vực, không phải năm.
    fig.update_xaxes(title="Khu vực", type="category", range=None, dtick=None,
                     tickangle=-15, automargin=True)
    return fig


def build_quantity_profit_forecast_figure(orders_filtered, target_year=2030, projection=None):
    try:
        p = _resolve(orders_filtered, target_year, projection)
    except ValueError:
        return go.Figure()
    scope = _orders_scope(orders_filtered, p)
    recent = _recent_orders(scope, p)
    sales = float(recent["Sales"].sum())
    qty_ratio = float(recent["Quantity"].sum()) / sales if sales > 0 else 0
    profit_ratio = float(recent["Profit"].sum()) / sales if sales > 0 else 0
    visible = scope[scope["Month"].between(p["start"], p["end"])]
    actual = visible.groupby(visible["Month"].dt.year)[["Quantity", "Profit"]].sum()
    forecast = p["visible_future"].groupby(p["visible_future"]["Order Date"].dt.year)["Base"].sum()
    predicted = pd.DataFrame({"Quantity": forecast * qty_ratio, "Profit": forecast * profit_ratio})
    combined = actual.add(predicted, fill_value=0).sort_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=combined.index, y=combined["Quantity"], name="Sản lượng (đơn vị)", marker_color="#38BDF8",
                        hovertemplate="%{x}: %{y:,.0f} đơn vị<extra>Sản lượng trong khoảng</extra>"))
    fig.add_trace(go.Scatter(x=combined.index, y=combined["Profit"], mode="lines+markers", name="Lợi nhuận ($)",
                            line=dict(color="#059669", width=3), yaxis="y2",
                            hovertemplate="%{x}: $%{y:,.0f}<extra>Lợi nhuận trong khoảng</extra>"))
    _finish(fig, p)
    fig.update_layout(yaxis=dict(title="Sản lượng (đơn vị)", tickformat=",.0f", showgrid=False),
                      yaxis2=dict(title="Lợi nhuận ($)", overlaying="y", side="right", tickformat="$,.0f", showgrid=False))
    return fig
