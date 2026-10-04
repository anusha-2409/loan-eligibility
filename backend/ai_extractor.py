# import os
# import re
# import time
# from typing import Optional

# from dotenv import load_dotenv
# from google import genai
# from google.genai import types
# from pydantic import BaseModel

# from backend.normalizer import normalize_amount


# load_dotenv()


# # ---------------------------------------------------------
# # Pydantic model for extracted applicant data
# # ---------------------------------------------------------

# class ExtractedApplicantData(BaseModel):
#     loan_type: Optional[str] = None
#     age: Optional[int] = None
#     employment_type: Optional[str] = None
#     monthly_income: Optional[float] = None
#     credit_score: Optional[int] = None
#     existing_emi: Optional[float] = None
#     requested_loan_amount: Optional[float] = None


# # ---------------------------------------------------------
# # Local extraction
# # Used before Gemini so simple answers are handled quickly
# # ---------------------------------------------------------

# def local_extract(
#     message: str,
#     current_field: Optional[str] = None
# ):
#     data = {}

#     text = message.strip()
#     lower_text = text.lower()

#     # -----------------------------------------------------
#     # Loan Type
#     # -----------------------------------------------------

#     if (
#         "home loan" in lower_text
#         or "housing loan" in lower_text
#     ):
#         data["loan_type"] = "Home Loan"

#     elif "personal loan" in lower_text:
#         data["loan_type"] = "Personal Loan"

#     elif (
#         "vehicle loan" in lower_text
#         or "car loan" in lower_text
#         or "auto loan" in lower_text
#     ):
#         data["loan_type"] = "Vehicle Loan"

#     elif (
#         "education loan" in lower_text
#         or "student loan" in lower_text
#     ):
#         data["loan_type"] = "Education Loan"

#     elif "business loan" in lower_text:
#         data["loan_type"] = "Business Loan"

#     # Short answers such as:
#     # home / personal / vehicle / education / business

#     elif current_field == "loan_type":

#         if lower_text in ["home", "housing"]:
#             data["loan_type"] = "Home Loan"

#         elif lower_text in ["personal"]:
#             data["loan_type"] = "Personal Loan"

#         elif lower_text in ["vehicle", "car", "auto"]:
#             data["loan_type"] = "Vehicle Loan"

#         elif lower_text in ["education", "student"]:
#             data["loan_type"] = "Education Loan"

#         elif lower_text in ["business"]:
#             data["loan_type"] = "Business Loan"

#     # -----------------------------------------------------
#     # Employment Type
#     # -----------------------------------------------------

#     if current_field == "employment_type":

#         # Self-employed variations
#         if lower_text in [
#             "self",
#             "self employed",
#             "self-employed",
#             "selfemployed",
#             "business owner",
#             "business",
#             "owner"
#         ]:
#             data["employment_type"] = "Self-Employed"

#         # Salaried variations
#         elif lower_text in [
#             "salary",
#             "salaried",
#             "employee",
#             "job"
#         ]:
#             data["employment_type"] = "Salaried"

#     else:

#         # Detect employment type inside a complete sentence

#         if (
#             "self-employed" in lower_text
#             or "self employed" in lower_text
#             or "selfemployed" in lower_text
#             or "business owner" in lower_text
#         ):
#             data["employment_type"] = "Self-Employed"

#         elif "salaried" in lower_text:
#             data["employment_type"] = "Salaried"

#     # -----------------------------------------------------
#     # Age
#     # -----------------------------------------------------

#     age_match = re.search(
#         r"\b(?:age\s*(?:is|:)?\s*)?(\d{2})\s*(?:years?|yrs?)?\b",
#         lower_text
#     )

#     if age_match:
#         age = int(age_match.group(1))

#         if 18 <= age <= 100:
#             data["age"] = age

#     # If the current question is asking age,
#     # allow a simple answer like "30"

#     elif current_field == "age":

#         if lower_text.isdigit():

#             age = int(lower_text)

#             if 18 <= age <= 100:
#                 data["age"] = age

#     # -----------------------------------------------------
#     # Monthly Income
#     # -----------------------------------------------------

#     income_match = re.search(
#         r"(?:monthly\s+income|income|salary)"
#         r"\s*(?:is|:|=)?\s*"
#         r"(₹?\s*[\d,.]+\s*(?:lakh|crore|k|thousand)?)",
#         lower_text
#     )

#     if income_match:

#         try:
#             data["monthly_income"] = normalize_amount(
#                 income_match.group(1)
#             )
#         except (ValueError, TypeError):
#             pass

#     elif current_field == "monthly_income":

#         try:
#             data["monthly_income"] = normalize_amount(text)
#         except (ValueError, TypeError):
#             pass

#     # -----------------------------------------------------
#     # Credit Score
#     # -----------------------------------------------------

#     credit_match = re.search(
#         r"(?:credit\s+score|credit)"
#         r"\s*(?:is|:|=)?\s*(\d{3})",
#         lower_text
#     )

#     if credit_match:

#         score = int(credit_match.group(1))

#         if 300 <= score <= 900:
#             data["credit_score"] = score

#     elif current_field == "credit_score":

#         if lower_text.isdigit():

#             score = int(lower_text)

#             if 300 <= score <= 900:
#                 data["credit_score"] = score

#     # -----------------------------------------------------
#     # Existing EMI
#     # -----------------------------------------------------

#     if current_field == "existing_emi":

#         if lower_text in [
#             "e",
#             "no",
#             "no emi",
#             "zero",
#             "zero emi",
#             "none",
#             "nil"
#         ]:
#             data["existing_emi"] = 0

#         else:
#             try:
#                 data["existing_emi"] = normalize_amount(text)
#             except (ValueError, TypeError):
#                 pass

#     else:

#         emi_match = re.search(
#             r"(?:existing\s+emi|emi|current\s+emi)"
#             r"\s*(?:is|:|=)?\s*"
#             r"(₹?\s*[\d,.]+\s*(?:lakh|crore|k|thousand)?)",
#             lower_text
#         )

#         if emi_match:

#             try:
#                 data["existing_emi"] = normalize_amount(
#                     emi_match.group(1)
#                 )
#             except (ValueError, TypeError):
#                 pass

#         elif (
#             "no emi" in lower_text
#             or "zero emi" in lower_text
#             or "no current emi" in lower_text
#         ):
#             data["existing_emi"] = 0

#     # -----------------------------------------------------
#     # Requested Loan Amount
#     # -----------------------------------------------------

#     loan_amount_match = re.search(
#         r"(?:loan\s+amount|amount|loan)"
#         r"\s*(?:is|:|=)?\s*"
#         r"(₹?\s*[\d,.]+\s*(?:lakh|crore|k|thousand)?)",
#         lower_text
#     )

#     if loan_amount_match:

#         try:
#             data["requested_loan_amount"] = normalize_amount(
#                 loan_amount_match.group(1)
#             )
#         except (ValueError, TypeError):
#             pass

#     elif current_field == "requested_loan_amount":

#         try:
#             data["requested_loan_amount"] = normalize_amount(
#                 text
#             )
#         except (ValueError, TypeError):
#             pass

#     return data


# # ---------------------------------------------------------
# # Gemini AI extraction
# # ---------------------------------------------------------

# def extract_applicant_data(
#     message: str,
#     current_field: Optional[str] = None
# ):

#     start_time = time.time()

#     # First use local extraction
#     local_data = local_extract(
#         message,
#         current_field
#     )

#     print("LOCAL EXTRACTION:", local_data)

#     api_key = os.getenv("GEMINI_API_KEY")

#     # -----------------------------------------------------
#     # If API key is not available,
#     # use local extraction only
#     # -----------------------------------------------------

#     if not api_key:
#         print("GEMINI_API_KEY not found.")
#         return local_data

#     try:

#         client = genai.Client(
#             api_key=api_key
#         )

#         prompt = f"""
# You are an AI assistant extracting loan applicant information.

# Extract only the following fields:

# loan_type
# age
# employment_type
# monthly_income
# credit_score
# existing_emi
# requested_loan_amount

# Possible loan types:
# - Home Loan
# - Personal Loan
# - Vehicle Loan
# - Education Loan
# - Business Loan

# Possible employment types:
# - Salaried
# - Self-Employed

# Rules:

# 1. Do not invent missing information.
# 2. Return null for fields that are not present.
# 3. Convert lakh to rupees.
# 4. Convert crore to rupees.
# 5. Convert k to rupees.
# 6. Convert thousand to rupees.
# 7. "e", "no emi", "zero emi", "none" means existing_emi = 0.
# 8. If the user says "self", interpret it as Self-Employed.
# 9. If the user says "salary", "employee", or "salaried", interpret it as Salaried.
# 10. The current field being asked is: {current_field}

# User message:
# {message}
# """

#         response = client.models.generate_content(
#             model="gemini-3.8-flash",
#             contents=prompt,
#             config=types.GenerateContentConfig(
#                 temperature=0,
#                 response_mime_type="application/json",
#                 response_schema=ExtractedApplicantData,
#             )
#         )

#         ai_data = response.parsed

#         if ai_data is None:
#             print("Gemini returned no parsed data.")
#             return local_data

#         ai_data = ai_data.model_dump(
#             exclude_none=True
#         )

#         print("GEMINI EXTRACTION:", ai_data)

#         # -------------------------------------------------
#         # Merge local extraction with Gemini extraction
#         #
#         # Local extraction gets priority for values that
#         # are confidently detected.
#         # -------------------------------------------------

#         final_data = ai_data.copy()

#         for field, value in local_data.items():

#             if value is not None:
#                 final_data[field] = value

#         print("FINAL EXTRACTION:", final_data)

#         response_time = round(
#             time.time() - start_time,
#             2
#         )

#         print(
#             "AI EXTRACTION TIME:",
#             response_time,
#             "seconds"
#         )

#         return final_data

#     except Exception as e:

#         print(
#             "GEMINI EXTRACTION ERROR:",
#             repr(e)
#         )

#         # If Gemini fails, local extraction still works
#         return local_data





import os
import re
import time
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

from backend.normalizer import normalize_amount


load_dotenv()


# =========================================================
# Pydantic Model
# =========================================================

class ExtractedApplicantData(BaseModel):

    loan_type: Optional[str] = None
    age: Optional[int] = None
    employment_type: Optional[str] = None
    monthly_income: Optional[float] = None
    credit_score: Optional[int] = None
    existing_emi: Optional[float] = None
    requested_loan_amount: Optional[float] = None


# =========================================================
# LOCAL EXTRACTION
# =========================================================

def local_extract(
    message: str,
    current_field: Optional[str] = None
):
    """
    Local extraction for common loan-applicant inputs.

    This works as a fallback when Gemini is unavailable
    or when the API quota is exhausted.
    """

    data = {}

    text = message.strip()
    lower_text = text.lower()


    # =====================================================
    # Loan Type
    # =====================================================

    if (
        "home loan" in lower_text
        or "housing loan" in lower_text
    ):
        data["loan_type"] = "Home Loan"

    elif "personal loan" in lower_text:

        data["loan_type"] = "Personal Loan"

    elif (
        "vehicle loan" in lower_text
        or "car loan" in lower_text
        or "auto loan" in lower_text
    ):
        data["loan_type"] = "Vehicle Loan"

    elif (
        "education loan" in lower_text
        or "student loan" in lower_text
    ):
        data["loan_type"] = "Education Loan"

    elif "business loan" in lower_text:

        data["loan_type"] = "Business Loan"

    elif current_field == "loan_type":

        if lower_text in [
            "home",
            "housing"
        ]:
            data["loan_type"] = "Home Loan"

        elif lower_text == "personal":

            data["loan_type"] = "Personal Loan"

        elif lower_text in [
            "vehicle",
            "car",
            "auto"
        ]:
            data["loan_type"] = "Vehicle Loan"

        elif lower_text in [
            "education",
            "student"
        ]:
            data["loan_type"] = "Education Loan"

        elif lower_text == "business":

            data["loan_type"] = "Business Loan"


    # =====================================================
    # Employment Type
    # =====================================================

    if current_field == "employment_type":

        # Self-employed
        if lower_text in [
            "self",
            "self employed",
            "self-employed",
            "selfemployed",
            "business owner",
            "business",
            "owner"
        ]:

            data["employment_type"] = "Self-Employed"

        # Salaried
        elif lower_text in [
            "salary",
            "salaried",
            "employee",
            "job"
        ]:

            data["employment_type"] = "Salaried"

    else:

        # Self-employed inside a sentence
        if (
            "self-employed" in lower_text
            or "self employed" in lower_text
            or "selfemployed" in lower_text
            or "business owner" in lower_text
        ):

            data["employment_type"] = "Self-Employed"

        # Salaried inside a sentence
        elif (
            "salaried" in lower_text
            or "salaried employee" in lower_text
        ):

            data["employment_type"] = "Salaried"


    # =====================================================
    # AGE
    # =====================================================
    #
    # IMPORTANT:
    # Do NOT extract every 2-digit number as age.
    #
    # Example:
    # "I am 30 years old" -> age = 30
    #
    # "20 lakh" -> NOT age
    #
    # =====================================================

    age_match = re.search(
        r"\b(?:age\s*(?:is|:)?\s*|i\s*am\s+|i'm\s+)"
        r"(\d{2})"
        r"\s*(?:years?\s*old|years?|yrs?)?\b",
        lower_text
    )

    if age_match:

        age = int(
            age_match.group(1)
        )

        if 18 <= age <= 100:

            data["age"] = age

    elif current_field == "age":

        # Allow simple answer:
        # 30
        # 35
        # 42

        if lower_text.isdigit():

            age = int(lower_text)

            if 18 <= age <= 100:

                data["age"] = age


    # =====================================================
    # MONTHLY INCOME
    # =====================================================

    income_match = re.search(
        r"(?:monthly\s+income|income|salary)"
        r"\s*(?:is|:|=|of)?\s*"
        r"(₹?\s*[\d,.]+\s*"
        r"(?:lakh|crore|k|thousand)?)",
        lower_text
    )

    if income_match:

        try:

            data["monthly_income"] = normalize_amount(
                income_match.group(1)
            )

        except (
            ValueError,
            TypeError
        ):

            pass

    elif current_field == "monthly_income":

        try:

            data["monthly_income"] = normalize_amount(
                text
            )

        except (
            ValueError,
            TypeError
        ):

            pass


    # =====================================================
    # CREDIT SCORE
    # =====================================================

    credit_match = re.search(
        r"(?:credit\s+score|credit)"
        r"\s*(?:is|:|=|of)?\s*"
        r"(\d{3})",
        lower_text
    )

    if credit_match:

        score = int(
            credit_match.group(1)
        )

        if 300 <= score <= 900:

            data["credit_score"] = score

    elif current_field == "credit_score":

        if lower_text.isdigit():

            score = int(
                lower_text
            )

            if 300 <= score <= 900:

                data["credit_score"] = score


    # =====================================================
    # EXISTING EMI
    # =====================================================

    if current_field == "existing_emi":

        # Examples:
        # e
        # no
        # none
        # no emi
        # zero emi

        if lower_text in [
            "e",
            "no",
            "none",
            "nil",
            "zero",
            "no emi",
            "zero emi",
            "no current emi"
        ]:

            data["existing_emi"] = 0

        else:

            try:

                data["existing_emi"] = normalize_amount(
                    text
                )

            except (
                ValueError,
                TypeError
            ):

                pass

    else:

        emi_match = re.search(
            r"(?:existing\s+emi|current\s+emi|monthly\s+emi)"
            r"\s*(?:is|:|=|of)?\s*"
            r"(₹?\s*[\d,.]+\s*"
            r"(?:lakh|crore|k|thousand)?)",
            lower_text
        )

        if emi_match:

            try:

                data["existing_emi"] = normalize_amount(
                    emi_match.group(1)
                )

            except (
                ValueError,
                TypeError
            ):

                pass

        elif (
            "no emi" in lower_text
            or "zero emi" in lower_text
            or "no current emi" in lower_text
        ):

            data["existing_emi"] = 0


    # =====================================================
    # REQUESTED LOAN AMOUNT
    # =====================================================

    loan_amount_match = re.search(
        r"(?:loan\s+amount|loan\s+of|loan\s+for|amount)"
        r"\s*(?:is|:|=|of)?\s*"
        r"(₹?\s*[\d,.]+\s*"
        r"(?:lakh|crore|k|thousand)?)",
        lower_text
    )

    if loan_amount_match:

        try:

            data["requested_loan_amount"] = normalize_amount(
                loan_amount_match.group(1)
            )

        except (
            ValueError,
            TypeError
        ):

            pass

    elif current_field == "requested_loan_amount":

        try:

            data["requested_loan_amount"] = normalize_amount(
                text
            )

        except (
            ValueError,
            TypeError
        ):

            pass


    return data


# =========================================================
# GEMINI EXTRACTION
# =========================================================

def extract_applicant_data(
    message: str,
    current_field: Optional[str] = None
):

    start_time = time.time()


    # =====================================================
    # STEP 1: LOCAL EXTRACTION
    # =====================================================

    local_data = local_extract(
        message,
        current_field
    )

    print(
        "LOCAL EXTRACTION:",
        local_data
    )


    # =====================================================
    # STEP 2: CHECK GEMINI API KEY
    # =====================================================

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:

        print(
            "GEMINI_API_KEY not found."
        )

        print(
            "Using local extraction."
        )

        return local_data


    # =====================================================
    # STEP 3: GEMINI CLIENT
    # =====================================================

    try:

        client = genai.Client(
            api_key=api_key
        )


        # =================================================
        # GEMINI PROMPT
        # =================================================

        prompt = f"""
You are an AI assistant that extracts loan applicant
information from natural language.

Extract only the following fields:

loan_type
age
employment_type
monthly_income
credit_score
existing_emi
requested_loan_amount

Supported loan types:

Home Loan
Personal Loan
Vehicle Loan
Education Loan
Business Loan

Supported employment types:

Salaried
Self-Employed

Conversion rules:

75k = 75000
60k = 60000
10 lakh = 1000000
25 lakh = 2500000
1 crore = 10000000
no EMI = 0
zero EMI = 0
none = 0
e = 0

Important rules:

1. Extract only information clearly provided by the user.

2. Never guess missing information.

3. Return null for fields that are not provided.

4. A number followed by "lakh", "crore", "k",
   or "thousand" is a monetary amount, NOT age.

5. Age should only be extracted when the user clearly
   refers to age, for example:
   "I am 30 years old"
   "I am 30"
   "age is 30"
   "my age is 30"

6. If the user says "self", use Self-Employed.

7. If the user says "salary", "employee", or "salaried",
   use Salaried.

8. Extract all clearly provided fields from the message.

Current field being requested:

{current_field}

User message:

{message}
"""


        # =================================================
        # GEMINI API CALL
        # =================================================

        response = client.models.generate_content(

            model="gemini-3.8-flash",

            contents=prompt,

            config=types.GenerateContentConfig(

                temperature=0,

                response_mime_type="application/json",

                response_schema=ExtractedApplicantData
            )
        )


        # =================================================
        # GET PARSED GEMINI DATA
        # =================================================

        ai_data = response.parsed


        if ai_data is None:

            print(
                "Gemini returned no parsed data."
            )

            print(
                "Using local extraction."
            )

            return local_data


        ai_data = ai_data.model_dump(
            exclude_none=True
        )


        print(
            "GEMINI EXTRACTION:",
            ai_data
        )


        # =================================================
        # STEP 4: MERGE DATA
        # =================================================
        #
        # Local extraction gets priority because it handles
        # simple values such as:
        #
        # 30 years old
        # 20 lakh
        # 580
        # 10k
        # e
        #
        # This also prevents the old age bug.
        # =================================================

        final_data = ai_data.copy()


        for field, value in local_data.items():

            if value is not None:

                final_data[field] = value


        print(
            "FINAL EXTRACTION:",
            final_data
        )


        # =================================================
        # RESPONSE TIME
        # =================================================

        response_time = round(
            time.time() - start_time,
            2
        )

        print(
            "AI EXTRACTION TIME:",
            response_time,
            "seconds"
        )


        return final_data


    # =====================================================
    # GEMINI ERROR
    # =====================================================

    except Exception as e:

        print(
            "GEMINI EXTRACTION ERROR:",
            repr(e)
        )

        print(
            "Using local extraction."
        )

        return local_data