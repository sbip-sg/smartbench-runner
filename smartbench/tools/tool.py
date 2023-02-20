#!/usr/bin/env python3

"""Module handling analysis tools.

This is the shared interface for all tools.
"""

# Standard Library
import os

# Third Party
import toml


# Configuration keyword for tool information
INFO = "info"
NAME = "name"
HOMEPAGE = "homepage"
CATEGORY = "category"

# Configuration keyword for tool command
COMMAND = "command"
PATH = "path"
ARGUMENTS = "arguments"


class ToolConfig:
    """Configuration of an analysis tool."""

    def __init__(self, name, path, args, timeout=15):
        self.name = name
        self.path = path
        self.arguments = args
        self.timeout = timeout

    def make_execution_command(self):
        """Make execution command for a tool."""
        return self.path + " " + self.arguments


def parse_tool_configuration(tool):
    """Parse configuration of an analysis tool"""
    tool_root_dir_path = os.path.dirname(__file__)
    config_file_name = tool + ".toml"
    config_file_path = os.path.join(tool_root_dir_path, tool, config_file_name)
    with open(config_file_path, "r", encoding="utf-8") as file:
        file_content = file.read()
        config_data = toml.loads(file_content)

        # Parse tool info
        info = config_data.get(INFO)
        name = info.get(NAME)
        homepage = info.get(HOMEPAGE)
        tool_category = info.get(CATEGORY)

        # Parse tool command
        command = config_data.get(COMMAND)
        path = command.get(PATH)
        args = command.get(ARGUMENTS)

        return ToolConfig(name, path, args)
