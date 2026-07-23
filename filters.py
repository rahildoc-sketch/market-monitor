RESULT_KEYWORDS = ["financial result", "quarterly result", "annual result", "audited financial", "results"]
BOARD_KEYWORDS = ["board meeting", "outcome of board meeting"]
MTF_KEYWORDS = ["margin trading facility", "mtf", "margin update", "pledge"]
DERIVATIVES_KEYWORDS = ["derivatives", "institutional", "f&o", "open interest"]

def matches_filter(row, current_filter):
    text = f"{row.type} {row.company}".lower()

    if current_filter == "All": return True
    
    # Check individual categories
    is_result = any(k in text for k in RESULT_KEYWORDS)
    is_board = any(k in text for k in BOARD_KEYWORDS)

    if current_filter == "Results": return is_result
    if current_filter == "Board Meeting": return is_board
    
    # NEW: Combined filter
    if current_filter == "Results & Board": return is_result or is_board 
    
    if current_filter == "MTF": return any(k in text for k in MTF_KEYWORDS)
    if current_filter == "Derivatives": return any(k in text for k in DERIVATIVES_KEYWORDS)

    return True

def matches_search(row, search):
    if search.strip() == "": return True
    text = f"{row.exchange} {row.time} {row.symbol} {row.company} {row.type}".lower()
    return search.lower() in text