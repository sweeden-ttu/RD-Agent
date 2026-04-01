"""Offline tests for improve_notebook helpers (no LLM calls)."""

import json
from pathlib import Path

import jsonschema
import nbformat
import pytest

from rdagent.app.utils import improve_notebook as ib


@pytest.mark.offline
def test_split_on_assist_stop() -> None:
    before, after = ib.split_on_assist_stop(f"hello\n{ib.ASSIST_STOP}\n{{\"x\":1}}")
    assert before == "hello"
    assert after == '{"x":1}'
    b2, a2 = ib.split_on_assist_stop("no delimiter")
    assert b2 == "no delimiter"
    assert a2 is None


@pytest.mark.offline
def test_load_output_schema_and_validate_minimal() -> None:
    schema = ib.load_output_schema()
    instance = {"assistant": "test", "tokens": ""}
    ib.validate_experiment_output(instance, schema)


@pytest.mark.offline
def test_validate_experiment_output_with_address() -> None:
    schema = ib.load_output_schema()
    good = {
        "assistant": "a",
        "tokens": "",
        "address": {"property": "p", "findings": "f", "thinking": "12345"},
    }
    ib.validate_experiment_output(good, schema)
    bad = {
        "assistant": "a",
        "tokens": "",
        "address": {"property": "p", "findings": "f", "thinking": "12"},
    }
    with pytest.raises(jsonschema.ValidationError):
        ib.validate_experiment_output(bad, schema)


@pytest.mark.offline
def test_updates_from_experiment_instance_top_level_cells() -> None:
    obj = {"assistant": "x", "tokens": "", "cells": [{"cell_index": 0, "source": "print(1)"}]}
    u = ib._updates_from_experiment_instance(obj)
    assert u == [{"cell_index": 0, "source": "print(1)"}]


@pytest.mark.offline
def test_updates_from_experiment_instance_tokens_json() -> None:
    inner = json.dumps({"cells": [{"cell_index": 1, "source": "x"}]})
    obj = {"assistant": "x", "tokens": inner}
    u = ib._updates_from_experiment_instance(obj)
    assert u == [{"cell_index": 1, "source": "x"}]


@pytest.mark.offline
def test_apply_cell_updates_roundtrip(tmp_path: Path) -> None:
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_code_cell("a = 1"))
    nb.cells.append(nbformat.v4.new_markdown_cell("hi"))
    ib._apply_cell_updates(nb, [{"cell_index": 0, "source": "a = 2"}])
    assert nb.cells[0].source == "a = 2"
    assert nb.cells[1].source == "hi"
