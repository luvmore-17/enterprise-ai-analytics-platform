import streamlit as st
import pandas as pd
import plotly.express as px
from config.database import engine
from datetime import datetime
from zoneinfo import ZoneInfo  # Built-in: No installation needed!

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Enterprise AI Analytics Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# DATA FETCHING & PROCESSING
# ---------------------------------------------------------

# 1. Executive Summary KPIs
query_exec = """
SELECT *
FROM analytics.vw_executive_dashboard;
"""
df_exec = pd.read_sql(query_exec, engine)
row = df_exec.iloc[0]

# 2. Monthly Sales Trend Data
sales_query = """
SELECT
    year,
    month,
    month_name,
    total_revenue,
    total_profit,
    total_orders
FROM analytics.vw_sales_summary
ORDER BY year, month;
"""
sales_df = pd.read_sql(sales_query, engine)
sales_df["period"] = sales_df["month_name"].str[:3] + " " + sales_df["year"].astype(str)

# 3. Product Category Performance Data
category_query = """
SELECT
    category_name,
    SUM(revenue) AS revenue
FROM analytics.vw_product_performance
GROUP BY category_name
ORDER BY revenue DESC;
"""
category_df = pd.read_sql(category_query, engine)

# ---------------------------------------------------------
# CHART GENERATION
# ---------------------------------------------------------

# Chart 1: Revenue Trend Line Chart
fig_trend = px.line(
    sales_df,
    x="period",
    y="total_revenue",
    markers=True,
    title="Monthly Revenue Trend",
)
fig_trend.update_layout(
    hovermode="x unified",
    xaxis_title="Month",
    yaxis_title="Revenue ($)",
    template="plotly_white",
)

# Chart 2: Custom Flat Pie Chart
category_colors = {
    category_df.iloc[0]["category_name"] if len(category_df) > 0 else "Category 1": "#26B494",  # Teal Green
    category_df.iloc[1]["category_name"] if len(category_df) > 1 else "Category 2": "#80C6FF",  # Sky Blue
    category_df.iloc[2]["category_name"] if len(category_df) > 2 else "Category 3": "#FF2B2B",  # Vibrant Red
    category_df.iloc[3]["category_name"] if len(category_df) > 3 else "Category 4": "#0066CC",  # Deep Blue
    category_df.iloc[4]["category_name"] if len(category_df) > 4 else "Category 5": "#FFA6A6",  # Soft Pink
}

category_fig = px.pie(
    category_df,
    names="category_name",
    values="revenue",
    color="category_name",
    color_discrete_map=category_colors,
    title="Revenue by Product Category"
)

category_fig.update_traces(
    textinfo="none", 
    hovertemplate="<b>%{label}</b><br>Revenue: $%{value:,.2f}<br>%{percent}<extra></extra>"
)

category_fig.update_layout(
    template="plotly_white",
    title={
        'text': "<b>Revenue by Product Category</b>",
        'y': 0.95,
        'x': 0.05,
        'xanchor': 'left',
        'yanchor': 'top',
        'font': dict(size=16, color="#1E293B")
    },
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.15,
        xanchor="left",
        x=0.01,
        title=dict(text="category", font=dict(color="#64748B", size=12)),
        font=dict(color="#64748B", size=12)
    ),
    margin=dict(t=80, b=80, l=40, r=40)
)

# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------
def format_currency(value):
    if value >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"${value/1000:.2f}K"
    return f"${value:.2f}"

# ---------------------------------------------------------
# SIDEBAR NAVIGATION, DATE & TIME
# ---------------------------------------------------------
with st.sidebar:

    # -------------------------------------------------
    # DATE & TIME
    # -------------------------------------------------

    utc_now = datetime.now(ZoneInfo("UTC"))
    local_eat = utc_now.astimezone(ZoneInfo("Africa/Nairobi"))

    current_date_str = local_eat.strftime("%A, %B %d, %Y")

    eat_time = local_eat.strftime("%H:%M:%S")
    gmt_time = utc_now.astimezone(
        ZoneInfo("GMT")
    ).strftime("%H:%M:%S")

    est_time = utc_now.astimezone(
        ZoneInfo("America/New_York")
    ).strftime("%I:%M %p")

    st.markdown("### 📅 Today's Date")
    st.info(current_date_str)

    st.markdown("### 🕒 System Clocks")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.caption("🇰🇪 EAT")
        st.markdown(f"**{eat_time}**")

    with c2:
        st.caption("🇬🇧 GMT")
        st.markdown(f"**{gmt_time}**")

    with c3:
        st.caption("🇺🇸 EST")
        st.markdown(f"**{est_time}**")

    st.divider()

    # -------------------------------------------------
    # CURRENT PAGE
    # -------------------------------------------------

    st.markdown("### 📊 Current Module")

    st.success("🏠 Executive Dashboard")

    st.divider()

    # -------------------------------------------------
    # FOOTER
    # -------------------------------------------------

    st.caption("Enterprise AI Platform")
    st.caption("Powered by PostgreSQL")
    st.caption("Version 1.0")
    st.caption("© Joskevin Luvmore")
# ---------------------------------------------------------
# DASHBOARD MAIN HEADER
# ---------------------------------------------------------
st.title("🚀 Enterprise AI Analytics Platform")
st.caption(
    "AI-Powered Business Intelligence and Decision Support System Made by JOSKEVIN LUVMORE"
)
st.divider()

# ---------------------------------------------------------
# KPI ROW 1
# ---------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("💵 Revenue", format_currency(row["total_revenue"]))
c2.metric("💰 Profit", format_currency(row["total_profit"]))
c3.metric("📦 Orders", f"{int(row['total_orders']):,}")
c4.metric("👥 Customers", f"{int(row['total_customers']):,}")

# ---------------------------------------------------------
# KPI ROW 2
# ---------------------------------------------------------
c5, c6, c7, c8 = st.columns(4)
c5.metric("🛍 Products", f"{int(row['total_products'])}")
c6.metric("📈 Profit Margin", f"{row['profit_margin_pct']:.2f}%")
c7.metric("🧾 Avg Order", format_currency(row["average_order_value"]))
c8.metric("🔄 Returns", f"{int(row['total_returns']):,}")

st.divider()

# ---------------------------------------------------------
# TABS INTERFACE
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs(
    [
        "📊 Overview",
        "🤖 AI Insights",
        "⚠️ Business Alerts"
    ]
)

# ---------------------------------------------------------
# OVERVIEW TAB
# ---------------------------------------------------------
with tab1:
    st.subheader("Executive Summary")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info(
            """
            Welcome to the Enterprise AI Analytics Platform.
            This platform integrates:
            * Enterprise Data Warehouse
            * Business Intelligence
            * AI Decision Support
            * Product Recommendations
            * Customer Intelligence
            * Executive Reporting
            """
        )
    
    with col2:
        st.success("Top Product")
        st.write(row["top_product"])
        st.metric("Revenue", format_currency(row["top_product_revenue"]))
        
        st.success("Top Country")
        st.write(row["top_country"])

    st.divider()
    
    # Render Data Charts Side-by-Side (Line Graph & Custom Flat Pie Chart)
    left_chart, right_chart = st.columns(2)
    with left_chart:
        st.plotly_chart(fig_trend, use_container_width=True)
    with right_chart:
        st.plotly_chart(category_fig, use_container_width=True)

# ---------------------------------------------------------
# AI TAB
# ---------------------------------------------------------
# ---------------------------------------------------------
# AI INSIGHTS TAB (AUTOMATED)
# ---------------------------------------------------------

with tab2:

    st.subheader("🧠 AI Executive Intelligence")

    # -----------------------------
    # Calculate Business Metrics
    # -----------------------------

    profit_margin = row["profit_margin_pct"]
    revenue = row["total_revenue"]
    orders = row["total_orders"]
    customers = row["total_customers"]
    returns = row["total_returns"]

    return_rate = (returns / orders) * 100 if orders > 0 else 0

    # -----------------------------
    # Executive Summary
    # -----------------------------

    summary = []

    summary.append(
        f"Revenue currently stands at **{format_currency(revenue)}** "
        f"generated from **{orders:,}** completed orders."
    )

    summary.append(
        f"The company serves **{customers:,}** customers."
    )

    summary.append(
        f"The current profit margin is **{profit_margin:.2f}%**."
    )

    summary.append(
        f"The highest revenue product is **{row['top_product']}**, "
        f"contributing **{format_currency(row['top_product_revenue'])}**."
    )

    summary.append(
        f"The strongest performing territory is **{row['top_country']}**."
    )

    st.markdown("### 📊 Executive Summary")

    for sentence in summary:
        st.write("•", sentence)

    st.divider()

    # -----------------------------
    # AI Opportunities
    # -----------------------------

    left, right = st.columns(2)

    with left:

        st.success("🏆 AI Opportunities")

        opportunities = []

        if profit_margin >= 40:
            opportunities.append(
                f"Profit margin of **{profit_margin:.2f}%** indicates strong profitability."
            )

        if revenue >= 20000000:
            opportunities.append(
                f"Revenue has exceeded **{format_currency(20000000)}**, demonstrating strong business growth."
            )

        if orders >= 20000:
            opportunities.append(
                f"Customer demand remains high with **{orders:,}** completed orders."
            )

        opportunities.append(
            f"Increase inventory for **{row['top_product']}** due to strong sales performance."
        )

        opportunities.append(
            f"Expand operations in **{row['top_country']}**, the highest-performing territory."
        )

        for item in opportunities:
            st.write("✅", item)

    # -----------------------------
    # AI Risks
    # -----------------------------

    with right:

        st.warning("⚠ AI Risk Assessment")

        risks = []

        if return_rate >= 10:

            risks.append(
                f"Return rate is **{return_rate:.2f}%**, exceeding the recommended threshold."
            )

        else:

            risks.append(
                f"Return rate remains healthy at **{return_rate:.2f}%**."
            )

        if profit_margin < 30:

            risks.append(
                "Profit margin has dropped below the preferred business target."
            )

        if revenue < 10000000:

            risks.append(
                "Revenue growth requires further monitoring."
            )

        if len(risks) == 0:

            risks.append("No significant business risks detected.")

        for item in risks:
            st.write("⚠", item)

    st.divider()

    # -----------------------------
    # Automated AI Recommendations
    # -----------------------------

    st.subheader("💡 AI Recommendations")

    recommendations = []

    recommendations.append(
        f"Prioritize marketing for **{row['top_product']}**."
    )

    recommendations.append(
        f"Increase product availability within **{row['top_country']}**."
    )

    if return_rate >= 10:

        recommendations.append(
            "Investigate products contributing to higher return rates."
        )

    if profit_margin < 35:

        recommendations.append(
            "Review pricing strategy to improve profitability."
        )

    if revenue >= 20000000:

        recommendations.append(
            "Consider expanding into similar high-performing markets."
        )

    recommendations.append(
        "Continue monitoring customer purchasing behaviour using product affinity analysis."
    )

    for i, recommendation in enumerate(recommendations, start=1):
        st.info(f"{i}. {recommendation}")
# ---------------------------------------------------------
# ALERT TAB
# ---------------------------------------------------------
with tab3:

    st.subheader("⚠ Business Alerts & Monitoring")

    alert1, alert2 = st.columns(2)

    # -----------------------------
    # Revenue Alert
    # -----------------------------
    with alert1:

        if row["profit_margin_pct"] >= 40:

            st.success(
                f"""
🟢 Profit Margin Healthy

Current Profit Margin: **{row['profit_margin_pct']:.2f}%**

Business profitability remains above the target threshold.
                """
            )

        else:

            st.error(
                f"""
🔴 Profit Margin Warning

Current Profit Margin: **{row['profit_margin_pct']:.2f}%**

Review pricing strategy and operational costs.
                """
            )

    # -----------------------------
    # Returns Alert
    # -----------------------------
    with alert2:

        return_rate = (
            row["total_returns"] /
            row["total_orders"]
        ) * 100

        if return_rate < 10:

            st.success(
                f"""
🟢 Returns Healthy

Return Rate: **{return_rate:.2f}%**

Product quality appears stable.
                """
            )

        else:

            st.warning(
                f"""
🟠 High Returns Detected

Return Rate: **{return_rate:.2f}%**

Investigate returned products.
                """
            )

    st.divider()

    st.subheader("📋 Executive Business Alerts")

    alerts = []

    if row["profit_margin_pct"] >= 40:
        alerts.append("✅ Profit margins remain strong.")

    if return_rate < 10:
        alerts.append("✅ Product returns remain within acceptable levels.")

    if row["total_orders"] > 20000:
        alerts.append(
    f"📦 Strong customer demand for {row['top_product']} "
    f"with revenue of {format_currency(row['top_product_revenue'])}."
)

    if row["total_customers"] > 15000:
        alerts.append("👥 Customer acquisition remains healthy.")

    if row["total_revenue"] > 20000000:
        alerts.append("💰 Revenue has exceeded $20 Million.")

    for alert in alerts:
        st.info(alert)

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.divider()
st.divider()

st.caption("Enterprise AI Analytics")

st.caption("Powered by PostgreSQL")

st.caption("Version 1.0.0")

st.caption("Developed by")

st.markdown("**Joskevin Luvmore**")