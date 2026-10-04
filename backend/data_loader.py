import json


def load_loans():

    with open("data/loans.json", "r") as file:
        loans = json.load(file)

    return loans


def get_loan_by_type(loan_type):

    loans = load_loans()

    for loan in loans:

        if loan["loan_type"].lower() == loan_type.lower():
            return loan

    return None