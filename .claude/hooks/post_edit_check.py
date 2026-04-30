"""Post-edit hook: syntax check for .py files, dotnet build for .cs files."""
import json
import logging
import subprocess
import sys

logging.basicConfig(stream=sys.stdout, format="%(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)


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
            logger.error("Python syntax error in %s:", file_path)
            logger.error(result.stderr)
            sys.exit(1)
        logger.info("Syntax OK: %s", file_path)

    elif file_path.endswith(".cs"):
        logger.info("C# file modified — running dotnet build...")
        result = subprocess.run(
            ["dotnet", "build", "backend/SubscriptionTracker.Api",
             "--no-restore", "--verbosity", "minimal"],
            capture_output=True,
            text=True,
        )
        logger.info(result.stdout)
        if result.returncode != 0:
            logger.error(result.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
