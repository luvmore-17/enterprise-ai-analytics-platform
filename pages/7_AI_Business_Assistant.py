import streamlit as st
import pandas as pd
import plotly.express as px
from config.database import engine

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================
st.set_page_config(
    page_title="AI Business Assistant",
    page_icon="🧠",
    layout="wide"
)

# ==========================================================
# SIDEBAR
# ==========================================================
with st.sidebar:
    st.title("🧠 Luvmore AI")
    st.success("System Online")
    st.markdown("---")

    # Quick Enterprise Metric Pulled Live!
    st.markdown("### 📊 Quick Live Snapshot")
    try:
        quick_stats = pd.read_sql("""
            SELECT 
                (SELECT SUM(total_revenue) FROM analytics.vw_sales_summary) as revenue,
                (SELECT COUNT(DISTINCT product_name) FROM analytics.vw_product_performance) as products
        """, engine)
        
        rev = quick_stats.loc[0, 'revenue']
        prods = quick_stats.loc[0, 'products']
        
        st.metric(label="Total Revenue Live", value=f"${rev:,.0f}" if rev else "$0")
        st.metric(label="Monitored Products", value=int(prods) if prods else 0)
    except Exception as e:
        st.caption("Unable to fetch real-time sidebar metrics.")

    st.markdown("---")
    st.markdown("### Capabilities")
    st.write("📈 Sales Intelligence")
    st.write("🛍 Product Intelligence")
    st.write("👥 Customer Intelligence")
    st.write("🌍 Territory Intelligence")
    st.write("🔄 Returns Intelligence")
    st.write("📊 Executive Reporting")
    st.write("🤖 AI Decision Support")

    st.markdown("---")
    st.info("Enterprise Analytics Platform\nVersion 1.2")

# ==========================================================
# MAIN HEADER
# ==========================================================
st.title("🧠 Luvmore AI Copilot")
st.caption(
    "Your Enterprise Business Intelligence Assistant powered by PostgreSQL, Analytics and AI."
)
st.divider()

st.info("""
## 👋 Welcome to Luvmore AI Copilot

I'm your enterprise business intelligence assistant. Simply ask a question in natural language and I'll analyze your business data.
""")

# ==========================================================
# INITIALIZE CHAT HISTORY
# ==========================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================================
# EXAMPLE QUESTIONS (EXPANDED TO 20 CATEGORIZED BI QUESTIONS)
# ==========================================================
with st.expander("💡 Example Questions (20 Curated Prompts)", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📈 Sales Performance**
        * What is our total revenue across all operating periods?
        * What is our historical monthly sales trend?
        * How much total profit has our pipeline generated?
        * Show me our total order volume performance.
        
        **🛍 Product & Revenue Insights**
        * Which products generate the highest revenue?
        * Show me the top 5 most profitable products.
        * Which products should I stock more of based on margin?
        * Show me product recommendations for our top items.
        """)
        
    with col2:
        st.markdown("""
        **👥 Customer & Segment Intelligence**
        * Show me our top customer segments by spend.
        * Which customer segment spends the most?
        * How does customer segmentation impact overall revenue?
        * Where should we focus our next loyalty campaigns?
        
        **🌍 Regional & Territory Performance**
        * Which country has the highest profit margin?
        * Show me the best performing territory.
        * What is our market performance and revenue distribution by country?
        * Which region needs immediate sales intervention?
        
        **🔄 Returns & Risk Management**
        * Which products have the highest return rate?
        * Show the top 5 high-risk products due to returns.
        * What are the business recommendations for high-return items?
        * How can we reduce our financial impact from product returns?
        """)

# ==========================================================
# DISPLAY CHAT HISTORY
# ==========================================================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "chart" in message:
            st.plotly_chart(message["chart"], use_container_width=True)
        if "df" in message:
            st.dataframe(message["df"], use_container_width=True)

# ==========================================================
# CHAT INPUT
# ==========================================================
prompt = st.chat_input(
    "Ask Luvmore AI Copilot anything about your business..."
)

# ==========================================================
# BUSINESS INTENT DETECTION
# ==========================================================
def detect_intent(question):
    question = question.lower()
    if "product" in question or "stock" in question or "recommendation" in question:
        return "products"
    elif "customer" in question or "segment" in question or "loyalty" in question:
        return "customers"
    elif "territory" in question or "country" in question or "region" in question or "market" in question:
        return "territories"
    elif "return" in question or "risk" in question:
        return "returns"
    elif "sale" in question or "revenue" in question or "profit" in question or "trend" in question or "order" in question:
        return "sales"
    else:
        return "general"

# ==========================================================
# RESPOND & GENERATE PLOTS ON THE FLY
# ==========================================================
if prompt:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    intent = detect_intent(prompt)
    
    response = ""
    fig = None
    df_to_show = None

    # Process intents & craft specific SQL + dynamic plots
    if intent == "sales":
        query = """
        SELECT
            year,
            month_name,
            total_revenue,
            total_profit,
            total_orders
        FROM analytics.vw_sales_summary
        ORDER BY year, month;
        """
        df = pd.read_sql(query, engine)
        df_to_show = df
        
        # Calculate summary numbers
        total_revenue = df["total_revenue"].sum()
        total_profit = df["total_profit"].sum()
        total_orders = df["total_orders"].sum()

        response = f"""
### 📈 Sales Intelligence

Based on your operational pipeline, here is the cumulative summary:

* **Total Revenue**: ${total_revenue:,.2f}
* **Total Profit**: ${total_profit:,.2f}
* **Total Orders**: {total_orders:,.0f}

*I've generated a performance line chart below mapping your monthly revenue trends.*
"""
        # Line chart of revenue performance
        df["Period"] = df["month_name"].str[:3] + " " + df["year"].astype(str)
        fig = px.line(df, x="Period", y="total_revenue", markers=True, title="Revenue Growth Timeline")
        fig.update_layout(template="plotly_white")

    elif intent == "products":
        query = """
        SELECT
            product_name,
            revenue,
            profit,
            calculated_profit_margin_pct
        FROM analytics.vw_product_performance
        ORDER BY revenue DESC
        LIMIT 5;
        """
        df = pd.read_sql(query, engine)
        df_to_show = df

        response = f"""
### 🛍 Top Product Performance
The highest-performing product is **{df.iloc[0]['product_name']}**, bringing in **${df.iloc[0]['revenue']:,.2f}** at a profit margin of **{df.iloc[0]['calculated_profit_margin_pct']:.2f}%**.

*See the comparative chart below highlighting the top 5 revenue contributors.*
"""
        # Bar chart comparing top products
        fig = px.bar(df, x="product_name", y="revenue", color="revenue",
                     title="Top 5 Products by Revenue", color_continuous_scale="Viridis")
        fig.update_layout(template="plotly_white")

    elif intent == "customers":
        query = """
        SELECT
            customer_segment,
            SUM(total_spent) AS total_revenue
        FROM analytics.vw_customer_preferences
        GROUP BY customer_segment
        ORDER BY total_revenue DESC;
        """
        df = pd.read_sql(query, engine)
        df_to_show = df

        response = f"""
### 👥 Customer Insights

The top-performing audience group is the **{df.iloc[0]['customer_segment']}** segment, driving **${df.iloc[0]['total_revenue']:,.2f}** in acquisitions.

**Recommendation**: Tailor loyalty programs, custom promo campaigns, and active outreach initiatives to double down on this bracket.
"""
        # Donut Chart for Customer segments
        fig = px.pie(df, values='total_revenue', names='customer_segment', hole=0.4,
                     title='Revenue Share by Customer Segment')
        fig.update_layout(template="plotly_white")

    elif intent == "territories":
        query = """
        SELECT
            country,
            SUM(total_revenue) AS total_revenue,
            AVG(profit_margin_pct) AS margin
        FROM analytics.vw_territory_performance
        GROUP BY country
        ORDER BY total_revenue DESC
        LIMIT 5;
        """
        df = pd.read_sql(query, engine)
        df_to_show = df

        response = f"""
### 🌍 Regional/Territory Intelligence

Our strongest geographic market footprint is in **{df.iloc[0]['country']}** with a high-margin threshold of **{df.iloc[0]['margin']:.2f}%**.
"""
        # Funnel/Bar chart
        fig = px.bar(df, x="country", y="total_revenue", hover_data=["margin"],
                     title="Revenue Distribution by Country", color="total_revenue")
        fig.update_layout(template="plotly_white")

    elif intent == "returns":
        query = """
        SELECT
            product_name,
            return_rate_pct,
            business_recommendation
        FROM analytics.vw_returns_analysis
        ORDER BY return_rate_pct DESC
        LIMIT 5;
        """
        df = pd.read_sql(query, engine)
        df_to_show = df

        response = f"""
### 🔄 Returns Intelligence

The highest return-rate exposure lies in **{df.iloc[0]['product_name']}** with a return rate of **{df.iloc[0]['return_rate_pct']:.2f}%**.

**Strategic AI Action Point**: {df.iloc[0]['business_recommendation']}
"""
        # Horizontal Bar Chart for Returns
        fig = px.bar(df, y="product_name", x="return_rate_pct", orientation="h",
                     color="return_rate_pct", color_continuous_scale="Reds", title="Top Products with High Returns")
        fig.update_layout(template="plotly_white")

    else:
        response = """
I couldn't identify the specific business dataset you want to look at. 

Could you try rephrasing your request about:
* **Sales** (e.g., *"Show me recent sales trends"*)
* **Products** (e.g., *"Which products sell the most?"*)
* **Customers** (e.g., *"Show our top client segments"*)
* **Territories** (e.g., *"Which countries bring in the highest profits?"*)
* **Returns** (e.g., *"Are there products with high return rates?"*)
"""

    # Print and render responses in Chat interface
    with st.chat_message("assistant"):
        st.markdown(response)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        if df_to_show is not None:
            with st.expander("🔍 View Raw Query Results", expanded=False):
                st.dataframe(df_to_show, use_container_width=True)

    # Save details to state context so they stay visible if user scrolls or re-interacts
    history_item = {"role": "assistant", "content": response}
    if fig:
        history_item["chart"] = fig
    if df_to_show is not None:
        history_item["df"] = df_to_show
        
    st.session_state.messages.append(history_item)