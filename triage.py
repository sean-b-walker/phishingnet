import json
import sys

from judge import call_model, load_env
from mail import read_eml


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python3 triage.py samples/payroll-reset.eml")

    load_env()

    path = sys.argv[1]
    facts = read_eml(path)
    result = call_model(facts)

    print(path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
