#!/usr/bin/env python3

"""Module for running smart contract analyzers for testing contracts."""

# Standard Library
import multiprocessing
import os
import shlex
import signal
import subprocess

from datetime import datetime
from multiprocessing import Process, Queue
from typing import Dict, List, Optional

# Library
from smartbench import annotation, printer, result, validator
from smartbench.docker import DockerContainer
from smartbench.issue import Issue
from smartbench.printer import (
    debug,
    error_traceback,
    print_unless,
    safe_print,
    warning,
)
from smartbench.process import ignore_sigint
from smartbench.result import AnalysisResult
from smartbench.solidity import solc
from smartbench.tools.config import RESULTS_DIR, SMARTBENCH_ROOT, Confuzzius
from smartbench.tools.tool import Tool


class AnalysisJob:
    """Class modelling an analysis job, which can run locally or using Docker."""

    def __init__(
        self,
        id: int,
        tool: Tool,
        test_files: List[str],
        test_contracts: Optional[Dict[str, List[str]]],
        job_output_dir: str,
        solc_version: Optional[str] = None,
        timeout: Optional[int] = None,
        docker_container: Optional[DockerContainer] = None,
    ):
        self.id = int(id)
        self.tool: Tool = tool

        # List of test file, which are relative path to the `/root/`
        # folder in a Docker container
        self.test_files: List[str] = list(test_files)
        self.test_contracts: Optional[Dict[str, List[str]]] = test_contracts
        self.solc_version = solc_version

        # Output directory of a job to store results of all test files
        self.job_output_dir: str = job_output_dir
        self.timeout: Optional[int] = timeout
        self.docker_container: Optional[DockerContainer] = docker_container

    def __str__(self):
        return f"{self.docker_container.name}: {len(self.test_files)} tasks"


def log_analysis_command(
    tool: Tool,
    input_file: str,
    command: str,
    result_dir: str,
) -> bool:
    """Record execution log of an analysis tool in TOML format."""
    log_file = tool.configure_log_file(result_dir)
    try:
        with open(log_file, "w", encoding="utf-8") as file:
            separator = "-" * 55
            file.write(f"# Execution log of {tool.name}:\n\n")

            # Input file
            file.write(f"{separator}\n")
            file.write("[input contract]\n")
            file.write(f"{separator}\n\n")
            file.write(f"{input_file}\n\n")

            # Analysis command
            file.write(f"{separator}\n")
            file.write("[command]\n")
            file.write(f"{separator}\n\n")
            file.write(f"{command}\n\n")

            # Output section
            file.write(f"{separator}\n")
            file.write("[output]\n")
            file.write(f"{separator}\n\n")
        return True
    except Exception:
        error_traceback(f"Failed to log analysis command to: {log_file}")
        return False


def log_analysis_output(
    tool: Tool,
    proc,
    result_dir: str,
) -> None:
    """Record execution log of an analysis tool in TOML format.
    `stderr` should be redirected to `stdout` by the executable script.
    """
    # Read analysis output from process and write to log file
    log_file = tool.configure_log_file(result_dir)
    with open(log_file, "a", encoding="utf-8") as file:
        while True:
            if not (line := proc.stdout.readline()):
                break
            file.write(f"{line.decode('utf-8')}")


def log_analysis_info(
    tools: List[Tool], test_files: List[str], result_dir: str
) -> None:
    """Record analysis log of all tools."""
    log_file = os.path.join(result_dir, "smartbench_log.toml")
    with open(log_file, "w", encoding="utf-8") as file:
        file.write("# Smartbench benchmarking log \n\n")

        # Log tools
        tools_info = ", ".join([f'"{tool.id}"' for tool in tools])
        file.write(f"tools = [{tools_info}]\n\n")

        # Log test files
        if test_files is None or len(test_files) == 0:
            file.write("test_files = []\n")
        else:
            tests_info = ",\n  ".join([f'"{test}"' for test in test_files])
            file.write(f"test_files = [\n  {tests_info}\n]\n")


def collect_testing_contracts(
    tool: Tool,
    test_file: str,
    test_contracts: Optional[Dict[str, List[str]]],
    solc_version: Optional[str] = None,
) -> List[str]:
    """Collect list of testing contracts directly from the test file or from a
    contract list file."""

    # Auto detect target contracts if they is not specified explicitly
    if test_contracts is None:
        return solc.get_candidate_testing_contracts(
            test_file, False, solc_version
        )

    # Collect target contracts specified explicitly by users
    test_file_name = os.path.basename(test_file).removesuffix(".sol")
    contract_names = test_contracts.get(test_file_name)

    # Checking results
    if contract_names is None:
        return []
    elif isinstance(tool, Confuzzius) and len(contract_names) > 1:
        raise ValueError(
            "Confuzzius does not support specifiying multiple target contracts"
        )

    return contract_names


def analyze_test_file(
    tool: Tool,
    test_file: str,
    test_contracts: Optional[Dict[str, List[str]]],
    test_output_dir: str,
    solc_version: Optional[str] = None,
    job_id: Optional[int] = None,
    container: Optional[DockerContainer] = None,
    timeout: Optional[int] = None,
    validate: bool = False,  # REVIEW: consider merging `validate` with `benchmarking` as 1 param
    benchmarking: bool = False,
    parallel_mode: bool = False,
) -> AnalysisResult:
    """Analyze `test_file` using `tool` and write result to `test_output_dir`.

    If `validate` is True, the detected issues will be validated with
    bug annotations in the testing files."""

    test_name = os.path.basename(test_file)

    # Reset issue index counter for the current test file
    Issue.index_counter = 1

    # Run the analysis
    if parallel_mode:
        if container is None:
            runner = f"local:{tool.id}-{job_id}"
        else:
            runner = f"docker:{container.name}"
        safe_print(f"{runner}: {test_file}\n")
    else:
        printer.print_medium_dashed_separator_line()
        safe_print(f"Analyzing: {test_file}\n")

    contracts = collect_testing_contracts(
        tool, test_file, test_contracts, solc_version
    )

    if not contracts:
        safe_print(
            f"No input contract is specified for test file: {test_file}\n\n"
            "Skip analyzing it!"
        )
        return AnalysisResult(tool, test_name, False)

    # safe_print("Test contracts:", contracts)

    try:
        cmd = tool.make_analysis_command(
            test_file,
            contracts,
            test_output_dir,
            solc_version,
            container,
            timeout,
        )
    except Exception:
        error_traceback(f"Failed to make anlaysis command for: {tool.id}")
        return AnalysisResult(tool, test_name, False)

    if cmd is None:
        warning(f"Unable to make analysis command for tool: {tool.name}\n")
        return AnalysisResult(tool, test_name, False)

    if not log_analysis_command(tool, test_file, cmd, test_output_dir):
        return AnalysisResult(tool, test_name, False)

    debug(f"Analysis Command: {cmd}")
    print_unless(parallel_mode, f"Output dir: {test_output_dir}\n")

    try:
        # Run the analyzer
        with subprocess.Popen(
            shlex.split(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            # preexec_fn=ignore_sigint,
            shell=False,
        ) as proc:
            # Read process output and write to log file on the fly
            log_analysis_output(tool, proc, test_output_dir)
    except Exception:
        runner = "local" if container is None else f"docker:{container.name}"
        if parallel_mode and container:
            error_traceback(f"{container.name}: failed to run command: {cmd}")
        else:
            error_traceback(f"Failed to run command: {cmd}")
        return AnalysisResult(tool, test_name, False)

    # Process analysis output
    if (issues := tool.parse_analysis_output(test_output_dir)) is None:
        return AnalysisResult(tool, test_name, False)

    for issue in issues:
        print_unless(parallel_mode, "- " + str(issue))

    # Validating reported issues
    bug_annots = []
    validation = None
    if validate or benchmarking:
        print_unless(parallel_mode, "Bug annotations:")
        bug_annots = annotation.parse_bug_annotations(test_file)
        for annot in bug_annots:
            print_unless(parallel_mode, f"- {annot.print_concise()}")
        print_unless(parallel_mode, "")
        validation = validator.validate_issues(tool, issues, bug_annots)

    res = AnalysisResult(tool, test_name, True, issues, bug_annots, validation)

    # Print benchmarking information
    res.print_detailed_summary(parallel_mode)

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
        # Configure test output directory for the curren test file
        tool_output_dir = job.job_output_dir
        if job.docker_container:
            test_output_dir = os.path.join(tool_output_dir, test_file)
        elif test_file.startswith(SMARTBENCH_ROOT):
            test_file_rel_path = os.path.relpath(test_file, SMARTBENCH_ROOT)
            test_output_dir = os.path.join(tool_output_dir, test_file_rel_path)
        else:
            common_path = os.path.commonpath([tool_output_dir, test_file])
            test_file_rel_path = os.path.relpath(test_file, common_path)
            test_output_dir = os.path.join(tool_output_dir, test_file_rel_path)

        # Analyze the test file
        if res := analyze_test_file(
            job.tool,
            test_file,
            job.test_contracts,
            test_output_dir,
            job.solc_version,
            job.id,
            job.docker_container,
            job.timeout,
            validate,
            benchmarking,
            parallel_mode,
        ):
            all_results.append(res)

    result_queue.put(all_results)


def run_analysis_tool(
    tool: Tool,
    test_files: List[str],
    test_contracts: Optional[Dict[str, List[str]]],
    tool_output_dir: str,
    solc_version: Optional[str] = None,
    timeout: Optional[int] = None,
    use_docker: bool = True,
    keep_docker_alive: bool = False,
    jobs: int = 1,
    validate: bool = False,
    benchmarking: bool = False,
) -> List[AnalysisResult]:
    """Run one analysis tool for all `test_files` and write all results
    to `tool_output_dir`.

    If `validate` is True, the detected issues will be validated with
    bug annotations in the testing files.

    Allow launching multiple Docker containers to run in parallel.
    """

    printer.print_long_double_separator_line()
    safe_print(f"Running analysis tool: {tool.name}")

    # When running in Docker mode, use relative path of output directory
    # mounted to the Docker container so that the container can access to it
    if use_docker:
        tool_output_dir = os.path.relpath(tool_output_dir, SMARTBENCH_ROOT)

    all_results: List[AnalysisResult] = []

    # Start Docker containers if using Docker mode
    docker_containers = []
    if use_docker:
        docker_containers = start_docker_containers(tool, jobs)

    printer.print_short_double_separator_line()
    safe_print("Running analysis jobs...\n")

    # Distribute test files to containers
    test_batches: List[List[str]] = []
    for _ in range(jobs):
        test_batches.append([])

    for idx, test_file in enumerate(test_files):
        idx = idx % jobs

        if use_docker:
            # Get relative path of the test file compared to `SMARTBENCH_ROOT`
            # so that the Docker container can access to it
            test_file_rel_path = os.path.relpath(test_file, SMARTBENCH_ROOT)
            test_batches[idx].append(test_file_rel_path)
        else:
            test_batches[idx].append(test_file)

    analysis_jobs = []
    for i in range(jobs):
        container = None if not docker_containers else docker_containers[i]
        analysis_job = AnalysisJob(
            i,
            tool,
            test_batches[i],
            test_contracts,
            tool_output_dir,
            solc_version,
            timeout,
            container,
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

    if use_docker and not keep_docker_alive:
        # Stop Docker containers after analysis
        stop_docker_containers(docker_containers)

    return all_results


def perform_analysis(
    tools: List[Tool],
    test_files: List[str],
    test_contracts: Optional[Dict[str, List[str]]],
    solc_version: Optional[str] = None,
    timeout: Optional[int] = None,
    use_docker: bool = True,
    keep_docker_alive: bool = False,
    jobs: int = 1,
    validate: bool = False,
    benchmarking: bool = False,
) -> List[AnalysisResult]:
    """Function to run all tools to analyze all test files.

    If `validate` is True, the detected issues will be validated with
    bug annotations in the testing files.

    When `jobs` > 1, the analysis can be performed concurrently.
    """
    # Prepare output directory for all tests and all tools in this run
    safe_print("Start analyzing all test cases...")
    results_dir = os.path.join(
        RESULTS_DIR,
        datetime.now().strftime("%Y_%m_%d_%H_%M_%S"),
    )
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    # Record the analysis details to a log file
    log_analysis_info(tools, test_files, results_dir)

    # Perform the analysis
    all_results = []
    for tool in tools:
        tool_output_dir = os.path.join(results_dir, tool.id)
        results = run_analysis_tool(
            tool,
            test_files,
            test_contracts,
            tool_output_dir,
            solc_version,
            timeout,
            use_docker,
            keep_docker_alive,
            jobs,
            validate,
            benchmarking,
        )

        all_results.extend(results)

    printer.print_short_double_separator_line()
    safe_print("Benchmarking completed!\n")
    safe_print(f"Results are recorded at: {results_dir}")

    if benchmarking:
        result.print_benchmarking_results(results_dir, all_results)

    return all_results
