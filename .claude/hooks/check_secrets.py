"""Pre-edit hook: detect hardcoded secrets in files being written."""
import json
import re
import sys

PATTERNS = [
    re.compile(r'api[_-]?key\s*[:=]\s*["\'][^"\']{8,}["\']', re.IGNORECASE),
    re.compile(r'secret\s*[:=]\s*["\'][^"\']{8,}["\']', re.IGNORECASE),
    re.compile(r'password\s*[:=]\s*["\'][^"\']{8,}["\']', re.IGNORECASE),
    re.compile(r'token\s*[:=]\s*["\'][^"\']{16,}["\']', re.IGNORECASE),
]

WHITELISTED_VALUES = {
    "dev-secret-key-change-me",
    "your-api-key-here",
    "your-key-here",
    "changeme",
    "placeholder",
}


def is_whitelisted(match_text: str) -> bool:
    return any(w in match_text.lower() for w in WHITELISTED_VALUES)


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    content = tool_input.get("new_string", "") or tool_input.get("content", "")

    if not content:
        sys.exit(0)

    findings = []
    for line_num, line in enumerate(content.splitlines(), 1):
        for pattern in PATTERNS:
            m = pattern.search(line)
            if m and not is_whitelisted(m.group(0)):
                findings.append(f"  Line {line_num}: {line.strip()[:80]}")

    if findings:
        print(f"SECRET DETECTED in {file_path}:")
        for f in findings:
            print(f)
        print("Use .env or appsettings.Development.json for real credentials.")
        sys.exit(1)


if __name__ == "__main__":
    main()
