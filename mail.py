import json
import re
import sys
from email import message_from_binary_file, policy
from email.utils import parseaddr


url_re = re.compile(r"https?://[^\s<>\"']+")


def find_urls(text):
    urls = []
    for match in url_re.findall(text):
        url = match.rstrip(".,;:!?)]}")
        if url not in urls:
            urls.append(url)
    return urls


def read_eml(path):
    with open(path, "rb") as f:
        msg = message_from_binary_file(f, policy=policy.default)

    from_name, from_addr = parseaddr(str(msg.get("From", "")))
    _, reply_to = parseaddr(str(msg.get("Reply-To", "")))

    part = msg.get_body(preferencelist=("plain", "html"))
    body = part.get_content() if part else ""

    return {
        "from_name": from_name,
        "from_addr": from_addr,
        "reply_to": reply_to,
        "subject": str(msg.get("Subject", "")),
        "urls": find_urls(body),
        "body": body,
    }


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python3 mail.py samples/payroll-reset.eml")

    facts = read_eml(sys.argv[1])
    print(json.dumps(facts, indent=2))


if __name__ == "__main__":
    main()
