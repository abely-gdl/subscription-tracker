"""Post-edit hook: syntax check for .py files, dotnet build for .cs files."""
import json
import subprocess
import sys


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    file_path = data.get("tool_input", {}).get("file_path", "")

    if file_path.endswith(".py"):
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

    elif file_path.endswith(".cs"):
        print(f"C# file modified — running dotnet build...")
        result = subprocess.run(
            ["dotnet", "build", "backend/SubscriptionTracker.Api",
             "--no-restore", "--verbosity", "minimal"],
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
