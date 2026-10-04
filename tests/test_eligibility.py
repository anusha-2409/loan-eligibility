from backend.eligibility import calculate_dti, check_eligibility


def test_calculate_dti():

    result = calculate_dti(10000, 75000)

    assert result == 13.33


def test_eligible_home_loan_applicant():

    applicant = {
        "loan_type": "Home Loan",
        "age": 30,
        "employment_type": "Salaried",
        "monthly_income": 75000,
        "credit_score": 725,
        "existing_emi": 10000,
        "requested_loan_amount": 2500000
    }

    result = check_eligibility(applicant)

    assert result["status"] == "Eligible"

    assert result["calculated_dti"] == 13.33

    assert result["age_passed"] is True

    assert result["income_passed"] is True

    assert result["credit_score_passed"] is True

    assert result["dti_passed"] is True

    assert result["loan_amount_passed"] is True

    assert result["credit_score_category"] == "Good"


def test_low_credit_score_applicant():

    applicant = {
        "loan_type": "Home Loan",
        "age": 30,
        "employment_type": "Salaried",
        "monthly_income": 75000,
        "credit_score": 650,
        "existing_emi": 10000,
        "requested_loan_amount": 2500000
    }

    result = check_eligibility(applicant)

    assert result["status"] == "Not Eligible"

    assert result["credit_score_passed"] is False

    assert len(result["failed_conditions"]) > 0

    assert len(result["recommendations"]) > 0


def test_high_dti_applicant():

    applicant = {
        "loan_type": "Home Loan",
        "age": 30,
        "employment_type": "Salaried",
        "monthly_income": 50000,
        "credit_score": 725,
        "existing_emi": 25000,
        "requested_loan_amount": 2500000
    }

    result = check_eligibility(applicant)

    assert result["status"] == "Not Eligible"

    assert result["calculated_dti"] == 50.0

    assert result["dti_passed"] is False


def test_excessive_loan_amount():

    applicant = {
        "loan_type": "Home Loan",
        "age": 30,
        "employment_type": "Salaried",
        "monthly_income": 75000,
        "credit_score": 725,
        "existing_emi": 10000,
        "requested_loan_amount": 6000000
    }

    result = check_eligibility(applicant)

    assert result["status"] == "Not Eligible"

    assert result["loan_amount_passed"] is False


def test_age_below_minimum():

    applicant = {
        "loan_type": "Home Loan",
        "age": 20,
        "employment_type": "Salaried",
        "monthly_income": 75000,
        "credit_score": 725,
        "existing_emi": 10000,
        "requested_loan_amount": 2500000
    }

    result = check_eligibility(applicant)

    assert result["status"] == "Not Eligible"

    assert result["age_passed"] is False