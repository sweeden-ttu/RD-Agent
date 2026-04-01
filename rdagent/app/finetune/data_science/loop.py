import asyncio
import sys
from pathlib import Path

for _root in Path(__file__).resolve().parents:
    if (_root / "rdagent" / "app" / "cli.py").is_file():
        _s = str(_root)
        if _s not in sys.path:
            sys.path.insert(0, _s)
        break

try:
    import loguru  # noqa: F401
except ModuleNotFoundError as _e:
    raise SystemExit(
        "rdagent dependencies are missing (e.g. loguru). From the rdagent repo root, use conda and run:\n"
        "  conda activate RD-Agent && pip install -e .\n"
        "Homebrew Python is PEP 668–managed; install into a conda env, not system Python."
    ) from _e

import fire

from rdagent.app.data_science.conf import DS_RD_SETTING
from rdagent.app.finetune.data_science.conf import update_settings
from rdagent.core.utils import import_class
from rdagent.log import rdagent_logger as logger
from rdagent.scenarios.data_science.loop import DataScienceRDLoop


def main(
    model: str | None = None,
    competition: str | None = None,
):
    """
    Parameters
    ----------
    competition :
        Competition name.

    Auto R&D Evolving loop for models finetune.
    You can continue running a session by using the command:
    .. code-block:: bash
        dotenv run -- python rdagent/app/finetune/data_science/loop.py --competition aerial-cactus-identification
    """
    if not competition:
        raise Exception("Please specify competition name.")

    model_folder = Path(DS_RD_SETTING.local_data_path) / competition / "prev_model"
    if not model_folder.exists():
        raise Exception(f"Please put the model path to {model_folder}.")
    update_settings(competition)
    rd_loop: DataScienceRDLoop = DataScienceRDLoop(DS_RD_SETTING)
    asyncio.run(rd_loop.run())


if __name__ == "__main__":
    fire.Fire(main)
