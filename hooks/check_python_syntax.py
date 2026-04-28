"""Post-edit hook: run py_compile on edited Python files."""
import json
import subprocess
import sys


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    file_path = data.get("tool_input", {}).get("file_path", "")

    if not file_path.endswith(".py"):
        sys.exit(0)

    result = subprocess.run(
        [sys.executable, "-m", "py_compile", file_path],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Python syntax error in {file_path}:")
        print(result.stderr)
        sys.exit(1)

    print(f"Syntax OK: {file_path}")


if __name__ == "__main__":
    main()
