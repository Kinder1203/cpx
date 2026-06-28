"""Optional Codex CLI adapter for free-question concept matching."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from collections import OrderedDict
from pathlib import Path
from threading import RLock
from time import monotonic
from typing import Any, Callable, Sequence


Runner = Callable[..., subprocess.CompletedProcess[str]]
Clock = Callable[[], float]


class CodexConceptMatcher:
    """Map a free-form question to allowed card concepts without creating facts."""

    def __init__(
        self,
        *,
        executable: str | None = None,
        timeout_seconds: int = 8,
        runner: Runner = subprocess.run,
        failure_threshold: int = 2,
        cooldown_seconds: float = 30.0,
        cache_size: int = 256,
        clock: Clock = monotonic,
    ) -> None:
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be positive")
        if cooldown_seconds < 0:
            raise ValueError("cooldown_seconds must not be negative")
        if cache_size < 1:
            raise ValueError("cache_size must be positive")
        self._executable = executable or shutil.which("codex")
        self._timeout_seconds = timeout_seconds
        self._runner = runner
        self._failure_threshold = failure_threshold
        self._cooldown_seconds = cooldown_seconds
        self._cache_size = cache_size
        self._clock = clock
        self._consecutive_failures = 0
        self._circuit_open_until = 0.0
        self._cache: OrderedDict[tuple[str, tuple[str, ...]], tuple[str, ...]] = OrderedDict()
        self._lock = RLock()

    @property
    def available(self) -> bool:
        return bool(self._executable) and self._clock() >= self._circuit_open_until

    def __call__(
        self,
        question: str,
        concepts: tuple[dict[str, Any], ...],
    ) -> tuple[str, ...]:
        if not self._executable:
            raise RuntimeError("Codex CLI is not available")

        candidates = [
            {
                "id": item["id"],
                "label": item["label"],
                "keywords": list(item["keywords"]),
            }
            for item in concepts
        ]
        allowed_ids = [item["id"] for item in candidates]
        cache_key = (question.strip().casefold(), tuple(allowed_ids))
        with self._lock:
            cached = self._cache.get(cache_key)
            if cached is not None:
                self._cache.move_to_end(cache_key)
                return cached
            if self._clock() < self._circuit_open_until:
                raise RuntimeError("Codex CLI concept matching is temporarily disabled")
        payload = {
            "learner_question": question,
            "candidate_concepts": candidates,
        }
        prompt = (
            "Classify the learner's Korean CPX history-taking question. "
            "Return only concept IDs that the learner directly asked about. "
            "Use an empty array when no candidate clearly matches. Do not answer the question, "
            "infer patient facts, diagnose, or explain the classification.\n\nINPUT:\n"
            + json.dumps(payload, ensure_ascii=False)
        )
        schema = {
            "type": "object",
            "properties": {
                "concept_ids": {
                    "type": "array",
                    "items": {"type": "string", "enum": allowed_ids},
                    "maxItems": len(allowed_ids),
                }
            },
            "required": ["concept_ids"],
            "additionalProperties": False,
        }

        with tempfile.TemporaryDirectory(prefix="cpx-codex-") as temp_dir:
            root = Path(temp_dir)
            schema_path = root / "response.schema.json"
            output_path = root / "response.json"
            schema_path.write_text(json.dumps(schema, ensure_ascii=True), encoding="utf-8")
            command: Sequence[str] = (
                self._executable,
                "exec",
                "--config",
                'model_reasoning_effort="low"',
                "--ephemeral",
                "--skip-git-repo-check",
                "--ignore-user-config",
                "--ignore-rules",
                "--sandbox",
                "read-only",
                "--cd",
                str(root),
                "--output-schema",
                str(schema_path),
                "--output-last-message",
                str(output_path),
                "-",
            )
            try:
                completed = self._runner(
                    command,
                    input=prompt,
                    text=True,
                    encoding="utf-8",
                    capture_output=True,
                    timeout=self._timeout_seconds,
                    check=False,
                )
            except Exception:
                self._record_failure()
                raise
            if completed.returncode != 0 or not output_path.exists():
                error_lines = completed.stderr.strip().splitlines()
                message_lines = [line.strip() for line in error_lines if '"message"' in line]
                detail = message_lines[-1] if message_lines else (error_lines[-1] if error_lines else "no CLI error output")
                self._record_failure()
                raise RuntimeError(f"Codex CLI concept matching failed: {detail[:300]}")
            try:
                result = json.loads(output_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                self._record_failure()
                raise

        if not isinstance(result, dict):
            self._record_failure()
            raise ValueError("Codex CLI returned invalid response")

        concept_ids = result.get("concept_ids")
        if not isinstance(concept_ids, list) or not all(isinstance(item, str) for item in concept_ids):
            self._record_failure()
            raise ValueError("Codex CLI returned invalid concept IDs")
        if any(concept_id not in allowed_ids for concept_id in concept_ids):
            self._record_failure()
            raise ValueError("Codex CLI returned an unknown concept ID")
        matched = tuple(dict.fromkeys(concept_ids))
        with self._lock:
            self._consecutive_failures = 0
            self._circuit_open_until = 0.0
            self._cache[cache_key] = matched
            self._cache.move_to_end(cache_key)
            while len(self._cache) > self._cache_size:
                self._cache.popitem(last=False)
        return matched

    def _record_failure(self) -> None:
        with self._lock:
            self._consecutive_failures += 1
            if self._consecutive_failures >= self._failure_threshold:
                self._circuit_open_until = self._clock() + self._cooldown_seconds
