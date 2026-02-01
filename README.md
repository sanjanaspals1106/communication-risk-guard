# Communication Intent & Risk Guard

A multi-agent AI system that analyzes messages before you send them to detect intent, emotional leakage, and misinterpretation risk — and explains why.

## Architecture

```
communication-risk-guard/
├── agents/
│   ├── base_agent.py      # Base class with shared functionality
│   ├── intent_agent.py    # Detects communication intent
│   ├── emotion_agent.py   # Analyzes emotional tone & leakage
│   ├── risk_agent.py      # Identifies misinterpretation risks
│   └── rewrite_agent.py   # Suggests improved versions
├── prompts/
│   ├── intent.txt         # Intent detection prompt
│   ├── emotion.txt        # Emotion analysis prompt
│   ├── risk.txt           # Risk assessment prompt
│   └── rewrite.txt        # Rewrite suggestion prompt
├── examples/
│   ├── low_risk.txt       # Safe message examples
│   └── high_risk.txt      # Risky message examples
├── app.py                 # Main CLI orchestrator
└── requirements.txt
```

## Multi-Agent Pipeline

The system uses 4 specialized agents that work in sequence:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Intent    │────▶│   Emotion   │────▶│    Risk     │────▶│   Rewrite   │
│    Agent    │     │    Agent    │     │    Agent    │     │    Agent    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
      │                   │                   │                    │
      ▼                   ▼                   ▼                    ▼
 What are you       How do you          How could this       How can you
 trying to do?      really feel?        go wrong?            say it better?
```

Each agent builds on the previous analysis, creating a comprehensive understanding of the message.

## Setup

1. Install dependencies:
```bash
cd communication-risk-guard
pip install -r requirements.txt
```

2. Set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY=your-api-key-here
```

## Usage

### Analyze a single message
```bash
python app.py -m "Fine. I guess I'll just do it myself."
```

### Interactive mode
```bash
python app.py -i
```

### Analyze from file
```bash
python app.py -f examples/high_risk.txt
```

### Skip rewrite suggestions
```bash
python app.py -m "Your message here" --no-rewrite
```

## What Each Agent Detects

### Intent Agent
- Primary intent (request, inform, persuade, vent, confront, etc.)
- Secondary intents
- Hidden agendas
- Confidence level

### Emotion Agent
- Primary emotion and intensity
- Secondary emotions
- **Emotional leakage** - unintended emotions showing through:
  - Excessive punctuation
  - Passive-aggressive phrasing
  - Sarcasm markers
  - Unusual formality

### Risk Agent
- Overall risk score (1-10)
- Misinterpretation risks with probability & impact
- Red flags:
  - Passive-aggressive language
  - Ambiguous statements
  - Loaded/accusatory words
  - Missing context
- Specific ambiguities

### Rewrite Agent
- Multiple rewrite versions (professional, friendly, neutral)
- Specific phrase-level fixes
- General communication advice

## Example Output

```
╭─────────────────────── Message Analyzed ────────────────────────╮
│ Fine. I guess I'll just do it myself since nobody else seems... │
╰─────────────────────────────────────────────────────────────────╯
╭─────────────────────── Analysis Results ────────────────────────╮
│ Risk Score: 8/10 (HIGH)                                         │
╰─────────────────────────────────────────────────────────────────╯

Intent Detection
  Primary: Vent/Confront
  Secondary: deflect, manipulate
  Hidden agenda: Inducing guilt in the recipient

Emotional Analysis
  Primary: Frustration (intensity: high)
  Secondary: resentment, disappointment
  Tone: passive-aggressive, martyred, bitter

  Emotional Leakage Detected
    Leaked emotions: anger, resentment
    - "Fine."
    - "I guess"
    - "nobody else seems to care"

Red Flags
  ● "Fine."
    Single-word response indicating suppressed anger
    Category: passive-aggressive

  ● "nobody else seems to care"
    Accusatory generalization, induces guilt
    Category: loaded

Suggested Rewrites
╭─────────────────── Professional Version ────────────────────────╮
│ I'll take care of this task. In the future, it would help if   │
│ we could clarify task ownership earlier in the process.         │
│                                                                 │
│ Tone: Assertive but non-accusatory                              │
╰─────────────────────────────────────────────────────────────────╯
```

## Customizing Prompts

Edit the files in `prompts/` to customize agent behavior:

- `intent.txt` - Modify intent categories or detection criteria
- `emotion.txt` - Add emotion categories or leakage indicators
- `risk.txt` - Adjust risk categories or scoring criteria
- `rewrite.txt` - Change rewrite styles or guidelines

## License

MIT
