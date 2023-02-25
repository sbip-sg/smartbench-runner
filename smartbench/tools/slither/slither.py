#!/usr/bin/env python3

"""Module handling Slither."""

# Standard Library
import json
import os

from typing import List

# Library
from smartbench.buginfo import BugInfo
from smartbench.debug import debug, warning
from smartbench.tools.util import get_output_directory


# Tool name
TOOL_NAME = "slither"


def make_slither_analysis_command(
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
        output_dir = get_output_directory(tool_id, test_file, result_dir)
        output_file = os.path.join(output_dir, output_file)
        command = command + " --json " + output_file

    return command


def parse_slither_json_output(
    tool_id: str,
    test_file: str,
    result_dir: str,
    output_file: str,
) -> List[BugInfo]:
    output_dir = get_output_directory(tool_id, test_file, result_dir)
    output_file = os.path.join(output_dir, output_file)
    output = None

    debug("Slither parse file: ", output_file)
    with open(output_file, "r", encoding="utf-8") as file:
        try:
            output = json.load(file)
        except ValueError:
            warning("Failed to parse Slither output file:", output_file)
            return []

    if output is None:
        warning("Failed to parse Slither's output file:", output_file)
        return []

    try:
        success = output.get("success")
        if not success:
            warning("An error happened when running Slither!")
            warning("See output file for more details: " + output_file)
            return []

        results = output.get("results")
        # TODO: parsing results
        return []
    except ValueError:
        return []
