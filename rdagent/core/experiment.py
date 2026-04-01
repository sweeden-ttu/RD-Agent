from __future__ import annotations

import io
import os
import platform
import re
import shutil
import typing
import uuid
import zipfile
from abc import ABC, abstractmethod
from collections.abc import Sequence
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generic, TypeVar, Literal

from rdagent.core.conf import RD_AGENT_SETTINGS
from rdagent.core.evaluation import Feedback

if TYPE_CHECKING:
    from rdagent.utils.env import EnvResult


if typing.TYPE_CHECKING:
    from rdagent.core.proposal import Hypothesis
    from rdagent.utils.env import Env

"""
This file contains the all the class about organizing the task in RD-Agent.
"""


class AbsTask(ABC):
    def __init__(self, name: str, version: int = 1) -> None:
        """
        The version of the task, default is 1
        Because qlib tasks execution and kaggle tasks execution are different, we need to distinguish them.
        TODO: We may align them in the future.
        """
        self.version = version
        self.name = name

    @abstractmethod
    def get_task_information(self) -> str:
        """
        Get the task information string to build the unique key
        """


class UserInstructions(list[str]):
    def __str__(self) -> str:
        if self:
            return ("\nUser Instructions (Top priority!):\n" + "\n".join(f"- {ui}" for ui in self)) if self else ""
        return ""


class Task(AbsTask):
    def __init__(
        self,
        name: str,
        version: int = 1,
        description: str = "",
        user_instructions: UserInstructions | None = None,
    ) -> None:
        super().__init__(name, version)
        self.description = description
        self.user_instructions = user_instructions

    def get_task_information(self) -> str:
        return f"Task Name: {self.name}\nDescription: {self.description}{self.user_instructions!s}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name}>"


ASpecificTask = TypeVar("ASpecificTask", bound=Task)
ASpecificFeedback = TypeVar("ASpecificFeedback", bound=Feedback)


@dataclass
class RunningInfo:
    result: object = None  # The result of the experiment, can be different types in different scenarios.
    running_time: float | None = None


class Workspace(ABC, Generic[ASpecificTask, ASpecificFeedback]):
    """
    A workspace is a place to store the task implementation. It evolves as the developer implements the task.
    To get a snapshot of the workspace, make sure call `copy` to get a copy of the workspace.
    """

    def __init__(self, target_task: ASpecificTask | None = None) -> None:
        self.target_task: ASpecificTask | None = target_task
        self.feedback: ASpecificFeedback | None = None
        self.running_info: RunningInfo = RunningInfo()

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> object | None:
        error_message = "execute method is not implemented."
        raise NotImplementedError(error_message)

    @abstractmethod
    def copy(self) -> Workspace:
        error_message = "copy method is not implemented."
        raise NotImplementedError(error_message)

    @property
    @abstractmethod
    def all_codes(self) -> str:
        """
        Get all the code files in the workspace as a single string.
        """

    # when the workspace is mutable inplace, provide support for creating checkpoints and recovering.
    @abstractmethod
    def create_ws_ckp(self) -> None:
        """
        Create an in-memory checkpoint of the workspace so it can be restored later.
        """

    @abstractmethod
    def recover_ws_ckp(self) -> None:
        """
        Restore the workspace from the checkpoint created by :py:meth:`create_ws_ckp`.
        """


ASpecificWS = TypeVar("ASpecificWS", bound=Workspace)


class WsLoader(ABC, Generic[ASpecificTask, ASpecificWS]):
    @abstractmethod
    def load(self, task: ASpecificTask) -> ASpecificWS:
        error_message = "load method is not implemented."
        raise NotImplementedError(error_message)


class FBWorkspace(Workspace):
    """
    File-based task workspace

    The implemented task will be a folder which contains related elements.
    - Data
    - Code Workspace
    - Output
        - After execution, it will generate the final output as file.

    A typical way to run the pipeline of FBWorkspace will be:
    (We didn't add it as a method due to that we may pass arguments into
    `prepare` or `execute` based on our requirements.)

    .. code-block:: python

        def run_pipeline(self, **files: str):
            self.prepare()
            self.inject_files(**files)
            self.execute()

    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.file_dict: dict[str, Any] = (
            {}
        )  # The code injected into the folder, store them in the variable to reproduce the former result
        self.workspace_path: Path = RD_AGENT_SETTINGS.workspace_path / uuid.uuid4().hex
        self.ws_ckp: bytes | None = None  # In-memory checkpoint data created by ``create_ws_ckp``.
        self.change_summary: str | None = None  # The change from the previous version of workspace

    @staticmethod
    def _format_code_dict(code_dict: dict[str, str]) -> str:
        """
        Helper function to format the code dictionary into a string.
        """
        code_string = ""
        for file_name in sorted(code_dict.keys()):
            code_string += f"\nFile Path: {file_name}\n```\n{code_dict[file_name]}\n```"
        return code_string

    @property
    def all_codes(self) -> str:
        """
        Get all the code files in the workspace as a single string, excluding test files.
        """
        filtered_dict = {k: v for k, v in self.file_dict.items() if k.endswith(".py") and "test" not in k}
        return self._format_code_dict(filtered_dict)

    def get_codes(self, pattern: str) -> str:
        """
        Get code files matching a specific pattern as a single string, excluding test files.
        """
        filtered_dict = {
            k: v for k, v in self.file_dict.items() if re.search(pattern, k) and k.endswith(".py") and "test" not in k
        }
        return self._format_code_dict(filtered_dict)

    def prepare(self) -> None:
        """
        Prepare the workspace except the injected code
        - Data
        - Documentation
            typical usage of `*args, **kwargs`:
                Different methods shares the same data. The data are passed by the arguments.
        """
        self.workspace_path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def link_all_files_in_folder_to_workspace(data_path: Path, workspace_path: Path) -> None:
        data_path = Path(data_path).absolute()  # in case of relative path that will be invalid when we change cwd.
        workspace_path = Path(workspace_path)
        for data_file_path in data_path.iterdir():
            workspace_data_file_path = workspace_path / data_file_path.name
            if workspace_data_file_path.exists():
                workspace_data_file_path.unlink()
            if platform.system() in ("Linux", "Darwin"):
                workspace_data_file_path.symlink_to(data_file_path)
            if platform.system() == "Windows":
                os.link(data_file_path, workspace_data_file_path)

    DEL_KEY = "__DEL__"

    def inject_files(self, **files: str) -> None:
        """
        Inject the code into the folder.
        {
            <file name1>: <code>,  // indicate writing <code> into <file name>
                          (create new file or replace existing file)
            <file name2>: "__DEL__"  // indicate removing file name2. When we want to replace a file to a new one,
                          we usually use this
        }
        """
        self.prepare()
        for k, v in files.items():
            target_file_path = self.workspace_path / k  # Define target_file_path before using it
            if v == self.DEL_KEY:  # Use self.DEL_KEY to access the class variable
                if target_file_path.exists():
                    target_file_path.unlink()  # Unlink the file if it exists
                self.file_dict.pop(k, None)  # Safely remove the key from file_dict
            else:
                self.file_dict[k] = v
                target_file_path.parent.mkdir(parents=True, exist_ok=True)
                target_file_path.write_text(v)

    def remove_files(self, file_names: str | list[str]) -> None:
        """
        Remove specified files from the workspace.
        """
        if isinstance(file_names, str):
            file_names = [file_names]
        for file_name in file_names:
            target_file_path = self.workspace_path / file_name
            if target_file_path.exists():
                target_file_path.unlink()  # Unlink the file if it exists
            self.file_dict.pop(file_name, None)  # Safely remove the key from file_dict

    def get_files(self) -> list[Path]:
        """
        Get the environment description.

        To be general, we only return a list of filenames.
        How to summarize the environment is the responsibility of the Developer.
        """
        return list(self.workspace_path.iterdir())

    def inject_code_from_folder(self, folder_path: Path) -> None:
        """
        Load the workspace from the folder
        """
        for file_path in folder_path.rglob("*"):
            if file_path.suffix in (".py", ".yaml", ".md"):
                relative_path = file_path.relative_to(folder_path)
                self.inject_files(**{str(relative_path): file_path.read_text()})

    def inject_code_from_file_dict(self, workspace: FBWorkspace) -> None:
        """
        Load the workspace from the file_dict
        """
        # NOTE: this is a deprecated method, use inject_from_workspace instead
        # TODO: remove this method; it is only for compatibility with old codes
        self.inject_from_workspace(workspace)

    def inject_from_workspace(self, workspace: FBWorkspace) -> None:
        for name, code in workspace.file_dict.items():
            self.inject_files(**{name: code})

    def copy(self) -> FBWorkspace:
        """
        copy the workspace from the original one
        """
        return deepcopy(self)

    def clear(self) -> None:
        """
        Clear the workspace
        """
        shutil.rmtree(self.workspace_path, ignore_errors=True)
        self.file_dict = {}

    def before_execute(self) -> None:
        """
        Before executing the code, we need to prepare the workspace and inject code into the workspace.
        """
        self.prepare()
        self.inject_files(**self.file_dict)

    def execute(self, env: Env, entry: str) -> str:
        """
        Before each execution, make sure to prepare and inject code.
        """
        result = self.run(env, entry)
        return result.stdout  # NOTE: truncating just for aligning with the old code.

    def run(self, env: Env, entry: str) -> EnvResult:
        """
        Execute the code in the environment and return an EnvResult object (stdout, exit_code, running_time).

        Before each execution, make sure to prepare and inject code.
        """
        self.prepare()
        self.inject_files(**self.file_dict)
        return env.run(entry, str(self.workspace_path), env={"PYTHONPATH": "./"})

    def create_ws_ckp(self) -> None:
        """
        Zip the contents of ``workspace_path`` and persist the archive on
        ``self.ws_ckp`` for later restoration via :py:meth:`recover_ws_ckp`.
        """
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in self.workspace_path.rglob("*"):
                # Only include regular files up to 100 KB so that the checkpoint
                # remains lightweight. Larger files (for example, datasets) are
                # expected to be recreated or mounted separately.
                if file_path.is_symlink():
                    # Preserve symbolic links within the archive
                    zi = zipfile.ZipInfo(str(file_path.relative_to(self.workspace_path)))
                    zi.create_system = 3  # indicates Unix
                    zi.external_attr = 0o120777 << 16  # symlink file type + 0777 perms
                    zf.writestr(zi, str(file_path.readlink()))
                elif file_path.is_file():
                    size_limit = RD_AGENT_SETTINGS.workspace_ckp_size_limit
                    if (
                        RD_AGENT_SETTINGS.workspace_ckp_white_list_names is not None
                        and file_path.name in RD_AGENT_SETTINGS.workspace_ckp_white_list_names
                    ) or (size_limit <= 0 or file_path.stat().st_size <= size_limit):
                        zf.write(file_path, file_path.relative_to(self.workspace_path))
        self.ws_ckp = buf.getvalue()

    def recover_ws_ckp(self) -> None:
        """
        Restore the workspace directory from the in-memory checkpoint created by
        :py:meth:`create_ws_ckp`.
        """
        if self.ws_ckp is None:
            msg = "Workspace checkpoint doesn't exist. Call `create_ws_ckp` first."
            raise RuntimeError(msg)
        shutil.rmtree(self.workspace_path, ignore_errors=True)
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        buf = io.BytesIO(self.ws_ckp)
        with zipfile.ZipFile(buf, "r") as zf:
            for info in zf.infolist():
                dest_path = self.workspace_path / info.filename
                # File type bits (upper 4) are in high 16 bits of external_attr
                mode = (info.external_attr >> 16) & 0o170000
                symlink_mode = 0o120000  # Constant for symlink file type in Unix
                if mode == symlink_mode:  # Symlink
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    link_target = zf.read(info).decode()
                    dest_path.symlink_to(link_target)
                elif info.is_dir():
                    dest_path.mkdir(parents=True, exist_ok=True)
                else:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    with dest_path.open("wb") as f:
                        f.write(zf.read(info))
        # NOTE: very important to reduce the size of the object
        self.ws_ckp = None

    def __str__(self) -> str:
        return f"Workspace[{self.workspace_path=}" + (
            "]" if self.target_task is None else f",{self.target_task.name=}]"
        )


ASpecificWSForExperiment = TypeVar("ASpecificWSForExperiment", bound=Workspace)
ASpecificWSForSubTasks = TypeVar("ASpecificWSForSubTasks", bound=Workspace)


class ExperimentPlan(dict[str, Any]):
    """
    A plan for the experiment, which is a dictionary that contains the plan to each stage.
    """


class Experiment(
    ABC,
    Generic[ASpecificTask, ASpecificWSForExperiment, ASpecificWSForSubTasks],
):
    """
    The experiment is a sequence of tasks and the implementations of the tasks after generated by the Developer.
    """

    def __init__(
        self,
        sub_tasks: Sequence[ASpecificTask],
        based_experiments: Sequence[ASpecificWSForExperiment] = [],
        hypothesis: Hypothesis | None = None,
    ) -> None:
        self.hypothesis: Hypothesis | None = hypothesis  # Experiment is optionally generated by hypothesis
        self.sub_tasks: Sequence[ASpecificTask] = sub_tasks
        # None means
        # - initialization placeholder  before implementation
        # - the developer actively skip the task;
        self.sub_workspace_list: list[ASpecificWSForSubTasks | None] = [None] * len(self.sub_tasks)
        # TODO:
        # It will be used in runner in history
        # If we implement the whole workflow, we don't have to use it, then we remove it.
        self.based_experiments: Sequence[ASpecificWSForExperiment] = based_experiments

        self.experiment_workspace: ASpecificWSForExperiment | None = None

        # The experiment may be developed by different developers.
        # Last feedback is used to propagate info to the next developer.
        # Life cycle:
        # - Developer assigns feedback for next component;
        # - Workflow control clears feedback.
        self.prop_dev_feedback: Feedback | None = None

        # TODO: (xiao) I think this is too concrete; we should move it into
        # NOTE: Assumption
        # - only runner will assign this variable
        # - We will always create a new Experiment without copying previous results when we goto the next new loop.
        self.running_info = RunningInfo()
        self.sub_results: dict[str, float] = (
            {}
        )  # TODO: in Kaggle, now sub results are all saved in self.result, remove this in the future.

        # For parallel multi-trace support
        self.local_selection: tuple[int, ...] | None = None
        self.plan: ExperimentPlan | None = (
            None  # To store the planning information for this experiment, should be generated inside exp_gen.gen
        )
        self.user_instructions: UserInstructions | None = None  # To store the user instructions for this experiment

    def set_user_instructions(self, user_instructions: UserInstructions | None) -> None:
        if user_instructions is None:
            return
        if not isinstance(user_instructions, UserInstructions) and isinstance(user_instructions, list):
            user_instructions = UserInstructions(user_instructions)
        self.user_instructions = user_instructions
        for ws in self.sub_workspace_list:
            if ws is not None:
                ws.target_task.user_instructions = user_instructions  # type: ignore[union-attr]
        for task in self.sub_tasks:
            task.user_instructions = user_instructions
        if self.experiment_workspace is not None and self.experiment_workspace.target_task is not None:
            self.experiment_workspace.target_task.user_instructions = user_instructions

    @property
    def result(self) -> object:
        return self.running_info.result

    @result.setter
    def result(self, value: object) -> None:
        self.running_info.result = value

    # when the workspace is mutable inplace, provide support for creating checkpoints and recovering.
    def create_ws_ckp(self) -> None:
        if self.experiment_workspace is not None:
            self.experiment_workspace.create_ws_ckp()
        for ws in self.sub_workspace_list:
            if ws is not None:
                ws.create_ws_ckp()

    def recover_ws_ckp(self) -> None:
        if self.experiment_workspace is not None:
            self.experiment_workspace.recover_ws_ckp()
        for ws in self.sub_workspace_list:
            if ws is not None:
                try:
                    ws.recover_ws_ckp()
                except RuntimeError:
                    # the FBWorkspace is shared between experiment_workspace and sub_workspace_list,
                    # so recover_ws_ckp will raise RuntimeError if a workspace is recovered twice.
                    print("recover_ws_ckp failed due to one workspace is recovered twice.")


ASpecificExp = TypeVar("ASpecificExp", bound=Experiment)
ASpecificPlan = TypeVar("ASpecificPlan", bound=ExperimentPlan)

TaskOrExperiment = TypeVar("TaskOrExperiment", Task, Experiment)


class Loader(ABC, Generic[TaskOrExperiment]):
    @abstractmethod
    def load(self, *args: Any, **kwargs: Any) -> TaskOrExperiment:
        err_msg = "load method is not implemented."
        raise NotImplementedError(err_msg)


# -----------------------------------------------------------------------------
# AES avalanche homework scaffolding (Parts A–D)
# -----------------------------------------------------------------------------

Bytes16 = bytes
StageName = Literal["AddRoundKey", "SubBytes", "ShiftRows", "MixColumns"]


@dataclass(frozen=True)
class AesTraceConfig:
    """
    Configuration hooks matching the homework prompt:
    - disable_shift_rows: if True, ShiftRows is a no-op.
    - custom_mix_matrix: if provided, MixColumns uses this matrix instead of AES MDS matrix.
    """

    disable_shift_rows: bool = False
    custom_mix_matrix: list[list[int]] | None = None


@dataclass(frozen=True)
class AesLoggedState:
    round_idx: int
    stage: StageName
    state: Bytes16


def _require_len_16(x: bytes, *, name: str) -> None:
    if len(x) != 16:
        raise ValueError(f"{name} must be 16 bytes, got {len(x)}")


def flip_bit_at_position(block16: bytes, *, bit_index: int) -> bytes:
    """
    Flip a single bit in a 16-byte block.

    bit_index is 0..127 (inclusive), where 0 targets MSB of byte 0.
    """
    _require_len_16(block16, name="block16")
    if not (0 <= bit_index < 128):
        raise ValueError("bit_index must be in [0, 127]")

    byte_i = bit_index // 8
    bit_in_byte = 7 - (bit_index % 8)
    mask = 1 << bit_in_byte

    b = bytearray(block16)
    b[byte_i] ^= mask
    return bytes(b)


def calculate_bit_hamming_distance(a16: bytes, b16: bytes) -> int:
    _require_len_16(a16, name="a16")
    _require_len_16(b16, name="b16")
    return sum((x ^ y).bit_count() for x, y in zip(a16, b16, strict=True))


def calculate_byte_hamming_distance(a16: bytes, b16: bytes) -> int:
    _require_len_16(a16, name="a16")
    _require_len_16(b16, name="b16")
    return sum(1 for x, y in zip(a16, b16, strict=True) if x != y)


def AES_Encrypt_Trace(plaintext16: bytes, key16: bytes, config: AesTraceConfig) -> list[AesLoggedState]:
    """
    AES-128 encryption tracer implementation.

    It logs the 16-byte state after each stage (AddRoundKey/SubBytes/ShiftRows/MixColumns)
    across rounds, matching the homework prompt:

    - Round 0: AddRoundKey only
    - Rounds 1..9: SubBytes -> ShiftRows (optional no-op) -> MixColumns (standard or custom) -> AddRoundKey
    - Round 10: SubBytes -> ShiftRows (optional no-op) -> AddRoundKey

    State convention:
    - Input/output are 16 bytes.
    - Internally we use AES column-major state: state[r + 4*c] is row r, col c.
    """
    _require_len_16(plaintext16, name="plaintext16")
    _require_len_16(key16, name="key16")
    sbox = _AES_SBOX
    round_keys = _key_expansion_128(key16)

    log: list[AesLoggedState] = []

    state = list(plaintext16)  # 16 ints
    _add_round_key_inplace(state, round_keys[0])
    log.append(AesLoggedState(round_idx=0, stage="AddRoundKey", state=bytes(state)))

    for rnd in range(1, 11):
        _sub_bytes_inplace(state, sbox)
        log.append(AesLoggedState(round_idx=rnd, stage="SubBytes", state=bytes(state)))

        if not config.disable_shift_rows:
            _shift_rows_inplace(state)
        log.append(AesLoggedState(round_idx=rnd, stage="ShiftRows", state=bytes(state)))

        if rnd < 10:
            if config.custom_mix_matrix is not None:
                _mix_columns_custom_inplace(state, config.custom_mix_matrix)
            else:
                _mix_columns_inplace(state)
            log.append(AesLoggedState(round_idx=rnd, stage="MixColumns", state=bytes(state)))

        _add_round_key_inplace(state, round_keys[rnd])
        log.append(AesLoggedState(round_idx=rnd, stage="AddRoundKey", state=bytes(state)))

    return log


# --- AES primitives (AES-128) ------------------------------------------------

# AES S-box (FIPS-197)
_AES_SBOX: tuple[int, ...] = (
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
    0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
    0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
    0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
    0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
    0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
    0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
    0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
    0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
    0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
    0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
    0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
    0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
    0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
    0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
    0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16,
)

_RCON: tuple[int, ...] = (0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36)


def _xtime(a: int) -> int:
    a &= 0xFF
    return (((a << 1) & 0xFF) ^ 0x1B) if (a & 0x80) else ((a << 1) & 0xFF)


def _gf_mul(a: int, b: int) -> int:
    """Multiply in GF(2^8) with AES modulus (0x11B)."""
    a &= 0xFF
    b &= 0xFF
    res = 0
    x = a
    y = b
    for _ in range(8):
        if y & 1:
            res ^= x
        y >>= 1
        x = _xtime(x)
    return res & 0xFF


def _sub_bytes_inplace(state: list[int], sbox: tuple[int, ...]) -> None:
    for i in range(16):
        state[i] = sbox[state[i]]


def _shift_rows_inplace(state: list[int]) -> None:
    # state[r + 4*c] layout. Shift each row r left by r.
    tmp = state.copy()
    for r in range(4):
        row = [tmp[r + 4 * c] for c in range(4)]
        row = row[r:] + row[:r]
        for c in range(4):
            state[r + 4 * c] = row[c]


def _mix_single_column(col: list[int]) -> list[int]:
    a0, a1, a2, a3 = col
    return [
        _gf_mul(0x02, a0) ^ _gf_mul(0x03, a1) ^ a2 ^ a3,
        a0 ^ _gf_mul(0x02, a1) ^ _gf_mul(0x03, a2) ^ a3,
        a0 ^ a1 ^ _gf_mul(0x02, a2) ^ _gf_mul(0x03, a3),
        _gf_mul(0x03, a0) ^ a1 ^ a2 ^ _gf_mul(0x02, a3),
    ]


def _mix_columns_inplace(state: list[int]) -> None:
    for c in range(4):
        col = [state[r + 4 * c] for r in range(4)]
        mixed = _mix_single_column(col)
        for r in range(4):
            state[r + 4 * c] = mixed[r] & 0xFF


def _mix_columns_custom_inplace(state: list[int], m: list[list[int]]) -> None:
    """
    Custom MixColumns where m is a 4x4 matrix of coefficients in GF(2^8).
    """
    if len(m) != 4 or any(len(row) != 4 for row in m):
        raise ValueError("custom_mix_matrix must be 4x4")
    for c in range(4):
        a = [state[r + 4 * c] for r in range(4)]
        out = []
        for r in range(4):
            acc = 0
            for k in range(4):
                coeff = m[r][k] & 0xFF
                acc ^= _gf_mul(coeff, a[k])
            out.append(acc & 0xFF)
        for r in range(4):
            state[r + 4 * c] = out[r]


def _add_round_key_inplace(state: list[int], round_key16: bytes) -> None:
    for i in range(16):
        state[i] ^= round_key16[i]


def _rot_word(w: list[int]) -> list[int]:
    return [w[1], w[2], w[3], w[0]]


def _sub_word(w: list[int], sbox: tuple[int, ...]) -> list[int]:
    return [sbox[b] for b in w]


def _key_expansion_128(key16: bytes) -> list[bytes]:
    """
    AES-128 key expansion.
    Returns 11 round keys, each 16 bytes.
    """
    _require_len_16(key16, name="key16")
    sbox = _AES_SBOX

    # words are 4 bytes; need 44 words for AES-128 (4*(Nr+1) where Nr=10)
    w: list[list[int]] = []
    for i in range(4):
        w.append([key16[4 * i + 0], key16[4 * i + 1], key16[4 * i + 2], key16[4 * i + 3]])

    for i in range(4, 44):
        temp = w[i - 1].copy()
        if i % 4 == 0:
            temp = _sub_word(_rot_word(temp), sbox)
            temp[0] ^= _RCON[(i // 4) - 1]
        w.append([w[i - 4][j] ^ temp[j] for j in range(4)])

    round_keys: list[bytes] = []
    for r in range(11):
        rk = []
        for i in range(4):
            rk.extend(w[4 * r + i])
        round_keys.append(bytes(rk))
    return round_keys


@dataclass(frozen=True)
class AesAvalancheRow:
    part: str
    round_idx: int
    stage: StageName
    byte_hd: int
    bit_hd: int


def _compare_traces(part_name: str, t1: list[AesLoggedState], t2: list[AesLoggedState]) -> list[AesAvalancheRow]:
    if len(t1) != len(t2):
        raise ValueError("Traces must have identical length/stages to compare.")
    rows: list[AesAvalancheRow] = []
    for s1, s2 in zip(t1, t2, strict=True):
        if (s1.round_idx, s1.stage) != (s2.round_idx, s2.stage):
            raise ValueError("Trace stage alignment mismatch.")
        rows.append(
            AesAvalancheRow(
                part=part_name,
                round_idx=s1.round_idx,
                stage=s1.stage,
                byte_hd=calculate_byte_hamming_distance(s1.state, s2.state),
                bit_hd=calculate_bit_hamming_distance(s1.state, s2.state),
            )
        )
    return rows


def Execute_Part_A(*, bit_positions: list[int] | None = None) -> list[list[AesAvalancheRow]]:
    """
    Part A: Avalanche across rounds (plaintext bit flip), standard AES.

    Returns one table (list of rows) per bit flip position.
    """
    key = bytes([0x00] * 16)
    base_plaintext = bytes([0x00] * 16)
    config = AesTraceConfig(disable_shift_rows=False, custom_mix_matrix=None)

    if bit_positions is None:
        bit_positions = list(range(10))  # TODO: adjust to match the prompt's required 10 positions

    tables: list[list[AesAvalancheRow]] = []
    for bit_index in bit_positions:
        p_prime = flip_bit_at_position(base_plaintext, bit_index=bit_index)
        t_p = AES_Encrypt_Trace(base_plaintext, key, config)
        t_p2 = AES_Encrypt_Trace(p_prime, key, config)
        tables.append(_compare_traces("Part A", t_p, t_p2))
    return tables


def Execute_Part_B(*, bit_positions: list[int] | None = None) -> list[list[AesAvalancheRow]]:
    """
    Part B: Disable ShiftRows and observe diffusion degradation.
    """
    key = bytes([0x00] * 16)
    base_plaintext = bytes([0x00] * 16)
    config = AesTraceConfig(disable_shift_rows=True, custom_mix_matrix=None)

    if bit_positions is None:
        bit_positions = list(range(10))  # TODO: adjust to match the prompt's required 10 positions

    tables: list[list[AesAvalancheRow]] = []
    for bit_index in bit_positions:
        p_prime = flip_bit_at_position(base_plaintext, bit_index=bit_index)
        t_p = AES_Encrypt_Trace(base_plaintext, key, config)
        t_p2 = AES_Encrypt_Trace(p_prime, key, config)
        tables.append(_compare_traces("Part B", t_p, t_p2))
    return tables


def Execute_Part_C(*, bit_positions: list[int] | None = None) -> list[list[AesAvalancheRow]]:
    """
    Part C: Modify MixColumns matrix.
    """
    key = bytes([0x00] * 16)
    base_plaintext = bytes([0x00] * 16)

    m_new = [
        [0x01, 0x01, 0x00, 0x00],
        [0x00, 0x01, 0x01, 0x00],
        [0x00, 0x00, 0x01, 0x01],
        [0x00, 0x00, 0x00, 0x01],
    ]
    config = AesTraceConfig(disable_shift_rows=False, custom_mix_matrix=m_new)

    if bit_positions is None:
        bit_positions = list(range(10))  # TODO: adjust to match the prompt's required 10 positions

    tables: list[list[AesAvalancheRow]] = []
    for bit_index in bit_positions:
        p_prime = flip_bit_at_position(base_plaintext, bit_index=bit_index)
        t_p = AES_Encrypt_Trace(base_plaintext, key, config)
        t_p2 = AES_Encrypt_Trace(p_prime, key, config)
        tables.append(_compare_traces("Part C", t_p, t_p2))
    return tables


def Execute_Part_D() -> dict[str, list[AesAvalancheRow]]:
    """
    Part D: Key-bit flip experiment (fixed all-zero plaintext), repeat configurations A/B/C.

    Returns a mapping: config_name -> table rows.
    """
    fixed_plaintext = bytes([0x00] * 16)
    base_key = bytes([0x00] * 16)
    modified_key = flip_bit_at_position(base_key, bit_index=0)  # TODO: choose bit per prompt if needed

    m_new = [
        [0x01, 0x01, 0x00, 0x00],
        [0x00, 0x01, 0x01, 0x00],
        [0x00, 0x00, 0x01, 0x01],
        [0x00, 0x00, 0x00, 0x01],
    ]

    configs: list[tuple[str, AesTraceConfig]] = [
        ("Part A Config", AesTraceConfig(disable_shift_rows=False, custom_mix_matrix=None)),
        ("Part B Config", AesTraceConfig(disable_shift_rows=True, custom_mix_matrix=None)),
        ("Part C Config", AesTraceConfig(disable_shift_rows=False, custom_mix_matrix=m_new)),
    ]

    out: dict[str, list[AesAvalancheRow]] = {}
    for name, conf in configs:
        t_k = AES_Encrypt_Trace(fixed_plaintext, base_key, conf)
        t_k2 = AES_Encrypt_Trace(fixed_plaintext, modified_key, conf)
        out[f"Part D - {name}"] = _compare_traces(f"Part D - {name}", t_k, t_k2)
    return out
