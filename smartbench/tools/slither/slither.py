#!/usr/bin/env python3

"""Module handling Slither."""


# Library
from smartbench.tools import tool


TOOL_NAME = "Slither"


def read_slither_configuration():
    """Read configuration of Slither."""
    config = tool.parse_tool_configuration("slither")
    print("Command:", config.path)
    return config


def make_analysis_command(config, test_file):
    """Make analysis command for Slither."""
    command = config.path

    if config.default_arguments:
        command += " " + config.default_arguments

    command += " " + test_file

    # TODO: make output

    return command
