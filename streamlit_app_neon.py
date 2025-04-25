# # import streamlit as st
# # import plotly.express as px
# # import pandas as pd
# # from datetime import datetime
# # import psycopg2
# # from app_direct_db_neon import generate_sql_query, get_db_connection

# # # Streamlit page configuration
# # st.set_page_config(page_title="Myntra Inventory Analysis", layout="wide")

# # # Custom CSS for pastel theme with vibrant peach accents
# # st.markdown("""
# #     <style>
# #     body {
# #         background-color: #FFF7F0; /* Pale cream background */
# #         color: #2F4F4F; /* Slate text */
# #     }
# #     .stButton>button {
# #         background-color: #FF6666; /* Vibrant peach */
# #         color: #2F4F4F;
# #         border-radius: 10px;
# #         border: none;
# #         padding: 12px 24px;
# #         font-weight: bold;
# #         font-size: 16px;
# #     }
# #     .stButton>button:hover {
# #         background-color: #FF4D4D; /* Darker peach */
# #         color: #FFF7F0;
# #     }
# #     .stTextInput>div>input {
# #         border-radius: 5px;
# #         border: 2px solid #FF6666; /* Vibrant peach border */
# #         font-size: 18px;
# #         padding: 10px;
# #         color: #2F4F4F;
# #         background-color: #FFFFFF;
# #         text-align: center;
# #     }
# #     .stSelectbox>div {
# #         border-radius: 5px;
# #         border: 1px solid #FF6666;
# #         font-size: 16px;
# #     }
# #     .st-container {
# #         background-color: #FFFFFF;
# #         border-radius: 10px;
# #         padding: 20px;
# #         box-shadow: 0 2px 4px rgba(0,0,0,0.1);
# #     }
# #     h1, h2, h3 {
# #         color: #2F4F4F;
# #         font-weight: bold;
# #     }
# #     .stMarkdown {
# #         color: #2F4F4F;
# #     }
# #     </style>
# # """, unsafe_allow_html=True)

# # # Title
# # st.title("Myntra Inventory Analysis Chatbot")

# # # Initialize session state
# # if 'query_history' not in st.session_state:
# #     st.session_state.query_history = []
# # if 'alerts_run' not in st.session_state:
# #     st.session_state.alerts_run = False
# # if 'restock_run' not in st.session_state:
# #     st.session_state.restock_run = False

# # # Database connection
# # @st.cache_resource
# # def init_connection():
# #     return get_db_connection()

# # # Cache query results
# # @st.cache_data(ttl=300)  # Cache for 5 minutes
# # def run_query(query, _conn, _cache_key, user_query):
# #     try:
# #         df = pd.read_sql(query, _conn)
# #         # Check for revenue-related queries
# #         is_revenue = ('revenue' in user_query.lower() or
# #                       'revenue' in query.lower() or
# #                       any('revenue' in col.lower() or 'revenueinrs' in col.lower() for col in df.columns))
# #         if df.shape == (1, 1) and is_revenue:
# #             value = df.iloc[0, 0]
# #             # Convert to rupees if in crores
# #             if 'revenue_in_crores' in df.columns or 'crores' in query.lower():
# #                 value *= 10000000
# #             return pd.DataFrame({'Revenue': [value]})
# #         return df
# #     except Exception as e:
# #         st.error(f"Query Error: {str(e)}")
# #         return pd.DataFrame()

# # # Sidebar for natural language query
# # with st.sidebar:
# #     st.header("Ask About Inventory")
# #     user_query = st.text_input("Enter your query (e.g., 'stock of jeans from sangria')", key="user_query",
# #                                placeholder="Type your inventory question here...")
# #     if st.button("Run Query"):
# #         if user_query:
# #             conn = init_connection()
# #             sql_query = generate_sql_query(user_query)
# #             # Maintain only 5 queries in history
# #             st.session_state.query_history.append((user_query, sql_query))
# #             if len(st.session_state.query_history) > 5:
# #                 st.session_state.query_history = st.session_state.query_history[-5:]
# #             df = run_query(sql_query, conn, _cache_key=user_query, user_query=user_query)
# #             if not df.empty:
# #                 st.write("**Query Result:**")
# #                 # Display single value if applicable
# #                 if df.shape == (1, 1):
# #                     value = df.iloc[0, 0]
# #                     # Format revenue in rupees
# #                     if df.columns[0] == 'Revenue':
# #                         st.write(f"₹{value:,.2f}")
# #                     else:
# #                         st.write(f"{value}")
# #                 else:
# #                     # Format revenue columns in tables
# #                     format_dict = {
# #                         col: "₹{:.2f}" for col in df.columns if 'revenue' in col.lower() or 'revenueinrs' in col.lower()
# #                     }
# #                     format_dict.update({
# #                         "predicted_stockout_date": "{:%Y-%m-%d}",
# #                         "predicted_restock_date": "{:%Y-%m-%d}",
# #                         "discountpriceinrs": "₹{:.2f}"
# #                     })
# #                     st.dataframe(df.style.format(format_dict), use_container_width=True)
# #                 # Show generated SQL query
# #                 st.write("**Generated SQL Query:**")
# #                 st.code(sql_query, language="sql")
# #                 # Export to CSV
# #                 csv = df.to_csv(index=False)
# #                 st.download_button(
# #                     label="Download Result as CSV",
# #                     data=csv,
# #                     file_name=f"query_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
# #                     mime="text/csv"
# #                 )
# #             else:
# #                 st.warning("No results found for the query.")

# #     # Display query history (max 5)
# #     if st.session_state.query_history:
# #         st.write("**Query History (Last 5):**")
# #         for i, (q, sql) in enumerate(st.session_state.query_history, 1):
# #             st.write(f"{i}. {q}")

# #     # Reset button
# #     st.header("Reset State")
# #     if st.button("Reset App State"):
# #         st.session_state.alerts_run = False
# #         st.session_state.query_history = []
# #         st.success("App state reset.")

# # # Main dashboard
# # with st.container():
# #     st.header("Inventory Dashboard")

# #     # Time filter for charts
# #     time_filter = st.selectbox("Select Time Period", ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"], key="time_filter")
# #     time_delta = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90, "All Time": None}
# #     days = time_delta[time_filter]

# #     # Category performance
# #     st.subheader("Category Performance")
# #     conn = init_connection()
# #     query = "SELECT category, SUM(revenueinrs) as revenueinrs FROM sales_and_stock_info"
# #     if days:
# #         query += f" WHERE predicted_stockout_date >= CURRENT_DATE - INTERVAL '{days} days'"
# #     query += " GROUP BY category"
# #     cat_df = run_query(query, conn, _cache_key=f"category_{time_filter}", user_query="category revenue")
# #     if not cat_df.empty:
# #         # Revenue by Category pie chart with percentage on hover
# #         fig = px.pie(cat_df, values="revenueinrs", names="category", title="Revenue by Category",
# #                      color_discrete_sequence=px.colors.sequential.Peach[::-1])
# #         fig.update_traces(textinfo='none')  # Remove text on chart
# #         fig.update_traces(hovertemplate='%{percent:.1%}')  # Show percentage on hover
# #         st.plotly_chart(fig, use_container_width=True)
# #         # Category revenue table with revenue in crores
# #         cat_df['RevenueInCrores'] = cat_df['revenueinrs'] / 10000000  # Convert to crores
# #         st.write("**Revenue by Category:**")
# #         st.dataframe(cat_df[["category", "RevenueInCrores"]].style.format({"RevenueInCrores": "{:.2f} Cr"}),
# #                      use_container_width=True)

# #     # Dropdown for additional visuals
# #     st.subheader("Additional Insights")
# #     visual_option = st.selectbox("Select Visualization", [
# #         "Top 5 Brands by Revenue",
# #         "Top 5 Individual Categories by Revenue",
# #         "Revenue Distribution by Gender"
# #     ], key="visual_select")

# #     # Top 5 Brands by Revenue
# #     if visual_option == "Top 5 Brands by Revenue":
# #         query = "SELECT brandname, SUM(revenueinrs) as revenueinrs FROM sales_and_stock_info"
# #         if days:
# #             query += f" WHERE predicted_stockout_date >= CURRENT_DATE - INTERVAL '{days} days'"
# #         query += " GROUP BY brandname ORDER BY revenueinrs DESC LIMIT 5"
# #         brand_df = run_query(query, conn, _cache_key=f"top_brands_{time_filter}", user_query="brand revenue")
# #         if not brand_df.empty:
# #             # Convert revenue to crores for display and debug print
# #             brand_df['revenueinrs_crores'] = brand_df['revenueinrs'] / 10000000  # Convert to crores
# #             print(f"Debug: brand_df['revenueinrs_crores'] = {brand_df['revenueinrs_crores'].tolist()}")  # Debug output
# #             fig = px.bar(brand_df, x="revenueinrs", y="brandname", title="Top 5 Brands by Revenue",
# #                          color="brandname", color_discrete_sequence=px.colors.sequential.Peach[::-1])
# #             fig.update_traces(text=brand_df['revenueinrs_crores'].round(2).astype(str),  # Explicitly set text values
# #                               texttemplate='₹%{text} Cr',  # Use %{text} with explicit values
# #                               textposition='inside')
# #             st.plotly_chart(fig, use_container_width=True)
# #     # Top 5 Individual Categories by Revenue
# #     elif visual_option == "Top 5 Individual Categories by Revenue":
# #         query = "SELECT individual_category, SUM(revenueinrs) as revenueinrs FROM sales_and_stock_info"
# #         if days:
# #             query += f" WHERE predicted_stockout_date >= CURRENT_DATE - INTERVAL '{days} days'"
# #         query += " GROUP BY individual_category ORDER BY revenueinrs DESC LIMIT 5"
# #         cat_ind_df = run_query(query, conn, _cache_key=f"top_categories_{time_filter}", user_query="category revenue")
# #         if not cat_ind_df.empty:
# #             fig = px.bar(cat_ind_df, x="revenueinrs", y="individual_category",
# #                          title="Top 5 Individual Categories by Revenue",
# #                          color="individual_category", color_discrete_sequence=px.colors.sequential.Peach[::-1],
# #                          text_auto=".2f")
# #             fig.update_traces(texttemplate='₹{text}', textposition='inside')
# #             st.plotly_chart(fig, use_container_width=True)

# #     # Revenue Distribution by Gender
# #     elif visual_option == "Revenue Distribution by Gender":
# #         query = "SELECT category_by_gender, SUM(revenueinrs) as revenueinrs FROM sales_and_stock_info"
# #         if days:
# #             query += f" WHERE predicted_stockout_date >= CURRENT_DATE - INTERVAL '{days} days'"
# #         query += " GROUP BY category_by_gender"
# #         gender_df = run_query(query, conn, _cache_key=f"gender_{time_filter}", user_query="gender revenue")
# #         if not gender_df.empty:
# #             fig = px.pie(gender_df, values="revenueinrs", names="category_by_gender",
# #                          title="Revenue Distribution by Gender",
# #                          color_discrete_sequence=px.colors.sequential.Peach[::-1])
# #             fig.update_traces(textinfo='none')  # Remove text on chart
# #             fig.update_traces(hovertemplate='%{percent:.1%}')  # Show percentage on hover
# #             st.plotly_chart(fig, use_container_width=True)

# # # Alerts section
# # with st.container():
# #     st.subheader("Alerts")
# #     if st.button("View Alerts") and not st.session_state.alerts_run:
# #         st.session_state.alerts_run = True
# #         query = """
# #         SELECT brandname, individual_category, size, current_stock, discountpriceinrs, predicted_stockout_date
# #         FROM sales_and_stock_info
# #         WHERE current_stock <= reorder_level OR predicted_stockout_date <= CURRENT_DATE + INTERVAL '30 days'
# #         ORDER BY current_stock::FLOAT / NULLIF(reorder_level, 0) ASC
# #         LIMIT 10
# #         """
# #         alert_df = run_query(query, conn, _cache_key="alerts", user_query="alerts")
# #         if not alert_df.empty:
# #             # Display table
# #             st.write("**Top 10 Low Stock or Stock-Out Alerts:**")
# #             st.dataframe(alert_df.style.format({
# #                 "discountpriceinrs": "₹{:.2f}",
# #                 "predicted_stockout_date": "{:%Y-%m-%d}"
# #             }), use_container_width=True)
# #         else:
# #             st.info("No alerts at this time.")
# #         st.session_state.alerts_run = False

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

# # Database connection using SQLAlchemy engine
# @st.cache_resource
# def init_connection():
#     return get_db_connection()

# # Cache query results
# @st.cache_data(ttl=300)  # Cache for 5 minutes
# def run_query(query, _engine, _cache_key, user_query):
#     try:
#         df = pd.read_sql(query, _engine)
#         # Check for revenue-related queries
#         is_revenue = ('revenue' in user_query.lower() or
#                       'revenue' in query.lower() or
#                       any('revenue' in col.lower() or 'revenueinrs' in col.lower() for col in df.columns))
#         if df.shape == (1, 1) and is_revenue:
#             value = df.iloc[0, 0]
#             # Convert to rupees if in crores
#             if 'revenue_in_crores' in df.columns or 'crores' in query.lower():
#                 value *= 10000000
#             return pd.DataFrame({'Revenue': [value]})
#         return df
#     except Exception as e:
#         st.error(f"Query Error: {str(e)}")
#         return pd.DataFrame()

# # Sidebar for natural language query
# with st.sidebar:
#     st.header("Ask About Inventory")
#     user_query = st.text_input("Enter your query (e.g., 'stock of jeans from sangria')", key="user_query",
#                                placeholder="Type your inventory question here...")
#     if st.button("Run Query"):
#         if user_query:
#             engine = init_connection()
#             sql_query = generate_sql_query(user_query)
#             # Maintain only 5 queries in history
#             st.session_state.query_history.append((user_query, sql_query))
#             if len(st.session_state.query_history) > 5:
#                 st.session_state.query_history = st.session_state.query_history[-5:]
#             df = run_query(sql_query, engine, _cache_key=user_query, user_query=user_query)
#             if not df.empty:
#                 st.write("**Query Result:**")
#                 # Display single value if applicable
#                 if df.shape == (1, 1):
#                     value = df.iloc[0, 0]
#                     # Format revenue in rupees
#                     if df.columns[0] == 'Revenue':
#                         st.write(f"₹{value:,.2f}")
#                     else:
#                         st.write(f"{value}")
#                 else:
#                     # Format revenue columns in tables
#                     format_dict = {
#                         col: "₹{:.2f}" for col in df.columns if 'revenue' in col.lower() or 'revenueinrs' in col.lower()
#                     }
#                     format_dict.update({
#                         "predicted_stockout_date": "{:%Y-%m-%d}",
#                         "predicted_restock_date": "{:%Y-%m-%d}",
#                         "discountpriceinrs": "₹{:.2f}"
#                     })
#                     st.dataframe(df.style.format(format_dict), use_container_width=True)
#                 # Show generated SQL query
#                 st.write("**Generated SQL Query:**")
#                 st.code(sql_query, language="sql")
#                 # Export to CSV
#                 csv = df.to_csv(index=False)
#                 st.download_button(
#                     label="Download Result as CSV",
#                     data=csv,
#                     file_name=f"query_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
#                     mime="text/csv"
#                 )
#             else:
#                 st.warning("No results found for the query.")

#     # Display query history (max 5)
#     if st.session_state.query_history:
#         st.write("**Query History (Last 5):**")
#         for i, (q, sql) in enumerate(st.session_state.query_history, 1):
#             st.write(f"{i}. {q}")

#     # Reset button
#     st.header("Reset State")
#     if st.button("Reset App State"):
#         st.session_state.alerts_run = False
#         st.session_state.query_history = []
#         st.success("App state reset.")

# # Main dashboard
# with st.container():
#     st.header("Inventory Dashboard")

#     # Time filter for charts
#     time_filter = st.selectbox("Select Time Period", ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"], key="time_filter")
#     time_delta = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90, "All Time": None}
#     days = time_delta[time_filter]

#     # Category performance
#     st.subheader("Category Performance")
#     engine = init_connection()
#     query = "SELECT category, SUM(revenueinrs) as revenueinrs FROM sales_and_stock_info"
#     if days:
#         query += f" WHERE predicted_stockout_date >= CURRENT_DATE - INTERVAL '{days} days'"
#     query += " GROUP BY category"
#     cat_df = run_query(query, engine, _cache_key=f"category_{time_filter}", user_query="category revenue")
#     if not cat_df.empty:
#         # Revenue by Category pie chart with percentage on hover
#         fig = px.pie(cat_df, values="revenueinrs", names="category", title="Revenue by Category",
#                      color_discrete_sequence=px.colors.sequential.Peach[::-1])
#         fig.update_traces(textinfo='none')  # Remove text on chart
#         fig.update_traces(hovertemplate='%{percent:.1%}')  # Show percentage on hover
#         st.plotly_chart(fig, use_container_width=True)
#         # Category revenue table with revenue in crores
#         cat_df['RevenueInCrores'] = cat_df['revenueinrs'] / 10000000  # Convert to crores
#         st.write("**Revenue by Category:**")
#         st.dataframe(cat_df[["category", "RevenueInCrores"]].style.format({"RevenueInCrores": "{:.2f} Cr"}),
#                      use_container_width=True)

#     # Dropdown for additional visuals
#     st.subheader("Additional Insights")
#     visual_option = st.selectbox("Select Visualization", [
#         "Top 5 Brands by Revenue",
#         "Top 5 Individual Categories by Revenue",
#         "Revenue Distribution by Gender"
#     ], key="visual_select")

#     # Top 5 Brands by Revenue
#     if visual_option == "Top 5 Brands by Revenue":
#         query = "SELECT brandname, SUM(revenueinrs) as revenueinrs FROM sales_and_stock_info"
#         if days:
#             query += f" WHERE predicted_stockout_date >= CURRENT_DATE - INTERVAL '{days} days'"
#         query += " GROUP BY brandname ORDER BY revenueinrs DESC LIMIT 5"
#         brand_df = run_query(query, engine, _cache_key=f"top_brands_{time_filter}", user_query="brand revenue")
#         if not brand_df.empty:
#             # Convert revenue to crores for display and debug print
#             brand_df['revenueinrs_crores'] = brand_df['revenueinrs'] / 10000000  # Convert to crores
#             print(f"Debug: brand_df['revenueinrs_crores'] = {brand_df['revenueinrs_crores'].tolist()}")  # Debug output
#             fig = px.bar(brand_df, x="revenueinrs", y="brandname", title="Top 5 Brands by Revenue",
#                          color="brandname", color_discrete_sequence=px.colors.sequential.Peach[::-1])
#             fig.update_traces(text=brand_df['revenueinrs_crores'].round(2).astype(str),  # Explicitly set text values
#                               texttemplate='₹%{text} Cr',  # Use %{text} with explicit values
#                               textposition='inside')
#             st.plotly_chart(fig, use_container_width=True)
#     # Top 5 Individual Categories by Revenue
#     elif visual_option == "Top 5 Individual Categories by Revenue":
#         query = "SELECT individual_category, SUM(revenueinrs) as revenueinrs FROM sales_and_stock_info"
#         if days:
#             query += f" WHERE predicted_stockout_date >= CURRENT_DATE - INTERVAL '{days} days'"
#         query += " GROUP BY individual_category ORDER BY revenueinrs DESC LIMIT 5"
#         cat_ind_df = run_query(query, engine, _cache_key=f"top_categories_{time_filter}", user_query="category revenue")
#         if not cat_ind_df.empty:
#             fig = px.bar(cat_ind_df, x="revenueinrs", y="individual_category",
#                          title="Top 5 Individual Categories by Revenue",
#                          color="individual_category", color_discrete_sequence=px.colors.sequential.Peach[::-1],
#                          text_auto=".2f")
#             fig.update_traces(texttemplate='₹{text}', textposition='inside')
#             st.plotly_chart(fig, use_container_width=True)

#     # Revenue Distribution by Gender
#     elif visual_option == "Revenue Distribution by Gender":
#         query = "SELECT category_by_gender, SUM(revenueinrs) as revenueinrs FROM sales_and_stock_info"
#         if days:
#             query += f" WHERE predicted_stockout_date >= CURRENT_DATE - INTERVAL '{days} days'"
#         query += " GROUP BY category_by_gender"
#         gender_df = run_query(query, engine, _cache_key=f"gender_{time_filter}", user_query="gender revenue")
#         if not gender_df.empty:
#             fig = px.pie(gender_df, values="revenueinrs", names="category_by_gender",
#                          title="Revenue Distribution by Gender",
#                          color_discrete_sequence=px.colors.sequential.Peach[::-1])
#             fig.update_traces(textinfo='none')  # Remove text on chart
#             fig.update_traces(hovertemplate='%{percent:.1%}')  # Show percentage on hover
#             st.plotly_chart(fig, use_container_width=True)

# # Alerts section
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
#             # Display table
#             st.write("**Top 10 Low Stock or Stock-Out Alerts:**")
#             st.dataframe(alert_df.style.format({
#                 "discountpriceinrs": "₹{:.2f}",
#                 "predicted_stockout_date": "{:%Y-%m-%d}"
#             }), use_container_width=True)
#         else:
#             st.info("No alerts at this time.")
#         st.session_state.alerts_run = False

# below is the correct code and showing the revenue in rs correctly
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

# Database connection using SQLAlchemy engine
@st.cache_resource
def init_connection():
    return get_db_connection()

# Cache query results
@st.cache_data(ttl=300)  # Cache for 5 minutes
def run_query(query, _engine, _cache_key, user_query):
    try:
        df = pd.read_sql(query, _engine)
        # Check for revenue-related queries
        is_revenue = ('revenue' in user_query.lower() or
                      'revenue' in query.lower() or
                      any('revenue' in col.lower() or 'revenueinrs' in col.lower() for col in df.columns))
        if df.shape == (1, 1) and is_revenue:
            value = df.iloc[0, 0]
            # Convert to rupees if in crores
            if 'revenue_in_crores' in df.columns or 'crores' in query.lower():
                value *= 10000000
            return pd.DataFrame({'Revenue': [value]})
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
                    # Format revenue in rupees
                    if df.columns[0] == 'Revenue':
                        st.write(f"₹{value:,.2f}")
                    else:
                        st.write(f"{value}")
                else:
                    # Format revenue columns in tables
                    format_dict = {
                        col: "₹{:.2f}" for col in df.columns if 'revenue' in col.lower() or 'revenueinrs' in col.lower()
                    }
                    format_dict.update({
                        "predicted_stockout_date": "{:%Y-%m-%d}",
                        "predicted_restock_date": "{:%Y-%m-%d}",
                        "discountpriceinrs": "₹{:.2f}"
                    })
                    st.dataframe(df.style.format(format_dict), use_container_width=True)
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
        st.session_state.alerts_run = False
        st.session_state.query_history = []
        st.success("App state reset.")

# Main dashboard
with st.container():
    st.header("Inventory Dashboard")

    # Time filter for charts
    time_filter = st.selectbox("Select Time Period", ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"], key="time_filter")
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
        fig = px.pie(cat_df, values="revenueinrs", names="category", title="Revenue by Category",
                     color_discrete_sequence=px.colors.sequential.Peach[::-1])
        fig.update_traces(textinfo='none')  # Remove text on chart
        fig.update_traces(hovertemplate='%{percent:.1%}')  # Show percentage on hover
        st.plotly_chart(fig, use_container_width=True)
        # Category revenue table with raw revenue
        st.write("**Revenue by Category (Raw):**")
        st.dataframe(cat_df[["category", "revenueinrs"]], use_container_width=True)

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
            # Debug raw and grouped data
            print(f"Debug: brand_df['revenueinrs'] (grouped) = {brand_df['revenueinrs'].tolist()}")  # Grouped sums
            raw_query = "SELECT brandname, revenueinrs FROM sales_and_stock_info LIMIT 10"
            raw_df = run_query(raw_query, engine, _cache_key="raw_data", user_query="raw data")
            print(f"Debug: Raw revenueinrs sample = {raw_df['revenueinrs'].tolist() if not raw_df.empty else 'Empty'}")
            # Use raw revenueinrs for now
            fig = px.bar(brand_df,
                         x="revenueinrs",
                         y="brandname",
                         title="Top 5 Brands by Revenue (Raw)",
                         color="brandname",
                         color_discrete_sequence=px.colors.sequential.Peach[::-1],
                         hover_data={"revenueinrs": ":,.0f"},  # Show raw rupees in tooltip
                         text=brand_df['revenueinrs'].round(2))
            fig.update_traces(texttemplate='₹%{text}', textposition='inside')
            fig.update_layout(xaxis_title="Revenue (₹)")
            st.plotly_chart(fig, use_container_width=True)

    # Top 5 Individual Categories by Revenue
    elif visual_option == "Top 5 Individual Categories by Revenue":
        query = "SELECT individual_category, SUM(revenueinrs) as revenueinrs FROM sales_and_stock_info"
        if days:
            query += f" WHERE predicted_stockout_date >= CURRENT_DATE - INTERVAL '{days} days'"
        query += " GROUP BY individual_category ORDER BY revenueinrs DESC LIMIT 5"
        cat_ind_df = run_query(query, engine, _cache_key=f"top_categories_{time_filter}", user_query="category revenue")
        if not cat_ind_df.empty:
            # Debug raw and grouped data
            print(f"Debug: cat_ind_df['revenueinrs'] (grouped) = {cat_ind_df['revenueinrs'].tolist()}")  # Grouped sums
            raw_query = "SELECT individual_category, revenueinrs FROM sales_and_stock_info LIMIT 10"
            raw_df = run_query(raw_query, engine, _cache_key="raw_data", user_query="raw data")
            print(f"Debug: Raw revenueinrs sample = {raw_df['revenueinrs'].tolist() if not raw_df.empty else 'Empty'}")
            # Use raw revenueinrs for now
            fig = px.bar(cat_ind_df,
                         x="revenueinrs",
                         y="individual_category",
                         title="Top 5 Individual Categories by Revenue (Raw)",
                         color="individual_category",
                         color_discrete_sequence=px.colors.sequential.Peach[::-1],
                         hover_data={"revenueinrs": ":,.0f"},  # Show raw rupees in tooltip
                         text=cat_ind_df['revenueinrs'].round(2))
            fig.update_traces(texttemplate='₹%{text}', textposition='inside')
            fig.update_layout(xaxis_title="Revenue (₹)")
            st.plotly_chart(fig, use_container_width=True)

    # Revenue Distribution by Gender
    elif visual_option == "Revenue Distribution by Gender":
        query = "SELECT category_by_gender, SUM(revenueinrs) as revenueinrs FROM sales_and_stock_info"
        if days:
            query += f" WHERE predicted_stockout_date >= CURRENT_DATE - INTERVAL '{days} days'"
        query += " GROUP BY category_by_gender"
        gender_df = run_query(query, engine, _cache_key=f"gender_{time_filter}", user_query="gender revenue")
        if not gender_df.empty:
            fig = px.pie(gender_df, values="revenueinrs", names="category_by_gender",
                         title="Revenue Distribution by Gender",
                         color_discrete_sequence=px.colors.sequential.Peach[::-1])
            fig.update_traces(textinfo='none')  # Remove text on chart
            fig.update_traces(hovertemplate='%{percent:.1%}')  # Show percentage on hover
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

