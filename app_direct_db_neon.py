# import streamlit as st
# import google.generativeai as genai
# import psycopg2
# import logging
# import time
# from psycopg2 import OperationalError
# from prompt_config_neon import PROMPT_TEMPLATE, BRAND_NAMES, CATEGORIES, INDIVIDUAL_CATEGORIES, SAMPLE_QUESTIONS

# # Configure logging to ERROR only
# logging.basicConfig(level=logging.ERROR)
# logger = logging.getLogger(__name__)

# # Access secrets from Streamlit's secrets management
# GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
# genai.configure(api_key=GOOGLE_API_KEY)

# # Database connection
# def get_db_connection(max_attempts=3, delay=5):
#     attempt = 1
#     while attempt <= max_attempts:
#         try:
#             conn = psycopg2.connect(
#                 dbname=st.secrets.get("DB_NAME", "neondb"),
#                 user=st.secrets.get("DB_USER", "neondb_owner"),
#                 password=st.secrets.get("DB_PASSWORD", "npg_s7ZtPY4rzBWb"),
#                 host=st.secrets.get("DB_HOST", "100.26.116.133"),
#                 port="5432",
#                 sslmode="require",
#                 options=f"endpoint={st.secrets.get('DB_ENDPOINT', 'ep-solitary-breeze-a44gdzow')}"
#             )
#             return conn
#         except OperationalError as e:
#             logger.error(f"Database connection attempt {attempt} failed: {str(e)}")
#             attempt += 1
#             time.sleep(delay)
#     logger.error("Failed to connect to Neon database after multiple attempts")
#     raise Exception("Failed to connect to Neon database after multiple attempts")

# # Preprocess query
# def preprocess_query(query):
#     query = query.lower().strip()
#     for brand in BRAND_NAMES:
#         if brand.lower() in query:
#             query = query.replace(brand.lower(), brand)  # Preserve exact brand case
#     for cat in CATEGORIES + INDIVIDUAL_CATEGORIES:
#         if cat.lower() in query:
#             query = query.replace(cat.lower(), cat)  # Preserve exact category case
#     return query

# # Generate SQL query
# def generate_sql_query(natural_query):
#     try:
#         model = genai.GenerativeModel("gemini-1.5-pro")
#         brand_samples = ", ".join(BRAND_NAMES[:5])
#         category_samples = ", ".join(CATEGORIES[:5])
#         individual_category_samples = ", ".join(INDIVIDUAL_CATEGORIES[:5])
#         sample_questions = "\n".join([f"- '{k}': {v}" for k, v in SAMPLE_QUESTIONS.items()])

#         prompt = PROMPT_TEMPLATE.format(
#             query=natural_query,
#             brand_samples=brand_samples,
#             category_samples=category_samples,
#             individual_category_samples=individual_category_samples,
#             sample_questions=sample_questions,
#             brand_count=len(BRAND_NAMES),
#             category_count=len(CATEGORIES),
#             individual_category_count=len(INDIVIDUAL_CATEGORIES)
#         )

#         processed_query = preprocess_query(natural_query)
#         response = model.generate_content(prompt)
#         sql_query = response.text.strip()

#         # Clean up the query if it includes markdown
#         if sql_query.startswith("```sql") and sql_query.endswith("```"):
#             sql_query = sql_query[6:-3].strip()
#         elif sql_query.startswith("```") and sql_query.endswith("```"):
#             sql_query = sql_query[3:-3].strip()

#         # Validate query
#         if not sql_query.upper().startswith("SELECT"):
#             logger.error(f"Invalid SQL query generated: {sql_query}")
#             return "SELECT 'Invalid query generated' AS error"

#         return sql_query
#     except Exception as e:
#         logger.error(f"Error generating SQL query: {str(e)}")
#         return f"SELECT 'Error: {str(e)}' AS error"
import streamlit as st
import google.generativeai as genai
from sqlalchemy import create_engine
import logging
import time
from prompt_config_neon import PROMPT_TEMPLATE, BRAND_NAMES, CATEGORIES, INDIVIDUAL_CATEGORIES, SAMPLE_QUESTIONS

# Configure logging to ERROR only
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Access secrets from Streamlit's secrets management
GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

# Database connection using SQLAlchemy
def get_db_connection():
    try:
        engine = create_engine(
            f"postgresql://{st.secrets['DB_USER']}:{st.secrets['DB_PASSWORD']}@{st.secrets['DB_HOST']}/{st.secrets['DB_NAME']}?sslmode=require&options=endpoint={st.secrets['DB_ENDPOINT']}"
        )
        return engine
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise

# Preprocess query
def preprocess_query(query):
    query = query.lower().strip()
    for brand in BRAND_NAMES:
        if brand.lower() in query:
            query = query.replace(brand.lower(), brand)  # Preserve exact brand case
    for cat in CATEGORIES + INDIVIDUAL_CATEGORIES:
        if cat.lower() in query:
            query = query.replace(cat.lower(), cat)  # Preserve exact category case
    return query

# Generate SQL query
def generate_sql_query(natural_query):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        brand_samples = ", ".join(BRAND_NAMES[:5])
        category_samples = ", ".join(CATEGORIES[:5])
        individual_category_samples = ", ".join(INDIVIDUAL_CATEGORIES[:5])
        sample_questions = "\n".join([f"- '{k}': {v}" for k, v in SAMPLE_QUESTIONS.items()])

        prompt = PROMPT_TEMPLATE.format(
            query=natural_query,
            brand_samples=brand_samples,
            category_samples=category_samples,
            individual_category_samples=individual_category_samples,
            sample_questions=sample_questions,
            brand_count=len(BRAND_NAMES),
            category_count=len(CATEGORIES),
            individual_category_count=len(INDIVIDUAL_CATEGORIES)
        )

        processed_query = preprocess_query(natural_query)
        response = model.generate_content(prompt)
        sql_query = response.text.strip()

        # Clean up the query if it includes markdown
        if sql_query.startswith("```sql") and sql_query.endswith("```"):
            sql_query = sql_query[6:-3].strip()
        elif sql_query.startswith("```") and sql_query.endswith("```"):
            sql_query = sql_query[3:-3].strip()

        # Validate query
        if not sql_query.upper().startswith("SELECT"):
            logger.error(f"Invalid SQL query generated: {sql_query}")
            return "SELECT 'Invalid query generated' AS error"

        return sql_query
    except Exception as e:
        logger.error(f"Error generating SQL query: {str(e)}")
        return f"SELECT 'Error: {str(e)}' AS error"
