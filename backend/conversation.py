required_fields = [

    "loan_type",
    "age",
    "employment_type",
    "monthly_income",
    "credit_score",
    "existing_emi",
    "requested_loan_amount"

]


follow_up_questions = {

    "loan_type": "Which type of loan do you need?",

    "age": "What is your age?",

    "employment_type":
        "What is your employment type: Salaried or Self-Employed?",

    "monthly_income": "What is your monthly income?",

    "credit_score": "What is your credit score?",

    "existing_emi":
        "What is your current monthly EMI? Enter e if you have no EMI.",

    "requested_loan_amount":
        "What loan amount do you require?"

}


def get_missing_fields(applicant_data):

    missing_fields = []

    for field in required_fields:

        if field not in applicant_data or applicant_data[field] is None:

            missing_fields.append(field)

    return missing_fields


def get_next_question(applicant_data):

    missing_fields = get_missing_fields(applicant_data)

    if missing_fields:

        next_field = missing_fields[0]

        return follow_up_questions[next_field]

    return None


# Temporary memory for chatbot conversations
sessions = {}


def get_session(session_id):

    if session_id not in sessions:

        sessions[session_id] = {}

    return sessions[session_id]


def update_session(session_id, new_data):

    applicant_data = get_session(session_id)

    for field, value in new_data.items():

        if value is not None:

            applicant_data[field] = value

    return applicant_data


def reset_session(session_id):

    if session_id in sessions:

        del sessions[session_id]

    return {
        "message": "Conversation reset successfully"
    }