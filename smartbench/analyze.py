#!/usr/bin/env python3

"""Module for running smart contract analyzers for testing contracts."""

# Standard Library
import os
import shlex
import signal
import subprocess
import threading
import traceback

from datetime import datetime
from multiprocessing import Process
from subprocess import CompletedProcess
from typing import List, Optional

# Library
from smartbench import annotation, printer, result, solc, validator
from smartbench.docker import DockerContainer, DockerJob
from smartbench.issue import Issue
from smartbench.printer import debug
from smartbench.tools.config import RESULTS_DIR, SMARTBENCH_ROOT
from smartbench.tools.mythril.mythril import Mythril
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
    validate=False,
    benchmarking=False,
) -> List[Issue]:
    """Analyze `test_file` using `tool` and write result to `test_output_dir`.

    If `validate` is True, the detected issues will be validated with
    bug annotations in the testing files."""

    # Reset issue index counter for the current test file
    Issue.index_counter = 1

    try:
        # Run the analysis
        print(f"{'-' * 45}\n")
        print(f"Analyzing: {test_file}\n")

        contracts = solc.get_candidate_testing_contracts(test_file)
        # print("Test contracts:", contracts)

        cmd = tool.make_analysis_command(
            test_file,
            contracts,
            test_output_dir,
            container,
            timeout,
        )

        if cmd is None:
            print(f"Unable to make analysis command for tool: {tool.name}\n")
            return []

        log_analysis_command(tool, test_file, cmd, test_output_dir)

        debug(f"COMMAND: {cmd}")
        print(f"Output dir: {test_output_dir}")

        # Prepare to run the analyzer
        proc = subprocess.Popen(
            shlex.split(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Run the analyzer
        (stdout, _) = proc.communicate()

        log_analysis_output(tool, stdout, test_output_dir)

        if isinstance(tool, Mythril):
            # the results of `mythril` is in `stdout`
            tool.write_to_output_file(stdout, test_output_dir)

    except ValueError as err:
        print(f"Failed to run command: {cmd}\n")
        print(f"** Error: {err}")
        traceback.print_exc()
        return []

    # Process results
    issues = result.process_analysis_result(tool, test_output_dir)
    for issue in issues:
        print("- " + str(issue))

    # Validating results
    bug_annots = None
    validation = None
    test_name = os.path.basename(test_file)
    if validate or benchmarking:
        print("Bug annotations:")
        bug_annots = annotation.parse_bug_annotations(test_file)
        for annot in bug_annots:
            print(f"- {annot.print_concise()}")
        print("")
        validation = validator.validate_issues(
            tool, test_file, issues, bug_annots
        )

    # Print benchmarking information

    result.print_summary(tool, test_name, issues, bug_annots, validation)
    return issues


def run_analysis_tool_locally(
    tool: Tool,
    test_files: List[str],
    tool_output_dir: str,
    timeout=None,
    validate=False,
    benchmarking=False,
) -> List[Issue]:
    """Run one analysis tool for all `test_files` and write all results
    to `tool_output_dir`.

    If `validate` is True, the detected issues will be validated with
    bug annotations in the testing files.

    """
    printer.print_long_double_horizontal_line()
    print(f"Running analysis tool: {tool.name}\n")

    # For local run, extract a common path in all test files
    # to shorten the output file names when storing the results
    test_files_common_path = os.path.commonpath(test_files)
    test_file_parent = os.path.dirname(test_files_common_path)

    all_issues = []

    for test_file in test_files:
        # Prepare output directory for one test file
        test_file_rel_path = os.path.relpath(test_file, start=test_file_parent)
        test_output_dir = os.path.join(tool_output_dir, test_file_rel_path)
        if not os.path.exists(test_output_dir):
            os.makedirs(test_output_dir)

        # Analyze the test file
        issues = analyze_test_file(
            tool,
            test_file,
            test_output_dir,
            None,
            timeout,
            validate,
            benchmarking,
        )
        all_issues += issues

    return all_issues


def start_docker_containers(tool: Tool, jobs) -> List[DockerContainer]:
    printer.print_short_double_horizontal_line()
    print("Preparing docker containers...")

    if jobs == 1:
        container_names = [tool.id]
    else:
        container_names = [f"{tool.id}-{i}" for i in range(1, jobs + 1)]

    containers = []
    for name in container_names:
        container = DockerContainer(name)
        containers.append(container)
        container.start()

    return containers


def stop_docker_containers(containers: List[DockerContainer]):
    printer.print_short_double_horizontal_line()
    print("Cleaning docker containers...")

    for container in containers:
        container.stop()


def run_docker_job(
    job: DockerJob,
    validate=False,
    benchmarking=False,
) -> List[Issue]:
    all_issues = []

    for test_file in job.test_files:
        test_output_dir = os.path.join(job.job_output_dir, test_file)

        # Analyze the test file
        issues = analyze_test_file(
            job.tool,
            test_file,
            test_output_dir,
            job.container,
            job.timeout,
            validate,
            benchmarking,
        )
        all_issues.extend(issues)

    return all_issues


def run_analysis_tool_using_docker(
    tool: Tool,
    test_files: List[str],
    tool_output_dir: str,
    timeout=None,
    jobs=1,
    validate=False,
    benchmarking=False,
) -> List[Issue]:
    """Run one analysis tool for all `test_files` and write all results
    to `tool_output_dir`.

    If `validate` is True, the detected issues will be validated with
    bug annotations in the testing files.

    Allow launching multiple Docker containers to run in parallel.
    """

    printer.print_long_double_horizontal_line()
    print(f"Running analysis tool: {tool.name}\n")

    # Get relative path of output directory before passing to the Docker container
    # so that the container can access to it
    tool_output_dir_docker = os.path.relpath(tool_output_dir, SMARTBENCH_ROOT)

    all_issues: List[Issue] = []

    containers = start_docker_containers(tool, jobs)

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

    docker_jobs = []
    for i in range(jobs):
        docker_job = DockerJob(
            containers[i],
            tool,
            test_batches[i],
            tool_output_dir_docker,
            timeout,
        )
        docker_jobs.append(docker_job)

    # Run docker jobs in parallel
    processes = []
    for docker_job in docker_jobs:
        proc = Process(target=run_docker_job, args=(docker_job, validate))
        processes.append(proc)
        proc.start()
        # issues = run_docker_job(docker_job, validate)
        # all_issues.extend(issues)

    for proc in processes:
        proc.join()

    # Stop Docker containers after analysis
    stop_docker_containers(containers)

    return all_issues


def perform_analysis(
    tools: List[Tool],
    test_files: List[str],
    timeout=None,
    use_docker=True,
    jobs=1,
    validate=False,
    benchmarking=False,
) -> List[Issue]:
    """Function to run all tools to analyze all test files.

    If `validate` is True, the detected issues will be validated with
    bug annotations in the testing files.

    When `jobs` > 1, the analysis can be performed concurrently.
    """
    # Prepare output directory for all tests and all tools in this run
    print("Start analyzing all test cases...\n")
    results_dir = os.path.join(
        RESULTS_DIR,
        datetime.now().strftime("%Y_%m_%d_%H_%M_%S"),
    )
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    # Record the analysis details to a log file
    log_analysis_info(tools, test_files, results_dir)

    # Perform the analysis
    all_issues = []
    for tool in tools:
        tool_output_dir = os.path.join(results_dir, tool.id)
        if use_docker:
            issues = run_analysis_tool_using_docker(
                tool,
                test_files,
                tool_output_dir,
                timeout,
                jobs,
                validate,
                benchmarking,
            )
        else:
            issues = run_analysis_tool_locally(
                tool,
                test_files,
                tool_output_dir,
                timeout,
                validate,
                benchmarking,
            )

        all_issues += issues

    print("Benchmarking completed!\n")
    print(f"Results are recorded at: {results_dir}")

    return all_issues
