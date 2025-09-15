import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime
from app_direct_db_neon import generate_sql_query, get_db_connection

# Streamlit page configuration
st.set_page_config(page_title="Myntra Inventory Analysis", layout="wide")

# Custom CSS for pastel theme with vibrant peach accents
st.markdown("""
    <style>
    body {
        background-color: #FFF7F0; /* Pale cream background */
        color: #2F4F4F; /* Slate text */
    }
    .stButton>button {
        background-color: #FF6666; /* Vibrant peach */
        color: #2F4F4F;
        border-radius: 10px;
        border: none;
        padding: 12px 24px;
        font-weight: bold;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #FF4D4D; /* Darker peach */
        color: #FFF7F0;
    }
    .stTextInput>div>input {
        border-radius: 5px;
        border: 2px solid #FF6666; /* Vibrant peach border */
        font-size: 18px;
        padding: 10px;
        color: #2F4F4F;
        background-color: #FFFFFF;
        text-align: center;
    }
    .stSelectbox>div {
        border-radius: 5px;
        border: 1px solid #FF6666;
        font-size: 16px;
    }
    .st-container {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1, h2, h3 {
        color: #2F4F4F;
        font-weight: bold;
    }
    .stMarkdown {
        color: #2F4F4F;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("Myntra Inventory Analysis Chatbot")

# Initialize session state
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'alerts_run' not in st.session_state:
    st.session_state.alerts_run = False
if 'restock_run' not in st.session_state:
    st.session_state.restock_run = False
if 'time_filter' not in st.session_state:
    st.session_state.time_filter = "Last 7 Days"

# Database connection using SQLAlchemy engine
@st.cache_resource
def init_connection():
    return get_db_connection()

# Cache query results
@st.cache_data(ttl=300)  # Cache for 5 minutes
def run_query(query, _engine, _cache_key, user_query):
    try:
        df = pd.read_sql(query, _engine)
        # Convert revenueinrs to crores
        if 'revenueinrs' in df.columns:
            df['revenue_crores'] = df['revenueinrs'] / 1_00_00_000
            df = df.drop(columns=['revenueinrs'])  # Remove original column
        return df
    except Exception as e:
        st.error(f"Query Error: {str(e)}")
        return pd.DataFrame()

# Sidebar for natural language query
with st.sidebar:
    st.header("Ask About Inventory")
    user_query = st.text_input("Enter your query (e.g., 'stock of jeans from sangria')", key="user_query",
                               placeholder="Type your inventory question here...")
    if st.button("Run Query"):
        if user_query:
            engine = init_connection()
            sql_query = generate_sql_query(user_query)
            # Maintain only 5 queries in history
            st.session_state.query_history.append((user_query, sql_query))
            if len(st.session_state.query_history) > 5:
                st.session_state.query_history = st.session_state.query_history[-5:]
            df = run_query(sql_query, engine, _cache_key=user_query, user_query=user_query)
            if not df.empty:
                st.write("**Query Result:**")
                # Display single value if applicable
                if df.shape == (1, 1):
                    value = df.iloc[0, 0]
                    if 'revenue_crores' in df.columns:
                        st.write(f"₹{value:,.2f} crore")
                    else:
                        st.write(f"{value}")
                else:
                    # Format columns for display
                    format_dict = {
                        'revenue_crores': "₹{:.2f} crore",
                        "predicted_stockout_date": "{:%Y-%m-%d}",
                        "predicted_restock_date": "{:%Y-%m-%d}",
                        "discountpriceinrs": "₹{:.2f}"
                    }
                    st.dataframe(df.style.format(format_dict, na_rep="-"), use_container_width=True)
                # Show generated SQL query
                st.write("**Generated SQL Query:**")
                st.code(sql_query, language="sql")
                # Export to CSV
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download Result as CSV",
                    data=csv,
                    file_name=f"query_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No results found for the query.")

    # Display query history (max 5)
    if st.session_state.query_history:
        st.write("**Query History (Last 5):**")
        for i, (q, sql) in enumerate(st.session_state.query_history, 1):
            st.write(f"{i}. {q}")

    # Reset button
    st.header("Reset State")
    if st.button("Reset App State"):
        st.session_state.query_history = []
        st.session_state.alerts_run = False
        st.session_state.restock_run = False
        st.session_state.time_filter = "Last 7 Days"
        st.success("App state reset.")
        st.rerun()

# Main dashboard
with st.container():
    st.header("Inventory Dashboard")

    # Time filter for charts
    time_filter = st.selectbox("Select Time Period", ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"],
                               key="time_filter")
    time_delta = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90, "All Time": None}
    days = time_delta[time_filter]

    # Category performance
    st.subheader("Category Performance")
    engine = init_connection()
    query = "SELECT category, SUM(revenueinrs) as revenueinrs FROM sales_and_stock_info"
    if days:
        query += f" WHERE predicted_stockout_date >= CURRENT_DATE - INTERVAL '{days} days'"
    query += " GROUP BY category"
    cat_df = run_query(query, engine, _cache_key=f"category_{time_filter}", user_query="category revenue")
    if not cat_df.empty:
        # Revenue by Category pie chart with percentage on hover
        fig = px.pie(cat_df, values="revenue_crores", names="category", title="Revenue by Category (Crores)",
                     color_discrete_sequence=px.colors.sequential.Peach[::-1])
        fig.update_traces(textinfo='none')  # Remove text on chart
        fig.update_traces(hovertemplate='₹%{value:.2f} crore (%{percent:.1%})')  # Show crores and percentage
        st.plotly_chart(fig, use_container_width=True)
        # Category revenue table
        st.write("**Revenue by Category (Crores):**")
        st.dataframe(cat_df[["category", "revenue_crores"]].style.format({"revenue_crores": "₹{:.2f} crore"}),
                     use_container_width=True)

    # Dropdown for additional visuals
    st.subheader("Additional Insights")
    visual_option = st.selectbox("Select Visualization", [
        "Top 5 Brands by Revenue",
        "Top 5 Individual Categories by Revenue",
        "Revenue Distribution by Gender"
    ], key="visual_select")

    # Top 5 Brands by Revenue
    if visual_option == "Top 5 Brands by Revenue":
        query = "SELECT brandname, SUM(revenueinrs) as revenueinrs FROM sales_and_stock_info"
        if days:
            query += f" WHERE predicted_stockout_date >= CURRENT_DATE - INTERVAL '{days} days'"
        query += " GROUP BY brandname ORDER BY revenueinrs DESC LIMIT 5"
        brand_df = run_query(query, engine, _cache_key=f"top_brands_{time_filter}", user_query="brand revenue")
        if not brand_df.empty:
            fig = px.bar(brand_df,
                         x="revenue_crores",
                         y="brandname",
                         title="Top 5 Brands by Revenue (Crores)",
                         color="brandname",
                         color_discrete_sequence=px.colors.sequential.Peach[::-1],
                         hover_data={"revenue_crores": ":,.2f"},  # Show crores in tooltip
                         text=brand_df['revenue_crores'].round(2))
            fig.update_traces(texttemplate='₹%{text} crore', textposition='inside')
            fig.update_layout(xaxis_title="Revenue (₹ crore)")
            st.plotly_chart(fig, use_container_width=True)

    # Top 5 Individual Categories by Revenue
    elif visual_option == "Top 5 Individual Categories by Revenue":
        query = "SELECT individual_category, SUM(revenueinrs) as revenueinrs FROM sales_and_stock_info"
        if days:
            query += f" WHERE predicted_stockout_date >= CURRENT_DATE - INTERVAL '{days} days'"
        query += " GROUP BY individual_category ORDER BY revenueinrs DESC LIMIT 5"
        cat_ind_df = run_query(query, engine, _cache_key=f"top_categories_{time_filter}", user_query="category revenue")
        if not cat_ind_df.empty:
            fig = px.bar(cat_ind_df,
                         x="revenue_crores",
                         y="individual_category",
                         title="Top 5 Individual Categories by Revenue (Crores)",
                         color="individual_category",
                         color_discrete_sequence=px.colors.sequential.Peach[::-1],
                         hover_data={"revenue_crores": ":,.2f"},  # Show crores in tooltip
                         text=cat_ind_df['revenue_crores'].round(2))
            fig.update_traces(texttemplate='₹%{text} crore', textposition='inside')
            fig.update_layout(xaxis_title="Revenue (₹ crore)")
            st.plotly_chart(fig, use_container_width=True)

    # Revenue Distribution by Gender
    elif visual_option == "Revenue Distribution by Gender":
        query = "SELECT category_by_gender, SUM(revenueinrs) as revenueinrs FROM sales_and_stock_info"
        if days:
            query += f" WHERE predicted_stockout_date >= CURRENT_DATE - INTERVAL '{days} days'"
        query += " GROUP BY category_by_gender"
        gender_df = run_query(query, engine, _cache_key=f"gender_{time_filter}", user_query="gender revenue")
        if not gender_df.empty:
            fig = px.pie(gender_df, values="revenue_crores", names="category_by_gender",
                         title="Revenue Distribution by Gender (Crores)",
                         color_discrete_sequence=px.colors.sequential.Peach[::-1])
            fig.update_traces(textinfo='none')  # Remove text on chart
            fig.update_traces(hovertemplate='₹%{value:.2f} crore (%{percent:.1%})')  # Show crores and percentage
            st.plotly_chart(fig, use_container_width=True)

# Alerts section
with st.container():
    st.subheader("Alerts")
    if st.button("View Alerts") and not st.session_state.alerts_run:
        st.session_state.alerts_run = True
        query = """
        SELECT brandname, individual_category, size, current_stock, discountpriceinrs, predicted_stockout_date
        FROM sales_and_stock_info
        WHERE current_stock <= reorder_level OR predicted_stockout_date <= CURRENT_DATE + INTERVAL '30 days'
        ORDER BY current_stock::FLOAT / NULLIF(reorder_level, 0) ASC
        LIMIT 10
        """
        alert_df = run_query(query, engine, _cache_key="alerts", user_query="alerts")
        if not alert_df.empty:
            # Display table
            st.write("**Top 10 Low Stock or Stock-Out Alerts:**")
            st.dataframe(alert_df.style.format({
                "discountpriceinrs": "₹{:.2f}",
                "predicted_stockout_date": "{:%Y-%m-%d}"
            }), use_container_width=True)
        else:
            st.info("No alerts at this time.")
        st.session_state.alerts_run = False

# import streamlit as st
# import plotly.express as px
# import pandas as pd
# from datetime import datetime
# from app_direct_db_neon import generate_sql_query, get_db_connection

# # Streamlit page configuration
# st.set_page_config(page_title="Myntra Inventory Analysis", layout="wide")

# # Custom CSS for pastel theme with vibrant peach accents
# st.markdown("""
#     <style>
#     body {
#         background-color: #FFF7F0; /* Pale cream background */
#         color: #2F4F4F; /* Slate text */
#     }
#     .stButton>button {
#         background-color: #FF6666; /* Vibrant peach */
#         color: #2F4F4F;
#         border-radius: 10px;
#         border: none;
#         padding: 12px 24px;
#         font-weight: bold;
#         font-size: 16px;
#     }
#     .stButton>button:hover {
#         background-color: #FF4D4D; /* Darker peach */
#         color: #FFF7F0;
#     }
#     .stTextInput>div>input {
#         border-radius: 5px;
#         border: 2px solid #FF6666; /* Vibrant peach border */
#         font-size: 18px;
#         padding: 10px;
#         color: #2F4F4F;
#         background-color: #FFFFFF;
#         text-align: center;
#     }
#     .stSelectbox>div {
#         border-radius: 5px;
#         border: 1px solid #FF6666;
#         font-size: 16px;
#     }
#     .st-container {
#         background-color: #FFFFFF;
#         border-radius: 10px;
#         padding: 20px;
#         box-shadow: 0 2px 4px rgba(0,0,0,0.1);
#     }
#     h1, h2, h3 {
#         color: #2F4F4F;
#         font-weight: bold;
#     }
#     .stMarkdown {
#         color: #2F4F4F;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # Title
# st.title("Myntra Inventory Analysis Chatbot")

# # Initialize session state
# if 'query_history' not in st.session_state:
#     st.session_state.query_history = []
# if 'alerts_run' not in st.session_state:
#     st.session_state.alerts_run = False
# if 'restock_run' not in st.session_state:
#     st.session_state.restock_run = False
# # --- CHANGE 1: Set default to a working filter ---
# if 'time_filter' not in st.session_state:
#     st.session_state.time_filter = "Last 90 Days"

# # Database connection using SQLAlchemy engine
# @st.cache_resource
# def init_connection():
#     return get_db_connection()

# # Cache query results with robust error handling
# @st.cache_data(ttl=300)  # Cache for 5 minutes
# def run_query(query, _engine, _cache_key, user_query):
#     try:
#         df = pd.read_sql(query, _engine)
#         # Convert revenueinrs to crores
#         if 'revenueinrs' in df.columns:
#             df['revenue_crores'] = df['revenueinrs'] / 1_00_00_000
#             df = df.drop(columns=['revenueinrs'])  # Remove original column
#         return df
#     except Exception as e:
#         st.error(f"Query Error: {str(e)}")
#         if _engine:
#             _engine.dispose()
#         st.warning("The database connection was reset due to an error. Please try your query again.")
#         return pd.DataFrame()

# # Sidebar for natural language query
# with st.sidebar:
#     st.header("Ask About Inventory")
#     user_query = st.text_input("Enter your query (e.g., 'stock of jeans from sangria')", key="user_query",
#                                   placeholder="Type your inventory question here...")
#     if st.button("Run Query"):
#         if user_query:
#             engine = init_connection()
#             try:
#                 sql_query = generate_sql_query(user_query)
#                 st.session_state.query_history.append((user_query, sql_query))
#                 if len(st.session_state.query_history) > 5:
#                     st.session_state.query_history = st.session_state.query_history[-5:]
#                 df = run_query(sql_query, engine, _cache_key=user_query, user_query=user_query)
#                 if not df.empty:
#                     st.write("**Query Result:**")
#                     if df.shape == (1, 1):
#                         value = df.iloc[0, 0]
#                         if 'revenue_crores' in df.columns:
#                             st.write(f"₹{value:,.2f} crore")
#                         else:
#                             st.write(f"{value}")
#                     else:
#                         format_dict = {
#                             'revenue_crores': "₹{:.2f} crore",
#                             "predicted_stockout_date": "{:%Y-%m-%d}",
#                             "predicted_restock_date": "{:%Y-%m-%d}",
#                             "discountpriceinrs": "₹{:.2f}"
#                         }
#                         st.dataframe(df.style.format(format_dict, na_rep="-"), use_container_width=True)
#                     st.write("**Generated SQL Query:**")
#                     st.code(sql_query, language="sql")
#                     csv = df.to_csv(index=False)
#                     st.download_button(
#                         label="Download Result as CSV",
#                         data=csv,
#                         file_name=f"query_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
#                         mime="text/csv"
#                     )
#                 else:
#                     st.warning("No results found for the query.")
#             except Exception as e:
#                 st.error(f"An unexpected error occurred: {e}")
#                 if 'engine' in locals() and engine:
#                     engine.dispose()
#                 st.warning("The app encountered an issue. The connection has been reset. Please try again.")

#     if st.session_state.query_history:
#         st.write("**Query History (Last 5):**")
#         for i, (q, sql) in enumerate(st.session_state.query_history, 1):
#             st.write(f"{i}. {q}")

#     st.header("Reset State")
#     if st.button("Reset App State"):
#         st.session_state.query_history = []
#         st.session_state.alerts_run = False
#         st.session_state.restock_run = False
#         st.session_state.time_filter = "Last 90 Days"
#         st.success("App state reset.")
#         st.rerun()

# # Main dashboard
# with st.container():
#     st.header("Inventory Dashboard")

#     # --- CHANGE 2: Only show working filters ---
#     time_filter = st.selectbox("Select Time Period", ["Last 90 Days", "All Time"], key="time_filter")
    
#     time_delta = {"Last 90 Days": 90, "All Time": None} # Simplified dictionary
#     days = time_delta.get(time_filter)

#     st.subheader("Category Performance")
#     engine = init_connection()
#     query = "SELECT category, SUM(revenueinrs) as revenueinrs FROM sales_and_stock_info"
#     if days:
#         query += f" WHERE predicted_stockout_date >= CURRENT_DATE - INTERVAL '{days} days'"
#     query += " GROUP BY category"
#     cat_df = run_query(query, engine, _cache_key=f"category_{time_filter}", user_query="category revenue")
#     if not cat_df.empty:
#         fig = px.pie(cat_df, values="revenue_crores", names="category", title="Revenue by Category (Crores)",
#                        color_discrete_sequence=px.colors.sequential.Peach[::-1])
#         fig.update_traces(textinfo='none')
#         fig.update_traces(hovertemplate='₹%{value:.2f} crore (%{percent:.1%})')
#         st.plotly_chart(fig, use_container_width=True)
#         st.write("**Revenue by Category (Crores):**")
#         st.dataframe(cat_df[["category", "revenue_crores"]].style.format({"revenue_crores": "₹{:.2f} crore"}),
#                        use_container_width=True)
#     else:
#         st.info(f"No data available for the selected time period: {time_filter}")

#     st.subheader("Additional Insights")
#     visual_option = st.selectbox("Select Visualization", [
#         "Top 5 Brands by Revenue",
#         "Top 5 Individual Categories by Revenue",
#         "Revenue Distribution by Gender"
#     ], key="visual_select")

#     if visual_option == "Top 5 Brands by Revenue":
#         query = "SELECT brandname, SUM(revenueinrs) as revenueinrs FROM sales_and_stock_info"
#         if days:
#             query += f" WHERE predicted_stockout_date >= CURRENT_DATE - INTERVAL '{days} days'"
#         query += " GROUP BY brandname ORDER BY revenueinrs DESC LIMIT 5"
#         brand_df = run_query(query, engine, _cache_key=f"top_brands_{time_filter}", user_query="brand revenue")
#         if not brand_df.empty:
#             fig = px.bar(brand_df, x="revenue_crores", y="brandname", title="Top 5 Brands by Revenue (Crores)",
#                          color="brandname", color_discrete_sequence=px.colors.sequential.Peach[::-1],
#                          hover_data={"revenue_crores": ":,.2f"}, text=brand_df['revenue_crores'].round(2))
#             fig.update_traces(texttemplate='₹%{text} crore', textposition='inside')
#             fig.update_layout(xaxis_title="Revenue (₹ crore)")
#             st.plotly_chart(fig, use_container_width=True)
#         else:
#             st.info(f"No data available for the selected time period: {time_filter}")

#     elif visual_option == "Top 5 Individual Categories by Revenue":
#         query = "SELECT individual_category, SUM(revenueinrs) as revenueinrs FROM sales_and_stock_info"
#         if days:
#             query += f" WHERE predicted_stockout_date >= CURRENT_DATE - INTERVAL '{days} days'"
#         query += " GROUP BY individual_category ORDER BY revenueinrs DESC LIMIT 5"
#         cat_ind_df = run_query(query, engine, _cache_key=f"top_categories_{time_filter}", user_query="category revenue")
#         if not cat_ind_df.empty:
#             fig = px.bar(cat_ind_df, x="revenue_crores", y="individual_category", title="Top 5 Individual Categories by Revenue (Crores)",
#                          color="individual_category", color_discrete_sequence=px.colors.sequential.Peach[::-1],
#                          hover_data={"revenue_crores": ":,.2f"}, text=cat_ind_df['revenue_crores'].round(2))
#             fig.update_traces(texttemplate='₹%{text} crore', textposition='inside')
#             fig.update_layout(xaxis_title="Revenue (₹ crore)")
#             st.plotly_chart(fig, use_container_width=True)
#         else:
#             st.info(f"No data available for the selected time period: {time_filter}")

#     elif visual_option == "Revenue Distribution by Gender":
#         query = "SELECT category_by_gender, SUM(revenueinrs) as revenueinrs FROM sales_and_stock_info"
#         if days:
#             query += f" WHERE predicted_stockout_date >= CURRENT_date - INTERVAL '{days} days'"
#         query += " GROUP BY category_by_gender"
#         gender_df = run_query(query, engine, _cache_key=f"gender_{time_filter}", user_query="gender revenue")
#         if not gender_df.empty:
#             fig = px.pie(gender_df, values="revenue_crores", names="category_by_gender",
#                          title="Revenue Distribution by Gender (Crores)",
#                          color_discrete_sequence=px.colors.sequential.Peach[::-1])
#             fig.update_traces(textinfo='none')
#             fig.update_traces(hovertemplate='₹%{value:.2f} crore (%{percent:.1%})')
#             st.plotly_chart(fig, use_container_width=True)
#         else:
#             st.info(f"No data available for the selected time period: {time_filter}")

# with st.container():
#     st.subheader("Alerts")
#     if st.button("View Alerts") and not st.session_state.alerts_run:
#         st.session_state.alerts_run = True
#         query = """
#         SELECT brandname, individual_category, size, current_stock, discountpriceinrs, predicted_stockout_date
#         FROM sales_and_stock_info
#         WHERE current_stock <= reorder_level OR predicted_stockout_date <= CURRENT_DATE + INTERVAL '30 days'
#         ORDER BY current_stock::FLOAT / NULLIF(reorder_level, 0) ASC
#         LIMIT 10
#         """
#         alert_df = run_query(query, engine, _cache_key="alerts", user_query="alerts")
#         if not alert_df.empty:
#             st.write("**Top 10 Low Stock or Stock-Out Alerts:**")
#             st.dataframe(alert_df.style.format({
#                 "discountpriceinrs": "₹{:.2f}",
#                 "predicted_stockout_date": "{:%Y-%m-%d}"
#             }), use_container_width=True)
#         else:
#             st.info("No alerts at this time.")
#         st.session_state.alerts_run = False

