import time

from fastapi import FastAPI

from backend.models import ApplicantRequest, ChatRequest
from backend.eligibility import check_eligibility
from backend.ai_extractor import extract_applicant_data
from backend.extractor import extract_field_value

from backend.conversation import (
    get_session,
    update_session,
    get_missing_fields,
    get_next_question
)


app = FastAPI(
    title="Automated Loan Eligibility Chatbot"
)


@app.get("/")
def home():

    return {
        "message": "Loan Eligibility API is running"
    }


@app.post("/check-eligibility")
def check_loan_eligibility(
    applicant: ApplicantRequest
):

    applicant_data = applicant.model_dump()

    result = check_eligibility(
        applicant_data
    )

    return result


@app.post("/chat")
def chat(
    request: ChatRequest
):

    start_time = time.time()

    applicant_data = get_session(
        request.session_id
    )

    missing_fields = get_missing_fields(
        applicant_data
    )

    current_field = (
        missing_fields[0]
        if missing_fields
        else None
    )


    # --------------------------------
    # Gemini AI Extraction
    # --------------------------------

    try:

        extracted_data = extract_applicant_data(
            request.message,
            current_field
        )

        applicant_data = update_session(
            request.session_id,
            extracted_data
        )


    # --------------------------------
    # Fallback Extraction
    # --------------------------------

    except Exception as e:

        print(
            "GEMINI ERROR:",
            repr(e)
        )

        if current_field is None:

            return {
                "status": "invalid_input",
                "message": (
                    "I could not process your message "
                    "right now. Please try again."
                )
            }


        try:

            extracted_value = extract_field_value(
                request.message,
                current_field
            )

        except (
            ValueError,
            TypeError
        ):

            extracted_value = None


        if extracted_value is None:

            return {
                "status": "invalid_input",
                "message": (
                    "I could not understand your answer. "
                    f"{get_next_question(applicant_data)}"
                )
            }


        applicant_data = update_session(
            request.session_id,
            {
                current_field: extracted_value
            }
        )


    # --------------------------------
    # Check Missing Fields
    # --------------------------------

    missing_fields = get_missing_fields(
        applicant_data
    )


    if missing_fields:

        response_time = round(
            time.time() - start_time,
            2
        )

        return {
            "status": "collecting_information",
            "collected_data": applicant_data,
            "missing_fields": missing_fields,
            "message": get_next_question(
                applicant_data
            ),
            "response_time_seconds": response_time
        }


    # --------------------------------
    # Eligibility Assessment
    # --------------------------------

    result = check_eligibility(
        applicant_data
    )


    response_time = round(
        time.time() - start_time,
        2
    )


    return {
        "status": "assessment_completed",
        "collected_data": applicant_data,
        "eligibility_result": result,
        "response_time_seconds": response_time
    }