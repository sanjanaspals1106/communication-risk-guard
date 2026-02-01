"""Intent Detection Agent - Analyzes the sender's underlying intent."""

from .base_agent import BaseAgent


class IntentAgent(BaseAgent):
    """Agent specialized in detecting communication intent."""

    def __init__(self):
        super().__init__(prompt_file="intent.txt")

    def analyze(self, message: str, context: dict = None) -> dict:
        """
        Analyze the intent behind a message.

        Returns:
            dict: {
                "primary_intent": str,
                "secondary_intents": list[str],
                "confidence": str (high/medium/low),
                "explanation": str,
                "hidden_agenda": str | None
            }
        """
        prompt = self.prompt_template.format(message=message)
        response = self._call_api(prompt)
        return self._parse_json_response(response)
