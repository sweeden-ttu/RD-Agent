from abc import ABC, abstractmethod

from rdagent.core.experiment import Task


class Scenario(ABC):
    """
    We should include scenario information here. Following inform should not be included
    - method related (e.g. rag... config for a concrete module)
    """

    @property
    @abstractmethod
    def background(self) -> str:
        """Background information"""

    # TODO: We have to change all the sub classes to override get_source_data_desc instead of `source_data`
    def get_source_data_desc(self, task: Task | None = None) -> str:  # noqa: ARG002
        """
        Source data description

        The choice of data may vary based on the specific task at hand.
        """
        return ""

    @property
    def source_data(self) -> str:
        """
        A convenient shortcut for describing source data
        """
        return self.get_source_data_desc()

    # NOTE: we should keep the interface simpler. So some previous interfaces are deleted.
    # If we need some specific function only used in the subclass(no external usage).
    # We should not set them in the base class

    @property
    @abstractmethod
    def rich_style_description(self) -> str:
        """Rich style description to present"""

    @abstractmethod
    def get_scenario_all_desc(
        self,
        task: Task | None = None,
        filtered_tag: str | None = None,
        simple_background: bool | None = None,
    ) -> str:
        """
        Combine all descriptions together

        The scenario description varies based on the task being performed.
        """

    @abstractmethod
    def get_runtime_environment(self) -> str:
        """
        Get the runtime environment information
        """

    @property
    def experiment_setting(self) -> str | None:
        """Get experiment setting and return as rich text string"""
        return None


class AesAvalancheScenario(Scenario):
    """
    A lightweight, concrete scenario for the AES diffusion/avalanche homework experiments.

    This scenario is intentionally *not* a full AES implementation. It exists to host
    background/task descriptions and provide a stable place to hang experiment settings.
    """

    def __init__(self, *, assignment_name: str = "AES avalanche/diffusion experiments") -> None:
        self.assignment_name = assignment_name

    @property
    def background(self) -> str:
        return (
            "We study diffusion (avalanche effect) in AES-128 by tracing intermediate states across rounds.\n"
            "We compare two executions that differ by a single bit (either in plaintext or in key),\n"
            "and compute Hamming distances at each logged stage (SubBytes/ShiftRows/MixColumns/AddRoundKey)."
        )

    @property
    def rich_style_description(self) -> str:
        return (
            f"Scenario: {self.assignment_name}\n\n"
            "Outputs should be tabular per stage/round, reporting byte- and bit-level Hamming distances."
        )

    def get_scenario_all_desc(
        self,
        task: Task | None = None,  # noqa: ARG002
        filtered_tag: str | None = None,  # noqa: ARG002
        simple_background: bool | None = None,  # noqa: ARG002
    ) -> str:
        return f"{self.rich_style_description}\n\nBackground:\n{self.background}"

    def get_runtime_environment(self) -> str:
        return "Python runtime (no external crypto libraries assumed for the scaffolding)."
