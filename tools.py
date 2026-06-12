import pandas as pd
from langchain.tools import tool
from databricks_connector import run_query

def query_to_df(query: str) -> pd.DataFrame:
    columns, rows = run_query(query)
    if not rows:
        return pd.DataFrame(columns=columns)
    # Convert Row objects to plain tuples if needed
    plain_rows = [tuple(r) if not isinstance(r, tuple) else r for r in rows]
    return pd.DataFrame(plain_rows, columns=columns)


@tool
def inspect_data(dataset_name: str) -> str:
    """
    Use this tool FIRST to inspect a dataset before querying it.
    Input: dataset name - one of 'customers', 'transactions', 'promotions'
    Returns: column names, data types, shape and sample rows
    """
    dataset_name = dataset_name.strip().strip("'\"").lower()
    valid = ['customers', 'transactions', 'promotions']
    if dataset_name not in valid:
        return f"Dataset '{dataset_name}' not found. Choose from: customers, transactions, promotions"

    df = query_to_df(f"SELECT * FROM retail_agent.{dataset_name} LIMIT 5")
    count_df = query_to_df(f"SELECT COUNT(*) as total FROM retail_agent.{dataset_name}")
    total = count_df['total'][0]

    return f"""
Dataset: {dataset_name}
Total rows: {total}

Columns and Data Types:
{df.dtypes.to_string()}

Sample Data (first 5 rows):
{df.to_string()}
    """


@tool
def query_data(query: str) -> str:
    """
    Use this tool to query and analyze the retail data.
    Input: a plain English description of what you want to analyze.
    Examples:
    - 'total revenue by category'
    - 'count of customers by segment'
    - 'top 5 stores by total sales'
    - 'average discount percentage by channel'
    - 'monthly revenue trend'
    - 'gender analysis'
    - 'at risk customers by region'
    """
    try:
        query = query.strip().strip("'\"")
        query_lower = query.lower()

        if 'gender' in query_lower:
            df = query_to_df("""
                SELECT c.gender,
                    COUNT(DISTINCT c.customer_id) as customer_count,
                    ROUND(SUM(t.total_amount), 2) as total_revenue,
                    ROUND(AVG(t.total_amount), 2) as avg_order_value,
                    COUNT(t.transaction_id) as total_orders
                FROM retail_agent.customers c
                JOIN retail_agent.transactions t ON c.customer_id = t.customer_id
                GROUP BY c.gender
                ORDER BY total_revenue DESC
            """)
            return f"Revenue and orders by gender:\n{df.to_string()}"

        elif 'segment' in query_lower and 'customer' in query_lower:
            df = query_to_df("""
                SELECT segment,
                    COUNT(*) as customer_count,
                    ROUND(AVG(age), 2) as avg_age
                FROM retail_agent.customers
                GROUP BY segment
                ORDER BY customer_count DESC
            """)
            return f"Customer count by segment:\n{df.to_string()}"

        elif 'region' in query_lower and 'customer' in query_lower:
            df = query_to_df("""
                SELECT region,
                    COUNT(*) as customer_count
                FROM retail_agent.customers
                GROUP BY region
                ORDER BY customer_count DESC
            """)
            return f"Customer count by region:\n{df.to_string()}"

        elif ('category' in query_lower or 'categories' in query_lower) and ('revenue' in query_lower or 'sales' in query_lower or 'top' in query_lower or 'performing' in query_lower):
            df = query_to_df("""
                SELECT category,
                    ROUND(SUM(total_amount), 2) as total_revenue,
                    ROUND(AVG(total_amount), 2) as avg_order_value,
                    COUNT(transaction_id) as total_orders
                FROM retail_agent.transactions
                GROUP BY category
                ORDER BY total_revenue DESC
            """)
            return f"Revenue by category:\n{df.to_string()}"

        elif 'store' in query_lower and ('revenue' in query_lower or 'sales' in query_lower or 'top' in query_lower):
            df = query_to_df("""
                SELECT store,
                    ROUND(SUM(total_amount), 2) as total_revenue,
                    COUNT(transaction_id) as total_orders,
                    ROUND(AVG(total_amount), 2) as avg_order_value
                FROM retail_agent.transactions
                GROUP BY store
                ORDER BY total_revenue DESC
            """)
            return f"Revenue by store:\n{df.to_string()}"

        elif 'promotion' in query_lower or 'promo' in query_lower or 'campaign' in query_lower or 'roi' in query_lower:
            if any(word in query_lower for word in ['individual', 'name', 'rank', 'top', 'best', 'each', 'specific', 'list']):
                df = query_to_df("""
                    SELECT promo_name, promo_type, channel,
                        ROUND(revenue_generated, 2) as revenue,
                        ROUND(cost, 2) as cost,
                        ROUND((revenue_generated - cost) / cost * 100, 2) as roi_pct,
                        redemptions
                    FROM retail_agent.promotions
                    ORDER BY roi_pct DESC
                    LIMIT 10
                """)
                return f"Top 10 promotions by ROI:\n{df.to_string()}"
            else:
                df = query_to_df("""
                    SELECT channel,
                        ROUND(SUM(revenue_generated), 2) as total_revenue,
                        ROUND(SUM(cost), 2) as total_cost,
                        ROUND(AVG((revenue_generated - cost) / cost * 100), 2) as avg_roi,
                        SUM(redemptions) as total_redemptions
                    FROM retail_agent.promotions
                    GROUP BY channel
                    ORDER BY avg_roi DESC
                """)
                return f"Promotion performance by channel:\n{df.to_string()}"

        elif 'discount' in query_lower:
            df = query_to_df("""
                SELECT discount_applied,
                    COUNT(*) as transaction_count,
                    ROUND(AVG(total_amount), 2) as avg_order_value,
                    ROUND(SUM(total_amount), 2) as total_revenue
                FROM retail_agent.transactions
                GROUP BY discount_applied
            """)
            return f"Discount impact analysis:\n{df.to_string()}"

        elif 'monthly' in query_lower or 'trend' in query_lower:
            df = query_to_df("""
                SELECT DATE_FORMAT(date, 'yyyy-MM') as month,
                    ROUND(SUM(total_amount), 2) as total_revenue,
                    COUNT(transaction_id) as total_orders
                FROM retail_agent.transactions
                GROUP BY DATE_FORMAT(date, 'yyyy-MM')
                ORDER BY month DESC
                LIMIT 6
            """)
            return f"Monthly revenue trend (last 6 months):\n{df.to_string()}"

        elif 'at risk' in query_lower or 'churn' in query_lower:
            df = query_to_df("""
                SELECT region,
                    COUNT(*) as at_risk_count
                FROM retail_agent.customers
                WHERE segment = 'At Risk'
                GROUP BY region
                ORDER BY at_risk_count DESC
            """)
            total = query_to_df("SELECT COUNT(*) as total FROM retail_agent.customers WHERE segment = 'At Risk'")
            return f"At Risk customers by region:\n{df.to_string()}\nTotal at risk: {total['total'][0]}"

        else:
            return """I can analyze:
- Customer segments and regions
- Revenue by category or store
- Promotion and campaign ROI
- Discount impact
- Monthly revenue trends
- At risk / churning customers
- Gender analysis
Please rephrase your query using these topics."""

    except Exception as e:
        return f"Query error: {str(e)}"


@tool
def generate_insight(data_summary: str) -> str:
    """
    Use this tool LAST after querying data.
    Input: a summary of the data findings you want to turn into a business insight.
    Returns: a clear, actionable business insight with recommendations.
    """
    return f"""
Based on the analysis:

{data_summary}

Please provide:
1. A 2-3 sentence executive summary of what this data shows
2. The top 3 key findings
3. Two concrete business recommendations
"""