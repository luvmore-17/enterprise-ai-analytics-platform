import streamlit as st
import pandas as pd
import plotly.express as px

from config.database import engine

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="Product Analytics",
    page_icon="🛍",
    layout="wide"
)

st.title("🛍 Product Analytics")
st.caption("Enterprise Product Intelligence Dashboard")

st.divider()

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

product_query = """
SELECT *
FROM analytics.vw_product_performance;
"""

recommendation_query = """
SELECT *
FROM analytics.vw_product_recommendations
ORDER BY confidence_pct DESC;
"""

product_df = pd.read_sql(product_query, engine)
recommendation_df = pd.read_sql(recommendation_query, engine)

# ---------------------------------------------------------
# HELPER FUNCTION
# ---------------------------------------------------------

def money(x):
    if x >= 1_000_000:
        return f"${x/1_000_000:.2f}M"
    elif x >= 1_000:
        return f"${x/1000:.2f}K"
    return f"${x:.2f}"

# ---------------------------------------------------------
# FILTERS
# ---------------------------------------------------------

st.subheader("Filters")

c1, c2, c3 = st.columns(3)

with c1:
    categories = ["All"] + sorted(product_df["category_name"].unique())
    selected_category = st.selectbox("Category", categories)

with c2:
    sub_df = product_df.copy()

    if selected_category != "All":
        sub_df = sub_df[
            sub_df["category_name"] == selected_category
        ]

    subcategories = ["All"] + sorted(sub_df["subcategory_name"].unique())

    selected_subcategory = st.selectbox(
        "Subcategory",
        subcategories
    )

with c3:

    product_filter = sub_df.copy()

    if selected_subcategory != "All":
        product_filter = product_filter[
            product_filter["subcategory_name"] == selected_subcategory
        ]

    products = ["All"] + sorted(product_filter["product_name"].unique())

    selected_product = st.selectbox(
        "Product",
        products
    )

# ---------------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------------

filtered = product_df.copy()

if selected_category != "All":
    filtered = filtered[
        filtered["category_name"] == selected_category
    ]

if selected_subcategory != "All":
    filtered = filtered[
        filtered["subcategory_name"] == selected_subcategory
    ]

if selected_product != "All":
    filtered = filtered[
        filtered["product_name"] == selected_product
    ]

# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------

st.subheader("Product Performance")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "💰 Revenue",
    money(filtered["revenue"].sum())
)

k2.metric(
    "💵 Profit",
    money(filtered["profit"].sum())
)

k3.metric(
    "📦 Quantity",
    f"{int(filtered['total_quantity'].sum()):,}"
)

k4.metric(
    "🛒 Avg Selling Price",
    money(filtered["average_selling_price"].mean())
)

st.divider()

# ---------------------------------------------------------
# CATEGORY CHARTS
# ---------------------------------------------------------

left, right = st.columns(2)

with left:

    category = (
        filtered.groupby("category_name", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)
    )

    fig = px.bar(
        category,
        x="revenue",
        y="category_name",
        orientation="h",
        title="Revenue by Category",
        text_auto=".2s",
        color="revenue"
    )

    st.plotly_chart(fig, use_container_width=True)

with right:

    pie = px.pie(
        category,
        names="category_name",
        values="revenue",
        hole=.55,
        title="Revenue Share"
    )

    st.plotly_chart(pie, use_container_width=True)

# ---------------------------------------------------------
# TOP PRODUCTS
# ---------------------------------------------------------

left, right = st.columns(2)

with left:

    top_rev = (
        filtered.sort_values("revenue", ascending=False)
        .head(10)
    )

    fig = px.bar(
        top_rev,
        x="revenue",
        y="product_name",
        orientation="h",
        title="Top 10 Products by Revenue",
        color="revenue"
    )

    st.plotly_chart(fig, use_container_width=True)

with right:

    top_profit = (
        filtered.sort_values("profit", ascending=False)
        .head(10)
    )

    fig = px.bar(
        top_profit,
        x="profit",
        y="product_name",
        orientation="h",
        title="Top 10 Products by Profit",
        color="profit"
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# PRODUCT TABLE
# ---------------------------------------------------------

st.subheader("Product Performance Table")

table = filtered[
    [
        "product_name",
        "category_name",
        "subcategory_name",
        "revenue",
        "profit",
        "calculated_profit_margin_pct",
        "total_orders",
        "average_selling_price"
    ]
]

st.dataframe(
    table,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ---------------------------------------------------------
# AI PRODUCT INTELLIGENCE
# ---------------------------------------------------------

st.subheader("🤖 AI Product Intelligence")

top_revenue = filtered.loc[
    filtered["revenue"].idxmax()
]

top_profit = filtered.loc[
    filtered["profit"].idxmax()
]

top_margin = filtered.loc[
    filtered["calculated_profit_margin_pct"].idxmax()
]

lowest = filtered.loc[
    filtered["profit"].idxmin()
]

best_category = (
    filtered.groupby("category_name")["revenue"]
    .sum()
    .idxmax()
)

st.success(
    f"🏆 Highest Revenue Product: **{top_revenue['product_name']}** "
    f"generated **{money(top_revenue['revenue'])}**."
)

st.info(
    f"💰 Highest Profit Product: **{top_profit['product_name']}** "
    f"earned **{money(top_profit['profit'])}**."
)

st.info(
    f"📈 Highest Margin Product: **{top_margin['product_name']}** "
    f"achieved **{top_margin['calculated_profit_margin_pct']:.2f}%** margin."
)

st.warning(
    f"⚠ Lowest Profit Product: **{lowest['product_name']}** "
    f"generated **{money(lowest['profit'])}**."
)

st.success(
    f"📦 Best Performing Category: **{best_category}**."
)

st.divider()

# ---------------------------------------------------------
# PRODUCT RECOMMENDATIONS
# ---------------------------------------------------------

st.subheader("🎯 Cross-Selling Recommendations")

top5 = recommendation_df.head(5)

for _, rec in top5.iterrows():

    with st.container(border=True):

        c1, c2, c3 = st.columns([3,2,2])

        with c1:

            st.markdown(
                f"### {rec['product_name']}"
            )

            st.write(
                f"Customers also buy **{rec['recommended_product']}**"
            )

        with c2:

            st.metric(
                "Confidence",
                f"{rec['confidence_pct']:.2f}%"
            )

        with c3:

            st.metric(
                "Strength",
                rec["recommendation_strength"]
            )

        if rec["confidence_pct"] >= 50:

            st.success(
                "AI Recommendation: Bundle these products."
            )

        elif rec["confidence_pct"] >= 20:

            st.info(
                "AI Recommendation: Cross-sell during checkout."
            )

        else:

            st.warning(
                "AI Recommendation: Monitor customer buying behaviour."
            )

st.divider()

st.caption(
    "Enterprise AI Analytics Platform | Product Analytics Module"
)