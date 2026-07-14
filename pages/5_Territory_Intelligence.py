import streamlit as st
import pandas as pd
import plotly.express as px

from config.database import engine

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="Territory Intelligence",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Territory Intelligence")

st.caption(
    "AI-Powered Geographic Business Intelligence"
)

st.divider()

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

query = """
SELECT *
FROM analytics.vw_territory_performance;
"""

territory_df = pd.read_sql(query, engine)

# ---------------------------------------------------------
# HELPER
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

    countries = ["All"] + sorted(
        territory_df["country"].unique()
    )

    selected_country = st.selectbox(
        "Country",
        countries
    )

with f2:

    continents = ["All"] + sorted(
        territory_df["continent"].unique()
    )

    selected_continent = st.selectbox(
        "Continent",
        continents
    )

filtered_df = territory_df.copy()

if selected_country != "All":

    filtered_df = filtered_df[
        filtered_df["country"] == selected_country
    ]

if selected_continent != "All":

    filtered_df = filtered_df[
        filtered_df["continent"] == selected_continent
    ]

# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------

st.subheader("Territory Overview")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "🌍 Countries",
    filtered_df["country"].nunique()
)

k2.metric(
    "💰 Revenue",
    format_currency(
        filtered_df["total_revenue"].sum()
    )
)

k3.metric(
    "📈 Profit",
    format_currency(
        filtered_df["total_profit"].sum()
    )
)

k4.metric(
    "📦 Orders",
    f"{filtered_df['total_orders'].sum():,.0f}"
)

st.divider()

# ---------------------------------------------------------
# TERRITORY VISUAL ANALYTICS
# ---------------------------------------------------------

st.subheader("📊 Territory Performance")

left, right = st.columns(2)

# Revenue by Country

country_revenue = (
    filtered_df
    .groupby("country", as_index=False)
    .agg(
        revenue=("total_revenue", "sum")
    )
    .sort_values("revenue", ascending=False)
)

fig1 = px.bar(
    country_revenue,
    x="revenue",
    y="country",
    orientation="h",
    color="revenue",
    title="Revenue by Country"
)

fig1.update_layout(
    yaxis={"categoryorder":"total ascending"}
)

left.plotly_chart(
    fig1,
    width="stretch"
)

# Profit by Country

country_profit = (
    filtered_df
    .groupby("country", as_index=False)
    .agg(
        profit=("total_profit","sum")
    )
    .sort_values("profit", ascending=False)
)

fig2 = px.bar(
    country_profit,
    x="profit",
    y="country",
    orientation="h",
    color="profit",
    title="Profit by Country"
)

fig2.update_layout(
    yaxis={"categoryorder":"total ascending"}
)

right.plotly_chart(
    fig2,
    width="stretch"
)

st.divider()

left, right = st.columns(2)

market_share = (
    filtered_df
    .groupby("country", as_index=False)
    .agg(
        revenue=("total_revenue","sum")
    )
)

pie = px.pie(
    market_share,
    names="country",
    values="revenue",
    hole=.55,
    title="Market Share"
)

left.plotly_chart(
    pie,
    width="stretch"
)

orders = (
    filtered_df
    .groupby("country", as_index=False)
    .agg(
        orders=("total_orders","sum")
    )
)

bar = px.bar(
    orders,
    x="country",
    y="orders",
    color="orders",
    title="Orders by Country"
)

right.plotly_chart(
    bar,
    width="stretch"
)

st.divider()
# ---------------------------------------------------------
# AI TERRITORY INTELLIGENCE
# ---------------------------------------------------------

st.subheader("🤖 AI Territory Intelligence")

# Top performing country
top_country = (
    filtered_df.groupby("country")["total_revenue"]
    .sum()
    .idxmax()
)

top_country_revenue = (
    filtered_df.groupby("country")["total_revenue"]
    .sum()
    .max()
)

# Highest profit country
best_profit_country = (
    filtered_df.groupby("country")["total_profit"]
    .sum()
    .idxmax()
)

best_profit = (
    filtered_df.groupby("country")["total_profit"]
    .sum()
    .max()
)

# Highest margin country
margin_df = (
    filtered_df.groupby("country", as_index=False)
    .agg(
        avg_margin=("profit_margin_pct", "mean")
    )
)

best_margin = margin_df.loc[
    margin_df["avg_margin"].idxmax()
]

# Largest customer base
customer_df = (
    filtered_df.groupby("country", as_index=False)
    .agg(
        customers=("total_customers", "sum")
    )
)

largest_market = customer_df.loc[
    customer_df["customers"].idxmax()
]

st.success(f"""

### Executive Summary

🌍 **Top Revenue Market**

**{top_country}**

Revenue Generated:

**{format_currency(top_country_revenue)}**

---

💰 **Highest Profit Market**

**{best_profit_country}**

Profit Generated:

**{format_currency(best_profit)}**

---

📈 **Highest Profit Margin**

**{best_margin['country']}**

Profit Margin:

**{best_margin['avg_margin']:.2f}%**

---

👥 **Largest Customer Base**

**{largest_market['country']}**

Customers:

**{int(largest_market['customers']):,}**

""")

st.divider()

# ---------------------------------------------------------
# AI EXPANSION OPPORTUNITIES
# ---------------------------------------------------------

st.subheader("🚀 Expansion Opportunities")

recommendations = []

country_summary = (
    filtered_df.groupby("country", as_index=False)
    .agg(
        revenue=("total_revenue", "sum"),
        profit=("total_profit", "sum"),
        margin=("profit_margin_pct", "mean")
    )
)

for _, row in country_summary.iterrows():

    if row["margin"] > 45:

        action = "Expand premium product lines."

    elif row["revenue"] > country_summary["revenue"].median():

        action = "Increase inventory and marketing."

    else:

        action = "Launch promotional campaigns."

    recommendations.append(
        {
            "Country": row["country"],
            "Revenue": format_currency(row["revenue"]),
            "Profit Margin": f"{row['margin']:.2f}%",
            "AI Recommendation": action
        }
    )

recommendation_df = pd.DataFrame(recommendations)

st.dataframe(
    recommendation_df,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ---------------------------------------------------------
# TERRITORY RISK ANALYSIS
# ---------------------------------------------------------

st.subheader("⚠ Territory Risk Assessment")

for _, row in country_summary.iterrows():

    if row["margin"] < 35:

        st.error(
            f"🔴 {row['country']} - Low profit margin ({row['margin']:.2f}%). Review pricing strategy."
        )

    elif row["margin"] < 42:

        st.warning(
            f"🟡 {row['country']} - Moderate profitability. Monitor operational costs."
        )

    else:

        st.success(
            f"🟢 {row['country']} - Healthy performance. Continue investing."
        )

st.divider()

# ---------------------------------------------------------
# EXECUTIVE DECISION PANEL
# ---------------------------------------------------------

st.subheader("🧠 Executive Decision Panel")

left, right = st.columns(2)

with left:

    st.info("📌 Recommended Action")

    st.markdown(f"""
- Increase investment in **{top_country}**
- Expand premium products in **{best_margin['country']}**
- Prioritize customer acquisition in emerging territories
- Optimize logistics in lower-performing regions
""")

with right:

    revenue_opportunity = country_summary["revenue"].sum() * 0.08

    st.success("💡 Estimated Growth Opportunity")

    st.metric(
        "Potential Additional Revenue",
        format_currency(revenue_opportunity)
    )

    st.write(
        "Estimated if AI recommendations are implemented successfully."
    )

st.divider()

st.caption(
    "Enterprise AI Analytics Platform | Territory Intelligence Module"
)