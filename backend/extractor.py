from backend.normalizer import normalize_amount


def extract_loan_type(message):
    message = message.lower()

    if "home loan" in message or "housing loan" in message:
        return "Home Loan"

    if "personal loan" in message:
        return "Personal Loan"

    if "vehicle loan" in message or "car loan" in message:
        return "Vehicle Loan"

    if "education loan" in message or "student loan" in message:
        return "Education Loan"

    if "business loan" in message:
        return "Business Loan"

    return None


def extract_field_value(message, field):

    message = message.strip()

    if field == "loan_type":
        return extract_loan_type(message)

    if field == "age":
        return int(message)

    if field == "employment_type":

        if "self" in message.lower():
            return "Self-Employed"

        if "salaried" in message.lower():
            return "Salaried"

        return None

    if field == "monthly_income":
        return normalize_amount(message)

    if field == "credit_score":
        return int(message)

    if field == "existing_emi":

        # User can enter e when they have no EMI
        if message.lower() in ["e", "no emi", "zero emi", "none"]:
            return 0

        return normalize_amount(message)

    if field == "requested_loan_amount":
        return normalize_amount(message)

    return None

