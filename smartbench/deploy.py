#!/usr/bin/env python3

"""Module for deploying smart contracts for testing."""

# Standard Library
import os
import shlex
import subprocess

from datetime import datetime
from subprocess import CompletedProcess
from typing import List

# Library
from smartbench import result
from smartbench.solidity import solc
from smartbench.tools.config import DEPLOY_DIR
from smartbench.tools.tool import Tool


def log_deployment_result(
    tool: Tool,
    input_file: str,
    command: str,
    output: CompletedProcess,
    result_dir: str,
):
    """Record execution log of an analysis tool in TOML format."""
    log_file = tool.configure_log_file(result_dir)
    with open(log_file, "w", encoding="utf-8") as file:
        file.write(f"# Deployment log of {tool.name}:\n\n")

        # Log input
        file.write("[input]\n")
        file.write(f'test_file = """{input_file}"""\n\n')
        file.write(f'command = """{command}"""\n\n')

        # Log output
        file.write("[output]\n")
        stdout = output.stdout.decode("utf-8")
        file.write(f'stdout = """{stdout}"""\n\n')
        stderr = output.stderr.decode("utf-8")
        file.write(f'stderr = """{stderr}"""')


def log_deployment_info(tools, test_files, result_dir: str):
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


def deploy_one_contracts(
    tool: Tool,
    test_file: str,
    tool_deploy_dir: str,
) -> None:
    """Deploy one test  for an analysis tool."""

    # Configure Solc compiler
    solc_path = solc.configure_local_solc_path(test_file)

    try:
        # Run the analysis
        print(f"{'-' * 45}\n")
        print(f"Deploying: {test_file}\n")

        command = tool.make_deployment_command(
            test_file, tool_deploy_dir, solc_path
        )

        if command is None:
            print(f"Unable to make deployment command for tool: {tool.name}\n")
            return None

        output = subprocess.run(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        log_deployment_result(tool, test_file, command, output, tool_deploy_dir)
    except ValueError:
        print("Failed to run command: " + str(command))

    # # Process results
    # issues = result.process_analysis_result(tool, tool_deploy_dir)
    # for issue in issues:
    #     print("- " + str(issue))


def deploy_all_contracts(
    tool: Tool,
    test_files: List[str],
    deploy_dir: str,
) -> None:
    """Deploy testing contracts for one tool."""
    print(f"{'=' * 55}\n")
    print(f"Deploy contracts for tool: {tool.name}\n")
    common_path = os.path.commonpath(test_files)
    parent_path = os.path.dirname(common_path)

    for test_file in test_files:
        # Prepare output directory for one test file
        rel_path = os.path.relpath(test_file, start=parent_path)
        tool_deploy_dir = os.path.join(deploy_dir, tool.id, rel_path)
        if not os.path.exists(tool_deploy_dir):
            os.makedirs(tool_deploy_dir)

        # Analyze the test file
        deploy_one_contracts(tool, test_file, tool_deploy_dir)

    return None


def perform_deployment(tools: List[Tool], test_files: List[str]) -> str:
    """Deploy testing contracts for all given analysis tools.

    Return the path to deployment directory."""
    # Prepare output directory for all tests and all tools in this run
    print("Start deploying all test cases...\n")
    deploy_dir = os.path.join(
        DEPLOY_DIR,
        datetime.now().strftime("%Y_%m_%d_%H_%M_%S"),
    )
    if not os.path.exists(deploy_dir):
        os.makedirs(deploy_dir)

    # Record the analysis details to a log file
    log_deployment_info(tools, test_files, deploy_dir)

    # Perform the analysis
    for tool in tools:
        deploy_all_contracts(tool, test_files, deploy_dir)

    print("Deployment completed!\n")
    print(f"Contracts are deployed to: {deploy_dir}")

    return deploy_dir
