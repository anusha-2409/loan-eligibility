from backend.normalizer import normalize_amount


def test_thousand_format():

    assert normalize_amount("75k") == 75000


def test_lakh_format():

    assert normalize_amount("25 lakh") == 2500000


def test_decimal_lakh_format():

    assert normalize_amount("1.5 lakh") == 150000


def test_crore_format():

    assert normalize_amount("1 crore") == 10000000


def test_rupee_and_comma_format():

    assert normalize_amount("₹60,000") == 60000


def test_no_emi_format():

    assert normalize_amount("no EMI") == 0