"""Run code samples in src/code-samples/ and report results.

By default runs all code samples. Pass FILES to test specific files only.

  make test-code-samples
  make test-code-samples FILES="src/code-samples/langchain/return-a-string.py"
  make test-code-samples FILES="src/code-samples/langchain/return-a-string.py src/code-samples/langchain/return-a-string.ts"
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

TIMEOUT_SECONDS = 600

# Samples call the live LangSmith API and can hit its rate limits under CI
# load, independent of whether the sample itself is correct. Retry a few
# times with backoff before giving up, and don't fail the build if a sample
# is still rate-limited after retries are exhausted.
RATE_LIMIT_MAX_ATTEMPTS = 3
RATE_LIMIT_RETRY_DELAY_SECONDS = 15


def is_rate_limited(stdout: str, stderr: str) -> bool:
    """Best-effort detection of a 429/rate-limit response in sample output."""
    combined = f"{stdout}\n{stderr}".lower()
    return "429" in combined and (
        "too many requests" in combined
        or "rate limit" in combined
        or "ratelimit" in combined
    )


def print_failure(rel_path: Path, stdout: str, stderr: str) -> None:
    """Print failure output immediately so CI logs show errors as they occur."""
    print(f"  ✗ {rel_path}")
    print(f"--- {rel_path} ---")
    if stdout:
        print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)
    print()


def print_rate_limited(rel_path: Path, stdout: str, stderr: str) -> None:
    """Print a distinct notice for samples skipped due to persistent rate limiting."""
    print(f"  ⚠ {rel_path} (skipped: still rate-limited after retries)")
    print(f"--- {rel_path} ---")
    if stdout:
        print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)
    print()


def is_valid_sample(p: Path, code_samples_dir: Path) -> bool:
    """Check path is a valid code sample (under code-samples, not __pycache__/node_modules)."""
    try:
        rel = p.relative_to(code_samples_dir)
    except ValueError:
        return False
    return "__pycache__" not in rel.parts and "node_modules" not in rel.parts


def collect_files_to_test(
    repo_root: Path, code_samples_dir: Path
) -> list[tuple[Path, str]]:
    """Return list of (path, lang) for files to test.

    Uses FILES env var if set (space-separated paths). Otherwise runs all.
    """
    files_env = os.environ.get("FILES", "").strip()

    if files_env:
        # Explicit list of files
        result = []
        for raw in files_env.split():
            path = (repo_root / raw.strip()).resolve()
            if not path.exists():
                print(f"Warning: {path} not found, skipping")
                continue
            if path.suffix not in (".py", ".ts", ".java", ".kt", ".go", ".sh"):
                print(
                    f"Warning: {path} not .py, .ts, .java, .kt, .go, or .sh, skipping"
                )
                continue
            if code_samples_dir.resolve() not in path.parents:
                print(f"Warning: {path} not under src/code-samples/, skipping")
                continue
            if path.suffix == ".py":
                lang = "python"
            elif path.suffix == ".ts":
                lang = "ts"
            elif path.suffix == ".java":
                lang = "java"
            elif path.suffix == ".kt":
                lang = "kotlin"
            elif path.suffix == ".go":
                lang = "go"
            else:
                lang = "bash"
            result.append((path, lang))
        return result

    # No FILES specified: run all by default
    py_files = sorted(
        p
        for p in code_samples_dir.rglob("*.py")
        if is_valid_sample(p, code_samples_dir)
    )
    ts_files = sorted(
        p
        for p in code_samples_dir.rglob("*.ts")
        if is_valid_sample(p, code_samples_dir)
    )
    java_files = sorted(
        p
        for p in code_samples_dir.rglob("*.java")
        if is_valid_sample(p, code_samples_dir)
    )
    kt_files = sorted(
        p
        for p in code_samples_dir.rglob("*.kt")
        if is_valid_sample(p, code_samples_dir)
    )
    go_files = sorted(
        p
        for p in code_samples_dir.rglob("*.go")
        if is_valid_sample(p, code_samples_dir)
    )
    sh_files = sorted(
        p
        for p in code_samples_dir.rglob("*.sh")
        if is_valid_sample(p, code_samples_dir)
    )
    return (
        [(p, "python") for p in py_files]
        + [(p, "ts") for p in ts_files]
        + [(p, "java") for p in java_files]
        + [(p, "kotlin") for p in kt_files]
        + [(p, "go") for p in go_files]
        + [(p, "bash") for p in sh_files]
    )


def run_sample(
    file_path: Path, lang: str, repo_root: Path, code_samples_dir: Path
) -> tuple[bool, str, str]:
    """Run one code sample once and return (success, stdout, stderr)."""
    stdout = ""
    stderr = ""
    success = False

    try:
        # Pass full env so POSTGRES_URI, ANTHROPIC_API_KEY etc. reach child processes
        env = os.environ.copy()
        if lang == "python":
            result = subprocess.run(
                ["uv", "run", "python", str(file_path)],
                check=False,
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS,
                env=env,
            )
            success = result.returncode == 0
            stdout = result.stdout or ""
            stderr = result.stderr or ""
        elif lang == "ts":
            # TypeScript: run from code-samples dir so langchain resolve works
            result = subprocess.run(
                ["npx", "tsx", str(file_path.relative_to(code_samples_dir))],
                check=False,
                cwd=str(code_samples_dir),
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS,
                env=env,
            )
            success = result.returncode == 0
            stdout = result.stdout or ""
            stderr = result.stderr or ""
        elif lang == "go":
            # Go: run from code-samples dir so the shared go.mod resolves deps
            result = subprocess.run(
                ["go", "run", str(file_path.relative_to(code_samples_dir))],
                check=False,
                cwd=str(code_samples_dir),
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS,
                env=env,
            )
            success = result.returncode == 0
            stdout = result.stdout or ""
            stderr = result.stderr or ""
        elif lang == "bash":
            # Shell/cURL samples: run from code-samples dir for consistency with ts/go
            result = subprocess.run(
                ["bash", str(file_path.relative_to(code_samples_dir))],
                check=False,
                cwd=str(code_samples_dir),
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS,
                env=env,
            )
            success = result.returncode == 0
            stdout = result.stdout or ""
            stderr = result.stderr or ""
        else:
            # Java/Kotlin via JBang (single-file scripts).
            #
            # Some environments may have very new JDKs installed. Pin to a known-good
            # runtime to avoid toolchain incompatibilities (for example, Kotlin compiler
            # parsing errors on unsupported Java major versions).
            env.setdefault("JBANG_DEFAULT_JAVA_VERSION", "21")
            if not env.get("JAVA_HOME"):
                try:
                    # Prefer a JBang-managed JDK so JBang itself and the Kotlin compiler
                    # run under a compatible runtime (Java 21).
                    jdk_home = subprocess.run(
                        ["jbang", "jdk", "home", "21"],
                        check=False,
                        cwd=str(repo_root),
                        capture_output=True,
                        text=True,
                        timeout=30,
                        env=env,
                    )
                    candidate = (jdk_home.stdout or "").strip()
                    if jdk_home.returncode == 0 and candidate:
                        env["JAVA_HOME"] = candidate
                        env["PATH"] = (
                            str(Path(candidate) / "bin")
                            + os.pathsep
                            + env.get("PATH", "")
                        )
                except Exception:
                    # If JDK discovery fails, fall back to whatever the environment provides.
                    pass
            result = subprocess.run(
                ["jbang", "--java", "21", str(file_path)],
                check=False,
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS,
                env=env,
            )
            success = result.returncode == 0
            stdout = result.stdout or ""
            stderr = result.stderr or ""
    except subprocess.TimeoutExpired:
        stderr = f"Timed out after {TIMEOUT_SECONDS} seconds"
    except FileNotFoundError as e:
        stderr = str(e)

    return success, stdout, stderr


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    code_samples_dir = repo_root / "src" / "code-samples"

    if not code_samples_dir.exists():
        print("src/code-samples/ not found")
        return 1

    files_to_test = collect_files_to_test(repo_root, code_samples_dir)
    total = len(files_to_test)

    if total == 0:
        if os.environ.get("FILES"):
            print(
                "No valid files to test. Check that paths exist under src/code-samples/ and use .py, .ts, .java, .kt, .go, or .sh"
            )
        else:
            print("No code samples found in src/code-samples/")
        return 0

    print(f"Running {total} code sample(s)...\n")

    passed = 0
    failed = []
    rate_limited = []

    for file_path, lang in files_to_test:
        rel_path = file_path.relative_to(repo_root)
        success = False
        stdout = ""
        stderr = ""

        for attempt in range(1, RATE_LIMIT_MAX_ATTEMPTS + 1):
            success, stdout, stderr = run_sample(
                file_path, lang, repo_root, code_samples_dir
            )
            if success or not is_rate_limited(stdout, stderr):
                break
            if attempt < RATE_LIMIT_MAX_ATTEMPTS:
                print(
                    f"  ... {rel_path} hit a 429, retrying "
                    f"({attempt}/{RATE_LIMIT_MAX_ATTEMPTS})"
                )
                time.sleep(RATE_LIMIT_RETRY_DELAY_SECONDS)

        if success:
            passed += 1
            print(f"  ✓ {rel_path}")
        elif is_rate_limited(stdout, stderr):
            # The live LangSmith API rate-limited every attempt. This reflects CI
            # load, not a defect in the sample, so don't fail the build over it.
            rate_limited.append(rel_path)
            print_rate_limited(rel_path, stdout, stderr)
        else:
            failed.append(rel_path)
            print_failure(rel_path, stdout, stderr)

    # Summary
    print("-" * 40)
    if rate_limited:
        print(
            f"SKIPPED: {len(rate_limited)}/{total} code sample(s) skipped "
            "(rate-limited by the LangSmith API after retries)"
        )
    if failed:
        print(f"FAILED: {len(failed)}/{total} code sample(s) failed")
        return 1
    print(
        f"{passed}/{total} code sample(s) passed"
        + (
            f", {len(rate_limited)} skipped due to rate limiting."
            if rate_limited
            else "."
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
