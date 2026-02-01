"""Base agent class for all specialized agents."""

import json
import os
from pathlib import Path
from groq import Groq


class BaseAgent:
    """Base class for specialized analysis agents."""

    def __init__(self, prompt_file: str, model: str = "llama-3.3-70b-versatile"):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.model = model
        self.prompt_template = self._load_prompt(prompt_file)

    def _load_prompt(self, prompt_file: str) -> str:
        """Load prompt template from file."""
        prompts_dir = Path(__file__).parent.parent / "prompts"
        prompt_path = prompts_dir / prompt_file

        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        return prompt_path.read_text()

    def _parse_json_response(self, response_text: str) -> dict:
        """Parse JSON from response, handling markdown code blocks."""
        text = response_text.strip()

        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]

        try:
            return json.loads(text.strip())
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse response: {e}", "raw": response_text}

    def analyze(self, message: str, context: dict = None) -> dict:
        """Run analysis on the message. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement analyze()")

    def _call_api(self, prompt: str, max_tokens: int = 1000) -> str:
        """Make API call to Groq."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
