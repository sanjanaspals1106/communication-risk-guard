"""
Communication Intent & Risk Guard - Streamlit Web Interface
"""

import streamlit as st
from agents import IntentAgent, EmotionAgent, RiskAgent, RewriteAgent


st.set_page_config(
    page_title="Communication Risk Guard",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .risk-score-low { color: #28a745; font-size: 2em; font-weight: bold; }
    .risk-score-medium { color: #ffc107; font-size: 2em; font-weight: bold; }
    .risk-score-high { color: #dc3545; font-size: 2em; font-weight: bold; }
    .red-flag { background-color: #ffe6e6; padding: 10px; border-radius: 5px; margin: 5px 0; }
    .suggestion { background-color: #e6ffe6; padding: 15px; border-radius: 5px; margin: 10px 0; }
    .leakage-warning { background-color: #fff3e6; padding: 10px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_agents():
    """Load agents once and cache them."""
    return {
        "intent": IntentAgent(),
        "emotion": EmotionAgent(),
        "risk": RiskAgent(),
        "rewrite": RewriteAgent()
    }


def get_risk_color(score: int) -> str:
    """Return color class based on risk score."""
    if score <= 3:
        return "low"
    elif score <= 6:
        return "medium"
    return "high"


def run_analysis(message: str, agents: dict) -> dict:
    """Run the full analysis pipeline."""
    results = {}

    # Intent Analysis
    results["intent"] = agents["intent"].analyze(message)

    # Emotion Analysis
    results["emotion"] = agents["emotion"].analyze(message)

    # Risk Assessment
    results["risk"] = agents["risk"].analyze(message, context={
        "intent": results["intent"],
        "emotion": results["emotion"]
    })

    # Rewrite Suggestions (only for risky messages)
    risk_score = results["risk"].get("overall_risk_score", 0)
    if risk_score >= 4:
        results["rewrite"] = agents["rewrite"].analyze(message, context=results)

    return results


def display_intent(intent: dict):
    """Display intent analysis results."""
    if "error" in intent:
        st.error(f"Intent analysis error: {intent['error']}")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Primary Intent", intent.get("primary_intent", "Unknown"))

    with col2:
        st.metric("Confidence", intent.get("confidence", "Unknown").upper())

    secondary = intent.get("secondary_intents", [])
    if secondary:
        st.write(f"**Secondary intents:** {', '.join(secondary)}")

    st.write(f"*{intent.get('explanation', '')}*")

    if intent.get("hidden_agenda"):
        st.warning(f"⚠️ **Hidden Agenda Detected:** {intent['hidden_agenda']}")


def display_emotion(emotion: dict):
    """Display emotion analysis results."""
    if "error" in emotion:
        st.error(f"Emotion analysis error: {emotion['error']}")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Primary Emotion", emotion.get("primary_emotion", "Unknown"))

    with col2:
        st.metric("Intensity", emotion.get("intensity", "Unknown").upper())

    secondary = emotion.get("secondary_emotions", [])
    if secondary:
        st.write(f"**Secondary emotions:** {', '.join(secondary)}")

    tone = emotion.get("tone_descriptors", [])
    if tone:
        st.write(f"**Tone:** {', '.join(tone)}")

    # Emotional Leakage
    leakage = emotion.get("emotional_leakage", {})
    if leakage.get("detected"):
        st.markdown("---")
        st.markdown('<div class="leakage-warning">', unsafe_allow_html=True)
        st.subheader("⚠️ Emotional Leakage Detected")

        leaked = leakage.get("leaked_emotions", [])
        if leaked:
            st.write(f"**Leaked emotions:** {', '.join(leaked)}")

        indicators = leakage.get("indicators", [])
        if indicators:
            st.write("**Indicators:**")
            for ind in indicators:
                st.write(f'- *"{ind}"*')

        st.write(leakage.get("explanation", ""))
        st.markdown('</div>', unsafe_allow_html=True)


def display_risk(risk: dict):
    """Display risk analysis results."""
    if "error" in risk:
        st.error(f"Risk analysis error: {risk['error']}")
        return

    score = risk.get("overall_risk_score", 0)
    level = risk.get("risk_level", "unknown")
    color = get_risk_color(score)

    st.markdown(
        f'<p class="risk-score-{color}">{score}/10 ({level.upper()})</p>',
        unsafe_allow_html=True
    )

    # Misinterpretation Risks
    risks_list = risk.get("misinterpretation_risks", [])
    if risks_list:
        st.subheader("Misinterpretation Risks")

        for r in risks_list:
            with st.expander(f"⚠️ {r.get('risk', 'Risk')}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Probability:** {r.get('probability', '?').upper()}")
                with col2:
                    st.write(f"**Impact:** {r.get('impact', '?').upper()}")

                st.write(f"**Problematic phrase:** *\"{r.get('problematic_phrase', '')}\"*")
                st.write(r.get("explanation", ""))

    # Red Flags
    red_flags = risk.get("red_flags", [])
    if red_flags:
        st.subheader("🚩 Red Flags")

        for flag in red_flags:
            st.markdown('<div class="red-flag">', unsafe_allow_html=True)
            st.write(f'**"{flag.get("phrase", "")}"**')
            st.write(f"*{flag.get('why_problematic', '')}*")
            st.caption(f"Category: {flag.get('category', '')}")
            st.markdown('</div>', unsafe_allow_html=True)

    # Ambiguities
    ambiguities = risk.get("ambiguities", [])
    if ambiguities:
        st.subheader("❓ Ambiguities")
        for amb in ambiguities:
            st.write(f"- {amb}")


def display_rewrite(rewrite: dict):
    """Display rewrite suggestions."""
    if "error" in rewrite:
        st.error(f"Rewrite error: {rewrite['error']}")
        return

    if not rewrite.get("needs_rewrite"):
        st.success("✅ This message looks good! No major rewrites needed.")
        return

    # Rewrite versions
    rewrites = rewrite.get("rewrites", [])
    if rewrites:
        for rw in rewrites:
            st.markdown('<div class="suggestion">', unsafe_allow_html=True)
            st.subheader(f"✨ {rw.get('version', 'Alternative').title()} Version")
            st.markdown(f"> {rw.get('rewritten_message', '')}")

            changes = rw.get("changes_made", [])
            if changes:
                st.write("**Changes:**")
                for change in changes:
                    st.write(f"- {change}")

            st.caption(f"Tone shift: {rw.get('tone_shift', '')}")
            st.markdown('</div>', unsafe_allow_html=True)

    # Specific fixes
    fixes = rewrite.get("specific_fixes", [])
    if fixes:
        st.subheader("Quick Fixes")

        for fix in fixes:
            col1, col2 = st.columns(2)
            with col1:
                st.error(f"❌ \"{fix.get('original_phrase', '')}\"")
            with col2:
                st.success(f"✅ \"{fix.get('suggested_phrase', '')}\"")
            st.caption(fix.get("reason", ""))

    # General advice
    advice = rewrite.get("general_advice")
    if advice:
        st.info(f"💡 **Advice:** {advice}")


def main():
    st.title("🛡️ Communication Intent & Risk Guard")
    st.markdown("*Analyze your messages before sending to detect intent, emotional leakage, and misinterpretation risks.*")

    # Load agents
    with st.spinner("Loading agents..."):
        agents = load_agents()

    # Sidebar
    with st.sidebar:
        st.header("About")
        st.markdown("""
        This tool uses 4 specialized AI agents:

        1. **Intent Agent** - Detects what you're trying to achieve
        2. **Emotion Agent** - Analyzes emotional tone & leakage
        3. **Risk Agent** - Identifies misinterpretation risks
        4. **Rewrite Agent** - Suggests improvements
        """)

        st.header("Examples")
        example_messages = {
            "Select an example...": "",
            "Passive-aggressive": "Fine. I guess I'll just do it myself since nobody else seems to care.",
            "Accusatory": "I thought you said you'd handle this. Whatever, I'll figure it out.",
            "Sarcastic": "Must be nice to have so much free time. Some of us are actually busy.",
            "Professional (safe)": "Would it be possible to reschedule our meeting to Thursday? I have a conflict that just came up.",
        }

        selected_example = st.selectbox("Load example:", list(example_messages.keys()))

    # Main input
    default_text = example_messages.get(selected_example, "")

    message = st.text_area(
        "Enter your message:",
        value=default_text,
        height=150,
        placeholder="Type the message you want to analyze before sending..."
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        analyze_button = st.button("🔍 Analyze", type="primary", use_container_width=True)

    if analyze_button and message.strip():
        with st.spinner("Running analysis pipeline..."):
            results = run_analysis(message, agents)

        st.markdown("---")

        # Risk Score Header
        risk_score = results.get("risk", {}).get("overall_risk_score", 0)
        risk_color = get_risk_color(risk_score)

        if risk_score <= 3:
            st.success(f"✅ Low Risk Message (Score: {risk_score}/10)")
        elif risk_score <= 6:
            st.warning(f"⚠️ Medium Risk Message (Score: {risk_score}/10)")
        else:
            st.error(f"🚨 High Risk Message (Score: {risk_score}/10)")

        # Tabs for different analyses
        tab1, tab2, tab3, tab4 = st.tabs(["🎯 Intent", "💭 Emotion", "⚠️ Risk", "✨ Suggestions"])

        with tab1:
            display_intent(results.get("intent", {}))

        with tab2:
            display_emotion(results.get("emotion", {}))

        with tab3:
            display_risk(results.get("risk", {}))

        with tab4:
            if "rewrite" in results:
                display_rewrite(results["rewrite"])
            else:
                st.success("✅ This message has a low risk score. No rewrites suggested.")

    elif analyze_button:
        st.warning("Please enter a message to analyze.")


if __name__ == "__main__":
    main()
