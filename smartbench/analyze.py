#!/usr/bin/env python3

"""Module for running smart contract analyzers for testing contracts."""

# Standard Library
import multiprocessing
import os
import re
import shlex
import subprocess
import sys

from datetime import datetime
from multiprocessing import Process, Queue
from typing import Dict, List, Optional, Tuple

# Library
from smartbench import annotation, printer, result, validator
from smartbench.benchmark import TestConfig
from smartbench.docker import DockerContainer
from smartbench.printer import (
    debug,
    error_traceback,
    print_unless,
    safe_print,
    warning,
)
from smartbench.result import AnalysisResult
from smartbench.solidity import solc
from smartbench.tools.config import SMARTBENCH_ROOT, Confuzzius
from smartbench.tools.tool import Tool


RESULTS_DIR_RELATIVE_PATH = "results"


class AnalysisJob:
    """Class modelling an analysis job, which can run locally or using Docker."""

    def __init__(
        self,
        id: int,
        tool: Tool,
        test_files: List[str],
        test_configs: Optional[Dict[str, TestConfig]],
        job_output_dir_host: str,
        job_output_dir_docker: str,
        docker_container: DockerContainer,
        annot_format: Optional[str] = None,
        solc_version: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.id = int(id)
        self.tool: Tool = tool

        # List of test file, which are relative path to the `/root/`
        # folder in a Docker container
        self.test_files: List[str] = list(test_files)
        self.test_configs: Optional[Dict[str, TestConfig]] = test_configs
        self.job_output_dir_host: str = job_output_dir_host
        self.job_output_dir_docker: str = job_output_dir_docker
        self.docker_container: DockerContainer = docker_container
        self.solc_version = solc_version
        self.annot_format: Optional[str] = annot_format

        # Output directory of a job to store results of all test files
        self.timeout: Optional[int] = timeout

    def __str__(self):
        return f"{self.docker_container.name}: {len(self.test_files)} tasks"


def log_input_test_file(
    tool: Tool,
    input_file: str,
    result_dir: str,
) -> bool:
    """Record execution log of an analysis tool in TOML format."""
    log_file = tool.configure_log_file(result_dir)
    try:
        with open(log_file, "w", encoding="utf-8") as file:
            file.write(f"# Execution log of {tool.name}:\n\n")

            # Input file
            file.write(f"{'-' * 55}\n")
            file.write("[input test file]\n")
            file.write(f"{'-' * 55}\n\n")
            file.write(f"{input_file}\n\n")

        return True
    except Exception:
        error_traceback(f"Failed to log input test file to: {log_file}")
        return False


def log_analysis_command(
    tool: Tool,
    input_file: str,
    command: str,
    result_dir: str,
) -> bool:
    """Record execution log of an analysis tool in TOML format."""
    log_file = tool.configure_log_file(result_dir)
    try:
        with open(log_file, "a", encoding="utf-8") as file:
            # Analysis command
            file.write(f"{'-' * 55}\n")
            file.write("[command]\n")
            file.write(f"{'-' * 55}\n\n")
            file.write(f"{command}\n\n")

        return True
    except Exception:
        error_traceback(f"Failed to log analysis command to: {log_file}")
        return False


def log_analysis_output(
    tool: Tool,
    proc,
    result_dir: str,
) -> bool:
    """Record execution log of an analysis tool. `stderr` should be redirected
    to `stdout` by the executable script."""
    # Read analysis output from process and write to log file
    log_file = tool.configure_log_file(result_dir)
    try:
        with open(log_file, "a", encoding="utf-8") as file:
            # Analysis output
            file.write(f"{'-' * 55}\n")
            file.write("[output]\n")
            file.write(f"{'-' * 55}\n\n")

            while True:
                if not (line := proc.stdout.readline()):
                    break
                line = f"{line.decode('utf-8')}"
                # Remove ansi color from output log
                ansi_pattern = re.compile(r"\x1B\[\d+(;\d+){0,2}m")
                line = ansi_pattern.sub("", line)
                file.write(line)
        return True
    except Exception:
        error_traceback(f"Failed to log analysis output to: {log_file}")
        return False


def collect_target_contracts_and_solc_version(
    tool: Tool,
    test_file: str,
    test_config_dict: Optional[Dict[str, TestConfig]],
    solc_version: Optional[str] = None,
) -> Tuple[List[str], Optional[str]]:
    """Collect list of testing contracts directly from the test file or from a
    contract list file."""
    if test_config_dict is None:
        # Auto detect target contracts and compiler version if no test config is
        # specified
        return solc.get_target_contracts_and_solc_version(
            test_file, True, solc_version
        )
    else:
        # Collect target contracts and compiler versions that are explicitly
        # specified by users

        # Find test configuration for the input file
        test_config = None
        test_file_name = test_file.removesuffix(".sol")
        for config_file_name in test_config_dict:
            if test_file_name.endswith(config_file_name):
                test_config = test_config_dict[config_file_name]

        # Return empty contract list if no configuration is specified for this
        # input file.
        if test_config is None:
            return ([], None)

        # Always use the compiler version specified in test configure if
        # possible, otherwise, use the compiler version specified by CLI
        if test_config.compiler_version is not None:
            solc_version = test_config.compiler_version

        # Use contract names from test config
        contract_names = test_config.target_contracts

        # If contract names or compiler version are not specified in test
        # config, auto-detect them
        if contract_names == [] or solc_version is None:
            (
                contract_names_detected,
                solc_version_detected,
            ) = solc.get_target_contracts_and_solc_version(
                test_file, True, solc_version
            )

        if contract_names == []:
            contract_names = contract_names_detected
        if solc_version is None:
            solc_version = solc_version_detected

        return (contract_names, solc_version)


def analyze_test_file(
    tool: Tool,
    test_file: str,
    test_configs: Optional[Dict[str, TestConfig]],
    test_output_dir_host: str,
    test_output_dir_docker: str,
    container: DockerContainer,
    annot_format: Optional[str] = None,
    solc_version: Optional[str] = None,
    job_id: Optional[int] = None,
    timeout: Optional[int] = None,
    validate: bool = False,  # REVIEW: consider merging `validate` with `benchmarking` as 1 param
    parallel_mode: bool = False,
) -> Optional[AnalysisResult]:
    """Analyze `test_file` using `tool` and write result to `test_output_dir`.

    If `validate` is True, the detected issues will be validated with
    bug annotations in the testing files."""

    if not log_input_test_file(tool, test_file, test_output_dir_host):
        return None

    # Run the analysis
    if parallel_mode:
        safe_print(f"\ndocker:{container.name}: {test_file}")
    else:
        printer.print_medium_dashed_separator_line()
        safe_print(f"Analyzing: {test_file}\n")

    (contracts, solc_version) = collect_target_contracts_and_solc_version(
        tool, test_file, test_configs, solc_version
    )

    if not contracts:
        warning(
            f"No testing contract is specified for: {test_file}\n\n"
            "Skip analyzing it!"
        )
        return None

    if solc_version is None:
        warning(
            f"No Solc version is specifieed or detected for: {test_file}\n\n"
            "Skip analyzing it!"
        )
        return None

    cmd = tool.make_analysis_command(
        test_file,
        contracts,
        test_output_dir_docker,
        solc_version,
        container,
        timeout,
        annot_format=annot_format,
    )

    if cmd is None:
        warning(f"Failed to make analysis command for tool: {tool.name}\n")
        return None

    if not log_analysis_command(tool, test_file, cmd, test_output_dir_host):
        warning(f"Failed to log analysis command for tool: {tool.name}\n")
        return None

    debug(f"Analysis Command: {cmd}")
    print_unless(parallel_mode, f"Output dir: {test_output_dir_host}\n")

    try:
        # Run the analyzer
        with subprocess.Popen(
            shlex.split(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        ) as proc:
            # Read process output and write to log file on the fly
            log_analysis_output(tool, proc, test_output_dir_host)
    except Exception:
        error_traceback(f"{container.name}: failed to run command: {cmd}")
        return None

    res = None
    if not parallel_mode:
        debug(f"PARSE FILE: {test_output_dir_host}")
        res = result.parse_test_file_output_dir(
            tool, test_file, test_output_dir_host, None, validate
        )

        if res is None:
            safe_print(f"No analysis result for: {test_file}")
        elif res.is_successful:
            res.print_detailed_summary()
        else:
            warning(f"Failed to analyze test file: {test_file}")

    return res


def start_docker_containers(tool: Tool, jobs) -> List[DockerContainer]:
    """Start all docker containers to run analysis jobs."""
    printer.print_short_double_separator_line()
    safe_print("Preparing docker containers...\n")

    # By convention, containers are named as ${TOOL_ID}-${JOB_ID}
    container_names = [f"{tool.id}-{i}" for i in range(1, jobs + 1)]

    containers = []
    for name in container_names:
        container = DockerContainer(name)
        containers.append(container)
        container.start()

    return containers


def stop_docker_containers(containers: List[DockerContainer]):
    """Stop all docker containers after finishing analysis jobs."""
    printer.print_short_double_separator_line()
    safe_print("Cleaning docker containers...\n")

    for container in containers:
        container.stop()


def run_analysis_job(
    job: AnalysisJob,
    result_queue: Queue,
    validate: bool = False,
    benchmarking: bool = False,
    parallel_mode: bool = False,
) -> None:
    """Run an analysis job. Output will be stored in `result_queue`."""
    all_results: List[AnalysisResult] = []

    for test_file in job.test_files:
        # Configure test output directory for the current test file
        tool_output_dir_host = job.job_output_dir_host
        tool_output_dir_docker = job.job_output_dir_docker

        test_output_dir_host = os.path.join(tool_output_dir_host, test_file)
        test_output_dir_docker = os.path.join(tool_output_dir_docker, test_file)

        # Analyze the test file
        try:
            if res := analyze_test_file(
                job.tool,
                test_file,
                job.test_configs,
                test_output_dir_host,
                test_output_dir_docker,
                job.docker_container,
                job.annot_format,
                job.solc_version,
                job.id,
                job.timeout,
                validate,
                parallel_mode,
            ):
                if res is not None:
                    all_results.append(res)
        except Exception as err:
            error_traceback(
               f"An exception occurred when running analysis job!\n\n{err}"
            )
            pass

    result_queue.put(all_results)


def run_analysis_tool(
    tool: Tool,
    test_files: List[str],
    test_configs: Optional[Dict[str, TestConfig]],
    tool_output_dir_host: str,
    tool_output_dir_docker: str,
    solc_version: Optional[str] = None,
    timeout: Optional[int] = None,
    keep_docker_alive: bool = False,
    jobs: int = 1,
    validate: bool = False,
    benchmarking: bool = False,
    annot_format: Optional[str] = None,
) -> List[AnalysisResult]:
    """Run one analysis tool for all `test_files` and write all results
    to `tool_output_dir`.

    If `validate` is True, the detected issues will be validated with
    bug annotations in the testing files.

    Allow launching multiple Docker containers to run in parallel.
    """

    printer.print_long_double_separator_line()
    safe_print(f"Running analysis tool: {tool.name} ({tool.id})")

    all_results: List[AnalysisResult] = []

    # Start Docker containers if using Docker mode
    docker_containers = start_docker_containers(tool, jobs)

    printer.print_short_double_separator_line()
    safe_print("Running analysis jobs...")

    # Distribute test files to containers
    test_batches: List[List[str]] = []
    for _ in range(jobs):
        test_batches.append([])

    for idx, test_file in enumerate(test_files):
        idx = idx % jobs

        # Get relative path of the test file compared to `SMARTBENCH_ROOT`
        # so that the Docker container can access to it
        test_file_path = os.path.relpath(test_file, SMARTBENCH_ROOT)
        test_batches[idx].append(test_file_path)

    analysis_jobs = []
    for i in range(jobs):
        container = docker_containers[i]
        analysis_job = AnalysisJob(
            i,
            tool,
            test_batches[i],
            test_configs,
            tool_output_dir_host,
            tool_output_dir_docker,
            container,
            annot_format,
            solc_version,
            timeout,
        )
        analysis_jobs.append(analysis_job)

    # Prepare to run analysis jobs in parallel if needed.
    processes = []
    parallel_mode = jobs > 1

    # Use a queue to store all results
    result_queue: Queue[List[AnalysisResult]] = multiprocessing.Queue()

    # Run all analysis jobs
    for analysis_job in analysis_jobs:
        proc = Process(
            target=run_analysis_job,
            args=(
                analysis_job,
                result_queue,
                validate,
                benchmarking,
                parallel_mode,
            ),
        )
        processes.append(proc)
        proc.start()

    # Get result from queue
    for proc in processes:
        all_results.extend(result_queue.get())

    for proc in processes:
        proc.join()

    if not keep_docker_alive:
        # Stop Docker containers after analysis
        stop_docker_containers(docker_containers)

    return all_results


def perform_analysis(
    tools: List[Tool],
    test_files: List[str],
    test_configs: Optional[Dict[str, TestConfig]],
    result_dir: Optional[str] = None,
    solc_version: Optional[str] = None,
    timeout: Optional[int] = None,
    keep_docker_alive: bool = False,
    jobs: int = 1,
    validate: bool = False,
    benchmarking: bool = False,
    annot_format: Optional[str] = None,
) -> List[AnalysisResult]:
    """Function to run all tools to analyze all test files.

    If `validate` is True, the detected issues will be validated with
    bug annotations in the testing files.

    When `jobs` > 1, the analysis can be performed concurrently.
    """
    # Prepare output directory for all tests and all tools in this run
    safe_print(f"Start analyzing {len(test_files)} test files...")
    if result_dir is None:
        results_dir_host = results_dir_docker = os.path.join(
            RESULTS_DIR_RELATIVE_PATH,
            datetime.now().strftime("%Y_%m_%d_%H_%M_%S"),
        )
    else:
        results_dir_docker = RESULTS_DIR_RELATIVE_PATH
        results_dir_host = result_dir

    if not os.path.exists(results_dir_host):
        os.makedirs(results_dir_host)

    # Perform the analysis
    all_results = []
    for tool in tools:
        tool_output_dir_host = os.path.join(results_dir_host, tool.id)
        tool_output_dir_docker = os.path.join(results_dir_docker, tool.id)
        results = run_analysis_tool(
            tool,
            test_files,
            test_configs,
            tool_output_dir_host,
            tool_output_dir_docker,
            solc_version,
            timeout,
            keep_docker_alive,
            jobs,
            validate,
            benchmarking,
            annot_format,
        )

        all_results.extend(results)

    printer.print_short_double_separator_line()
    safe_print("Benchmarking completed!\n")
    safe_print(f"Results are recorded at: {results_dir_host}")

    if jobs == 1 and benchmarking:
        result.print_benchmarking_results(results_dir_host, all_results)

    return all_results
