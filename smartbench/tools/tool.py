#!/usr/bin/env python3

"""Module handling analysis tools.

This is the shared interface for all tools.
"""

# Standard Library
import os

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
ARGUMENTS = "arguments"
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
        args,
        json_output=None,
        timeout=None,
    ):
        self.name = name
        self.homepage = homepage
        self.category = category
        self.path = path
        self.additional_arguments = args
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
        args = command.get(ARGUMENTS)

        # Parse tool's output
        json_output = None
        try:
            output = config.get(OUTPUT)
            json_output = output.get(JSON_OUTPUT)
        except AttributeError:
            pass

        return Tool(name, homepage, category, path, args, json_output)
