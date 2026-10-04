import streamlit as st
import requests
import uuid


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Automated Loan Eligibility Chatbot",
    page_icon="🏦",
    layout="centered"
)


# --------------------------------------------------
# API Configuration
# --------------------------------------------------

CHAT_API_URL = "http://127.0.0.1:8000/chat"


# --------------------------------------------------
# Indian Currency Formatter
# --------------------------------------------------

def format_indian_currency(amount):
    amount = int(amount)
    s = str(amount)

    if len(s) <= 3:
        return s

    last_three = s[-3:]
    remaining = s[:-3]

    parts = []

    while len(remaining) > 2:
        parts.insert(0, remaining[-2:])
        remaining = remaining[:-2]

    if remaining:
        parts.insert(0, remaining)

    return ",".join(parts + [last_three])


# --------------------------------------------------
# Session State
# --------------------------------------------------

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "assessment" not in st.session_state:
    st.session_state.assessment = None


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("🏦 Automated Loan Eligibility Chatbot")

st.write(
    "Tell me about your loan requirement and I will "
    "help you understand your preliminary eligibility."
)

st.info(
    "This chatbot uses synthetic loan eligibility rules "
    "for demonstration purposes. The result does not "
    "represent final loan approval."
)


# --------------------------------------------------
# Start New Conversation
# --------------------------------------------------

if st.button("🔄 Start New Conversation"):

    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.assessment = None

    st.rerun()


# --------------------------------------------------
# Display Previous Messages
# --------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.write(message["content"])


# --------------------------------------------------
# Initial Bot Message
# --------------------------------------------------

if not st.session_state.messages:

    initial_message = (
        "Hello! 👋 I can help you check your preliminary "
        "loan eligibility.\n\n"
        "Which type of loan do you need?"
    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": initial_message
        }
    )

    with st.chat_message("assistant"):
        st.write(initial_message)


# --------------------------------------------------
# Chat Input
# --------------------------------------------------

user_message = st.chat_input(
    "Enter your loan requirements..."
)


if user_message:

    # --------------------------------------------------
    # Display User Message
    # --------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    with st.chat_message("user"):
        st.write(user_message)


    # --------------------------------------------------
    # Send Message to FastAPI
    # --------------------------------------------------

    try:

        with st.spinner("Understanding your requirements..."):

            response = requests.post(
                CHAT_API_URL,
                json={
                    "session_id": st.session_state.session_id,
                    "message": user_message
                },
                timeout=15
            )


        # --------------------------------------------------
        # Check API Response
        # --------------------------------------------------

        if response.status_code != 200:

            st.error(
                f"API Error: {response.status_code}"
            )

        else:

            data = response.json()


            # --------------------------------------------------
            # Response Time
            # --------------------------------------------------

            response_time = data.get(
                "response_time_seconds"
            )


            # --------------------------------------------------
            # Collecting Information
            # --------------------------------------------------

            if data.get("status") == "collecting_information":

                bot_message = data.get(
                    "message",
                    "Please provide the requested information."
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": bot_message
                    }
                )

                with st.chat_message("assistant"):

                    st.write(bot_message)

                    if response_time is not None:

                        st.caption(
                            f"Response time: {response_time} seconds"
                        )


            # --------------------------------------------------
            # Invalid Input
            # --------------------------------------------------

            elif data.get("status") == "invalid_input":

                bot_message = data.get(
                    "message",
                    "I could not understand your input."
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": bot_message
                    }
                )

                with st.chat_message("assistant"):

                    st.warning(bot_message)

                    if response_time is not None:

                        st.caption(
                            f"Response time: {response_time} seconds"
                        )


            # --------------------------------------------------
            # Assessment Completed
            # --------------------------------------------------

            elif data.get("status") == "assessment_completed":

                st.session_state.assessment = data

                result = data.get(
                    "eligibility_result",
                    {}
                )

                status = result.get(
                    "status",
                    "Unknown"
                )

                loan_type = result.get(
                    "loan_type",
                    "Not available"
                )

                dti = result.get(
                    "calculated_dti",
                    0
                )

                passed_conditions = result.get(
                    "passed_conditions",
                    []
                )

                failed_conditions = result.get(
                    "failed_conditions",
                    []
                )

                recommendations = result.get(
                    "recommendations",
                    []
                )

                required_documents = result.get(
                    "required_documents",
                    []
                )

                next_steps = result.get(
                    "next_steps",
                    []
                )

                disclaimer = result.get(
                    "disclaimer",
                    ""
                )

                collected_data = data.get(
                    "collected_data",
                    {}
                )

                credit_score = collected_data.get(
                    "credit_score"
                )

                monthly_income = collected_data.get(
                    "monthly_income"
                )

                existing_emi = collected_data.get(
                    "existing_emi"
                )

                requested_amount = collected_data.get(
                    "requested_loan_amount"
                )


                # --------------------------------------------------
                # Personalized Assistant Response
                # --------------------------------------------------

                if status == "Eligible":

                    bot_message = (
                        "Your preliminary loan eligibility "
                        "assessment is complete. 🟢\n\n"
                        f"Based on the information you provided, "
                        f"you are **preliminarily eligible for a "
                        f"{loan_type}.**\n\n"
                        "I have also provided the reasons, "
                        "required documents, and next steps below."
                    )

                else:

                    bot_message = (
                        "Your preliminary loan eligibility "
                        "assessment is complete. 🔴\n\n"
                        f"Based on the information you provided, "
                        f"you are **currently not eligible for a "
                        f"{loan_type}.**\n\n"
                        "I have listed the requirements that were "
                        "not satisfied and some recommendations below."
                    )


                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": bot_message
                    }
                )


                with st.chat_message("assistant"):

                    st.markdown(bot_message)

                    if response_time is not None:

                        st.caption(
                            f"Response time: {response_time} seconds"
                        )


                # --------------------------------------------------
                # Eligibility Result
                # --------------------------------------------------

                st.markdown("---")

                if status == "Eligible":

                    st.success(
                        f"🟢 Preliminary Eligibility: {status}"
                    )

                else:

                    st.error(
                        f"🔴 Preliminary Eligibility: {status}"
                    )


                # --------------------------------------------------
                # Applicant Information
                # --------------------------------------------------

                st.subheader("📋 Your Information")

                col1, col2 = st.columns(2)


                with col1:

                    st.write(
                        f"**Loan Type:** {loan_type}"
                    )

                    if monthly_income is not None:

                        st.write(
                            f"**Monthly Income:** "
                            f"₹{format_indian_currency(monthly_income)}"
                        )

                    if credit_score is not None:

                        st.write(
                            f"**Credit Score:** {credit_score}"
                        )


                with col2:

                    if requested_amount is not None:

                        st.write(
                            f"**Requested Amount:** "
                            f"₹{format_indian_currency(requested_amount)}"
                        )

                    if existing_emi is not None:

                        st.write(
                            f"**Existing EMI:** "
                            f"₹{format_indian_currency(existing_emi)}"
                        )

                    st.write(
                        f"**Calculated DTI:** {dti}%"
                    )


                # --------------------------------------------------
                # Why This Result?
                # --------------------------------------------------

                if status == "Eligible":

                    st.subheader(
                        "✅ Why You Are Eligible"
                    )

                    if passed_conditions:

                        for condition in passed_conditions:

                            st.write(
                                f"✓ {condition}"
                            )

                else:

                    st.subheader(
                        "❌ Requirements Not Satisfied"
                    )

                    if failed_conditions:

                        for condition in failed_conditions:

                            st.write(
                                f"• {condition}"
                            )

                    else:

                        st.write(
                            "No specific failed conditions were returned."
                        )


                # --------------------------------------------------
                # Recommendations
                # --------------------------------------------------

                if recommendations:

                    st.subheader(
                        "💡 Recommendations"
                    )

                    for recommendation in recommendations:

                        st.write(
                            f"• {recommendation}"
                        )


                # --------------------------------------------------
                # Required Documents
                # --------------------------------------------------

                st.subheader(
                    "📄 Required Documents"
                )

                if required_documents:

                    for document in required_documents:

                        st.write(
                            f"• {document}"
                        )


                # --------------------------------------------------
                # Next Steps
                # --------------------------------------------------

                st.subheader(
                    "🚀 What You Can Do Next"
                )

                if next_steps:

                    for index, step in enumerate(
                        next_steps,
                        start=1
                    ):

                        st.write(
                            f"{index}. {step}"
                        )


                # --------------------------------------------------
                # Performance
                # --------------------------------------------------

                if response_time is not None:

                    if response_time < 15:

                        st.caption(
                            f"⚡ Response time: "
                            f"{response_time} seconds"
                        )

                    else:

                        st.warning(
                            f"Response time: "
                            f"{response_time} seconds"
                        )


                # --------------------------------------------------
                # Disclaimer
                # --------------------------------------------------

                if disclaimer:

                    st.markdown("---")

                    st.caption(
                        disclaimer
                    )


    # --------------------------------------------------
    # Error Handling
    # --------------------------------------------------

    except requests.exceptions.Timeout:

        st.error(
            "The request took too long. "
            "Please try again."
        )

    except requests.exceptions.ConnectionError:

        st.error(
            "Could not connect to the FastAPI backend. "
            "Make sure the backend is running."
        )

    except Exception as e:

        st.error(
            f"Something went wrong: {str(e)}"
        )