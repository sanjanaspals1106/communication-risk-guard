"""Emotion Detection Agent - Analyzes emotional tone and leakage."""

from .base_agent import BaseAgent


class EmotionAgent(BaseAgent):
    """Agent specialized in detecting emotional content and leakage."""

    def __init__(self):
        super().__init__(prompt_file="emotion.txt")

    def analyze(self, message: str, context: dict = None) -> dict:
        """
        Analyze the emotional content of a message.

        Returns:
            dict: {
                "primary_emotion": str,
                "intensity": str (low/medium/high),
                "secondary_emotions": list[str],
                "emotional_leakage": {
                    "detected": bool,
                    "leaked_emotions": list[str],
                    "indicators": list[str],
                    "explanation": str
                },
                "tone_descriptors": list[str]
            }
        """
        prompt = self.prompt_template.format(message=message)
        response = self._call_api(prompt)
        return self._parse_json_response(response)
