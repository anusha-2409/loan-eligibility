
from backend.data_loader import get_loan_by_type


def calculate_dti(existing_emi, monthly_income):

    if monthly_income <= 0:
        raise ValueError("Monthly income must be greater than zero.")

    if existing_emi < 0:
        raise ValueError("Existing EMI cannot be negative.")

    dti = (existing_emi / monthly_income) * 100

    return round(dti, 2)


def get_credit_score_category(credit_score):

    if 300 <= credit_score <= 549:
        return "Poor"

    elif 550 <= credit_score <= 649:
        return "Fair"

    elif 650 <= credit_score <= 749:
        return "Good"

    elif 750 <= credit_score <= 799:
        return "Very Good"

    elif 800 <= credit_score <= 900:
        return "Excellent"

    return "Invalid Credit Score"


def check_eligibility(applicant):

    loan = get_loan_by_type(applicant["loan_type"])

    if loan is None:
        return {
            "status": "Not Eligible",
            "reason": "Loan type not found"
        }

    # --------------------------------------------------
    # Calculate DTI
    # --------------------------------------------------

    dti = calculate_dti(
        applicant["existing_emi"],
        applicant["monthly_income"]
    )

    # --------------------------------------------------
    # Credit Score Category
    # --------------------------------------------------

    credit_score_category = get_credit_score_category(
        applicant["credit_score"]
    )

    # --------------------------------------------------
    # Check Eligibility Conditions
    # --------------------------------------------------

    age_passed = (
        applicant["age"] >= loan["minimum_age"]
        and applicant["age"] <= loan["maximum_age"]
    )

    income_passed = (
        applicant["monthly_income"]
        >= loan["minimum_income"]
    )

    credit_score_passed = (
        applicant["credit_score"]
        >= loan["minimum_credit_score"]
    )

    dti_passed = (
        dti <= loan["maximum_dti"]
    )

    loan_amount_passed = (
        applicant["requested_loan_amount"]
        <= loan["maximum_loan_amount"]
    )

    # --------------------------------------------------
    # Failed Conditions
    # --------------------------------------------------

    failed_conditions = []

    if not age_passed:

        failed_conditions.append(
            f"Age requirement failed: applicant age is "
            f"{applicant['age']} years, but the permitted range is "
            f"{loan['minimum_age']} to {loan['maximum_age']} years."
        )

    if not income_passed:

        failed_conditions.append(
            f"Income requirement failed: monthly income is "
            f"{applicant['monthly_income']}, but the minimum required "
            f"income is {loan['minimum_income']}."
        )

    if not credit_score_passed:

        failed_conditions.append(
            f"Credit score requirement failed: applicant score is "
            f"{applicant['credit_score']}, but the minimum required "
            f"score is {loan['minimum_credit_score']}."
        )

    if not dti_passed:

        failed_conditions.append(
            f"DTI requirement failed: calculated DTI is {dti}%, "
            f"but the maximum permitted DTI is "
            f"{loan['maximum_dti']}%."
        )

    if not loan_amount_passed:

        failed_conditions.append(
            f"Loan amount requirement failed: requested amount is "
            f"{applicant['requested_loan_amount']}, but the maximum "
            f"permitted amount is {loan['maximum_loan_amount']}."
        )

    # --------------------------------------------------
    # Recommendations
    # --------------------------------------------------

    recommendations = []

    if not age_passed:

        recommendations.append(
            "Check another suitable loan product or contact the bank."
        )

    if not income_passed:

        recommendations.append(
            "Consider a lower loan amount or include a co-applicant."
        )

    if not credit_score_passed:

        recommendations.append(
            "Improve your credit score by making timely repayments."
        )

    if not dti_passed:

        recommendations.append(
            "Reduce your existing EMI obligations before applying again."
        )

    if not loan_amount_passed:

        recommendations.append(
            "Consider reducing the requested loan amount."
        )

    if not recommendations:

        recommendations.append(
            "No corrective recommendations are required at this stage."
        )

    # --------------------------------------------------
    # Required Documents
    # --------------------------------------------------

    required_documents = []

    # Common documents

    required_documents.extend(
        loan["required_documents"]["common"]
    )

    # Employment-specific documents

    employment_type = applicant["employment_type"]

    if employment_type == "Salaried":

        required_documents.extend(
            loan["required_documents"]["salaried"]
        )

    elif employment_type == "Self-Employed":

        required_documents.extend(
            loan["required_documents"]["self_employed"]
        )

    # Loan-specific documents

    required_documents.extend(
        loan["required_documents"]["additional"]
    )

    # --------------------------------------------------
    # Passed Conditions
    # --------------------------------------------------

    passed_conditions = []

    if age_passed:

        passed_conditions.append(
            f"Age requirement satisfied: applicant age is "
            f"{applicant['age']} years."
        )

    if income_passed:

        passed_conditions.append(
            f"Income requirement satisfied: monthly income is "
            f"{applicant['monthly_income']}."
        )

    if credit_score_passed:

        passed_conditions.append(
            f"Credit score requirement satisfied: applicant score is "
            f"{applicant['credit_score']} "
            f"({credit_score_category})."
        )

    if dti_passed:

        passed_conditions.append(
            f"DTI requirement satisfied: calculated DTI is {dti}%."
        )

    if loan_amount_passed:

        passed_conditions.append(
            f"Loan amount requirement satisfied: requested amount is "
            f"{applicant['requested_loan_amount']}."
        )

    # --------------------------------------------------
    # Next Steps
    # --------------------------------------------------

    next_steps = [
        "Prepare the required documents.",
        "Complete document, income, and credit verification.",
        "Continue with the formal loan application."
    ]

    # --------------------------------------------------
    # Disclaimer
    # --------------------------------------------------

    disclaimer = (
        "This is only a preliminary eligibility assessment "
        "based on synthetic demonstration rules. "
        "It does not represent final loan approval."
    )

    # --------------------------------------------------
    # Final Eligibility Status
    # --------------------------------------------------

    if (
        age_passed
        and income_passed
        and credit_score_passed
        and dti_passed
        and loan_amount_passed
    ):

        status = "Eligible"

    else:

        status = "Not Eligible"

    # --------------------------------------------------
    # Final Response
    # --------------------------------------------------

    return {
        "loan_type": applicant["loan_type"],
        "status": status,
        "calculated_dti": dti,
        "age_passed": age_passed,
        "income_passed": income_passed,
        "credit_score_passed": credit_score_passed,
        "credit_score_category": credit_score_category,
        "dti_passed": dti_passed,
        "loan_amount_passed": loan_amount_passed,
        "failed_conditions": failed_conditions,
        "recommendations": recommendations,
        "required_documents": required_documents,
        "next_steps": next_steps,
        "disclaimer": disclaimer,
        "passed_conditions": passed_conditions
    }
