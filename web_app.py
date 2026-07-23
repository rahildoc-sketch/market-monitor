import streamlit as st
import sqlite3
import pandas as pd
import time
from market_monitor import UnifiedMarketMonitor
from database import init_db

# 1. Setup webpage layout
st.set_page_config(page_title="Unified Market Monitor", layout="wide")
st.title("Unified Market Monitor (BSE & NSE)")

# 2. Initialize Database & Scraper directly inside Streamlit
@st.cache_resource
def get_scraper():
    init_db()
    return UnifiedMarketMonitor()

scraper = get_scraper()

# 3. Automatically fetch fresh exchange data on page load/refresh
try:
    scraper.fetch_bse()
    scraper.fetch_nse()
except Exception as e:
    st.error(f"Error connecting to exchanges: {e}")

# 4. Read latest data from the database
def load_data():
    try:
        conn = sqlite3.connect("announcements.db")
        query = "SELECT exchange, time, symbol, company, type, pdf FROM announcements ORDER BY time DESC"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data()

# 5. Quick filter options
filter_choice = st.radio(
    "Quick Filter:",
    ["All", "Results & Board", "MTF", "Derivatives"],
    horizontal=True
)

# 6. Apply filter logic
if not df.empty:
    if filter_choice == "Results & Board":
        keywords = ["financial result", "quarterly result", "annual result", "audited financial", "results", "board meeting", "outcome of board meeting"]
        df = df[df['type'].str.lower().str.contains('|'.join(keywords), na=False)]
        
    elif filter_choice == "MTF":
        keywords = ["margin trading facility", "mtf", "margin update", "pledge"]
        df = df[df['type'].str.lower().str.contains('|'.join(keywords), na=False)]
        
    elif filter_choice == "Derivatives":
        keywords = ["derivatives", "institutional", "f&o", "open interest"]
        df = df[df['type'].str.lower().str.contains('|'.join(keywords), na=False)]

    st.dataframe(
        df,
        column_config={
            "pdf": st.column_config.LinkColumn("PDF Link")
        },
        hide_index=True,
        use_container_width=True
    )
else:
    st.warning("Fetching initial data from BSE & NSE, please wait...")

# 7. Auto-Refresh Logic (Set to 10 seconds to avoid cloud rate limits)
st.divider()
auto_refresh = st.checkbox("🟢 Enable Live Auto-Refresh (Updates every 10 seconds)", value=True)

if auto_refresh:
    time.sleep(10)
    st.rerun()
