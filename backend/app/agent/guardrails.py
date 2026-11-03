import re
from typing import Tuple, Optional

DISCLAIMER_TEXT = "\n\nDisclaimer: Nutritional values and recommendations are estimates for educational and tracking purposes, not professional medical advice."

class Guardrails:
    # Pattern detecting severe restriction requests like "eat 500 calories a day", "diet on 400 kcal daily", "limit to 600 calories"
    EXTREME_CALORIE_PATTERN = re.compile(
        r"\b(?:eat(?:ing)?|diet(?:ing)?|consume|limit\s+(?:myself\s+)?to|restrict\s+(?:myself\s+)?to|starve\s+on)\s*(?:only\s+)?(?:under|less than)?\s*([1-7]\d{2})\s*(?:calories|kcal)(?:\s*(?:a|per)\s*day|\s*daily|\s*to\s*lose\s*weight)?\b",
        re.IGNORECASE,
    )

    MEDICAL_CLAIM_PATTERN = re.compile(
        r"\b(?:cure\s+(?:cancer|diabetes|kidney\s+disease|heart\s+disease)|stop\s+(?:taking\s+)?insulin|replace\s+(?:chemo|chemotherapy|medication))\b",
        re.IGNORECASE,
    )

    OFF_TOPIC_KEYWORDS = [
        "write python code to hack",
        "solve my calculus exam",
        "write a novel about space aliens",
        "stock market prediction",
        "write an essay on politics",
        "generate a bash exploit",
    ]

    @staticmethod
    def inspect_request(message: Optional[str], image_id: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """Validate user input before sending to LLM."""
        clean_text = (message or "").strip()

        # Handle empty/invalid input: if no text and no image, reject
        if not clean_text and not image_id:
            return False, "Please enter a message or upload an image to get started."

        # If it's an image-only message, allow it safely
        if not clean_text and image_id:
            return True, None

        lower = clean_text.lower()

        # Check for dangerous calorie restriction
        match = Guardrails.EXTREME_CALORIE_PATTERN.search(lower)
        if match:
            cals = match.group(1)
            return False, (
                f"Eating under {cals} kcal per day can be dangerous to your health and metabolic function. "
                "Safe caloric baselines depend on individual biometrics and activity levels (typically at least 1,200 kcal/day for women and 1,500 kcal/day for men). "
                "Please consult a physician or registered dietitian before attempting severe caloric restriction."
            )

        # Check for dangerous unsupported medical claims
        if Guardrails.MEDICAL_CLAIM_PATTERN.search(lower):
            return False, (
                "Nutrition and diet support overall wellness, but dietary changes cannot replace prescribed medical treatments for serious conditions. "
                "Please consult your physician or healthcare team for medical care and before making changes to prescribed treatments."
            )

        # Off-topic detection
        for kw in Guardrails.OFF_TOPIC_KEYWORDS:
            if kw in lower:
                return False, (
                    "I am dedicated to helping you with nutrition, meal tracking, calorie counting, and healthy eating habits. "
                    "How can I assist you with your diet and health goals today?"
                )

        return True, None

    @staticmethod
    def attach_disclaimer(content: str) -> str:
        if not content:
            return content
        if "disclaimer" not in content.lower():
            return content + DISCLAIMER_TEXT
        return content
