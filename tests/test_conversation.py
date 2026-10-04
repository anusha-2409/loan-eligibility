from backend.conversation import (
    get_missing_fields,
    get_next_question,
    get_session,
    update_session,
    reset_session
)


def test_missing_fields():

    applicant_data = {
        "loan_type": "Home Loan",
        "age": 30
    }

    result = get_missing_fields(applicant_data)

    assert "employment_type" in result

    assert "monthly_income" in result

    assert "credit_score" in result

    assert "existing_emi" in result

    assert "requested_loan_amount" in result


def test_next_question():

    applicant_data = {
        "loan_type": "Home Loan",
        "age": 30
    }

    result = get_next_question(applicant_data)

    assert result == (
        "What is your employment type: "
        "Salaried or Self-Employed?"
    )


def test_update_session():

    session_id = "pytest-session-001"

    reset_session(session_id)

    update_session(
        session_id,
        {"loan_type": "Home Loan"}
    )

    result = update_session(
        session_id,
        {"age": 30}
    )

    assert result["loan_type"] == "Home Loan"

    assert result["age"] == 30

    reset_session(session_id)


def test_reset_session():

    session_id = "pytest-session-002"

    update_session(
        session_id,
        {
            "loan_type": "Personal Loan",
            "age": 28
        }
    )

    reset_session(session_id)

    result = get_session(session_id)

    assert result == {}


def test_no_missing_fields():

    applicant_data = {
        "loan_type": "Home Loan",
        "age": 30,
        "employment_type": "Salaried",
        "monthly_income": 75000,
        "credit_score": 725,
        "existing_emi": 10000,
        "requested_loan_amount": 2500000
    }

    result = get_missing_fields(applicant_data)

    assert result == []

    assert get_next_question(applicant_data) is None