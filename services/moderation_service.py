BAD_WORDS = {
    "hate",
    "racist",
    "kill",
    "terrorist"
}


class ModerationService:

    @staticmethod
    def is_flagged(text: str) -> bool:

        text = text.lower()

        return any(
            word in text
            for word in BAD_WORDS
        )

    @staticmethod
    def review(text: str):

        flagged = ModerationService.is_flagged(text)

        return {
            "flagged": flagged
        }