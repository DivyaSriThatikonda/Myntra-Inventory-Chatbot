# # Myntra Inventory Analysis Chatbot 🛍️

Yo, welcome to my **Myntra Inventory Analysis Chatbot**! This slick **Streamlit** app is your fashion AI buddy, answering questions like “How many H&M kurtas are left?” with *bam*—dope rupee charts and alerts. It’s built to make Myntra’s inventory game super easy and cook like a pro! 😎

## What’s the Deal? ✨
This app lets you ask anything about Myntra’s inventory, and it turns your questions into **PostgreSQL queries** to grab data from a **Neon database**. You get cool charts, insights, and alerts to keep stock on point. It’s powered by **Python**, **NLP**, and **cloud tech**, with a fresh pastel vibe.

## Live Demo 🚀
Check it out: [myntra-inventory-chatbot.streamlit.app](https://myntra-inventory-chatbot-e4pjybdmi2pbfvdypumcda.streamlit.app/)

## Features 🌟
- **Ask Anything**: Type questions like “What’s Levi’s jeans revenue?” for instant answers.
- **Cool Charts**: See sales and stock in rupees with time filters (7, 30, 90 days, or all time).
- **Extra Insights**:
  - Top 5 brands by revenue (e.g., H&M at ₹328,230,000,000).
  - Top 5 styles by revenue (e.g., jeans, kurtas).
  - Sales split by gender (e.g., 60% women).
  - Top 10 low-stock alerts with predicted stockout dates .
- **Chill UI**: Pastel cream-peach theme, sidebar for questions, and 5-question history tracker.
- **Download Data**: Grab query results as CSV.
- **Fast Vibes**: **Streamlit** caching keeps it snappy.

## How It Works 🛠️
1. Type a question in the app’s sidebar (e.g., “Revenue of H&M tops”).
2. **LangChain’s SQLDatabaseChain** and **DeepSeek-V3-0324** turn it into a **PostgreSQL query**.
3. Data’s pulled from **Neon**’s database (104K+ rows, 500+ brands).
4. **Plotly Express** shows charts with time filters and insights, plus alerts for low stock.

## Frontend Details 🎨
- **Framework**: **Streamlit** for a clean, interactive UI.
- **UI Layout**:
  - **Sidebar**: Input questions and get the answers about the inventory. 
  - **Main Panel**: Shows query results, **Plotly** charts along with the time periods (7, 30, 90 days, all time), and Top 10 alerts for low stock.
  - **History Tracker**: Remembers your last 5 questions using **Streamlit** session state.
- **Charts** (via **Plotly Express**):
  - Bar charts: Top 5 brands and styles by revenue, with rupees (e.g., ₹328,230,000,000).
  - Pie chart: Revenue split by category and Gender sales split with hover percentages (e.g., 60% women).
  - Time Filters: Dropdown for 7, 30, 90 days, or all time to scope data.
- **Alerts**: Top 10 low-stock warnings with `predicted_stockout_date` (e.g., “Nike sneakers low, stockout by 2025-05-10”).
- **Style**: Pastel cream-peach theme for a fresh, modern look.
- **Extras**: CSV download button and **Streamlit** caching for speed.

## Datasets 📊
- **Overview**: Two CSV files power the app, with 500+ brands, 50+ subcategories (e.g., kurtas, jeans, shirts), and 5+ categories (e.g., top wear, bottom wear).
- **`myntra_fashion_clothing`** (104,237 rows, 14 columns):
  - `url`: Product’s web link (e.g., myntra.com/jeans/123).
  - `product_id`: Unique item ID (e.g., 12345).
  - `brandname`: Brand (e.g., Levi’s, H&M).
  - `category`: Main group (e.g., top wear).
  - `individual_category`: Style (e.g., shirts, jeans).
  - `category_by_gender`: Men, women, or unisex.
  - `description`: Item details (e.g., “Blue denim jeans”).
  - `discountpriceinrs`: Sale price in rupees (e.g., ₹1500).
  - `originalpriceinrs`: Full price in rupees (e.g., ₹2000).
  - `discountoffer`: Deal info (e.g., “25% off”).
  - `ratings`: Customer score (e.g., 4.2).
  - `reviews`: Comment count (e.g., 50).
  - `standardsize`: Sizes (e.g., S, M, L).
  - `discountpercent`: Savings percentage (e.g., 25).
- **`sales_and_stock_info`** (117,541 rows, 16 columns):
  - `product_id`: Unique item ID (e.g., P12345).
  - `brandname`: Brand (e.g., Levi’s).
  - `category`: Main group (e.g., bottom wear).
  - `individual_category`: Style (e.g., jeans).
  - `category_by_gender`: Men or women.
  - `description`: Item info (e.g., “Slim fit jeans”).
  - `discountpriceinrs`: Sale price in rupees (e.g., ₹1500).
  - `current_stock`: Items in stock (e.g., 30).
  - `reorder_level`: Restock trigger (e.g., 10).
  - `quantity_sold`: Items sold (e.g., 100).
  - `revenueinrs`: Revenue in rupees (e.g., ₹150,000).
  - `turnover_flag`: Stock speed (e.g., “fast”).
  - `predicted_restock_quantity`: Restock amount (e.g., 50).
  - `predicted_stockout_date`: Stockout date (e.g., 2025-05-10).
  - `predicted_restock_date`: Restock date (e.g., 2025-05-15).
  - `size`: Item size (e.g., 32).
- **Import**: Loaded CSVs into **Neon** using `psql \copy`, with `originalpriceinrs` set to `DOUBLE PRECISION` for decimals.

## Setup ⚙️
Wanna make it cook? Here’s how:
1. **Clone the Repo**:
   ```bash
   git clone https://github.com/DivyaSriThatikonda/Myntra-Inventory-Chatbot.git
   ```
2. **What You Need**:
   - Python 3.10+
   - **Neon** PostgreSQL account
   - **DeepSeek-V3-0324 API** key (from openrouter.ai)
   - Packages: `streamlit`, `plotly`, `pandas`, `sqlalchemy`, `psycopg2`, `langchain`, `google-generativeai`
3. **Install Packages**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Setup Steps**:
   - Add your **Neon** connection string  and **DeepSeek-V3-0324 API** key to `.env`.
   - Load `myntra_fashion_clothing.csv` and `sales_and_stock_info.csv` into **Neon** using `psql \copy`.
5. **Run the App**:
   ```bash
   streamlit run streamlit_app_neon.py
   ```

## Files 📂
- `streamlit_app_neon.py`: Powers the **Streamlit** UI, **Plotly** charts, time filters, and question tracker.
- `app_direct_db_neon.py`: Connects to **Neon** database with **SQLAlchemy** and **psycopg2**.
- `prompt_config_neon.py`: Guides queries with 500+ brands, 50+ subcategories, and 5+ categories.
- `myntra_fashion_clothing.csv`, `sales_and_stock_info.csv`: The data stash.
- `requirements.txt`: Lists all needed packages.
- `.gitignore`, `README.md`: Keeps the repo clean and explains setup.

## Tech Stack 🧑‍💻
- **Backend**: Python, SQL, LangChain, Gemini API, SQLAlchemy, psycopg2, Neon
- **Frontend**: Streamlit, Plotly Express
- **Tools**: PyCharm, psql, GitHub, Streamlit Cloud

## Wanna Connect? 🤝
Hit me up on LinkedIn or scope the code! 

**Connect**: [LinkedIn](https://www.linkedin.com/in/divyasri-thatikonda/)
**Live Demo**: [myntra-inventory-chatbot.streamlit.app](https://myntra-inventory-chatbot-e4pjybdmi2pbfvdypumcda.streamlit.app/)
