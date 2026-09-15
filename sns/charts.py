from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


ACCENT = "#e05a47"
INK = "#202a2e"
MUTED = "#657276"
GRID = "#e4e9e8"


def _layout(figure: go.Figure) -> go.Figure:
    figure.update_layout(
        font={"family": "Pretendard, Noto Sans KR, sans-serif", "color": INK},
        margin={"l": 12, "r": 12, "t": 20, "b": 12},
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hoverlabel={"bgcolor": INK, "font_color": "white"},
    )
    figure.update_xaxes(showgrid=False, linecolor=GRID, tickfont={"color": MUTED})
    figure.update_yaxes(gridcolor=GRID, zeroline=False, tickfont={"color": MUTED})
    return figure


def annual_chart(summary: pd.DataFrame) -> go.Figure:
    figure = px.bar(
        summary,
        x="year",
        y="total_passengers",
        labels={"year": "연도", "total_passengers": "승객 수"},
        color_discrete_sequence=[ACCENT],
    )
    figure.update_traces(hovertemplate="%{x}년<br>%{y:,.0f}명<extra></extra>")
    return _layout(figure)


def monthly_chart(summary: pd.DataFrame) -> go.Figure:
    figure = px.bar(
        summary,
        x="month_label",
        y="average_passengers",
        labels={"month_label": "월", "average_passengers": "평균 승객 수"},
        color_discrete_sequence=["#2d7d8a"],
    )
    figure.update_traces(hovertemplate="%{x}<br>%{y:,.0f}명<extra></extra>")
    return _layout(figure)


def timeline_chart(summary: pd.DataFrame, moving_average_months: int = 3) -> go.Figure:
    figure = px.line(
        summary,
        x="date",
        y="passengers",
        labels={"date": "기간", "passengers": "승객 수"},
        title=None,
        color_discrete_sequence=[ACCENT],
        markers=True,
    )
    figure.update_traces(
        name="월별 승객 수",
        hovertemplate="%{x|%Y년 %m월}<br>%{y:,.0f}명<extra></extra>",
    )
    figure.add_scatter(
        x=summary["date"],
        y=summary["rolling_average"],
        mode="lines",
        name=f"{moving_average_months}개월 이동평균",
        line={"color": "#202a2e", "width": 3},
        hovertemplate="%{x|%Y년 %m월}<br>이동평균 %{y:,.0f}명<extra></extra>",
    )
    figure.update_layout(legend={"orientation": "h", "y": 1.08, "x": 0})
    return _layout(figure)


def heatmap(matrix: pd.DataFrame) -> go.Figure:
    figure = px.imshow(
        matrix,
        labels={"x": "연도", "y": "월", "color": "승객 수"},
        color_continuous_scale=["#e9f0ee", "#2d7d8a", "#202a2e"],
        aspect="auto",
    )
    figure.update_traces(hovertemplate="%{y} / %{x}년<br>%{z:,.0f}명<extra></extra>")
    return _layout(figure)