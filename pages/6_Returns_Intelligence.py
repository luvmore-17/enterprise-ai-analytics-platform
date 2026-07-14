import streamlit as st
import pandas as pd
import plotly.express as px

from config.database import engine

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Returns Intelligence",
    page_icon="🔄",
    layout="wide"
)

st.title("🔄 Returns Intelligence")

st.caption(
    "AI-Powered Product Returns, Financial Impact and Recovery Analytics"
)

st.divider()

# =====================================================
# LOAD DATA
# =====================================================

query = """
SELECT *
FROM analytics.vw_returns_analysis;
"""

returns_df = pd.read_sql(query, engine)

# =====================================================
# HELPER FUNCTION
# =====================================================

def format_currency(value):

    if value >= 1_000_000:
        return f"${value/1_000_000:.2f}M"

    elif value >= 1_000:
        return f"${value/1000:.2f}K"

    return f"${value:.2f}"

# =====================================================
# FILTERS
# =====================================================

st.subheader("🔎 Filters")

col1, col2 = st.columns(2)

with col1:

    countries = ["All"] + sorted(
        returns_df["country"].unique()
    )

    selected_country = st.selectbox(
        "Country",
        countries
    )

with col2:

    categories = ["All"] + sorted(
        returns_df["category_name"].unique()
    )

    selected_category = st.selectbox(
        "Product Category",
        categories
    )

filtered_df = returns_df.copy()

if selected_country != "All":

    filtered_df = filtered_df[
        filtered_df["country"] == selected_country
    ]

if selected_category != "All":

    filtered_df = filtered_df[
        filtered_df["category_name"] == selected_category
    ]

st.divider()

# =====================================================
# KPI DASHBOARD
# =====================================================

st.subheader("📊 Returns Overview")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_returns = filtered_df["total_quantity_returned"].sum()

average_return_rate = filtered_df["return_rate_pct"].mean()

lost_revenue = filtered_df["lost_revenue"].sum()

lost_profit = filtered_df["lost_profit"].sum()

kpi1.metric(
    "🔄 Total Returns",
    f"{int(total_returns):,}"
)

kpi2.metric(
    "📉 Average Return Rate",
    f"{average_return_rate:.2f}%"
)

kpi3.metric(
    "💰 Revenue Lost",
    format_currency(lost_revenue)
)

kpi4.metric(
    "📉 Profit Lost",
    format_currency(lost_profit)
)

kpi5, kpi6 = st.columns(2)

net_profit = filtered_df["net_profit_after_returns"].sum()

financial_impact = filtered_df["financial_impact"].sum()

kpi5.metric(
    "💵 Net Profit After Returns",
    format_currency(net_profit)
)

kpi6.metric(
    "⚠ Financial Impact",
    format_currency(financial_impact)
)

st.divider()
# =====================================================
# RETURNS VISUAL ANALYTICS
# =====================================================

st.subheader("📈 Returns Performance Analysis")

# -----------------------------------------------------
# Chart 1 - Return Rate by Category
# -----------------------------------------------------

left, right = st.columns(2)

category_returns = (
    filtered_df
    .groupby("category_name", as_index=False)
    .agg(
        return_rate=("return_rate_pct", "mean")
    )
    .sort_values("return_rate", ascending=False)
)

fig1 = px.bar(
    category_returns,
    x="category_name",
    y="return_rate",
    color="return_rate",
    text_auto=".2f",
    title="Average Return Rate by Category"
)

fig1.update_layout(
    xaxis_title="Category",
    yaxis_title="Return Rate (%)",
    hovermode="x unified"
)

left.plotly_chart(
    fig1,
    width="stretch"
)

# -----------------------------------------------------
# Chart 2 - Lost Revenue by Category
# -----------------------------------------------------

lost_revenue_df = (
    filtered_df
    .groupby("category_name", as_index=False)
    .agg(
        lost_revenue=("lost_revenue", "sum")
    )
    .sort_values("lost_revenue", ascending=False)
)

fig2 = px.bar(
    lost_revenue_df,
    x="category_name",
    y="lost_revenue",
    color="lost_revenue",
    text_auto=".2s",
    title="Revenue Lost by Category"
)

fig2.update_layout(
    xaxis_title="Category",
    yaxis_title="Lost Revenue ($)",
    hovermode="x unified"
)

right.plotly_chart(
    fig2,
    width="stretch"
)

st.divider()

# -----------------------------------------------------
# Chart 3 - Returns by Country
# -----------------------------------------------------

left, right = st.columns(2)

country_returns = (
    filtered_df
    .groupby("country", as_index=False)
    .agg(
        total_returns=("total_quantity_returned", "sum")
    )
    .sort_values("total_returns", ascending=False)
)

fig3 = px.bar(
    country_returns,
    x="country",
    y="total_returns",
    color="total_returns",
    title="Returns by Country"
)

fig3.update_layout(
    xaxis_title="Country",
    yaxis_title="Returned Quantity",
    hovermode="x unified"
)

left.plotly_chart(
    fig3,
    width="stretch"
)

# -----------------------------------------------------
# Chart 4 - Top Returned Products
# -----------------------------------------------------

top_products = (
    filtered_df
    .sort_values(
        "total_quantity_returned",
        ascending=False
    )
    .head(10)
)

fig4 = px.bar(
    top_products,
    x="total_quantity_returned",
    y="product_name",
    orientation="h",
    color="return_rate_pct",
    text="total_quantity_returned",
    title="Top 10 Returned Products"
)

fig4.update_layout(
    yaxis={"categoryorder": "total ascending"},
    xaxis_title="Returned Quantity",
    yaxis_title="Product",
    hovermode="closest"
)

right.plotly_chart(
    fig4,
    width="stretch"
)

st.divider()

# =====================================================
# AI RETURNS INTELLIGENCE
# =====================================================

st.subheader("🤖 AI Returns Intelligence")

# Highest Return Rate Product
highest_return = filtered_df.loc[
    filtered_df["return_rate_pct"].idxmax()
]

# Highest Revenue Loss Product
highest_loss = filtered_df.loc[
    filtered_df["lost_revenue"].idxmax()
]

# Highest Profit Loss Product
highest_profit_loss = filtered_df.loc[
    filtered_df["lost_profit"].idxmax()
]

# Highest Financial Impact
highest_financial = filtered_df.loc[
    filtered_df["financial_impact"].idxmax()
]

st.success(f"""

### Executive AI Summary

📦 **Highest Return Rate Product**

**{highest_return['product_name']}**

Return Rate:

**{highest_return['return_rate_pct']:.2f}%**

---

💰 **Largest Revenue Loss**

**{highest_loss['product_name']}**

Revenue Lost:

**{format_currency(highest_loss['lost_revenue'])}**

---

📉 **Largest Profit Loss**

**{highest_profit_loss['product_name']}**

Profit Lost:

**{format_currency(highest_profit_loss['lost_profit'])}**

---

⚠ **Highest Financial Impact**

**{highest_financial['product_name']}**

Financial Impact:

**{format_currency(highest_financial['financial_impact'])}**

""")

st.divider()

# =====================================================
# AI RISK ASSESSMENT
# =====================================================

st.subheader("🚨 Product Return Risk Assessment")

risk_df = filtered_df.sort_values(
    "return_rate_pct",
    ascending=False
)

for _, row in risk_df.head(10).iterrows():

    if row["return_rate_pct"] >= 15:

        st.error(
            f"🔴 {row['product_name']} | Return Rate: {row['return_rate_pct']:.2f}%"
        )

    elif row["return_rate_pct"] >= 8:

        st.warning(
            f"🟡 {row['product_name']} | Return Rate: {row['return_rate_pct']:.2f}%"
        )

    else:

        st.success(
            f"🟢 {row['product_name']} | Return Rate: {row['return_rate_pct']:.2f}%"
        )

st.divider()

# =====================================================
# AI BUSINESS RECOMMENDATIONS
# =====================================================

st.subheader("💡 AI Business Recommendations")

recommendations = (
    filtered_df[
        [
            "product_name",
            "return_rate_pct",
            "business_recommendation"
        ]
    ]
    .sort_values(
        "return_rate_pct",
        ascending=False
    )
    .head(10)
)

st.dataframe(
    recommendations,
    use_container_width=True,
    hide_index=True
)

st.divider()

# =====================================================
# AI RECOVERY OPPORTUNITY
# =====================================================

st.subheader("💰 Estimated Recovery Opportunity")

reduction_rate = st.slider(
    "Assume AI reduces returns by (%)",
    5,
    50,
    10
)

potential_revenue = (
    filtered_df["lost_revenue"].sum()
    * reduction_rate
    / 100
)

potential_profit = (
    filtered_df["lost_profit"].sum()
    * reduction_rate
    / 100
)

col1, col2 = st.columns(2)

col1.metric(
    "Recovered Revenue",
    format_currency(potential_revenue)
)

col2.metric(
    "Recovered Profit",
    format_currency(potential_profit)
)

st.info(
    f"""
If return rates are reduced by **{reduction_rate}%**,

the business could recover approximately

**{format_currency(potential_revenue)}** in revenue

and

**{format_currency(potential_profit)}** in profit.
"""
)

st.divider()