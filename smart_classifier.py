import re


DOCUMENT_KEYWORDS = {
    "Resume": [
        "resume", "curriculum vitae", "work experience",
        "professional experience", "education", "skills",
        "career objective"
    ],
    "Invoice": [
        "invoice", "invoice number", "bill to",
        "amount due", "subtotal", "tax", "payment due"
    ],
    "Receipt": [
        "receipt", "cashier", "transaction id",
        "payment received", "items purchased",
        "change due", "thank you for shopping"
    ],
    "Academic Document": [
        "student name", "roll number", "semester",
        "university", "examination", "marks obtained",
        "grade point average"
    ],
    "Business Letter": [
        "dear sir", "dear madam", "dear mr",
        "dear ms", "yours sincerely", "yours faithfully",
        "subject:"
    ],
    "Identity Document": [
        "date of birth", "identity number",
        "identification number", "passport number",
        "place of birth", "nationality"
    ],
}


def classify_document(text: str) -> dict:
    """
    Classify a document using keyword matching.

    Returns the predicted document type and a confidence
    score based on the relative keyword matches.
    """

    if not text or not text.strip():
        return {
            "document_type": "Unknown",
            "confidence": 0,
            "message": "No text available to classify."
        }

    normalized_text = re.sub(
        r"\s+",
        " ",
        text.lower()
    )

    scores = {}

    for document_type, keywords in DOCUMENT_KEYWORDS.items():
        score = 0

        for keyword in keywords:
            pattern = (
                r"(?<!\w)"
                + re.escape(keyword.lower())
                + r"(?!\w)"
            )

            if re.search(pattern, normalized_text):
                score += 1

        scores[document_type] = score

    best_type = max(scores, key=scores.get)
    best_score = scores[best_type]
    total_matches = sum(scores.values())

    if best_score == 0:
        return {
            "document_type": "Other",
            "confidence": 0,
            "message": "No matching document keywords were found."
        }

    confidence = round(
        100 * best_score / total_matches
    )

    return {
        "document_type": best_type,
        "confidence": confidence,
        "message": (
            f"Matched {best_score} keywords for {best_type}."
        )
    }
