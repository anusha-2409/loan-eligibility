from typing import Literal

from pydantic import BaseModel, Field


# Supported loan products
LoanType = Literal[
    "Home Loan",
    "Personal Loan",
    "Vehicle Loan",
    "Education Loan",
    "Business Loan"
]


# Supported employment categories
EmploymentType = Literal[
    "Salaried",
    "Self-Employed"
]


class ApplicantRequest(BaseModel):
    """
    Represents applicant information received by the loan eligibility API.
    """

    loan_type: LoanType

    age: int = Field(
        ge=18,
        le=100,
        description="Applicant age"
    )

    employment_type: EmploymentType

    monthly_income: float = Field(
        gt=0,
        description="Applicant monthly income"
    )

    credit_score: int = Field(
        ge=300,
        le=900,
        description="Applicant credit score"
    )

    existing_emi: float = Field(
        ge=0,
        description="Existing monthly EMI obligations"
    )

    requested_loan_amount: float = Field(
        gt=0,
        description="Requested loan amount"
    )


class LoanDocuments(BaseModel):
    """
    Represents document requirements for a loan product.
    """

    common: list[str]
    salaried: list[str]
    self_employed: list[str]
    additional: list[str]


class LoanRule(BaseModel):
    """
    Represents one loan product and its eligibility rules
    loaded from loans.json.
    """

    loan_type: LoanType
    minimum_age: int
    maximum_age: int
    minimum_income: float
    minimum_credit_score: int
    maximum_loan_amount: float
    interest_rate: float
    maximum_dti: float
    required_documents: LoanDocuments


class EligibilityResponse(BaseModel):
    """
    Represents the final eligibility assessment returned
    by the FastAPI backend.
    """
    loan_type: str
    status: Literal["Eligible", "Not Eligible"]
    calculated_dti: float
    passed_conditions: list[str]
    failed_conditions: list[str]
    recommendations: list[str]
    required_documents: list[str]
    next_steps: list[str]
    disclaimer: str


class ChatRequest(BaseModel):
    session_id: str
    message: str