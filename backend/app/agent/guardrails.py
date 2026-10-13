import re
from typing import Tuple, Optional

DISCLAIMER_TEXT = "\n\n*Disclaimer: Nutritional values and recommendations are estimates for educational and tracking purposes, not professional medical advice.*"

class Guardrails:
    EXTREME_CALORIE_PATTERN = re.compile(
        r"\b(?:eat(?:ing)?\s*(?:under|less than)?\s*([1-7]\d{2})\s*(?:calories|kcal))\b",
        re.IGNORECASE,
    )

    OFF_TOPIC_KEYWORDS = [
        "write python code to hack",
        "solve my calculus exam",
        "write a novel about space aliens",
        "stock market prediction",
    ]

    @staticmethod
    def inspect_request(message: str) -> Tuple[bool, Optional[str]]:
        """Validate user input before sending to LLM."""
        lower = message.lower()

        # Check for dangerous calorie restriction
        match = Guardrails.EXTREME_CALORIE_PATTERN.search(lower)
        if match:
            cals = match.group(1)
            return False, (
                f"Eating under {cals} kcal per day can be dangerous to your health and metabolic function. "
                "The minimum safe baseline for adults is typically 1,200 kcal for women and 1,500 kcal for men. "
                "Please consult a physician or registered dietitian before attempting severe caloric restriction."
            )

        # Basic off-topic detection
        for kw in Guardrails.OFF_TOPIC_KEYWORDS:
            if kw in lower:
                return False, (
                    "I am dedicated to helping you with nutrition, meal tracking, calorie counting, and healthy eating habits. "
                    "How can I assist you with your diet and health goals today?"
                )

        return True, None

    @staticmethod
    def attach_disclaimer(content: str) -> str:
        if "disclaimer" not in content.lower():
            return content + DISCLAIMER_TEXT
        return content
