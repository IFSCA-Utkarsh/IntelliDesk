import json
from typing import Dict, List
from llm.client import ollama_generate

PORTAL_MODEL = "portal-model"

# =========================
# REQUIRED MEETING FIELDS
# =========================
REQUIRED_FIELDS = [
    "title",
    "date",
    "start_time",
    "duration",
    "participants",
    "type",
]


# =========================
# PROMPT BUILDER (CRITICAL)
# =========================
def build_portal_prompt(
    user_message: str,
    meeting_state: Dict,
    conversation_history: List[Dict],
) -> str:
    """
    Builds a context-aware prompt that mimics ollama CLI behavior.
    """

    history_text = ""
    for turn in conversation_history[-8:]:  # last 8 turns only
        role = "User" if turn["role"] == "user" else "Assistant"
        history_text += f"{role}: {turn['content']}\n"

    return f"""
You are an intelligent meeting assistant.

Your job:
- Extract meeting details step-by-step
- Support English, Hindi, Hinglish
- Ask for missing information
- Maintain context across messages
- Output JSON ONLY when meeting is complete

=========================
CURRENT MEETING STATE
=========================
{json.dumps(meeting_state, indent=2)}

=========================
CONVERSATION SO FAR
=========================
{history_text.strip()}

=========================
USER MESSAGE
=========================
{user_message}

=========================
RULES (VERY IMPORTANT)
=========================
1. Do NOT repeat information already present in meeting state
2. Only ask for missing fields
3. If meeting is COMPLETE:
   - Output ONLY valid JSON
   - No explanations, no extra text
4. If meeting is INCOMPLETE:
   - Respond in natural language
   - Ask exactly ONE clear question
5. Use 24-hour time format (HH:MM)
6. Duration format: HH:MM
7. Participants must be an integer
8. Date format: DD/MM (resolve "kal", "tomorrow", etc.)

Now respond.
""".strip()


# =========================
# COMPLETENESS CHECK
# =========================
def is_meeting_complete(meeting_state: Dict) -> bool:
    for field in REQUIRED_FIELDS:
        if not meeting_state.get(field):
            return False
    return True


# =========================
# MAIN ENTRY FUNCTION
# =========================
def process_meeting(
    user_message: str,
    meeting_state: Dict,
    conversation_history: List[Dict],
) -> Dict:
    """
    Processes meeting conversation using portal-model with full context.
    """

    prompt = build_portal_prompt(
        user_message=user_message,
        meeting_state=meeting_state,
        conversation_history=conversation_history,
    )

    raw_response = ollama_generate(
        model=PORTAL_MODEL,
        prompt=prompt,
    )

    # Try to parse JSON (ONLY when complete)
    try:
        parsed = json.loads(raw_response)

        if (
            isinstance(parsed, dict)
            and parsed.get("status") == "complete"
            and parsed.get("meeting")
        ):
            return {
                "status": "complete",
                "meeting": parsed["meeting"],
            }

    except json.JSONDecodeError:
        pass

    # Otherwise: normal assistant response
    return {
        "status": "incomplete",
        "message": raw_response.strip(),
    }