def normalize_amount(value):

    value = (
        value.lower()
        .replace(",", "")
        .replace("₹", "")
        .strip()
    )

    if "crore" in value:
        number = float(
            value.replace("crore", "").strip()
        )
        return int(number * 10000000)

    if "lakh" in value:
        number = float(
            value.replace("lakh", "").strip()
        )
        return int(number * 100000)

    if "thousand" in value:
        number = float(
            value.replace("thousand", "").strip()
        )
        return int(number * 1000)

    if value.endswith("k"):
        number = float(
            value.replace("k", "").strip()
        )
        return int(number * 1000)

    if value in ["no emi", "zero emi", "none"]:
        return 0

    return int(float(value))