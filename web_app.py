import streamlit as st
import sqlite3
import pandas as pd
import time

# 1. Setup the webpage layout
st.set_page_config(page_title="Unified Market Monitor", layout="wide")
st.title("Unified Market Monitor (BSE & NSE)")

# 2. Connect to the SQLite database
def load_data():
    try:
        conn = sqlite3.connect("announcements.db")
        # Load the data into a Pandas DataFrame
        query = "SELECT exchange, time, symbol, company, type, pdf FROM announcements ORDER BY time DESC"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame() # Return empty if the database doesn't exist yet

# Fetch the latest data
df = load_data()

# 3. Create the filter buttons at the top of the page
filter_choice = st.radio(
    "Quick Filter:",
    ["All", "Results & Board", "MTF", "Derivatives"],
    horizontal=True
)

# 4. Apply the filter logic
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

    # 5. Display the data as an interactive web table
    st.dataframe(
        df,
        column_config={
            "pdf": st.column_config.LinkColumn("PDF Link") # Automatically turns raw URLs into clickable links
        },
        hide_index=True,
        use_container_width=True
    )
else:
    st.warning("No data found in the database. Ensure your scraper is running!")

# 6. Auto-Refresh Logic
st.divider()
auto_refresh = st.checkbox("🟢 Enable Live Auto-Refresh (Updates every 3 seconds)", value=True)

if auto_refresh:
    time.sleep(3)
    st.rerun()