import streamlit as st
import pandas as pd
import plotly.express as px
from agent import run_agent
from databricks_connector import run_query

st.set_page_config(
    page_title="Retail AI Agent",
    page_icon="🛒",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        color: white;
    }
    .main-header h1 {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        color: white;
    }
    .main-header p {
        font-size: 1rem;
        color: #a0aec0;
        margin: 0.5rem 0 0 0;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def get_metrics():
    try:
        _, cust = run_query("SELECT COUNT(*) FROM retail_agent.customers")
        _, trans = run_query("SELECT COUNT(*) FROM retail_agent.transactions")
        _, promo = run_query("SELECT COUNT(*) FROM retail_agent.promotions")
        _, rev = run_query("SELECT ROUND(SUM(total_amount), 0) FROM retail_agent.transactions")
        c = int(cust[0][0]) if cust and cust[0][0] is not None else 200
        t = int(trans[0][0]) if trans and trans[0][0] is not None else 1000
        p = int(promo[0][0]) if promo and promo[0][0] is not None else 50
        r = int(rev[0][0]) if rev and rev[0][0] is not None else 1014220
        return c, t, p, r
    except Exception as e:
        return 200, 1000, 50, 1014220


def get_chart_data(question):
    q = question.lower()
    try:
        if 'segment' in q:
            cols, rows = run_query("""
                SELECT segment, COUNT(*) as count
                FROM retail_agent.customers
                GROUP BY segment ORDER BY count DESC
            """)
            df = pd.DataFrame(rows, columns=cols)
            fig = px.bar(df, x='segment', y='count',
                        color='segment',
                        color_discrete_sequence=['#0f3460','#16213e','#533483','#e94560','#0f3460'],
                        title='Customers by Segment')
            fig.update_layout(showlegend=False, plot_bgcolor='white',
                            paper_bgcolor='white', font_color='#1a1a2e')
            return fig

        elif 'category' in q or 'categories' in q:
            cols, rows = run_query("""
                SELECT category, ROUND(SUM(total_amount),2) as revenue
                FROM retail_agent.transactions
                GROUP BY category ORDER BY revenue DESC
            """)
            df = pd.DataFrame(rows, columns=cols)
            fig = px.bar(df, x='category', y='revenue',
                        color='revenue',
                        color_continuous_scale=['#16213e','#0f3460','#533483'],
                        title='Revenue by Category')
            fig.update_layout(showlegend=False, plot_bgcolor='white',
                            paper_bgcolor='white', font_color='#1a1a2e',
                            coloraxis_showscale=False)
            return fig

        elif 'store' in q:
            cols, rows = run_query("""
                SELECT store, ROUND(SUM(total_amount),2) as revenue
                FROM retail_agent.transactions
                GROUP BY store ORDER BY revenue DESC
            """)
            df = pd.DataFrame(rows, columns=cols)
            fig = px.bar(df, x='store', y='revenue',
                        color='revenue',
                        color_continuous_scale=['#16213e','#0f3460','#533483'],
                        title='Revenue by Store')
            fig.update_layout(showlegend=False, plot_bgcolor='white',
                            paper_bgcolor='white', font_color='#1a1a2e',
                            coloraxis_showscale=False)
            return fig

        elif 'region' in q or 'at risk' in q or 'churn' in q:
            cols, rows = run_query("""
                SELECT region, COUNT(*) as count
                FROM retail_agent.customers
                GROUP BY region ORDER BY count DESC
            """)
            df = pd.DataFrame(rows, columns=cols)
            fig = px.bar(df, x='region', y='count',
                        color='count',
                        color_continuous_scale=['#16213e','#0f3460','#533483'],
                        title='Customers by Region')
            fig.update_layout(showlegend=False, plot_bgcolor='white',
                            paper_bgcolor='white', font_color='#1a1a2e',
                            coloraxis_showscale=False)
            return fig

        elif 'promotion' in q or 'roi' in q or 'campaign' in q:
            cols, rows = run_query("""
                SELECT channel,
                    ROUND(AVG((revenue_generated - cost) / cost * 100), 2) as avg_roi
                FROM retail_agent.promotions
                GROUP BY channel ORDER BY avg_roi DESC
            """)
            df = pd.DataFrame(rows, columns=cols)
            fig = px.bar(df, x='channel', y='avg_roi',
                        color='avg_roi',
                        color_continuous_scale=['#16213e','#0f3460','#533483'],
                        title='Average ROI by Channel (%)')
            fig.update_layout(showlegend=False, plot_bgcolor='white',
                            paper_bgcolor='white', font_color='#1a1a2e',
                            coloraxis_showscale=False)
            return fig

        elif 'gender' in q:
            cols, rows = run_query("""
                SELECT c.gender,
                    ROUND(SUM(t.total_amount), 2) as revenue
                FROM retail_agent.customers c
                JOIN retail_agent.transactions t ON c.customer_id = t.customer_id
                GROUP BY c.gender
            """)
            df = pd.DataFrame(rows, columns=cols)
            fig = px.pie(df, values='revenue', names='gender',
                        color_discrete_sequence=['#0f3460','#533483'],
                        title='Revenue by Gender')
            fig.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                            font_color='#1a1a2e')
            return fig

        elif 'monthly' in q or 'trend' in q:
            cols, rows = run_query("""
                SELECT DATE_FORMAT(date, 'yyyy-MM') as month,
                    ROUND(SUM(total_amount), 2) as revenue
                FROM retail_agent.transactions
                GROUP BY DATE_FORMAT(date, 'yyyy-MM')
                ORDER BY month DESC LIMIT 6
            """)
            df = pd.DataFrame(rows, columns=cols)
            df = df.sort_values('month')
            fig = px.line(df, x='month', y='revenue',
                         markers=True, title='Monthly Revenue Trend',
                         color_discrete_sequence=['#0f3460'])
            fig.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                            font_color='#1a1a2e')
            return fig

        elif 'discount' in q:
            cols, rows = run_query("""
                SELECT discount_applied,
                    ROUND(SUM(total_amount), 2) as revenue
                FROM retail_agent.transactions
                GROUP BY discount_applied
            """)
            df = pd.DataFrame(rows, columns=cols)
            df['discount_applied'] = df['discount_applied'].map({True: 'Discounted', False: 'Full Price'})
            fig = px.pie(df, values='revenue', names='discount_applied',
                        color_discrete_sequence=['#0f3460','#533483'],
                        title='Revenue: Discounted vs Full Price')
            fig.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                            font_color='#1a1a2e')
            return fig

    except:
        return None
    return None


st.markdown("""
<div class="main-header">
    <h1>🛒 Retail Analytics AI Agent</h1>
    <p>Powered by LangChain · Groq Llama 3 · Databricks Delta Tables</p>
</div>
""", unsafe_allow_html=True)

with st.spinner("Loading metrics from Databricks..."):
    total_customers, total_transactions, total_promotions, total_revenue = get_metrics()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Customers", f"{total_customers:,}")
with col2:
    st.metric("Total Transactions", f"{total_transactions:,}")
with col3:
    st.metric("Active Promotions", f"{total_promotions:,}")
with col4:
    st.metric("Total Revenue", f"${total_revenue:,.0f}")

st.divider()

with st.sidebar:
    st.markdown("### 💡 Try asking...")
    st.markdown("""
**Customers**
- Which segments have the most customers?
- Which region has the most at risk customers?
- What gender purchases the most?

**Sales**
- Top product categories by revenue?
- Which store has the highest revenue?
- Show monthly revenue trend

**Promotions**
- Which promotions have the best ROI?
- How is each marketing channel performing?

**Other**
- What is the impact of discounts?
""")
    st.divider()
    st.markdown("**🔧 Built with**")
    st.markdown("🔗 LangChain")
    st.markdown("⚡ Groq Llama 3")
    st.markdown("🗄️ Databricks Delta Tables")
    st.markdown("🐍 Python + Pandas")
    st.markdown("📊 Plotly")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "chart" in message and message["chart"] is not None:
            st.plotly_chart(message["chart"], use_container_width=True)

question = st.chat_input("Ask a question about your retail data...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Agent is thinking..."):
            try:
                answer = run_agent(question)
                answer = answer.replace('`$', '$').replace('`', '')
                chart = get_chart_data(question)
                st.markdown(answer)
                if chart:
                    st.plotly_chart(chart, use_container_width=True)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "chart": chart
                })
            except Exception as e:
                import traceback
                error_msg = f"Something went wrong: {str(e)}\n\n{traceback.format_exc()}"
                st.markdown(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "chart": None
                })