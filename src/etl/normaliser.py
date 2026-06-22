import re

MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
}


def normalize_year(raw_year):
    if raw_year is None:
        return None

    text = str(raw_year).strip()

    if text == "" or text.lower() == "nan":
        return None

    if text.upper() == "TTM":
        return "TTM"

    if re.fullmatch(r"\d{4}(\.\d+)?", text):
        return int(float(text))

    match = re.fullmatch(r"([A-Za-z]{3})-(\d{2})", text)
    if match:
        month_str, yy = match.groups()
        year = 2000 + int(yy)
        return year

    match = re.match(r"([A-Za-z]{3})\s+(\d{4})", text)
    if match:
        month_str, yyyy = match.groups()
        return int(yyyy)

    match = re.search(r"(\d{4})", text)
    if match:
        return int(match.group(1))

    return None


def normalize_ticker(raw_ticker):
    if raw_ticker is None:
        return None

    text = str(raw_ticker).strip()

    if text == "" or text.lower() == "nan":
        return None

    text = text.upper()
    text = re.sub(r"\s+", "", text)

    return text
