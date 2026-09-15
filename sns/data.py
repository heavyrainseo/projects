from __future__ import annotations

import pandas as pd
import seaborn as sns


MONTH_ORDER = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

MONTH_LABELS = {
    "Jan": "1월",
    "Feb": "2월",
    "Mar": "3월",
    "Apr": "4월",
    "May": "5월",
    "Jun": "6월",
    "Jul": "7월",
    "Aug": "8월",
    "Sep": "9월",
    "Oct": "10월",
    "Nov": "11월",
    "Dec": "12월",
}

MONTH_NUMBERS = {month: number for number, month in enumerate(MONTH_ORDER, start=1)}


def load_flights() -> pd.DataFrame:
    flights = sns.load_dataset("flights").copy()
    flights["month"] = pd.Categorical(
        flights["month"], categories=MONTH_ORDER, ordered=True
    )
    flights["month_number"] = flights["month"].map(MONTH_NUMBERS).astype("int64")
    flights["date"] = pd.to_datetime(
        flights["year"].astype(str)
        + "-"
        + flights["month_number"].astype(str)
        + "-01"
    )
    flights["month_label"] = flights["month"].map(MONTH_LABELS)
    return flights


def filter_flights(
    flights: pd.DataFrame, years: tuple[int, int], selected_months: list[str]
) -> pd.DataFrame:
    filtered = flights[flights["year"].between(years[0], years[1])]
    if selected_months:
        filtered = filtered[filtered["month"].isin(selected_months)]
    return filtered.copy()


def annual_summary(flights: pd.DataFrame) -> pd.DataFrame:
    return (
        flights.groupby("year", as_index=False, observed=True)["passengers"]
        .sum()
        .rename(columns={"passengers": "total_passengers"})
    )


def monthly_summary(flights: pd.DataFrame) -> pd.DataFrame:
    summary = (
        flights.groupby("month", as_index=False, observed=True)["passengers"]
        .mean()
        .rename(columns={"passengers": "average_passengers"})
    )
    summary["month_label"] = summary["month"].map(MONTH_LABELS)
    return summary


def year_month_summary(
    flights: pd.DataFrame, moving_average_months: int = 3
) -> pd.DataFrame:
    summary = flights.sort_values("date")[['date', 'passengers']].copy()
    summary['rolling_average'] = summary['passengers'].rolling(
        window=moving_average_months, min_periods=1
    ).mean()
    return summary


def year_month_matrix(flights: pd.DataFrame) -> pd.DataFrame:
    return flights.pivot(index="month_label", columns="year", values="passengers").reindex(
        [MONTH_LABELS[month] for month in MONTH_ORDER]
    )