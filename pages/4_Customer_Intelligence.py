import streamlit as st
import pandas as pd
import plotly.express as px

from config.database import engine

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="Customer Intelligence",
    page_icon="👥",
    layout="wide"
)

st.title("👥 Customer Intelligence")
st.caption("AI-Powered Customer Analytics & Marketing Intelligence")

st.divider()

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

customer_query = """
SELECT *
FROM analytics.vw_customer_preferences;
"""

segment_query = """
SELECT *
FROM analytics.vw_customer_segments;
"""

customer_df = pd.read_sql(customer_query, engine)
segment_df = pd.read_sql(segment_query, engine)

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

st.subheader("Customer Filters")

f1, f2, f3 = st.columns(3)

with f1:

    genders = ["All"] + sorted(
        customer_df["gender"].dropna().unique().tolist()
    )

    selected_gender = st.selectbox(
        "Gender",
        genders
    )

with f2:

    age_groups = ["All"] + sorted(
        customer_df["age_group"].dropna().unique().tolist()
    )

    selected_age = st.selectbox(
        "Age Group",
        age_groups
    )

with f3:

    segments = ["All"] + sorted(
        customer_df["customer_segment"].dropna().unique().tolist()
    )

    selected_segment = st.selectbox(
        "Customer Segment",
        segments
    )

# ---------------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------------

filtered_df = customer_df.copy()

if selected_gender != "All":

    filtered_df = filtered_df[
        filtered_df["gender"] == selected_gender
    ]

if selected_age != "All":

    filtered_df = filtered_df[
        filtered_df["age_group"] == selected_age
    ]

if selected_segment != "All":

    filtered_df = filtered_df[
        filtered_df["customer_segment"] == selected_segment
    ]

# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------

st.subheader("Customer Overview")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "👥 Customers",
    f"{filtered_df['customer_key'].nunique():,}"
)

k2.metric(
    "💰 Revenue",
    format_currency(filtered_df["total_spent"].sum())
)

k3.metric(
    "💵 Average Spend",
    format_currency(filtered_df["total_spent"].mean())
)

k4.metric(
    "📦 Average Orders",
    f"{filtered_df['total_orders'].mean():.1f}"
)

st.divider()

# ---------------------------------------------------------
# CUSTOMER VISUAL ANALYTICS
# ---------------------------------------------------------

st.subheader("📊 Customer Insights")

# ============================================
# Row 1
# Customer Segments & Gender Distribution
# ============================================

left_chart, right_chart = st.columns(2)

with left_chart:

    segment_summary = (
        filtered_df
        .groupby("customer_segment", as_index=False)
        .agg(customers=("customer_key", "nunique"))
    )

    segment_fig = px.pie(
        segment_summary,
        names="customer_segment",
        values="customers",
        hole=0.55,
        title="Customer Segmentation"
    )

    segment_fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Customers: %{value}<extra></extra>"
    )

    st.plotly_chart(
        segment_fig,
        width="stretch"
    )


with right_chart:

    gender_summary = (
        filtered_df
        .groupby("gender", as_index=False)
        .agg(customers=("customer_key", "nunique"))
    )

    gender_fig = px.bar(
        gender_summary,
        x="gender",
        y="customers",
        color="gender",
        title="Gender Distribution",
        text_auto=True
    )

    gender_fig.update_layout(
        showlegend=False,
        xaxis_title="Gender",
        yaxis_title="Customers"
    )

    st.plotly_chart(
        gender_fig,
        width="stretch"
    )

# ============================================
# Row 2
# Income Band & Spending
# ============================================

left_chart, right_chart = st.columns(2)

with left_chart:

    income_summary = (
        filtered_df
        .groupby("income_band", as_index=False)
        .agg(customers=("customer_key", "nunique"))
    )

    income_fig = px.bar(
        income_summary,
        x="income_band",
        y="customers",
        color="income_band",
        title="Income Band Distribution",
        text_auto=True
    )

    income_fig.update_layout(
        showlegend=False,
        xaxis_title="Income Band",
        yaxis_title="Customers"
    )

    st.plotly_chart(
        income_fig,
        width="stretch"
    )

with right_chart:

    spending_summary = (
        filtered_df
        .groupby("customer_segment", as_index=False)
        .agg(
            average_spend=("total_spent", "mean")
        )
    )

    spending_fig = px.bar(
        spending_summary,
        x="customer_segment",
        y="average_spend",
        color="average_spend",
        title="Average Customer Spend by Segment",
        text_auto=".2s"
    )

    spending_fig.update_layout(
        xaxis_title="Customer Segment",
        yaxis_title="Average Spend"
    )

    st.plotly_chart(
        spending_fig,
        width="stretch"
    )

st.divider()

# ============================================
# TOP SPENDING CUSTOMERS
# ============================================

st.subheader("🏆 Top Spending Customers")

top_customers = (
    filtered_df
    .sort_values("total_spent", ascending=False)
    .head(15)
)

leaderboard_fig = px.bar(
    top_customers,
    x="total_spent",
    y="full_name",
    orientation="h",
    color="customer_segment",
    title="Top 15 Customers by Total Spend",
    hover_data=[
        "gender",
        "age_group",
        "income_band",
        "favourite_product"
    ]
)

leaderboard_fig.update_layout(
    yaxis={"categoryorder": "total ascending"},
    xaxis_title="Total Spend ($)",
    yaxis_title=""
)

st.plotly_chart(
    leaderboard_fig,
    width="stretch"
)

st.divider()

# ---------------------------------------------------------
# AI CUSTOMER INTELLIGENCE
# ---------------------------------------------------------

st.subheader("🤖 AI Customer Intelligence")

total_customers = filtered_df["customer_key"].nunique()

total_revenue = filtered_df["total_spent"].sum()

avg_spend = filtered_df["total_spent"].mean()

highest_customer = filtered_df.loc[
    filtered_df["total_spent"].idxmax()
]

highest_segment = (
    filtered_df
    .groupby("customer_segment")["total_spent"]
    .sum()
    .idxmax()
)

highest_income = (
    filtered_df
    .groupby("income_band")["total_spent"]
    .sum()
    .idxmax()
)

favorite_category = (
    filtered_df["favourite_category"]
    .mode()
    .iloc[0]
)

favourite_product = (
    filtered_df["favourite_product"]
    .mode()
    .iloc[0]
)

st.success(
    f"""
### Executive Summary

The company currently serves **{total_customers:,} customers**
who have generated **{format_currency(total_revenue)}**
in lifetime revenue.

Average customer spend is
**{format_currency(avg_spend)}**.

The highest spending customer is
**{highest_customer['full_name']}**
with purchases totaling
**{format_currency(highest_customer['total_spent'])}**.
"""
)

st.divider()

# ---------------------------------------------------------
# CUSTOMER INSIGHTS
# ---------------------------------------------------------

left, right = st.columns(2)

with left:

    st.info("🏆 Best Customer Segment")

    st.write(
        f"""
**{highest_segment}** customers currently generate the
highest overall revenue.

Recommendation:

Increase loyalty benefits to retain this segment.
"""
    )

    st.info("🛍 Favorite Category")

    st.write(
        f"""
Most customers prefer
**{favorite_category}**.

Consider expanding products within this category.
"""
    )

with right:

    st.info("💰 Highest Income Group")

    st.write(
        f"""
Customers in the
**{highest_income}**
income band generate the highest revenue.

Target premium marketing campaigns towards them.
"""
    )

    st.info("⭐ Favorite Product")

    st.write(
        f"""
Most frequently purchased product:

**{favourite_product}**
"""
    )

st.divider()

# ---------------------------------------------------------
# AI MARKETING CAMPAIGNS
# ---------------------------------------------------------

st.subheader("🎯 AI Marketing Campaign Generator")

campaigns = []

for segment in sorted(filtered_df["customer_segment"].unique()):

    if segment == "Platinum":

        campaigns.append(
            (
                segment,
                "VIP Loyalty Campaign",
                "Offer early access to premium products."
            )
        )

    elif segment == "Gold":

        campaigns.append(
            (
                segment,
                "Upgrade Campaign",
                "Spend more this month to unlock Platinum benefits."
            )
        )

    elif segment == "Silver":

        campaigns.append(
            (
                segment,
                "Bundle Promotion",
                "Bundle favourite products with accessories."
            )
        )

    else:

        campaigns.append(
            (
                segment,
                "Customer Reactivation",
                "Offer discount coupons and free shipping."
            )
        )

for segment, title, description in campaigns:

    with st.container(border=True):

        st.markdown(f"### {segment}")

        st.success(title)

        st.write(description)

st.divider()

# ---------------------------------------------------------
# AI PROMOTION ENGINE
# ---------------------------------------------------------

st.subheader("🏷 AI Promotion Engine")

promotion_df = (
    filtered_df
    .groupby("customer_segment", as_index=False)
    .agg(
        average_spend=("total_spent", "mean"),
        customers=("customer_key", "nunique")
    )
)

promotion_df["recommended_discount"] = promotion_df[
    "customer_segment"
].map(
    {
        "Platinum": "5% VIP Reward",
        "Gold": "10% Loyalty Discount",
        "Silver": "15% Promotional Discount",
        "Bronze": "20% Reactivation Discount"
    }
)

st.dataframe(
    promotion_df,
    width="stretch",
    hide_index=True
)

st.divider()

# ---------------------------------------------------------
# CUSTOMER RISK ANALYSIS
# ---------------------------------------------------------

st.subheader("⚠ Customer Risk Analysis")

risk_messages = []

for _, row in promotion_df.iterrows():

    segment = row["customer_segment"]

    spend = row["average_spend"]

    if segment == "Bronze":

        risk_messages.append(
            f"🔴 {segment}: Highest churn risk. Recommend aggressive retention campaigns."
        )

    elif segment == "Silver":

        risk_messages.append(
            f"🟡 {segment}: Moderate churn risk. Encourage upgrades through bundles."
        )

    elif segment == "Gold":

        risk_messages.append(
            f"🟢 {segment}: Strong customer base. Encourage Platinum upgrades."
        )

    else:

        risk_messages.append(
            f"⭐ {segment}: Highest value customers. Prioritize retention and VIP benefits."
        )

for message in risk_messages:

    st.warning(message)

st.divider()

st.caption(
    "Enterprise AI Analytics Platform | Customer Intelligence Module"
)
# ---------------------------------------------------------
# CUSTOMER ACTION CENTER
# ---------------------------------------------------------

st.subheader("🚀 Customer Action Center")

left, right = st.columns(2)

# ---------------------------------------------------------
# HIGH VALUE CUSTOMERS
# ---------------------------------------------------------

with left:

    st.markdown("### 🌟 High Value Customers")

    high_value = (
        filtered_df
        .sort_values("total_spent", ascending=False)
        .head(10)
    )

    for _, customer in high_value.iterrows():

        with st.container(border=True):

            st.markdown(f"**{customer['full_name']}**")

            st.write(
                f"Customer Segment: **{customer['customer_segment']}**"
            )

            st.write(
                f"Total Spend: **{format_currency(customer['total_spent'])}**"
            )

            st.success(
                "Recommendation: Offer VIP loyalty rewards and early access to premium products."
            )

# ---------------------------------------------------------
# CUSTOMER UPGRADE OPPORTUNITIES
# ---------------------------------------------------------

with right:

    st.markdown("### 📈 Upgrade Opportunities")

    upgrade_segments = (
        filtered_df[
            filtered_df["customer_segment"].isin(
                ["Bronze", "Silver", "Gold"]
            )
        ]
        .groupby("customer_segment", as_index=False)
        .agg(
            customers=("customer_key", "nunique"),
            average_spend=("total_spent", "mean")
        )
    )

    for _, row in upgrade_segments.iterrows():

        with st.container(border=True):

            st.markdown(
                f"### {row['customer_segment']}"
            )

            st.write(
                f"Customers: **{int(row['customers'])}**"
            )

            st.write(
                f"Average Spend: **{format_currency(row['average_spend'])}**"
            )

            if row["customer_segment"] == "Gold":

                st.info(
                    "Launch Platinum Upgrade Campaign."
                )

            elif row["customer_segment"] == "Silver":

                st.warning(
                    "Promote product bundles and seasonal discounts."
                )

            else:

                st.error(
                    "Focus on customer retention and first repeat purchase."
                )

st.divider()

# ---------------------------------------------------------
# AI NEXT BEST ACTION
# ---------------------------------------------------------

st.subheader("🧠 AI Next Best Actions")

actions = []

# Best category
best_category = (
    filtered_df
    .groupby("favourite_category")["total_spent"]
    .sum()
    .idxmax()
)

# Best product
best_product = (
    filtered_df
    .groupby("favourite_product")["total_spent"]
    .sum()
    .idxmax()
)

# Highest segment
highest_segment = (
    filtered_df
    .groupby("customer_segment")["total_spent"]
    .sum()
    .idxmax()
)

actions.append(
    f"Increase inventory for **{best_product}** because it generates the highest customer spending."
)

actions.append(
    f"Expand marketing campaigns around **{best_category}** products."
)

actions.append(
    f"Reward **{highest_segment}** customers with loyalty incentives."
)

actions.append(
    "Launch personalized email campaigns using customers' favourite products."
)

actions.append(
    "Use Product Recommendation Analytics to bundle complementary products."
)

actions.append(
    "Prioritize customers with high spending but low purchase frequency."
)

for action in actions:

    st.success(action)

st.divider()

# ---------------------------------------------------------
# CUSTOMER INTELLIGENCE SCORE
# ---------------------------------------------------------

st.subheader("🏅 Customer Intelligence Score")

score = 0

if avg_spend > 1000:
    score += 30

if total_customers > 100:
    score += 25

if highest_segment == "Platinum":
    score += 25

if favorite_category is not None:
    score += 20

if score >= 90:

    st.success(
        f"Customer Intelligence Score: **{score}/100**\n\nExcellent customer portfolio."
    )

elif score >= 70:

    st.info(
        f"Customer Intelligence Score: **{score}/100**\n\nHealthy customer portfolio with growth opportunities."
    )

else:

    st.warning(
        f"Customer Intelligence Score: **{score}/100**\n\nCustomer engagement should be improved."
    )

st.divider()

st.caption(
    "Enterprise AI Analytics Platform | Customer Intelligence | AI Decision Support"
)