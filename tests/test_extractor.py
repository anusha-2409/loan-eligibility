from backend.extractor import (
    extract_loan_type,
    extract_field_value
)


def test_extract_home_loan():

    result = extract_loan_type(
        "I need a home loan"
    )

    assert result == "Home Loan"


def test_extract_vehicle_loan():

    result = extract_loan_type(
        "I want a car loan"
    )

    assert result == "Vehicle Loan"


def test_extract_education_loan():

    result = extract_loan_type(
        "I need a student loan"
    )

    assert result == "Education Loan"


def test_extract_unknown_loan():

    result = extract_loan_type(
        "I need financial assistance"
    )

    assert result is None


def test_extract_age():

    result = extract_field_value(
        "30",
        "age"
    )

    assert result == 30


def test_extract_salaried_employment():

    result = extract_field_value(
        "Salaried",
        "employment_type"
    )

    assert result == "Salaried"


def test_extract_self_employed():

    result = extract_field_value(
        "Self employed",
        "employment_type"
    )

    assert result == "Self-Employed"


def test_extract_loan_amount():

    result = extract_field_value(
        "25 lakh",
        "requested_loan_amount"
    )

    assert result == 2500000


def test_extract_no_emi():

    result = extract_field_value(
        "no EMI",
        "existing_emi"
    )

    assert result == 0