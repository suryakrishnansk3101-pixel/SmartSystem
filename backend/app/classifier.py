def classify_ticket(description: str):

    text = description.lower()

    # IT
    if any(word in text for word in [
        "vpn",
        "password",
        "email",
        "wifi",
        "software",
        "laptop",
        "computer",
        "network",
        "github",
        "docker"
    ]):
        return "IT"

    # HR
    elif any(word in text for word in [
        "leave",
        "salary",
        "payroll",
        "insurance",
        "maternity",
        "attendance",
        "appraisal",
        "hr"
    ]):
        return "HR"

    # Facilities
    elif any(word in text for word in [
        "ac",
        "air conditioning",
        "chair",
        "parking",
        "desk",
        "office",
        "badge",
        "facility"
    ]):
        return "Facilities"

    return "General"