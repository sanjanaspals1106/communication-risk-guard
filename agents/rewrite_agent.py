"""Rewrite Agent - Suggests improved versions of risky messages."""

from .base_agent import BaseAgent


class RewriteAgent(BaseAgent):
    """Agent specialized in suggesting message improvements."""

    def __init__(self):
        super().__init__(prompt_file="rewrite.txt")

    def analyze(self, message: str, context: dict = None) -> dict:
        """
        Generate improved versions of a message.

        Args:
            message: The original message
            context: Dict with 'intent', 'emotion', and 'risk' analysis results

        Returns:
            dict: {
                "needs_rewrite": bool,
                "rewrites": [
                    {
                        "version": str (e.g., "professional", "friendly", "neutral"),
                        "rewritten_message": str,
                        "changes_made": list[str],
                        "tone_shift": str
                    }
                ],
                "specific_fixes": [
                    {
                        "original_phrase": str,
                        "suggested_phrase": str,
                        "reason": str
                    }
                ],
                "general_advice": str
            }
        """
        # Build context from other agents
        context_str = ""
        if context:
            if "intent" in context:
                context_str += f"\nDetected Intent: {context['intent'].get('primary_intent', 'unknown')}"
            if "emotion" in context:
                emo = context["emotion"]
                context_str += f"\nEmotional Tone: {emo.get('primary_emotion', 'unknown')} (intensity: {emo.get('intensity', 'unknown')})"
                if emo.get("emotional_leakage", {}).get("detected"):
                    context_str += f"\nEmotional Leakage: {emo['emotional_leakage'].get('explanation', '')}"
            if "risk" in context:
                risk = context["risk"]
                context_str += f"\nRisk Score: {risk.get('overall_risk_score', '?')}/10"
                red_flags = risk.get("red_flags", [])
                if red_flags:
                    flags = [f.get("phrase", "") for f in red_flags]
                    context_str += f"\nRed Flags: {', '.join(flags)}"

        prompt = self.prompt_template.format(message=message, context=context_str)
        response = self._call_api(prompt, max_tokens=1500)
        return self._parse_json_response(response)
