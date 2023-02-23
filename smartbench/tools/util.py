#!/usr/bin/env python3

# Standard Library
import os
import sys

# Third Party
import toml

# Library
import smartbench

from smartbench import debug
from smartbench.tools import tool
from smartbench.tools.slither import slither
from smartbench.tools.tool import Tool


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
JSON_OUTPUT = "json_output"
LOG_OUTPUT = "log_output"

# List of analysis tools
SLITHER = "slither"

# Initiate some global varibles
ALL_TOOLS_DIR = os.path.dirname(__file__)
SMARTBENCH_ROOT_DIR = os.path.dirname(smartbench.__file__)
ALL_RESULTS_DIR = os.path.join(os.path.dirname(SMARTBENCH_ROOT_DIR), "results")


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
        output = config.get(OUTPUT)
        try:
            log_output = output.get(LOG_OUTPUT)
            json_output = None
            json_output = output.get(JSON_OUTPUT)

            return Tool(
                id,
                name,
                homepage,
                category,
                path,
                args,
                json_output,
                log_output,
            )
        except AttributeError:
            debug.warning("Error in configuration of tool: " + str(tool))


def configure_one_tool(tool: str) -> Tool:
    """Configure one analysis tool."""
    global SLITHER
    if tool.casefold() == SLITHER:
        return parse_tool_configuration(SLITHER)

    return None


def configure_analysis_tools(args) -> [Tool]:
    """Configure all analysis tools."""
    tools = args.tools
    if tools is None or len(tools) == 0:
        sys.exit("No analysis tool is selected!")

    all_tool_configs = []
    for tool in tools:
        config = configure_one_tool(tool)
        if config is None:
            debug.warning("Failed to read configuration of: " + tool)
        else:
            all_tool_configs.append(config)

    return all_tool_configs
