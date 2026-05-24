from __future__ import annotations


class ScamDetectionAgent:
    async def run(self, user_message: str, memory_context: dict) -> dict:
        text = user_message.lower()
        patterns = [
            "wire transfer",
            "upfront fee",
            "cash in hand",
            "whatsapp only",
            "limited time",
            "urgent payment",
            "gift card",
        ]
        hits = [pattern for pattern in patterns if pattern in text]
        signal = min(100, len(hits) * 18 + (20 if "visa" in text and "pay" in text else 0))
        return {"scam_signal": signal, "red_flags": hits, "analysis": "Scam and fraud patterns analyzed."}

