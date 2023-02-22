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


def make_analysis_command(config, test_file):
    """Make analysis command for Slither."""
    command = config.path

    if config.default_arguments:
        command = command + " " + config.default_arguments

    command = command + " " + test_file

    # TODO: make output directory.

    if config.json_output:
        # Prepare output directory
        output_dir = os.path.join(
            tool.ALL_RESULTS_DIR,
            datetime.now().strftime("%Y_%m_%d__%H_%M_%S"),
            config.id,
        )
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Output file
        output_file = os.path.join(output_dir, config.json_output)
        command = command + " --json " + output_file

    return command
