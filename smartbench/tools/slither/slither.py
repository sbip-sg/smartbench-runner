#!/usr/bin/env python3

"""Module handling Slither."""

# Standard Library
import os

from datetime import datetime

# Library
from smartbench.tools import tool


TOOL_NAME = "slither"


def read_slither_configuration():
    """Read configuration of Slither."""
    config = tool.parse_tool_configuration("slither")
    print("Command:", config.path)
    return config


def make_analysis_command(tool, test_file, output_dir):
    """Make analysis command for Slither."""
    command = tool.path

    if tool.default_arguments:
        command = command + " " + tool.default_arguments

    command = command + " " + test_file

    # TODO: make output directory.

    if tool.json_output:
        # Prepare output directory
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Output file
        output_file = os.path.join(output_dir, tool.json_output)
        command = command + " --json " + output_file

    return command
