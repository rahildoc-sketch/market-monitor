import time
from market_monitor import UnifiedMarketMonitor
from database import init_db

def run_scraper():
    print("Initializing database...")
    init_db()
    
    print("Starting headless market monitor (BSE & NSE)...")
    scraper = UnifiedMarketMonitor()
    
    print("🟢 Scraper is now running silently in the background.")
    print("You can view the live data in your Streamlit web app.")
    print("Press Ctrl+C in this terminal to stop the scraper.")
    
    while True:
        try:
            # Fetch data from both exchanges
            # The scraper automatically inserts new rows into announcements.db
            # and triggers desktop notifications for new alerts
            scraper.fetch_bse()
            scraper.fetch_nse()
            
        except Exception as e:
            print(f"🔴 Error during scraping: {e}")
            
        # Sleep for 1.5 seconds to prevent rate-limiting from the exchanges
        time.sleep(1.5)

if __name__ == "__main__":
    run_scraper()