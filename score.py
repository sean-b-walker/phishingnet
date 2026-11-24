import json
import re
import sys
from pathlib import Path

from judge import call_model, load_env
from mail import read_eml


address_re = re.compile(r"\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b", re.I)
domain_re = re.compile(r"\b(?:[a-z0-9-]+\.)+[a-z]{2,}\b", re.I)


def unsupported_refs(facts, result):
    evidence = json.dumps(facts).lower()
    unsupported = set()

    for reason in result.get("reasons", []):
        if not isinstance(reason, str):
            continue

        refs = address_re.findall(reason) + domain_re.findall(reason)
        for ref in refs:
            if ref.lower() not in evidence:
                unsupported.add(ref.lower())

    return sorted(unsupported)


def main():
    load_env()

    root = Path(__file__).parent
    labels = json.loads((root / "labels.json").read_text())
    samples = sorted((root / "samples").glob("*.eml"))

    passed = 0
    warned = 0

    for path in samples:
        expected = labels.get(path.name)
        if expected is None:
            sys.exit(f"missing label for {path.name}")

        facts = read_eml(path)
        result = call_model(facts)
        actual = result.get("verdict", "missing")
        matched = actual == expected

        if matched:
            passed += 1
            print(f"PASS {path.name}: {actual}")
        else:
            print(f"FAIL {path.name}: expected {expected}, got {actual}")
            print(json.dumps(result, indent=2))

        refs = unsupported_refs(facts, result)
        if refs:
            warned += 1
            print(f"WARN {path.name}: unsupported references: {', '.join(refs)}")

    print(f"\n{passed}/{len(samples)} verdicts correct; {warned} grounding warnings")

    if passed != len(samples):
        sys.exit(1)


if __name__ == "__main__":
    main()
