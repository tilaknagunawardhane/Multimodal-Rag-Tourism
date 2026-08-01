# --- Helper: User-Friendly Error Classifier ---
def get_friendly_error_message(error_obj: Exception) -> str:
    """Translates raw technical exceptions into end-user-friendly messages."""
    err_str = str(error_obj).lower()
    
    if any(k in err_str for k in ["11001", "getaddrinfo", "connection", "timeout", "network"]):
        return "**Network Connection Issue**\n\nWe are having trouble reaching our travel servers right now. Please check your internet connection and try again."
    elif any(k in err_str for k in ["401", "403", "api key", "unauthorized"]):
        return "**System Configuration Error**\n\nOur travel guide system is currently experiencing a temporary configuration issue. Please try again later."
    elif any(k in err_str for k in ["429", "503", "quota", "rate limit"]):
        return "**Service Busy**\n\nOur travel guides are currently helping a lot of people! Please wait a moment and try your search again."
    else:
        return "**Search Interrupted**\n\nOops! Something went wrong while searching for your destinations. Please try asking your question differently or click retry."