"""Run code samples in src/code-samples/ and report results.

By default runs all code samples. Pass FILES to test specific files only.

  make test-code-samples
  make test-code-samples FILES="src/code-samples/langchain/return-a-string.py"
  make test-code-samples FILES="src/code-samples/langchain/return-a-string.py src/code-samples/langchain/return-a-string.ts"

Set ``CODE_SAMPLE_TRACING=1`` to enable LangSmith tracing, share public links for
agent runs from single-snippet samples, and update ``src/code-samples/trace-links.json``.

Set ``CODE_SAMPLE_JOBS`` to run samples concurrently (default: 4). Trace-link
collection stays serialized under a lock so parallel samples do not clobber the
shared manifest or claim each other's runs.

Samples that share a LangSmith dataset or experiment fixture are placed in a
serial group (see ``SERIAL_GROUPS``): they never run concurrently with others
in the same group, but still overlap with unrelated samples.

Rate-limit tuning (optional env overrides):

- ``CODE_SAMPLE_RATE_LIMIT_ATTEMPTS`` (default: 5)
- ``CODE_SAMPLE_RATE_LIMIT_DELAY_SECONDS`` (default: 30; grows per attempt)
"""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import nullcontext
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

# Allow ``from code_sample_tracing import …`` when run as ``python scripts/….py``.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from code_sample_tracing import DEFAULT_PROJECT, collect_trace_for_sample

TIMEOUT_SECONDS = int(os.environ.get("CODE_SAMPLE_TIMEOUT_SECONDS", "1200"))

# Samples call the live LangSmith API and can hit its rate limits under CI
# load, independent of whether the sample itself is correct. Retry a few
# times with backoff before giving up, and don't fail the build if a sample
# is still rate-limited after retries are exhausted.
RATE_LIMIT_MAX_ATTEMPTS = max(
    1, int(os.environ.get("CODE_SAMPLE_RATE_LIMIT_ATTEMPTS", "5"))
)
RATE_LIMIT_RETRY_DELAY_SECONDS = max(
    1, int(os.environ.get("CODE_SAMPLE_RATE_LIMIT_DELAY_SECONDS", "30"))
)
# Cap so a single sample cannot stall the suite for many minutes.
RATE_LIMIT_RETRY_DELAY_CAP_SECONDS = 120
TRACE_RATE_LIMIT_MAX_ATTEMPTS = RATE_LIMIT_MAX_ATTEMPTS

DEFAULT_JOBS = 4

# Relative-path prefixes. Matching samples share a lock so they do not race on
# the same LangSmith dataset or experiment fixture under CODE_SAMPLE_JOBS > 1.
SERIAL_GROUPS: dict[str, tuple[str, ...]] = {
    "evaluate-rag": ("src/code-samples/langsmith/evaluate-rag-",),
    "experiment-runs-query": (
        "src/code-samples/langsmith/smithdb-migration/experiment-runs-query-",
    ),
}


def serial_group_for(rel_path: Path) -> str | None:
    """Return the serial group name for a sample path, or None if unrestricted."""
    path = rel_path.as_posix()
    for group, prefixes in SERIAL_GROUPS.items():
        if any(path.startswith(prefix) for prefix in prefixes):
            return group
    return None


def worker_count() -> int:
    """Return how many samples to run concurrently."""
    raw = os.environ.get("CODE_SAMPLE_JOBS", "").strip()
    if raw:
        try:
            return max(1, int(raw))
        except ValueError:
            print(
                f"Warning: invalid CODE_SAMPLE_JOBS={raw!r}; using {DEFAULT_JOBS}",
                file=sys.stderr,
            )
    return DEFAULT_JOBS


def is_rate_limited(stdout: str, stderr: str, *, lang: str | None = None) -> bool:
    """Best-effort detection of a 429/rate-limit response in sample output."""
    combined = f"{stdout}\n{stderr}".lower()
    if "too many requests" in combined or "rate limit exceeded" in combined:
        return True
    if "429" in combined and (
        "rate limit" in combined
        or "ratelimit" in combined
        or "<title>429</title>" in combined
    ):
        return True
    # Shell samples often pipe curl into jq; HTML/error bodies from a 429 then
    # surface only as a jq parse failure with no status text in the logs.
    if lang == "bash" and "jq: parse error" in combined:
        return True
    return False


def rate_limit_sleep_seconds(attempt: int) -> int:
    """Return backoff delay after a rate-limited attempt (1-based)."""
    delay = RATE_LIMIT_RETRY_DELAY_SECONDS * attempt
    return min(RATE_LIMIT_RETRY_DELAY_CAP_SECONDS, delay)


def write_github_output(**values: object) -> None:
    """Append key=value lines to GITHUB_OUTPUT when running in Actions."""
    path = os.environ.get("GITHUB_OUTPUT", "").strip()
    if not path:
        return
    with open(path, "a", encoding="utf-8") as handle:
        for key, value in values.items():
            handle.write(f"{key}={value}\n")


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


def tracing_enabled() -> bool:
    """Return True when CODE_SAMPLE_TRACING requests LangSmith collection."""
    return os.environ.get("CODE_SAMPLE_TRACING", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }


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
        if tracing_enabled():
            env["LANGSMITH_TRACING"] = "true"
            env.setdefault(
                "LANGSMITH_PROJECT",
                os.environ.get("LANGSMITH_PROJECT", DEFAULT_PROJECT),
            )
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


@dataclass
class SampleOutcome:
    """Result of running one sample, including retry bookkeeping."""

    rel_path: Path
    file_path: Path
    success: bool
    stdout: str
    stderr: str
    started_at: datetime
    finished_at: datetime
    rate_limited: bool


def run_sample_with_retries(
    file_path: Path,
    lang: str,
    repo_root: Path,
    code_samples_dir: Path,
    print_lock: threading.Lock,
    group_locks: dict[str, threading.Lock],
) -> SampleOutcome:
    """Run one sample with rate-limit retries and return a structured outcome."""
    rel_path = file_path.relative_to(repo_root)
    success = False
    stdout = ""
    stderr = ""
    started_at = datetime.now(timezone.utc)
    group = serial_group_for(rel_path)
    group_lock = group_locks[group] if group is not None else nullcontext()

    with group_lock:
        for attempt in range(1, RATE_LIMIT_MAX_ATTEMPTS + 1):
            started_at = datetime.now(timezone.utc)
            success, stdout, stderr = run_sample(
                file_path, lang, repo_root, code_samples_dir
            )
            if success or not is_rate_limited(stdout, stderr, lang=lang):
                break
            if attempt < RATE_LIMIT_MAX_ATTEMPTS:
                delay = rate_limit_sleep_seconds(attempt)
                with print_lock:
                    print(
                        f"  ... {rel_path} hit a 429, retrying "
                        f"({attempt}/{RATE_LIMIT_MAX_ATTEMPTS}) "
                        f"after {delay}s"
                    )
                time.sleep(delay)

    return SampleOutcome(
        rel_path=rel_path,
        file_path=file_path,
        success=success,
        stdout=stdout,
        stderr=stderr,
        started_at=started_at,
        finished_at=datetime.now(timezone.utc),
        rate_limited=(not success)
        and is_rate_limited(stdout, stderr, lang=lang),
    )


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    code_samples_dir = repo_root / "src" / "code-samples"

    if not code_samples_dir.exists():
        print("src/code-samples/ not found")
        write_github_output(sample_failures=1, traces_updated=0)
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
        write_github_output(
            sample_failures=0,
            samples_passed=0,
            samples_total=0,
            samples_rate_limited=0,
            traces_updated=0,
            trace_failures=0,
        )
        return 0

    collect_traces = tracing_enabled()
    project_name = os.environ.get("LANGSMITH_PROJECT", DEFAULT_PROJECT)
    jobs = min(worker_count(), total)
    if collect_traces:
        print(
            f"Running {total} code sample(s) with LangSmith tracing "
            f"(project={project_name}, jobs={jobs})...\n"
        )
    else:
        print(f"Running {total} code sample(s) (jobs={jobs})...\n")

    passed = 0
    failed: list[Path] = []
    rate_limited: list[Path] = []
    traces_updated = 0
    trace_failures: list[Path] = []
    print_lock = threading.Lock()
    trace_lock = threading.Lock()
    group_locks = {name: threading.Lock() for name in SERIAL_GROUPS}
    claimed_run_ids: set[str] = set()

    def collect_trace_with_retries(outcome: SampleOutcome) -> dict | None:
        """Collect a public trace link, retrying LangSmith 429 responses."""
        last_exc: Exception | None = None
        for attempt in range(1, TRACE_RATE_LIMIT_MAX_ATTEMPTS + 1):
            try:
                with trace_lock:
                    entry = collect_trace_for_sample(
                        repo_root=repo_root,
                        source_path=outcome.file_path,
                        start_time=outcome.started_at,
                        end_time=outcome.finished_at,
                        exclude_ids=claimed_run_ids,
                        project_name=project_name,
                    )
                    if entry is not None:
                        run_id = str(entry.get("run_id") or "")
                        if run_id:
                            claimed_run_ids.add(run_id)
                    return entry
            except Exception as exc:  # noqa: BLE001 - retry or report
                last_exc = exc
                if (
                    not is_rate_limited("", str(exc))
                    or attempt >= TRACE_RATE_LIMIT_MAX_ATTEMPTS
                ):
                    raise
                delay = rate_limit_sleep_seconds(attempt)
                with print_lock:
                    print(
                        f"  ... {outcome.rel_path}: trace collection hit a "
                        f"429, retrying ({attempt}/"
                        f"{TRACE_RATE_LIMIT_MAX_ATTEMPTS}) after {delay}s"
                    )
                time.sleep(delay)
        if last_exc is not None:
            raise last_exc
        return None

    def handle_outcome(outcome: SampleOutcome) -> None:
        nonlocal passed, traces_updated
        if outcome.success:
            passed += 1
            with print_lock:
                print(f"  ✓ {outcome.rel_path}")
            if collect_traces:
                try:
                    entry = collect_trace_with_retries(outcome)
                    if entry is not None:
                        traces_updated += 1
                except Exception as exc:  # noqa: BLE001 - warn; do not fail suite
                    # Sample already passed. Trace-link refresh can still ship
                    # with a few missing shares; do not fail the whole run.
                    trace_failures.append(outcome.rel_path)
                    with print_lock:
                        print(
                            f"  ⚠ {outcome.rel_path}: trace collection "
                            f"failed (continuing): {exc}",
                            file=sys.stderr,
                        )
        elif outcome.rate_limited:
            # The live LangSmith API rate-limited every attempt. This reflects CI
            # load, not a defect in the sample, so don't fail the build over it.
            rate_limited.append(outcome.rel_path)
            with print_lock:
                print_rate_limited(
                    outcome.rel_path, outcome.stdout, outcome.stderr
                )
        else:
            failed.append(outcome.rel_path)
            with print_lock:
                print_failure(outcome.rel_path, outcome.stdout, outcome.stderr)

    if jobs == 1:
        for file_path, lang in files_to_test:
            handle_outcome(
                run_sample_with_retries(
                    file_path,
                    lang,
                    repo_root,
                    code_samples_dir,
                    print_lock,
                    group_locks,
                )
            )
    else:
        with ThreadPoolExecutor(max_workers=jobs) as executor:
            futures = [
                executor.submit(
                    run_sample_with_retries,
                    file_path,
                    lang,
                    repo_root,
                    code_samples_dir,
                    print_lock,
                    group_locks,
                )
                for file_path, lang in files_to_test
            ]
            for future in as_completed(futures):
                handle_outcome(future.result())

    # Summary
    print("-" * 40)
    if rate_limited:
        print(
            f"SKIPPED: {len(rate_limited)}/{total} code sample(s) skipped "
            "(rate-limited by the LangSmith API after retries)"
        )
    if collect_traces:
        print(f"Trace links updated: {traces_updated}")
        if trace_failures:
            print(
                f"WARNING: {len(trace_failures)}/{total} code sample(s) "
                "passed but trace collection failed"
            )
    write_github_output(
        sample_failures=len(failed),
        samples_passed=passed,
        samples_total=total,
        samples_rate_limited=len(rate_limited),
        traces_updated=traces_updated,
        trace_failures=len(trace_failures),
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
