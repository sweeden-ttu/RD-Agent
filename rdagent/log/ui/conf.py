from pydantic_settings import SettingsConfigDict

from rdagent.core.conf import ExtendedBaseSettings


class UIBasePropSetting(ExtendedBaseSettings):
    model_config = SettingsConfigDict(env_prefix="UI_", protected_namespaces=())

    default_log_folders: list[str] = ["./log"]

    baseline_result_path: str = "./baseline.csv"

    aide_path: str = "./aide"

    amlt_path: str = ".data/amlt"

    static_path: str = "/Users/sweeden/crypto_proj/AES_Hypothesis/git_ignore_folder/static"

    trace_folder: str = "/Users/sweeden/crypto_proj/AES_Hypothesis/git_ignore_folder/traces"

    enable_cache: bool = True


UI_SETTING = UIBasePropSetting()
