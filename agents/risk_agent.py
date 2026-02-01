"""Risk Assessment Agent - Identifies misinterpretation risks and red flags."""

from .base_agent import BaseAgent


class RiskAgent(BaseAgent):
    """Agent specialized in identifying communication risks."""

    def __init__(self):
        super().__init__(prompt_file="risk.txt")

    def analyze(self, message: str, context: dict = None) -> dict:
        """
        Analyze misinterpretation risks in a message.

        Args:
            message: The message to analyze
            context: Optional dict with 'intent' and 'emotion' analysis results

        Returns:
            dict: {
                "overall_risk_score": int (1-10),
                "risk_level": str (low/medium/high/critical),
                "misinterpretation_risks": [
                    {
                        "risk": str,
                        "probability": str (low/medium/high),
                        "impact": str (low/medium/high),
                        "problematic_phrase": str,
                        "explanation": str
                    }
                ],
                "red_flags": [
                    {
                        "phrase": str,
                        "category": str,
                        "severity": str,
                        "why_problematic": str
                    }
                ],
                "missing_context": list[str],
                "ambiguities": list[str]
            }
        """
        # Include context from other agents if available
        context_str = ""
        if context:
            if "intent" in context:
                context_str += f"\nIntent Analysis: {context['intent']}"
            if "emotion" in context:
                context_str += f"\nEmotion Analysis: {context['emotion']}"

        prompt = self.prompt_template.format(message=message, context=context_str)
        response = self._call_api(prompt, max_tokens=1500)
        return self._parse_json_response(response)
