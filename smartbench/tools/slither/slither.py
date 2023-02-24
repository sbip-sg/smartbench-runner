#!/usr/bin/env python3

"""Module handling Slither."""

# Standard Library
import os

from datetime import datetime

# Library
from smartbench.buginfo import BugInfo
from smartbench.tools.util import make_output_directory


# Tool name
TOOL_NAME = "slither"


def make_analysis_command(
    tool_id: str,
    executable_file: str,
    arguments: str,
    test_file: str,
    result_dir: str,
    output_file: str,
):
    """
    Function to make analysis command for Slither.
    This function should have the same signature with other tools.
    """
    command = executable_file

    if arguments:
        command = command + " " + arguments

    command = command + " " + test_file

    if output_file:
        output_dir = make_output_directory(tool_id, test_file, result_dir)
        output_file = os.path.join(output_dir, output_file)
        command = command + " --json " + output_file

    return command


# def parse_json_output(tool: Tool, output_dir: str) -> [BugInfo]:
#     json_output = os.path.join(output_dir, tool.id, tool.output_file)
