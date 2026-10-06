"""One command: run the unit tests, then print the routing report.

    python3 evaluate.py

Exits non-zero if any test fails.
"""

import csv
import sys
import unittest
from pathlib import Path

from router import route

ROOT = Path(__file__).parent
DATA = ROOT / "data"


def load_cases(name):
    with open(DATA / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_disputes():
    return {row["id"]: row for row in load_cases("label_disputes.csv")}


def summarize(cases, disputes=None):
    disputes = disputes or {}
    rows = []
    for case in cases:
        result = route(case["message"])
        dispute = disputes.get(case["id"])
        rows.append({
            "id": case["id"],
            "message": case["message"],
            "expected": case["expected_route"],
            "got": result["route"],
            "reason": result["reason"],
            "urgent": case["urgent"] == "yes",
            "correct": result["route"] == case["expected_route"],
            "dispute": {"proposed_route": dispute["proposed_route"], "why": dispute["why"]} if dispute else None,
            "known_gap": case.get("known_gap") or "",
        })

    urgent = [r for r in rows if r["urgent"]]
    non_urgent = [r for r in rows if not r["urgent"]]
    summary = {
        "total": len(rows),
        "correct": sum(r["correct"] for r in rows),
        "urgent_total": len(urgent),
        "urgent_caught": sum(r["got"] == "escalate" for r in urgent),
        "non_urgent_total": len(non_urgent),
        "false_escalations": sum(r["got"] == "escalate" for r in non_urgent),
        "correct_with_disputes": None,
        "rows": rows,
    }
    if disputes:
        summary["correct_with_disputes"] = sum(
            r["got"] == (r["dispute"]["proposed_route"] if r["dispute"] else r["expected"]) for r in rows
        )
    return summary


def _pct(n, total):
    return f"{n}/{total} ({100 * n / total:.1f}%)" if total else "0/0"


def report(title, summary):
    wrong = [r for r in summary["rows"] if not r["correct"]]

    print(f"\n== {title} ({summary['total']} messages) ==")
    print(f"Overall accuracy:              {_pct(summary['correct'], summary['total'])}")
    print(f"Urgent messages caught:        {summary['urgent_caught']}/{summary['urgent_total']}")
    print(f"Non-urgent wrongly escalated:  {summary['false_escalations']}/{summary['non_urgent_total']}")

    print(f"\nWrong rows ({len(wrong)}):" if wrong else "\nWrong rows: none")
    for row in wrong:
        tag = "  MISSED URGENT" if row["urgent"] and row["got"] != "escalate" else ""
        print(f"  #{row['id']}  expected={row['expected']}  got={row['got']}{tag}")
        print(f"       message: {row['message']}")
        print(f"       reason:  {row['reason']}")
        if row["dispute"]:
            print(f"       label disputed, we propose '{row['dispute']['proposed_route']}': {row['dispute']['why']}")
        if row["known_gap"]:
            print(f"       known gap: {row['known_gap']}")

    if summary["correct_with_disputes"] is not None:
        print(f"\nAccuracy with disputed labels corrected: {_pct(summary['correct_with_disputes'], summary['total'])}")


def run_tests():
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), top_level_dir=str(ROOT))
    return unittest.TextTestRunner(verbosity=1).run(suite).wasSuccessful()


def main():
    tests_passed = run_tests()
    report("Provided test set", summarize(load_cases("test_messages.csv"), load_disputes()))
    report("Additional cases (written by us)", summarize(load_cases("extra_messages.csv")))
    return 0 if tests_passed else 1


if __name__ == "__main__":
    sys.exit(main())
