#!/usr/bin/env python3

"""Module handling sFuzz."""

import os

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

    if "0.5" in solc_path:
        normal_contract = "NormalAttacker_0_5.sol"
        reentrancy_contract = "ReentrancyAttacker_0_5.sol"


    normal_contract = os.path.join(dir_path, normal_contract)
    reentrancy_contract = os.path.join(dir_path, reentrancy_contract)
    if arguments:
        command = command + " " + arguments

    command = (
        command
        + " "
        + test_file
        + " "
        + solc_path
        + " "
        + normal_contract
        + " "
        + reentrancy_contract
    )
    print(f"sfuzz command: {command}")
    return command
