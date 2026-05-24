from __future__ import annotations


class LegalResourceAgent:
    async def run(self, user_message: str, memory_context: dict, retrieval_context: list[dict]) -> dict:
        resources = [
            {"name": "UKCISA", "type": "legal_advice", "contact": "https://www.ukcisa.org.uk"},
            {
                "name": "OISC Adviser Finder",
                "type": "legal_advice",
                "contact": "https://www.gov.uk/find-an-immigration-adviser",
            },
        ]
        if retrieval_context:
            resources.append(
                {
                    "name": "Policy References",
                    "type": "citations",
                    "contact": ", ".join(ctx.get("citation", "") for ctx in retrieval_context[:3]),
                }
            )
        return {"legal_resources": resources, "analysis": "Legal and policy resources assembled."}

