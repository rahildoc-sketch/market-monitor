from dataclasses import dataclass

@dataclass
class Announcement:
    time: str
    symbol: str
    company: str
    type: str
    seq: str
    pdf: str
    exchange: str  # Identifies 'BSE' or 'NSE'