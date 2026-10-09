
import re


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+?91[\s.-]?)?[6-9]\d{4}[\s.-]?\d{5}(?!\d)"
)

DATE_PATTERNS = [
    re.compile(
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"
    ),
    re.compile(
        r"\b\d{4}-\d{1,2}-\d{1,2}\b"
    ),
    re.compile(
        r"\b\d{1,2}\s+"
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|"
        r"May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|"
        r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
        r"\s+\d{4}\b",
        re.IGNORECASE
    ),
    re.compile(
        r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|"
        r"May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|"
        r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
        r"\s+\d{4}\b",
        re.IGNORECASE
    )
]


def extract_information(text):
    if not text:
        return {
            "emails": [],
            "phone_numbers": [],
            "dates": []
        }

    emails = list(dict.fromkeys(EMAIL_PATTERN.findall(text)))

    phones = []
    for match in PHONE_PATTERN.finditer(text):
        digits = re.sub(r"\D", "", match.group())
        if digits.startswith("91") and len(digits) == 12:
            digits = digits[2:]
        if len(digits) == 10 and digits[0] in "6789":
            if digits not in phones:
                phones.append(digits)

    dates = []
    for pattern in DATE_PATTERNS:
        for match in pattern.findall(text):
            if match not in dates:
                dates.append(match)

    return {
        "emails": emails,
        "phone_numbers": phones,
        "dates": dates
    }
