"""JSON bridge so the PHP GUI uses the real Python router, not a copy of it.

    echo '{"message": "hi"}' | python3 gui/bridge.py route
    python3 gui/bridge.py evaluate
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from evaluate import load_cases, load_disputes, summarize  # noqa: E402
from router import route  # noqa: E402


def main(argv):
    command = argv[1] if len(argv) > 1 else ""
    if command == "route":
        payload = json.load(sys.stdin)
        output = route(payload.get("message") if isinstance(payload, dict) else None)
    elif command == "evaluate":
        output = {
            "provided": summarize(load_cases("test_messages.csv"), load_disputes()),
            "extra": summarize(load_cases("extra_messages.csv")),
        }
    else:
        print("usage: bridge.py route|evaluate", file=sys.stderr)
        return 2
    json.dump(output, sys.stdout, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
