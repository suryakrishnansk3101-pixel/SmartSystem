def predict_priority(description: str):

    text = description.lower()

    if any(word in text for word in [
        "server down",
        "production",
        "critical",
        "security breach",
        "system outage",
        "unable to work"
    ]):
        return "High"

    elif any(word in text for word in [
        "vpn",
        "email",
        "software",
        "network",
        "printer"
    ]):
        return "Medium"

    return "Low"