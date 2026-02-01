#!/usr/bin/env python3
"""
Communication Intent & Risk Guard
Main application orchestrating multi-agent analysis.
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from agents import IntentAgent, EmotionAgent, RiskAgent, RewriteAgent

console = Console()


class CommunicationGuard:
    """Orchestrates multi-agent message analysis."""

    def __init__(self):
        self.intent_agent = IntentAgent()
        self.emotion_agent = EmotionAgent()
        self.risk_agent = RiskAgent()
        self.rewrite_agent = RewriteAgent()

    def analyze(self, message: str, include_rewrite: bool = True) -> dict:
        """
        Run full analysis pipeline on a message.

        Pipeline:
        1. Intent Agent -> Detect sender's intent
        2. Emotion Agent -> Analyze emotional content
        3. Risk Agent -> Identify misinterpretation risks (uses intent + emotion context)
        4. Rewrite Agent -> Suggest improvements (uses all previous context)
        """
        results = {}

        # Stage 1: Intent Analysis
        console.print("  [dim]Analyzing intent...[/dim]")
        results["intent"] = self.intent_agent.analyze(message)

        # Stage 2: Emotion Analysis
        console.print("  [dim]Detecting emotions...[/dim]")
        results["emotion"] = self.emotion_agent.analyze(message)

        # Stage 3: Risk Assessment (with context from intent + emotion)
        console.print("  [dim]Assessing risks...[/dim]")
        results["risk"] = self.risk_agent.analyze(message, context={
            "intent": results["intent"],
            "emotion": results["emotion"]
        })

        # Stage 4: Rewrite Suggestions (with full context)
        if include_rewrite:
            risk_score = results["risk"].get("overall_risk_score", 0)
            if risk_score >= 4:  # Only suggest rewrites for risky messages
                console.print("  [dim]Generating suggestions...[/dim]")
                results["rewrite"] = self.rewrite_agent.analyze(message, context=results)

        return results


def get_risk_color(score: int) -> str:
    """Return color based on risk score."""
    if score <= 3:
        return "green"
    elif score <= 6:
        return "yellow"
    else:
        return "red"


def get_severity_style(severity: str) -> str:
    """Return style based on severity."""
    return {"low": "green", "medium": "yellow", "high": "red"}.get(severity.lower(), "white")


def display_results(message: str, results: dict):
    """Display analysis results in a formatted way."""

    # Header with risk score
    risk = results.get("risk", {})
    risk_score = risk.get("overall_risk_score", "?")
    risk_level = risk.get("risk_level", "unknown")
    risk_color = get_risk_color(risk_score) if isinstance(risk_score, int) else "white"

    console.print()
    console.print(Panel(
        f"[dim]{message[:100]}{'...' if len(message) > 100 else ''}[/dim]",
        title="[bold]Message Analyzed[/bold]",
        border_style="dim"
    ))

    console.print(Panel(
        f"[bold]Risk Score: [{risk_color}]{risk_score}/10[/{risk_color}][/bold] ({risk_level.upper()})",
        title="[bold blue]Analysis Results[/bold blue]",
        border_style="blue"
    ))

    # Intent Section
    intent = results.get("intent", {})
    if "error" not in intent:
        console.print()
        console.print("[bold cyan]Intent Detection[/bold cyan]")
        console.print(f"  Primary: [bold]{intent.get('primary_intent', 'Unknown')}[/bold]")
        secondary = intent.get("secondary_intents", [])
        if secondary:
            console.print(f"  Secondary: {', '.join(secondary)}")
        console.print(f"  Confidence: {intent.get('confidence', 'Unknown')}")
        console.print(f"  [dim]{intent.get('explanation', '')}[/dim]")
        if intent.get("hidden_agenda"):
            console.print(f"  [yellow]Hidden agenda:[/yellow] {intent['hidden_agenda']}")

    # Emotion Section
    emotion = results.get("emotion", {})
    if "error" not in emotion:
        console.print()
        console.print("[bold cyan]Emotional Analysis[/bold cyan]")
        console.print(
            f"  Primary: [bold]{emotion.get('primary_emotion', 'Unknown')}[/bold] "
            f"(intensity: {emotion.get('intensity', 'Unknown')})"
        )
        secondary = emotion.get("secondary_emotions", [])
        if secondary:
            console.print(f"  Secondary: {', '.join(secondary)}")
        tone = emotion.get("tone_descriptors", [])
        if tone:
            console.print(f"  Tone: {', '.join(tone)}")

        leakage = emotion.get("emotional_leakage", {})
        if leakage.get("detected"):
            console.print()
            console.print("  [yellow]Emotional Leakage Detected[/yellow]")
            leaked = leakage.get("leaked_emotions", [])
            if leaked:
                console.print(f"    Leaked emotions: {', '.join(leaked)}")
            indicators = leakage.get("indicators", [])
            for ind in indicators[:3]:
                console.print(f"    [dim]- \"{ind}\"[/dim]")
            console.print(f"    {leakage.get('explanation', '')}")

    # Risk Section
    if "error" not in risk:
        # Misinterpretation Risks
        risks_list = risk.get("misinterpretation_risks", [])
        if risks_list:
            console.print()
            console.print("[bold cyan]Misinterpretation Risks[/bold cyan]")

            risk_table = Table(box=box.ROUNDED, show_header=True, header_style="bold")
            risk_table.add_column("Risk", style="white", width=25)
            risk_table.add_column("Phrase", style="italic", width=20)
            risk_table.add_column("Prob", justify="center", width=8)
            risk_table.add_column("Impact", justify="center", width=8)

            for r in risks_list[:5]:
                prob = r.get("probability", "?")
                impact = r.get("impact", "?")
                risk_table.add_row(
                    r.get("risk", "")[:25],
                    f"\"{r.get('problematic_phrase', '')[:18]}\"",
                    Text(prob.upper(), style=get_severity_style(prob)),
                    Text(impact.upper(), style=get_severity_style(impact))
                )

            console.print(risk_table)

        # Red Flags
        red_flags = risk.get("red_flags", [])
        if red_flags:
            console.print()
            console.print("[bold red]Red Flags[/bold red]")

            for flag in red_flags[:5]:
                severity = flag.get("severity", "medium")
                console.print(
                    f"  [{get_severity_style(severity)}]●[/{get_severity_style(severity)}] "
                    f"[italic]\"{flag.get('phrase', '')}\"[/italic]"
                )
                console.print(f"    {flag.get('why_problematic', '')}")
                console.print(f"    [dim]Category: {flag.get('category', '')}[/dim]")

        # Ambiguities
        ambiguities = risk.get("ambiguities", [])
        if ambiguities:
            console.print()
            console.print("[bold yellow]Ambiguities[/bold yellow]")
            for amb in ambiguities[:3]:
                console.print(f"  - {amb}")

    # Rewrite Suggestions
    rewrite = results.get("rewrite", {})
    if rewrite and "error" not in rewrite and rewrite.get("needs_rewrite"):
        console.print()
        console.print("[bold green]Suggested Rewrites[/bold green]")

        for rw in rewrite.get("rewrites", [])[:2]:
            console.print(Panel(
                f"[green]{rw.get('rewritten_message', '')}[/green]\n\n"
                f"[dim]Tone: {rw.get('tone_shift', '')}[/dim]",
                title=f"[bold]{rw.get('version', 'Alternative').title()} Version[/bold]",
                border_style="green"
            ))

        # Specific fixes
        fixes = rewrite.get("specific_fixes", [])
        if fixes:
            console.print()
            console.print("[bold]Quick Fixes[/bold]")
            for fix in fixes[:3]:
                console.print(f"  [red]- \"{fix.get('original_phrase', '')}\"[/red]")
                console.print(f"  [green]+ \"{fix.get('suggested_phrase', '')}\"[/green]")
                console.print(f"    [dim]{fix.get('reason', '')}[/dim]")
                console.print()

        # General advice
        advice = rewrite.get("general_advice")
        if advice:
            console.print(f"[dim]Advice: {advice}[/dim]")


@click.command()
@click.option("--message", "-m", help="The message to analyze")
@click.option("--file", "-f", type=click.Path(exists=True), help="Read message from file")
@click.option("--interactive", "-i", is_flag=True, help="Interactive mode")
@click.option("--no-rewrite", is_flag=True, help="Skip rewrite suggestions")
def main(message: str, file: str, interactive: bool, no_rewrite: bool):
    """
    Communication Intent & Risk Guard

    A multi-agent system that analyzes messages for:
    - Intent detection
    - Emotional tone & leakage
    - Misinterpretation risks
    - Suggested rewrites
    """

    console.print(Panel(
        "[bold]Communication Intent & Risk Guard[/bold]\n"
        "[dim]Multi-agent pre-send analysis system[/dim]",
        border_style="blue"
    ))

    guard = CommunicationGuard()

    if interactive:
        console.print("[dim]Enter messages to analyze (Ctrl+C to exit):[/dim]\n")

        while True:
            try:
                console.print("[bold blue]Message>[/bold blue] ", end="")
                user_message = input()

                if user_message.lower() in ("quit", "exit", "q"):
                    break

                if not user_message.strip():
                    continue

                console.print()
                with console.status("[bold blue]Running analysis pipeline...[/bold blue]"):
                    results = guard.analyze(user_message, include_rewrite=not no_rewrite)

                display_results(user_message, results)
                console.print("\n" + "─" * 60 + "\n")

            except (EOFError, KeyboardInterrupt):
                console.print("\n[dim]Goodbye![/dim]")
                break

    elif file:
        with open(file, "r") as f:
            content = f.read().strip()

        # Handle multiple messages separated by ---
        messages = [m.strip() for m in content.split("---") if m.strip()]

        for i, msg in enumerate(messages, 1):
            if len(messages) > 1:
                console.print(f"\n[bold]Message {i}/{len(messages)}[/bold]")

            with console.status("[bold blue]Running analysis pipeline...[/bold blue]"):
                results = guard.analyze(msg, include_rewrite=not no_rewrite)

            display_results(msg, results)

            if i < len(messages):
                console.print("\n" + "═" * 60 + "\n")

    elif message:
        with console.status("[bold blue]Running analysis pipeline...[/bold blue]"):
            results = guard.analyze(message, include_rewrite=not no_rewrite)

        display_results(message, results)

    else:
        console.print("[yellow]Please provide a message using -m, -f, or -i[/yellow]")
        console.print("Use --help for usage information")


if __name__ == "__main__":
    main()
