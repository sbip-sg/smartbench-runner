#!/usr/bin/env python3

"""Module handling analysis tools.

This is the shared interface for all tools.
"""

# Standard Library
import os
import sys

from typing import List, Union

# Third Party
import toml

# Library
import smartbench

from smartbench import debug
from smartbench.tools.slither import slither


# List of keywords in configuration files
INFO = "info"
ID = "id"
NAME = "name"
HOMEPAGE = "homepage"
CATEGORY = "category"
COMMAND = "command"
PATH = "path"
DEFAULT_ARGUMENTS = "default_arguments"
OUTPUT = "output"
RESULT_FILE = "result_file"
LOG_FILE = "log_file"

# Initiate some global varibles
ALL_TOOLS_DIR = os.path.dirname(__file__)
SMARTBENCH_ROOT_DIR = os.path.dirname(smartbench.__file__)
ALL_RESULTS_DIR = os.path.join(os.path.dirname(SMARTBENCH_ROOT_DIR), "results")


class Tool:
    """Configuration of an analysis tool."""

    # Attributes of a tool
    id: str
    name: str
    homepage: str
    category: str
    path: str
    default_arguments: str
    additional_arguments: str
    output_file: str
    log_file: str
    timeout: int

    def __init__(
        self,
        id,
        name,
        homepage,
        category,
        path,
        default_arguments,
        output_file,
        log_file,
        additional_arguments=None,
        timeout=None,
    ):
        """Constructor"""
        self.id = id
        self.name = name
        self.homepage = homepage
        self.category = category
        self.path = path
        self.default_arguments = default_arguments
        self.additional_arguments = additional_arguments
        self.output_file = output_file
        self.log_file = log_file
        self.timeout = timeout

    def __str__(self):
        """Printing to string."""
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

    def make_analysis_command(self, test_file, result_dir, solc_path):
        """Make an analysis command for a tool."""
        # Prepare output directory for all results
        make_command = None

        if self.is_slither():
            make_command = slither.make_slither_analysis_command
        elif self.is_confuzzius():
            raise Exception("TODO: implement")
        elif self.is_smartfuzz():
            raise Exception("TODO: implement")

        if make_command is None:
            return None

        arguments = self.default_arguments
        if self.additional_arguments:
            arguments = arguments + " " + self.additional_arguments

        output_file = configure_output_file(self, result_dir)

        return make_command(
            self.path, arguments, test_file, output_file, solc_path
        )


def load_tool_configuration(tool_name: str) -> Union[Tool, None]:
    """Parse configuration of an analysis tool"""
    # Get path of the configuration file
    tool_name = tool_name.casefold()
    config_file_name = tool_name + ".toml"
    config_file_path = os.path.join(ALL_TOOLS_DIR, tool_name, config_file_name)

    # Read configuration file
    with open(config_file_path, "r", encoding="utf-8") as file:
        file_content = file.read()
        config = toml.loads(file_content)

        try:
            # Parse tool info
            info = config.get(INFO)
            if info:
                tool_id = info.get(ID)
                tool_name = info.get(NAME)
                homepage = info.get(HOMEPAGE)
                category = info.get(CATEGORY)

            # Parse tool command
            command = config.get(COMMAND)
            if command:
                path = command.get(PATH)
                default_arguments = command.get(DEFAULT_ARGUMENTS)

            # Parse tool's output
            output = config.get(OUTPUT)
            if output:
                result_file = output.get(RESULT_FILE)
                log_file = output.get(LOG_FILE)

            return Tool(
                tool_id,
                tool_name,
                homepage,
                category,
                path,
                default_arguments,
                result_file,
                log_file,
            )
        except AttributeError:
            debug.warning("Error in configuration of tool: " + str(tool_name))
            return None


def configure_output_file(tool: Tool, result_dir: str) -> str:
    """
    Configure output file of a tool for a test file.
    """

    # Prepare output directory
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    # Configure output file
    output_file = os.path.join(result_dir, tool.output_file)

    return output_file


def configure_log_file(tool: Tool, result_dir: str) -> str:
    """
    Configure log file of a tool for a test file.
    """

    # Prepare output directory
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    # Configure output file
    output_file = os.path.join(result_dir, tool.log_file)

    return output_file


def configure_analysis_tools(args) -> List[Tool]:
    """Configure all analysis tools."""
    print("Configure analysis tools...\n")

    tool_names = args.tools
    if tool_names is None or len(tool_names) == 0:
        sys.exit("No analysis tool is selected!")

    all_tool_configs = []
    for tool_name in tool_names:
        config = load_tool_configuration(tool_name)
        if config is None:
            debug.warning("Failed to read configuration of: " + tool_name)
        else:
            all_tool_configs.append(config)

    return all_tool_configs
