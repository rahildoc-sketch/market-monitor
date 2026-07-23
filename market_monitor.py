import requests
import streamlit as st
from datetime import datetime
from models import Announcement
from database import insert_announcement
from plyer import notification


def send_telegram_alert(message: str):
    # Safely pull credentials from Streamlit Secrets
    try:
        bot_token = st.secrets["TELEGRAM_BOT_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]
    except Exception as e:
        print(f"Secrets load error: {e}")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram alert failed: {e}")
def parse_and_standardize_time(raw_time):
    """Converts varying BSE and NSE time formats into a uniform YYYY-MM-DD HH:MM:SS string."""
    if not raw_time:
        return ""
    try:
        # Check if it's the BSE ISO format (e.g., 2026-07-23T00:52:19.12)
        if 'T' in raw_time:
            # Strip fractional seconds for clean parsing
            clean_time = raw_time.split('.')[0]
            dt = datetime.strptime(clean_time, "%Y-%m-%dT%H:%M:%S")
        # Otherwise, assume NSE format (e.g., 22-Jul-2026 23:40:06)
        else:
            dt = datetime.strptime(raw_time, "%d-%b-%Y %H:%M:%S")
            
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return raw_time  # Fallback to the raw string if parsing fails


class UnifiedMarketMonitor:
    def __init__(self):
        self.bse_url = "https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w"
        self.nse_url = "https://www.nseindia.com/api/corporate-announcements?index=equities"
        
        self.bse_session = requests.Session()
        self.bse_session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.bseindia.com/"
        })
        
        self.nse_session = requests.Session()
        self.nse_session.headers.update({
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.nseindia.com/companies-listing/corporate-filings-announcements"
        })
        
        self.bse_initialized = False
        self.nse_initialized = False
        
        try: self.nse_session.get("https://www.nseindia.com", timeout=10)
        except: pass

    def trigger_alert(self, ann: Announcement):
        # 1. Desktop Notification handling (cloud-safe)
        try:
            notification.notify(
                title=f"{ann.exchange}: {ann.symbol} Alert",
                message=ann.company,
                timeout=5
            )
        except Exception:
            pass

        # 2. Telegram Alert Filter (Board Meetings & Results)
        ann_type = (ann.type or "").lower()
        keywords = [
            "financial result", "quarterly result", "annual result", 
            "audited financial", "results", "board meeting", "outcome of board meeting"
        ]
        
        if any(keyword in ann_type for keyword in keywords):
            telegram_msg = (
                f"🚨 <b>{ann.exchange} Announcement</b>\n\n"
                f"<b>Company:</b> {ann.company} (<code>{ann.symbol}</code>)\n"
                f"<b>Type:</b> {ann.type}\n"
                f"<b>Time:</b> {ann.time}\n\n"
                f"🔗 <a href='{ann.pdf}'>Open PDF Filing</a>"
            )
            send_telegram_alert(telegram_msg)
    def fetch_bse(self):
        today = datetime.now().strftime("%Y%m%d")
        url = f"{self.bse_url}?pageno=1&strCat=-1&strPrevDate={today}&strScrip=&strSearch=P&strToDate={today}&strType=C&subcategory=-1"
        
        try:
            r = self.bse_session.get(url, timeout=10)
            data = r.json().get("Table", [])
            new_data = []
            
            for item in reversed(data):
                pdf = "https://www.bseindia.com/xml-data/corpfiling/AttachLive/" + item.get("ATTACHMENTNAME", "") if item.get("ATTACHMENTNAME") else ""
                
                # Apply the standardized time parser here
                clean_time = parse_and_standardize_time(item.get("NEWS_DT", ""))
                
                ann = Announcement(
                    time=clean_time,
                    symbol=str(item.get("SCRIP_CD", "")),
                    company=item.get("SLONGNAME", ""),
                    type=item.get("SUBCATNAME", "") or item.get("CATEGORYNAME", ""),
                    seq=str(item.get("NEWSID", "")),
                    pdf=pdf,
                    exchange="BSE"
                )
                
                if insert_announcement(ann):
                    if self.bse_initialized:
                        self.trigger_alert(ann)
                    new_data.append(ann)
            
            self.bse_initialized = True
            return new_data
        except Exception:
            return []

    def fetch_nse(self):
        try:
            r = self.nse_session.get(self.nse_url, timeout=10)
            data = r.json()
            new_data = []
            
            for item in reversed(data[:20]):
                # Apply the standardized time parser here
                clean_time = parse_and_standardize_time(item.get("an_dt", ""))
                
                ann = Announcement(
                    time=clean_time,
                    symbol=item.get("symbol", ""),
                    company=item.get("sm_name", ""),
                    type=item.get("desc", ""),
                    seq=str(item.get("seq_id", "")),
                    pdf=item.get("attchmntFile", ""),
                    exchange="NSE"
                )
                
                if insert_announcement(ann):
                    if self.nse_initialized:
                        self.trigger_alert(ann)
                    new_data.append(ann)
            
            self.nse_initialized = True
            return new_data
        except Exception:
            return []
