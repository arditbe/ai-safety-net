"""route(message) -> {"route", "reason"}

Checks run in this order and the first match wins: escalate, refuse
(prompt injection), code, faq, answer, refuse. Escalate goes first so a
greeting or "ignore your rules" can't hide an urgent message.
Reasons never quote the message, so they're safe to log.
"""

import re
import unicodedata

from . import rules


def _compile(patterns):
    return [re.compile(p) for p in patterns]


def _compile_groups(groups):
    return {name: _compile(patterns) for name, patterns in groups.items()}


URGENT_SYMPTOMS = _compile_groups(rules.URGENT_SYMPTOMS)
CLINICIAN_ONLY = _compile_groups(rules.CLINICIAN_ONLY)
PROMPT_INJECTION = _compile(rules.PROMPT_INJECTION)
CODE_INTENTS = _compile_groups(rules.CODE_INTENTS)
FAQ_TOPICS = _compile_groups(rules.FAQ_TOPICS)
HEALTH_TOPICS = _compile(rules.HEALTH_TOPICS)
PERSONAL_IDENTIFIERS = _compile(rules.PERSONAL_IDENTIFIERS)


def normalize(message):
    """Lowercase, strip accents, straighten quotes, collapse whitespace."""
    # split "é" into "e" + accent mark, then drop the marks
    text = unicodedata.normalize("NFKD", message)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    # phones send curly apostrophes
    text = text.replace("’", "'").replace("‘", "'")
    return " ".join(text.lower().split())


def _any_match(text, patterns):
    return any(p.search(text) for p in patterns)


def _first_group(text, groups):
    # dicts keep order, so groups are tried in rules.py order
    for name, patterns in groups.items():
        if _any_match(text, patterns):
            return name
    return None


def _result(route, reason):
    return {"route": route, "reason": reason}


def _route(message):
    if not isinstance(message, str) or not message.strip():
        return _result("refuse", "Empty message.")
    text = normalize(message)

    symptom = _first_group(text, URGENT_SYMPTOMS)
    if symptom:
        return _result(
            "escalate",
            f"Urgent symptom ({symptom}). Send to care team now and show emergency guidance (911 / 988).",
        )

    topic = _first_group(text, CLINICIAN_ONLY)
    if topic:
        return _result("escalate", f"Clinician-only topic ({topic}). The AI must not answer; send to care team.")

    if _any_match(text, PROMPT_INJECTION):
        return _result("refuse", "Attempt to override the assistant's instructions.")

    intent = _first_group(text, CODE_INTENTS)
    if intent:
        reason = f"Simple request ({intent}), handled by plain code."
        if _any_match(text, PERSONAL_IDENTIFIERS):
            reason += " Contains personal identifiers: redact before logging."
        return _result("code", reason)

    faq = _first_group(text, FAQ_TOPICS)
    if faq:
        return _result("faq", f"Covered by approved FAQ ({faq}).")

    if _any_match(text, HEALTH_TOPICS):
        return _result("answer", "General health or wearable question; answer from approved sources.")

    return _result("refuse", "Off-topic: no health, wearable or account topic recognized.")


def route(message):
    """Route a patient message. If routing crashes, escalate so a human sees it."""
    try:
        return _route(message)
    except Exception:
        return _result("escalate", "Router error; failing safe to the care team.")
