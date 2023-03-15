#!/usr/bin/env python3

"""Module handling sFuzz."""

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

    if arguments:
        command = command + " " + arguments

    command = (
        command
        + " "
        + test_file
    )

    print(f"sfuzz command: {command}")
    return command
