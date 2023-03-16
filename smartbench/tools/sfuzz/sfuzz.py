#!/usr/bin/env python3

"""Module handling sFuzz."""

import os
import subprocess
import shlex

# Tool name
TOOL_NAME = "sFuzz"

def make_sfuzz_analysis_command(
    executable_file: str,
    arguments: str,
    test_file: str,
    output_file: str,
    solc_path: str,
):
    """
    Function to make analysis command for Slither.
    This function should have the same signature with other tools.
    """
    command = executable_file

    dir_path = os.path.dirname(os.path.realpath(__file__))
    print(dir_path)

    normal_contract = "NormalAttacker_0_4.sol"
    reentrancy_contract = "ReentrancyAttacker_0_4.sol"

    normal_contract = os.path.join(dir_path, normal_contract)
    reentrancy_contract = os.path.join(dir_path, reentrancy_contract)
    if arguments:
        command = command + " " + arguments

    solc_version = os.path.basename(solc_path)
    solc_version.removeprefix("solc-")
    solc_cmd = "solc-select install " + solc_version + "; solc-select use " + solc_version;
    try:
        subprocess.run(
            shlex.split(solc_cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except ValueError:
        print("Failed to run command: " + str(solc_cmd))

    print(f"path: {solc_path}")

    output = subprocess.run(
        shlex.split("solc --version"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    print("solc version: ", output)

    command = (
        command
        + " "
        + test_file
        # + " "
        # + solc_path
    )
    print(f"sfuzz command: {command}")
    return command
