#!/usr/bin/env python3

"""Module for running smart contract analyzers for testing contracts."""

# Standard Library
import multiprocessing
import os
import shlex
import signal
import subprocess
import sys
import tempfile
import threading
import traceback

from datetime import datetime
from multiprocessing import Process, Queue
from subprocess import CompletedProcess, SubprocessError
from typing import List, Optional

# Library
from smartbench import annotation, printer, result, solc, validator
from smartbench.docker import AnalysisJob, DockerContainer
from smartbench.issue import Issue
from smartbench.printer import (
    debug,
    print_short_double_horizontal_line,
    print_unless,
    safe_print,
    safe_warning,
    warning,
)
from smartbench.result import AnalysisResult
from smartbench.tools.config import RESULTS_DIR, SMARTBENCH_ROOT
from smartbench.tools.tool import Tool


def log_analysis_command(
    tool: Tool,
    input_file: str,
    command: str,
    result_dir: str,
) -> None:
    """Record execution log of an analysis tool in TOML format."""
    log_file = tool.configure_log_file(result_dir)
    with open(log_file, "w", encoding="utf-8") as file:
        file.write(f"# Execution log of {tool.name}:\n\n")

        # Log input
        file.write("-------------------------------------------------------\n")
        file.write("[input contract]\n")
        file.write(
            "-------------------------------------------------------\n\n"
        )
        file.write(f"{input_file}\n\n")

        file.write("-------------------------------------------------------\n")
        file.write("[command]\n")
        file.write(
            "-------------------------------------------------------\n\n"
        )
        file.write(f"{command}\n\n")


def log_analysis_output(
    tool: Tool,
    stdout,
    result_dir: str,
) -> None:
    """Record execution log of an analysis tool in TOML format.
    `stderr` should be redirected to `stdout` by the executable script.
    """
    log_file = tool.configure_log_file(result_dir)
    with open(log_file, "a", encoding="utf-8") as file:
        file.write("-------------------------------------------------------\n")
        file.write("[output]\n")
        file.write(
            "-------------------------------------------------------\n\n"
        )
        output = stdout.decode("utf-8")
        file.write(f"{output}\n\n")


def log_analysis_info(
    tools: List[Tool], test_files: List[str], result_dir: str
):
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


def analyze_test_file(
    tool: Tool,
    test_file: str,
    test_output_dir: str,
    container=Optional[DockerContainer],
    timeout=None,
    validate=False,  # REVIEW: consider merging `validate` with `benchmarking` as 1 param
    benchmarking=False,
    parallel_mode=False,
) -> Optional[AnalysisResult]:
    """Analyze `test_file` using `tool` and write result to `test_output_dir`.

    If `validate` is True, the detected issues will be validated with
    bug annotations in the testing files."""

    # Reset issue index counter for the current test file
    Issue.index_counter = 1

    # Run the analysis
    if parallel_mode:
        runner = (
            "local-runner" if container is None else f"docker:{container.name}"
        )
        safe_print(f"{runner}: {test_file}\n")
    else:
        safe_print(f"{'-' * 45}\n")
        safe_print(f"Analyzing: {test_file}\n")

    try:
        contracts = solc.get_candidate_testing_contracts(test_file)
    except ValueError as err:
        warning(f"Failed to get testing contract names from: {test_file}!")
        print_unless(parallel_mode, f"** Error: {err}")
        return None

    # safe_print("Test contracts:", contracts)

    cmd = tool.make_analysis_command(
        test_file,
        contracts,
        test_output_dir,
        container,
        timeout,
    )

    if cmd is None:
        warning(f"Unable to make analysis command for tool: {tool.name}\n")
        return None

    log_analysis_command(tool, test_file, cmd, test_output_dir)

    debug(f"COMMAND: {cmd}")
    print_unless(parallel_mode, f"Output dir: {test_output_dir}")

    try:
        # Prepare to run the analyzer
        proc = subprocess.Popen(
            shlex.split(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )

        # Run the analyzer
        (stdout, _) = proc.communicate()

        # log_analysis_output(tool, stdout, test_output_dir)

    except SubprocessError as err:
        if parallel_mode and container:
            safe_warning(f"{container.name}: failed to run command: {cmd}\n")
        else:
            warning(f"Failed to run command: {cmd}\n")
            safe_print(f"** Error: {err}")
            traceback.print_exc()
        return None

    # Process analysis output
    issues = tool.parse_analysis_output(test_output_dir)

    for issue in issues:
        print_unless(parallel_mode, "- " + str(issue))

    # Validating reported issues
    bug_annots = []
    test_name = os.path.basename(test_file)
    validation = None
    if validate or benchmarking:
        print_unless(parallel_mode, "Bug annotations:")
        bug_annots = annotation.parse_bug_annotations(test_file)
        for annot in bug_annots:
            print_unless(parallel_mode, f"- {annot.print_concise()}")
        print_unless(parallel_mode, "")
        validation = validator.validate_issues(tool, issues, bug_annots)

    res = AnalysisResult(tool, test_name, issues, bug_annots, validation)

    # Print benchmarking information
    res.print_detailed_summary(parallel_mode)

    return res


def start_docker_containers(tool: Tool, jobs) -> List[DockerContainer]:
    print_short_double_horizontal_line()
    safe_print("Preparing docker containers...")

    # By convention, containers are named as ${TOOL_ID}-${JOB_ID}
    container_names = [f"{tool.id}-{i}" for i in range(1, jobs + 1)]

    containers = []
    for name in container_names:
        container = DockerContainer(name)
        containers.append(container)
        container.start()

    return containers


def stop_docker_containers(containers: List[DockerContainer]):
    printer.print_short_double_horizontal_line()
    safe_print("Cleaning docker containers...")

    for container in containers:
        container.stop()


def run_analysis_job(
    job: AnalysisJob,
    result_queue: Queue,
    validate=False,
    benchmarking=False,
    parallel_mode=False,
) -> None:
    """Run an analysis job. Output will be stored in `result_queue`."""
    all_results: List[AnalysisResult] = []

    for test_file in job.test_files:
        test_output_dir = os.path.join(job.job_output_dir, test_file)

        # Analyze the test file
        if res := analyze_test_file(
            job.tool,
            test_file,
            test_output_dir,
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
    tool_output_dir: str,
    timeout=None,
    use_docker=True,
    jobs=1,
    validate=False,
    benchmarking=False,
) -> List[AnalysisResult]:
    """Run one analysis tool for all `test_files` and write all results
    to `tool_output_dir`.

    If `validate` is True, the detected issues will be validated with
    bug annotations in the testing files.

    Allow launching multiple Docker containers to run in parallel.
    """

    printer.print_long_double_horizontal_line()
    safe_print(f"Running analysis tool: {tool.name}\n")

    # When running in Docker mode, use relative path of output directory mounted
    # to the Docker container so that the container can access to it
    if use_docker:
        tool_output_dir = os.path.relpath(tool_output_dir, SMARTBENCH_ROOT)

    all_results: List[AnalysisResult] = []

    # Start Docker containers if using Docker mode
    if use_docker:
        docker_containers = start_docker_containers(tool, jobs)
    else:
        docker_containers = [None] * jobs

    safe_print("")
    printer.print_short_double_horizontal_line()
    safe_print("Running analysis jobs...\n")

    # Distribute test files to containers
    test_batches: List[List[str]] = []
    for _ in range(jobs):
        test_batches.append([])
    for idx, test_file in enumerate(test_files):
        idx = idx % jobs

        # Get relative path of the test file compared to `SMARTBENCH_ROOT`
        # so that the Docker container can access to it
        test_file_rel_path = os.path.relpath(test_file, SMARTBENCH_ROOT)
        test_batches[idx].append(test_file_rel_path)

    analysis_jobs = []
    for i in range(jobs):
        analysis_job = AnalysisJob(
            tool,
            test_batches[i],
            tool_output_dir,
            timeout,
            docker_containers[i],
        )
        analysis_jobs.append(analysis_job)

    # Prepare to run analysis jobs in parallel if needed.
    processes = []
    parallel_mode = jobs > 1

    # Use a queue to store all results
    result_queue: Queue = multiprocessing.Queue()

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

    if use_docker:
        # Stop Docker containers after analysis
        stop_docker_containers(docker_containers)

    return all_results


def perform_analysis(
    tools: List[Tool],
    test_files: List[str],
    timeout=None,
    use_docker=True,
    jobs=1,
    validate=False,
    benchmarking=False,
) -> List[AnalysisResult]:
    """Function to run all tools to analyze all test files.

    If `validate` is True, the detected issues will be validated with
    bug annotations in the testing files.

    When `jobs` > 1, the analysis can be performed concurrently.
    """
    # Prepare output directory for all tests and all tools in this run
    safe_print("Start analyzing all test cases...\n")
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
            tool_output_dir,
            timeout,
            use_docker,
            jobs,
            validate,
            benchmarking,
        )

        all_results.extend(results)

    print_short_double_horizontal_line()
    safe_print("Benchmarking completed!\n")
    safe_print(f"Results are recorded at: {results_dir}")

    if benchmarking:
        result.print_benchmarking_results(results_dir, all_results)

    return all_results
