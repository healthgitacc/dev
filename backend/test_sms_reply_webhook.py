#!/usr/bin/env python3
"""
Helper to simulate an incoming YES/NO SMS reply webhook.
"""
import argparse
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def main() -> int:
    parser = argparse.ArgumentParser(description="Send a test SMS reply webhook")
    parser.add_argument("--url", required=True, help="Webhook URL, e.g. http://127.0.0.1:8000/api/webhooks/sms-replies")
    parser.add_argument("--from", dest="from_phone", required=True, help="Sender phone number")
    parser.add_argument("--body", required=True, help="Reply text, e.g. YES or NO")
    parser.add_argument("--sid", default="test-message-sid", help="Optional inbound message SID")
    args = parser.parse_args()

    payload = urlencode(
        {
            "From": args.from_phone,
            "Body": args.body,
            "MessageSid": args.sid,
        }
    ).encode("utf-8")

    request = Request(
        args.url,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=20) as response:
            content = response.read().decode("utf-8", errors="replace")
            print(f"HTTP {response.status}")
            print(content or "(empty response)")
        return 0
    except Exception as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
