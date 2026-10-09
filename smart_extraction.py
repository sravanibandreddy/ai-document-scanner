
import re


def extract_information(text):
    """
    Extract email addresses, Indian mobile numbers,
    and common date formats from OCR text.
    """

    # Fix common OCR mistakes only in likely contact details
    text = text.replace("\u00a0", " ")

    # ---------------- EMAIL EXTRACTION ----------------
    email_pattern = re.compile(
        r"(?<![\w.+-])"
        r"[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
        r"(?![\w.-])"
    )

    emails = email_pattern.findall(text)

    # ---------------- MOBILE NUMBER EXTRACTION ----------------
    # Supports:
    # 9876543210
    # 98765 43210
    # 98765-43210
    # +91 9876543210
    # +91-98765-43210
    # (98765) 43210

    phone_pattern = re.compile(
        r"(?<!\d)"
        r"(?:\+?\s*91[\s().-]*)?"
        r"[6-9](?:[\s().-]*\d){9}"
        r"(?!\d)"
    )

    phone_candidates = phone_pattern.findall(text)

    phones = []

    for candidate in phone_candidates:
        digits = re.sub(r"\D", "", candidate)

        # Remove India's country code when present
        if len(digits) == 12 and digits.startswith("91"):
            digits = digits[2:]

        # Keep only valid-length Indian mobile candidates
        if (
            len(digits) == 10
            and digits[0] in "6789"
            and digits not in phones
        ):
            phones.append(digits)

    # ---------------- DATE EXTRACTION ----------------
    date_pattern = re.compile(
        r"\b(?:"
        r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"
        r"|"
        r"\d{4}[/-]\d{1,2}[/-]\d{1,2}"
        r"|"
        r"\d{1,2}\s+"
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|"
        r"Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|"
        r"Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|"
        r"Nov(?:ember)?|Dec(?:ember)?)"
        r"\s+\d{4}"
        r")\b",
        re.IGNORECASE
    )

    dates = date_pattern.findall(text)

    return {
        "emails": list(dict.fromkeys(emails)),
        "phone_numbers": phones,
        "dates": list(dict.fromkeys(dates))
    }
