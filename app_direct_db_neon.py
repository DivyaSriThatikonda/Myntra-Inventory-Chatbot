from dotenv import load_dotenv
import os
import logging
import time
from openai import OpenAI
from sqlalchemy import create_engine
from prompt_config_neon import PROMPT_TEMPLATE, BRAND_NAMES, CATEGORIES, INDIVIDUAL_CATEGORIES, SAMPLE_QUESTIONS

# Load .env file
load_dotenv()

# Configure logging to ERROR and DEBUG
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Access environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_ENDPOINT = os.getenv("DB_ENDPOINT")

# Validate environment variables
if not all([OPENROUTER_API_KEY, DB_USER, DB_PASSWORD, DB_HOST, DB_NAME, DB_ENDPOINT]):
    missing = [k for k, v in {
        "OPENROUTER_API_KEY": OPENROUTER_API_KEY,
        "DB_USER": DB_USER,
        "DB_PASSWORD": DB_PASSWORD,
        "DB_HOST": DB_HOST,
        "DB_NAME": DB_NAME,
        "DB_ENDPOINT": DB_ENDPOINT
    }.items() if not v]
    logger.error(f"Missing environment variables: {missing}")
    raise ValueError(f"Missing environment variables: {missing}")

# Initialize OpenRouter client
try:
    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )
except Exception as e:
    logger.error(f"Error initializing OpenAI client: {str(e)}")
    raise

# Database connection using SQLAlchemy
def get_db_connection():
    try:
        engine = create_engine(
            f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?sslmode=require&options=endpoint={DB_ENDPOINT}"
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

# Generate SQL query with retry logic
def generate_sql_query(natural_query):
    try:
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
        for attempt in range(3):  # Retry up to 3 times
            try:
                response = client.chat.completions.create(
                    model="deepseek/deepseek-chat-v3-0324:free",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.7
                )
                # Check if response is valid
                if not response or not hasattr(response, 'choices') or not response.choices:
                    logger.error("Invalid API response: No choices returned")
                    return "SELECT 'Error: Invalid API response' AS error"
                
                sql_query = response.choices[0].message.content.strip()
                logger.debug(f"Generated SQL query: {sql_query}")

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
                error_msg = str(e)
                logger.error(f"API call failed (attempt {attempt + 1}): {error_msg}")
                if "rate limit" in error_msg.lower() or "429" in error_msg.lower():
                    if attempt < 2:
                        time.sleep(2 ** (attempt + 1))  # Exponential backoff: 2s, 4s
                        continue
                return f"SELECT 'Error: {error_msg.replace('\'', '\'\'')}' AS error"
        return "SELECT 'Error: Rate limit exceeded after retries' AS error"
    except Exception as e:
        logger.error(f"Error generating SQL query: {str(e)}")
        return f"SELECT 'Error: {str(e).replace('\'', '\'\'')}' AS error"
