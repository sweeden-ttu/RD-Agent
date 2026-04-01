"""
CLI entrance for all rdagent application.

This will
- make rdagent a nice entry and
- autoamtically load dotenv
"""

import sys
from pathlib import Path

for _root in Path(__file__).resolve().parents:
    if (_root / "rdagent" / "app" / "cli.py").is_file():
        _s = str(_root)
        if _s not in sys.path:
            sys.path.insert(0, _s)
        break

from dotenv import load_dotenv

load_dotenv(".env")
# 1) Make sure it is at the beginning of the script so that it will load dotenv before initializing BaseSettings.
# 2) The ".env" argument is necessary to make sure it loads `.env` from the current directory.

import subprocess
from importlib.resources import path as rpath
from typing import Optional

import typer
from typing_extensions import Annotated

# Loop / scenario modules run a loguru preflight on import; defer imports to subcommand bodies
# so ``python path/to/cli.py --help`` works under Homebrew Python before ``pip install -e .``.

app = typer.Typer(no_args_is_help=True)

CheckoutOption = Annotated[bool, typer.Option("--checkout/--no-checkout", "-c/-C")]
CheckEnvOption = Annotated[bool, typer.Option("--check-env/--no-check-env", "-e/-E")]
CheckDockerOption = Annotated[bool, typer.Option("--check-docker/--no-check-docker", "-d/-D")]
CheckPortsOption = Annotated[bool, typer.Option("--check-ports/--no-check-ports", "-p/-P")]


def ui(port=19899, log_dir="", debug: bool = False, data_science: bool = False):
    """
    start web app to show the log traces.
    """
    if data_science:
        with rpath("rdagent.log.ui", "dsapp.py") as app_path:
            cmds = ["streamlit", "run", app_path, f"--server.port={port}"]
            subprocess.run(cmds)
        return
    with rpath("rdagent.log.ui", "app.py") as app_path:
        cmds = ["streamlit", "run", app_path, f"--server.port={port}"]
        if log_dir or debug:
            cmds.append("--")
        if log_dir:
            cmds.append(f"--log_dir={log_dir}")
        if debug:
            cmds.append("--debug")
        subprocess.run(cmds)


def server_ui(port=19899):
    """
    start the Flask log server in real time
    """
    from rdagent.log.server.app import main as log_server_main

    log_server_main(port=port)


def ds_user_interact(port=19900):
    """
    start web app to show the log traces in real time
    """
    commands = ["streamlit", "run", "rdagent/log/ui/ds_user_interact.py", f"--server.port={port}"]
    subprocess.run(commands)


@app.command(name="fin_factor")
def fin_factor_cli(
    path: Optional[str] = None,
    step_n: Optional[int] = None,
    loop_n: Optional[int] = None,
    all_duration: Optional[str] = None,
    checkout: CheckoutOption = True,
):
    from rdagent.app.qlib_rd_loop.factor import main as fin_factor

    fin_factor(path=path, step_n=step_n, loop_n=loop_n, all_duration=all_duration, checkout=checkout)


@app.command(name="fin_model")
def fin_model_cli(
    path: Optional[str] = None,
    step_n: Optional[int] = None,
    loop_n: Optional[int] = None,
    all_duration: Optional[str] = None,
    checkout: CheckoutOption = True,
):
    from rdagent.app.qlib_rd_loop.model import main as fin_model

    fin_model(path=path, step_n=step_n, loop_n=loop_n, all_duration=all_duration, checkout=checkout)


@app.command(name="fin_quant")
def fin_quant_cli(
    path: Optional[str] = None,
    step_n: Optional[int] = None,
    loop_n: Optional[int] = None,
    all_duration: Optional[str] = None,
    checkout: CheckoutOption = True,
):
    from rdagent.app.qlib_rd_loop.quant import main as fin_quant

    fin_quant(path=path, step_n=step_n, loop_n=loop_n, all_duration=all_duration, checkout=checkout)


@app.command(name="fin_factor_report")
def fin_factor_report_cli(
    report_folder: Optional[str] = None,
    path: Optional[str] = None,
    all_duration: Optional[str] = None,
    checkout: CheckoutOption = True,
):
    from rdagent.app.qlib_rd_loop.factor_from_report import main as fin_factor_report

    fin_factor_report(report_folder=report_folder, path=path, all_duration=all_duration, checkout=checkout)


@app.command(name="general_model")
def general_model_cli(report_file_path: str):
    from rdagent.app.general_model.general_model import extract_models_and_implement as general_model

    general_model(report_file_path)


@app.command(name="data_science")
def data_science_cli(
    path: Optional[str] = None,
    checkout: CheckoutOption = True,
    step_n: Optional[int] = None,
    loop_n: Optional[int] = None,
    timeout: Optional[str] = None,
    competition: Optional[str] = None,
):
    from rdagent.app.data_science.loop import main as data_science

    data_science(
        path=path,
        checkout=checkout,
        step_n=step_n,
        loop_n=loop_n,
        timeout=timeout,
        competition=competition,
    )


@app.command(name="llm_finetune")
def llm_finetune_cli(
    path: Optional[str] = None,
    checkout: CheckoutOption = True,
    benchmark: Optional[str] = None,
    benchmark_description: Optional[str] = None,
    dataset: Optional[str] = None,
    base_model: Optional[str] = None,
    upper_data_size_limit: Optional[int] = None,
    step_n: Optional[int] = None,
    loop_n: Optional[int] = None,
    timeout: Optional[str] = None,
):
    from rdagent.app.finetune.llm.loop import main as llm_finetune

    llm_finetune(
        path=path,
        checkout=checkout,
        benchmark=benchmark,
        benchmark_description=benchmark_description,
        dataset=dataset,
        base_model=base_model,
        upper_data_size_limit=upper_data_size_limit,
        step_n=step_n,
        loop_n=loop_n,
        timeout=timeout,
    )


@app.command(name="grade_summary")
def grade_summary_cli(log_folder: str):
    from rdagent.log.mle_summary import grade_summary

    grade_summary(log_folder)


app.command(name="ui")(ui)
app.command(name="server_ui")(server_ui)


@app.command(name="health_check")
def health_check_cli(
    check_env: CheckEnvOption = True,
    check_docker: CheckDockerOption = True,
    check_ports: CheckPortsOption = True,
):
    from rdagent.app.utils.health_check import health_check

    health_check(check_env=check_env, check_docker=check_docker, check_ports=check_ports)


@app.command(name="improve_notebook")
def improve_notebook_cli(
    notebook: Annotated[str, typer.Argument(help="Path to the source .ipynb")],
    output: Annotated[
        Optional[str],
        typer.Option(
            "--output",
            "-o",
            help="Output path (default: <name>.improved.ipynb under experiment-dir)",
        ),
    ] = None,
    iterations: Annotated[int, typer.Option("--iterations", "-n", help="Number of LLM improvement passes")] = 5,
    instruction: Annotated[
        str,
        typer.Option("--instruction", "-i", help="Extra instructions for each pass"),
    ] = "",
    producer_consumer: Annotated[
        bool,
        typer.Option(
            "--producer-consumer/--no-producer-consumer",
            help="Consumer then producer with <|assist_stop|>; validates JSON schema and writes artifacts",
        ),
    ] = False,
    single_call: Annotated[
        bool,
        typer.Option(
            "--single-call/--no-single-call",
            help="One completion: analysis, <|assist_stop|>, then JSON (overrides two-call if both set)",
        ),
    ] = False,
    hypothesis_dir: Annotated[
        Optional[str],
        typer.Option("--hypothesis-dir", help="Directory of hypothesis .md/.txt/.json (default: AES_HYPOTHESIS_DIR)"),
    ] = None,
    experiment_dir: Annotated[
        Optional[str],
        typer.Option("--experiment-dir", help="Artifacts and default output notebook dir (default: AES_EXPERIMENT_DIR)"),
    ] = None,
):
    """Improve markdown and code cells in a Jupyter notebook using the configured chat model."""
    from pathlib import Path

    from rdagent.app.utils.improve_notebook import improve_notebook_loop

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


@app.command(name="collect_info")
def collect_info_cli():
    from rdagent.app.utils.info import collect_info

    collect_info()


app.command(name="ds_user_interact")(ds_user_interact)


if __name__ == "__main__":
    app()
