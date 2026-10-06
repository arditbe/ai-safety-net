# Omzo Air: message router

`route(message) -> {"route", "reason"}` decides what happens to each patient message: `code`, `faq`, `answer`, `refuse` or `escalate`.

## Run

Python 3.9+, no dependencies:

```bash
python3 evaluate.py
```

This runs the unit tests, then prints accuracy, urgent messages caught, non-urgent messages wrongly escalated, and every wrong row. It does this for the 20 provided messages and for 23 additional cases we wrote. The command exits non-zero if a test fails.

## Optional: browser GUI

A small PHP front end for trying messages by hand and browsing the test results. It calls the same Python router through `gui/bridge.py`, so there is still only one copy of the routing logic. Requires PHP 8.1+.

```bash
php -S 127.0.0.1:8000 -t gui
# open http://127.0.0.1:8000
```

If `python3` isn't on your PATH, set `OMZO_PYTHON=/path/to/python3`.

## Layout

| Path | What |
|---|---|
| `router/rules.py` | All patterns, grouped by category. Changing a rule is a one-line edit here. |
| `router/router.py` | `route()`: normalize the text, then check routes in priority order (escalate first) |
| `data/test_messages.csv` | The 20 messages from the brief, unchanged |
| `data/label_disputes.csv` | Labels we disagree with, and why |
| `data/extra_messages.csv` | Our own cases, including known gaps |
| `tests/test_router.py` | Unit tests |
| `evaluate.py` | The one command |
| `docs/` | The architecture diagram (`architecture.png`) and its editable source (`architecture.mmd`) |
| `system-prompt/` | The prompt for the one route that uses AI (`answer`), with its handoff rule |
| `experiments/` | Optional: the system prompt tested against a real model, with [results](experiments/RESULTS.md) (0 safety failures in 72 replies) |
| `gui/` | Optional PHP GUI (`index.php`, `app.js`, `style.css`) and `bridge.py`, the JSON bridge to the router |

## Results

```
== Provided test set (20 messages) ==
Overall accuracy:              19/20 (95.0%)
Urgent messages caught:        7/7
Non-urgent wrongly escalated:  0/13

Wrong rows (1):
  #19  expected=answer  got=code
       message: My name is Jane Doe DOB 04/12/1988 and I want a refund
       reason:  Simple request (billing), handled by plain code. Contains personal identifiers: redact before logging.
       label disputed, we propose 'code': ...

Accuracy with disputed labels corrected: 20/20 (100.0%)

== Additional cases (written by us) (23 messages) ==
Overall accuracy:              21/23 (91.3%)
Urgent messages caught:        12/13
Non-urgent wrongly escalated:  1/10
  #E11  expected=escalate  got=refuse  MISSED URGENT   ("I've been saving up my pills just in case")
  #E16  expected=answer  got=escalate                  (negated symptom, over-escalated)
```

## Which mistakes worry us most

Missed escalations worry us most, because a patient in danger who gets a refusal or an AI answer is the one failure we cannot recover from; E11 ("saving up my pills just in case") shows that keyword rules miss indirect self-harm signals, however many patterns we add. Second are urgent messages in languages or phrasings the rules have never seen, since 7/7 on the provided set only proves the rules cover the phrasings we thought of. Over-escalations such as E16 worry us least: they cost care-team time, not patient safety, which is why every ambiguous rule leans toward escalating.
