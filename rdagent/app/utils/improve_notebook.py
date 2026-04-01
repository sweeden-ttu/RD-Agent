"""
Iteratively improve a Jupyter notebook via the configured LLM (e.g. LM Studio OpenAI-compatible /v1).

Uses rdagent.oai.backend.base.APIBackend. Configure models and base URL via .env / LITELLM_* (see .env.example).
Reachable host examples: 127.0.0.1, localhost, host.docker.internal, or a Docker service name (e.g. rdagent).
Do not use the literal host ``null`` shown in some LM Studio log lines.

Optional producer–consumer mode uses ``<|assist_stop|>`` between analysis (consumer) and JSON output (producer).
Validated producer JSON is written under the experiment directory (see ``AES_EXPERIMENT_DIR``).
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

for _root in Path(__file__).resolve().parents:
    if (_root / "rdagent" / "app" / "cli.py").is_file():
        _s = str(_root)
        if _s not in sys.path:
            sys.path.insert(0, _s)
        break

try:
    from dotenv import load_dotenv
    import jsonschema
    import nbformat
    from nbformat.validator import validate
    import loguru  # noqa: F401 — pulled in by rdagent.log; fail fast with a clear message
except ModuleNotFoundError as _e:
    raise SystemExit(
        f"Missing dependency {_e.name!r}. From the RD-Agent repo root: conda activate <env> && pip install -e .\n"
        "Homebrew Python is PEP 668–managed; install into a conda env, not system Python."
    ) from _e

load_dotenv(".env")

from rdagent.log import rdagent_logger as logger
from rdagent.oai.backend.base import APIBackend

ASSIST_STOP = "<|assist_stop|>"

DEFAULT_HYPOTHESIS_DIR = Path(
    os.environ.get("AES_HYPOTHESIS_DIR", "/Users/sweeden/crypto_proj/AES_Hypothesis")
)
DEFAULT_EXPERIMENT_DIR = Path(
    os.environ.get("AES_EXPERIMENT_DIR", "/Users/sweeden/crypto_proj/AES_Experiment")
)

HYPOTHESIS_SUFFIXES = frozenset({".md", ".txt", ".json"})

SYSTEM_PROMPT_LEGACY = """You are an expert technical editor for Jupyter notebooks.
You receive notebook cell sources (markdown and code). Improve clarity, fix factual or typographic errors,
keep an educational tone, and preserve structure unless a fix requires a small reorganization.
Return ONLY a single JSON object, no markdown fences, no commentary.
Schema:
{"cells":[{"cell_index":<int>,"source":"<string>"},...]}
Include one entry per markdown or code cell you were given, in the same order; use \\n for newlines inside source."""

CONSUMER_SYSTEM_PROMPT = f"""You are analyzing a Jupyter notebook (cells JSON in the user message) plus hypothesis context.
Write a concise analysis: issues, priorities, and constraints relative to the hypotheses.
End your reply with a line that contains only the delimiter token (nothing after it on that line):
{ASSIST_STOP}
Do not output JSON or notebook patches in this step."""

PRODUCER_SYSTEM_PROMPT = """You are the producer assistant. Output ONLY one JSON object (no markdown fences, no commentary).
Required top-level keys: "assistant" (string) and "tokens" (string). Optional keys: "agent", "findings", "cells".
- "address" if present must include "property", "findings", and "thinking" (all strings). Optional "street". "thinking" must be exactly five lines long, and follow the scientific method. Evidence is a must!
- "findings" if present is an array of strings.
- "cells" if present is an array of {"cell_index": int, "source": string} for notebook patches.
- "tokens" may be empty or contain a string that parses as JSON with a top-level "cells" array in that same shape (patches may be top-level "cells" or nested under "tokens")."""


def _schema_path() -> Path:
    return Path(__file__).resolve().parent / "schemas" / "aes_experiment_output.schema.json"


def load_output_schema() -> dict[str, Any]:
    raw = _schema_path().read_text(encoding="utf-8")
    return json.loads(raw)


def _strip_json_fence(text: str) -> str:
    t = text.strip()
    m = re.match(r"^```(?:json)?\s*\n?(.*)\n?```\s*$", t, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else t


def split_on_assist_stop(text: str) -> tuple[str, str | None]:
    """Return (before_stop, after_stop_or_none). After part excludes the delimiter."""
    if ASSIST_STOP in text:
        before, after = text.split(ASSIST_STOP, 1)
        rest = after.strip()
        return before.strip(), rest if rest else None
    return text.strip(), None


def load_hypothesis_text(hypothesis_dir: Path) -> str:
    if not hypothesis_dir.is_dir():
        logger.warning(f"Hypothesis directory missing or not a directory: {hypothesis_dir}")
        return ""
    chunks: list[str] = []
    for path in sorted(hypothesis_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in HYPOTHESIS_SUFFIXES:
            chunks.append(path.read_text(encoding="utf-8", errors="replace"))
    if not chunks:
        logger.warning(f"No hypothesis files (.md/.txt/.json) under {hypothesis_dir}")
    return "\n\n---\n\n".join(chunks)


def _normalize_cell_items(items: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("each cell must be an object")
        idx = item.get("cell_index")
        src = item.get("source")
        if not isinstance(idx, int) or not isinstance(src, str):
            raise ValueError("each cell needs int cell_index and string source")
        out.append({"cell_index": idx, "source": src})
    return out


def _parse_cells_json(raw: str) -> list[dict[str, Any]]:
    payload = json.loads(_strip_json_fence(raw))
    cells = payload.get("cells")
    if not isinstance(cells, list):
        raise ValueError("JSON must contain a 'cells' array")
    return _normalize_cell_items(cells)


def _updates_from_experiment_instance(obj: dict[str, Any]) -> list[dict[str, Any]] | None:
    cells = obj.get("cells")
    if isinstance(cells, list) and cells:
        return _normalize_cell_items(cells)
    tok = obj.get("tokens")
    if isinstance(tok, str) and tok.strip():
        try:
            inner = json.loads(tok.strip())
            if isinstance(inner, dict):
                inner_cells = inner.get("cells")
                if isinstance(inner_cells, list) and inner_cells:
                    return _normalize_cell_items(inner_cells)
        except json.JSONDecodeError:
            pass
    return None


def validate_experiment_output(instance: dict[str, Any], schema: dict[str, Any]) -> None:
    jsonschema.validate(instance=instance, schema=schema)


def _serialize_editable_cells(nb: nbformat.NotebookNode) -> list[dict[str, Any]]:
    """Return payload list for markdown/code cells only."""
    editable: list[dict[str, Any]] = []
    for i, cell in enumerate(nb.cells):
        if cell.get("cell_type") not in ("markdown", "code"):
            continue
        src = cell.get("source", "")
        if isinstance(src, list):
            src = "".join(src)
        editable.append(
            {
                "cell_index": i,
                "cell_type": cell["cell_type"],
                "source": src,
            }
        )
    return editable


def _apply_cell_updates(nb: nbformat.NotebookNode, updates: list[dict[str, Any]]) -> None:
    by_index = {u["cell_index"]: u["source"] for u in updates}
    for idx, src in by_index.items():
        if idx < 0 or idx >= len(nb.cells):
            raise ValueError(f"cell_index out of range: {idx}")
        cell = nb.cells[idx]
        if cell.get("cell_type") not in ("markdown", "code"):
            raise ValueError(f"cannot update non-editable cell at index {idx}")
        cell["source"] = src


def _build_user_payload(editable: list[dict[str, Any]], hypothesis_text: str, extra_instruction: str) -> str:
    hyp_block = (
        f"## Hypotheses / constraints\n{hypothesis_text}" if hypothesis_text.strip() else "## Hypotheses / constraints\n(none provided)"
    )
    cells_block = f"## Notebook cells (JSON)\n{json.dumps(editable, indent=2)}"
    extra = f"\n\n## Additional instructions\n{extra_instruction}" if extra_instruction.strip() else ""
    return f"{hyp_block}\n\n{cells_block}{extra}"


def _save_artifact(experiment_dir: Path, name: str, content: str) -> Path:
    experiment_dir.mkdir(parents=True, exist_ok=True)
    path = experiment_dir / name
    path.write_text(content, encoding="utf-8")
    logger.info(f"Wrote artifact {path}")
    return path


def _improve_notebook_loop_round(
    nb: nbformat.NotebookNode,
    *,
    user_instruction: str = "",
    producer_consumer: bool = True,
    single_call: bool = False,
    hypothesis_dir: Path | None = None,
    experiment_dir: Path | None = None,
    round_index: int = 0,
) -> nbformat.NotebookNode:
    """Run one improvement loop round on ``nb`` (mutates in place)."""
    backend = APIBackend()
    editable = _serialize_editable_cells(nb)
    if not editable:
        raise ValueError("No markdown or code cells to improve.")

    hyp_dir = hypothesis_dir if hypothesis_dir is not None else DEFAULT_HYPOTHESIS_DIR
    exp_dir = experiment_dir if experiment_dir is not None else DEFAULT_EXPERIMENT_DIR
    hypothesis_text = load_hypothesis_text(hyp_dir)
    user_payload = _build_user_payload(editable, hypothesis_text, user_instruction)
    schema = load_output_schema()

    if not producer_consumer and not single_call:
        extra = f"\n\nAdditional instructions:\n{user_instruction}" if user_instruction.strip() else ""
        user_prompt = (
            "Improve the following notebook cells. Respond with JSON only.\n"
            f"{json.dumps(editable, indent=2)}{extra}"
        )
        raw = backend.build_messages_and_create_chat_completion(
            user_prompt=user_prompt,
            system_prompt=SYSTEM_PROMPT_LEGACY,
        )
        updates = _parse_cells_json(raw)
        _apply_cell_updates(nb, updates)
        validate(nb)
        return nb

    if single_call:
        user_prompt = (
            f"{user_payload}\n\n"
            f"First write your analysis. Then on its own line output exactly {ASSIST_STOP}.\n"
            "Then output ONLY one JSON object matching the experiment schema (assistant, tokens required; "
            "optional cells array for patches, etc.). No markdown fences."
        )
        raw = backend.build_messages_and_create_chat_completion(
            user_prompt=user_prompt,
            system_prompt=CONSUMER_SYSTEM_PROMPT + "\n" + PRODUCER_SYSTEM_PROMPT,
        )
        before, after = split_on_assist_stop(raw)
        _save_artifact(exp_dir, f"single_call_r{round_index}_{datetime.now(timezone.utc).strftime('%H%M%S')}.txt", raw)
        json_raw = after if after else _strip_json_fence(raw)
        instance = json.loads(_strip_json_fence(json_raw))
        validate_experiment_output(instance, schema)
        _save_artifact(
            exp_dir,
            f"producer_output_r{round_index}_{datetime.now(timezone.utc).strftime('%H%M%S')}.json",
            json.dumps(instance, indent=2),
        )
        updates = _updates_from_experiment_instance(instance)
        if updates:
            _apply_cell_updates(nb, updates)
        validate(nb)
        return nb

    # Two-call producer–consumer
    consumer_raw = backend.build_messages_and_create_chat_completion(
        user_prompt=user_payload,
        system_prompt=CONSUMER_SYSTEM_PROMPT,
        stop=[ASSIST_STOP],
    )
    logger.info(f"Consumer segment (round {round_index}):\n{consumer_raw}")
    _save_artifact(
        exp_dir,
        f"consumer_r{round_index}_{datetime.now(timezone.utc).strftime('%H%M%S')}.txt",
        consumer_raw,
    )

    former_messages = [
        {"role": "user", "content": user_payload},
        {"role": "assistant", "content": consumer_raw},
    ]
    producer_user = (
        "Using the notebook + hypotheses in my first message and your analysis in your previous reply, "
        "output ONLY one JSON object. " + PRODUCER_SYSTEM_PROMPT
    )
    producer_raw = backend.build_messages_and_create_chat_completion(
        user_prompt=producer_user,
        system_prompt=PRODUCER_SYSTEM_PROMPT,
        former_messages=former_messages,
    )
    instance = json.loads(_strip_json_fence(producer_raw))
    validate_experiment_output(instance, schema)
    _save_artifact(
        exp_dir,
        f"producer_output_r{round_index}_{datetime.now(timezone.utc).strftime('%H%M%S')}.json",
        json.dumps(instance, indent=2),
    )
    updates = _updates_from_experiment_instance(instance)
    if updates:
        _apply_cell_updates(nb, updates)
    validate(nb)
    return nb


def improve_notebook_loop(
    input_path: str | Path,
    output_path: str | Path | None = None,
    iterations: int = 5,
    user_instruction: str = "",
    *,
    producer_consumer: bool = False,
    single_call: bool = False,
    hypothesis_dir: Path | None = None,
    experiment_dir: Path | None = None,
) -> Path:
    """
    Load notebook, run ``iterations`` improvement rounds, write result.

    When ``producer_consumer`` or ``single_call`` is True, validated producer JSON and transcripts
    are written under ``experiment_dir`` (default ``AES_EXPERIMENT_DIR``).
    """
    input_path = Path(input_path).resolve()
    if not input_path.is_file():
        raise FileNotFoundError(input_path)

    exp_dir = experiment_dir if experiment_dir is not None else DEFAULT_EXPERIMENT_DIR
    if output_path is None:
        exp_dir.mkdir(parents=True, exist_ok=True)
        output_path = exp_dir / f"{input_path.stem}.improved.ipynb"
    else:
        output_path = Path(output_path).resolve()

    nb = nbformat.read(input_path, as_version=4)
    validate(nb)

    for round_i in range(iterations):
        logger.info(f"Improvement round {round_i + 1}/{iterations}")
        _improve_notebook_loop_round(
            nb,
            user_instruction=user_instruction,
            producer_consumer=producer_consumer,
            single_call=single_call,
            hypothesis_dir=hypothesis_dir,
            experiment_dir=exp_dir,
            round_index=round_i,
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(nb, output_path)
    logger.info(f"Wrote {output_path}")
    return output_path


def main(
    notebook: str,
    output: str | None = None,
    iterations: int = 5,
    instruction: str = "",
    producer_consumer: bool = True,
    single_call: bool = False,
    hypothesis_dir: str | None = None,
    experiment_dir: str | None = None,
) -> None:
    """CLI entry (Fire-style) for ``python -m rdagent.app.utils.improve_notebook``."""
    improve_notebook_loop(
        notebook,
        output_path=output,
        iterations=iterations,
        user_instruction=instruction,
        producer_consumer=producer_consumer,
        single_call=single_call,
        hypothesis_dir=Path(hypothesis_dir) if hypothesis_dir else None,
        experiment_dir=Path(experiment_dir) if experiment_dir else None,
    )


if __name__ == "__main__":
    import fire

    fire.Fire(main)
