#!/usr/bin/env python3

"""Module handling analysis tools.

This is the shared interface for all tools.
"""

# Standard Library
import os
import sys

# Third Party
import toml

# Library
from smartbench.tools.slither import slither


# CONSTANT for tool configuration keywords in TOML file.
INFO = "info"
NAME = "name"
HOMEPAGE = "homepage"
CATEGORY = "category"
COMMAND = "command"
PATH = "path"
DEFAULT_ARGUMENTS = "default_arguments"
OUTPUT = "output"
JSON_OUTPUT = "json_output"


class Tool:
    """Configuration of an analysis tool."""

    def __init__(
        self,
        name,
        homepage,
        category,
        path,
        default_arguments,
        json_output=None,
        timeout=None,
    ):
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

    def make_analysis_command(self, test_file):
        """Make an analysis command for a tool."""
        if self.name == slither.TOOL_NAME:
            return slither.make_analysis_command(self, test_file)

        return ""


def parse_tool_configuration(tool):
    """Parse configuration of an analysis tool"""
    tool_root_dir_path = os.path.dirname(__file__)
    config_file_name = tool + ".toml"
    config_file_path = os.path.join(tool_root_dir_path, tool, config_file_name)
    with open(config_file_path, "r", encoding="utf-8") as file:
        file_content = file.read()
        config = toml.loads(file_content)

        # Parse tool info
        info = config.get(INFO)
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
            pass

        return Tool(name, homepage, category, path, args, json_output)


def configure_one_tool(tool: str) -> Tool:
    """Configure one analysis tool."""
    if tool == slither.TOOL_NAME:
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
