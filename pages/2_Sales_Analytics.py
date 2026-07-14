import streamlit as st
import pandas as pd
import plotly.express as px

from config.database import engine

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="Sales Analytics",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Sales Analytics")
st.caption("Interactive Sales Performance Dashboard")

st.divider()

# ---------------------------------------------------------
# LOAD SALES DATA
# ---------------------------------------------------------

query = """
SELECT *
FROM analytics.vw_sales_summary
ORDER BY year, month;
"""

sales_df = pd.read_sql(query, engine)

sales_df["period"] = (
    sales_df["month_name"].str[:3]
    + " "
    + sales_df["year"].astype(str)
)

# ---------------------------------------------------------
# HELPER FUNCTION
# ---------------------------------------------------------

def format_currency(value):
    if value >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"${value/1000:.2f}K"
    return f"${value:.2f}"

# ---------------------------------------------------------
# FILTERS
# ---------------------------------------------------------

st.subheader("Filters")

f1, f2 = st.columns(2)

with f1:
    years = ["All"] + sorted(sales_df["year"].unique().tolist())
    selected_year = st.selectbox("Year", years)

with f2:
    quarters = ["All"] + sorted(sales_df["quarter"].unique().tolist())
    selected_quarter = st.selectbox("Quarter", quarters)

filtered_df = sales_df.copy()

if selected_year != "All":
    filtered_df = filtered_df[
        filtered_df["year"] == selected_year
    ]

if selected_quarter != "All":
    filtered_df = filtered_df[
        filtered_df["quarter"] == selected_quarter
    ]

# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------

st.subheader("Sales Performance")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "💵 Revenue",
    format_currency(filtered_df["total_revenue"].sum())
)

k2.metric(
    "💰 Profit",
    format_currency(filtered_df["total_profit"].sum())
)

k3.metric(
    "📦 Orders",
    f"{int(filtered_df['total_orders'].sum()):,}"
)

k4.metric(
    "🛒 Quantity Sold",
    f"{int(filtered_df['total_quantity'].sum()):,}"
)

st.divider()

# ---------------------------------------------------------
# REVENUE & PROFIT TRENDS
# ---------------------------------------------------------

left, right = st.columns(2)

with left:

    revenue_fig = px.line(
        filtered_df,
        x="period",
        y="total_revenue",
        markers=True,
        title="Monthly Revenue Trend"
    )

    revenue_fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        xaxis_title="Period",
        yaxis_title="Revenue ($)"
    )

    st.plotly_chart(revenue_fig, width="stretch")

with right:

    profit_fig = px.line(
        filtered_df,
        x="period",
        y="total_profit",
        markers=True,
        title="Monthly Profit Trend"
    )

    profit_fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        xaxis_title="Period",
        yaxis_title="Profit ($)"
    )

    st.plotly_chart(profit_fig, width="stretch")

# ---------------------------------------------------------
# ORDERS & REVENUE VS PROFIT
# ---------------------------------------------------------

left2, right2 = st.columns(2)

with left2:

    orders_fig = px.bar(
        filtered_df,
        x="period",
        y="total_orders",
        title="Monthly Orders"
    )

    orders_fig.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(orders_fig, width="stretch")

with right2:

    compare_df = filtered_df.melt(
        id_vars="period",
        value_vars=[
            "total_revenue",
            "total_profit"
        ],
        var_name="Metric",
        value_name="Amount"
    )

    compare_fig = px.area(
        compare_df,
        x="period",
        y="Amount",
        color="Metric",
        title="Revenue vs Profit"
    )

    compare_fig.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(compare_fig, width="stretch")

st.divider()

# ---------------------------------------------------------
# SALES TABLE
# ---------------------------------------------------------

st.subheader("Monthly Sales Summary")

display_df = filtered_df[
    [
        "year",
        "month_name",
        "quarter",
        "total_orders",
        "total_quantity",
        "total_revenue",
        "total_cost",
        "total_profit"
    ]
]

st.dataframe(display_df, width="stretch")

st.divider()

# ---------------------------------------------------------
# AI SALES INSIGHTS
# ---------------------------------------------------------

st.subheader("🤖 AI Sales Insights")

total_revenue = filtered_df["total_revenue"].sum()
total_profit = filtered_df["total_profit"].sum()
total_orders = filtered_df["total_orders"].sum()

profit_margin = (
    total_profit /
    total_revenue
) * 100

best_month = filtered_df.loc[
    filtered_df["total_revenue"].idxmax()
]

worst_month = filtered_df.loc[
    filtered_df["total_revenue"].idxmin()
]

insights = []

insights.append(
    f"Revenue reached **{format_currency(total_revenue)}**."
)

insights.append(
    f"Profit reached **{format_currency(total_profit)}** "
    f"with a margin of **{profit_margin:.2f}%**."
)

insights.append(
    f"Total completed orders: **{int(total_orders):,}**."
)

insights.append(
    f"Highest revenue month: **{best_month['month_name']} {best_month['year']}** "
    f"({format_currency(best_month['total_revenue'])})."
)

insights.append(
    f"Lowest revenue month: **{worst_month['month_name']} {worst_month['year']}** "
    f"({format_currency(worst_month['total_revenue'])})."
)

for insight in insights:
    st.info(insight)

st.divider()

st.caption(
    "Enterprise AI Analytics Platform | Sales Analytics Module"
)

