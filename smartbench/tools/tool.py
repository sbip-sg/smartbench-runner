#!/usr/bin/env python3

"""Module handling analysis tools.

This is the shared interface for all tools.
"""

# Standard Library
import os
import sys
import warnings

# Third Party
import toml

# Library
import smartbench

from smartbench.tools.slither import slither


# CONSTANT for configuration key
INFO = "info"
ID = "id"
NAME = "name"
HOMEPAGE = "homepage"
CATEGORY = "category"
COMMAND = "command"
PATH = "path"
DEFAULT_ARGUMENTS = "default_arguments"
OUTPUT = "output"
JSON_OUTPUT = "json_output"

# Initiate some global varibles
ALL_TOOLS_DIR = os.path.dirname(__file__)
SMARTBENCH_ROOT_DIR = os.path.dirname(smartbench.__file__)
ALL_RESULTS_DIR = os.path.join(os.path.dirname(SMARTBENCH_ROOT_DIR), "results")


class Tool:
    """Configuration of an analysis tool."""

    def __init__(
        self,
        id,
        name,
        homepage,
        category,
        path,
        default_arguments,
        json_output=None,
        timeout=None,
    ):
        self.id = id
        self.name = name
        self.homepage = homepage
        self.category = category
        self.path = path
        self.default_arguments = default_arguments
        self.json_output = json_output
        self.timeout = timeout

    def __str__(self):
        return (
            '{ Tool: "'
            + self.name
            + '", Path: "'
            + self.path
            + '", Arguments: "'
            + self.additional_arguments
            + '"}'
        )

    def is_slither(self):
        """Check if the current tool is Slither."""
        return self.id.casefold() == slither.TOOL_NAME.casefold()

    def is_confuzzius(self):
        """Check if the current tool is Confuzzius."""
        raise Exception("TODO: implement")

    def is_smartfuzz(self):
        """Check if the current tool is SmartFuzz."""
        raise Exception("TODO: implement")

    def make_analysis_command(self, test_file):
        """Make an analysis command for a tool."""
        if self.is_slither():
            return slither.make_analysis_command(self, test_file)

        if self.is_confuzzius():
            raise Exception("TODO: implement")

        if self.is_smartfuzz():
            raise Exception("TODO: implement")

        return "Unknown"


def parse_tool_configuration(tool):
    """Parse configuration of an analysis tool"""

    # Get path of the confiuration file
    config_file_name = tool + ".toml"
    config_file_path = os.path.join(ALL_TOOLS_DIR, tool, config_file_name)

    # Read configuration file
    with open(config_file_path, "r", encoding="utf-8") as file:
        file_content = file.read()
        config = toml.loads(file_content)

        # Parse tool info
        info = config.get(INFO)
        id = info.get(ID)
        name = info.get(NAME)
        homepage = info.get(HOMEPAGE)
        category = info.get(CATEGORY)

        # Parse tool command
        command = config.get(COMMAND)
        path = command.get(PATH)
        args = command.get(DEFAULT_ARGUMENTS)

        # Parse tool's output
        json_output = None
        try:
            output = config.get(OUTPUT)
            json_output = output.get(JSON_OUTPUT)
        except AttributeError:
            warnings.warn("JSON output file is not configured: " + config.name)
            pass

        return Tool(id, name, homepage, category, path, args, json_output)


def configure_one_tool(tool: str) -> Tool:
    """Configure one analysis tool."""
    if tool.casefold() == slither.TOOL_NAME:
        return slither.read_slither_configuration()


def configure_analysis_tools(args) -> [Tool]:
    """Configure all analysis tools."""
    tools = args.tools
    if tools is None or len(tools) == 0:
        sys.exit("No analysis tool is selected!")

    configs = []
    for tool in tools:
        configs.append(configure_one_tool(tool))

    return configs
