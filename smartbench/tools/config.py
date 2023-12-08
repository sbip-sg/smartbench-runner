#!/usr/bin/env python3

# Standard Library
import os
import sys

from typing import Callable, List, Optional

# Third Party
import tomli

# Library
from smartbench.printer import error, error_traceback, safe_print, warning
from smartbench.tools.confuzzius.confuzzius import Confuzzius
from smartbench.tools.ilf.ilf import Ilf
from smartbench.tools.mythril.mythril import Mythril
from smartbench.tools.sfuzz.sfuzz import Sfuzz
from smartbench.tools.slither.slither import Slither
from smartbench.tools.efcf.efcf import EFCF
from smartbench.tools.smartfuzz.smartfuzz import SmartFuzz
from smartbench.tools.verismart.verismart import VeriSmart
from smartbench.tools.smartian.smartian import Smartian
from smartbench.tools.tool import Tool


# List of keywords in configuration files
INFO = "info"
NAME = "name"
COMMAND = "command"
EXECUTABLE = "executable"
DEFAULT_TIMEOUT = "default_timeout"
DEFAULT_ARGUMENTS = "default_arguments"

# Initiate some global varibles
TOOLS_DIR = os.path.dirname(__file__)
SMARTBENCH_ROOT = os.path.dirname(os.path.dirname(TOOLS_DIR))
RESULTS_DIR = os.path.join(SMARTBENCH_ROOT, "results")
DEPLOY_DIR = os.path.join(os.path.dirname(SMARTBENCH_ROOT), "deploy")

# TOOL ID
SUPPORTED_TOOLS = [
    "confuzzius",
    "ilf",
    "mythril",
    "sfuzz",
    "slither",
    "smartfuzz",
    "smartian",
    "verismart",
    "efcf"
]


# Helper function to report configuration error
def report_config_error(
    tool: str, config_key: str, config_file: str
) -> ValueError:
    raise ValueError(
        f"{tool}: '{config_key}' is not specified in: {config_file}"
    )


def load_tool_configuration(tool_name: str) -> Optional[Tool]:
    """Parse configuration of an analysis tool"""
    # Normalize tool ID
    tool_name = tool_name.casefold()

    # Find tool root ID. This is to handle the case where a tool can
    # have multiple variants, like confuzzius, confuzzius-sbip,
    tool_base_name = tool_name
    if (idx := tool_name.find("-")) >= 0:
        tool_base_name = tool_name[:idx]
    elif (idx := tool_name.find("_")) >= 0:
        tool_base_name = tool_name[:idx]

    if tool_base_name not in SUPPORTED_TOOLS:
        warning(f"Invalid or unspported tool ID: {tool_name}")
        return None

    # Get path of the configuration file
    config_file_name = tool_base_name + ".toml"
    config_file_path = os.path.join(TOOLS_DIR, tool_base_name, config_file_name)

    # Read configuration file
    with open(config_file_path, "r", encoding="utf-8") as file:
        file_content = file.read()
        config = tomli.loads(file_content)

        try:
            # Parse tool info
            if (info := config.get(INFO)) is None:
                report_config_error(tool_name, INFO, config_file_path)

            assert info is not None

            if (tool_name := info.get(NAME)) is None:
                report_config_error(tool_name, NAME, config_file_path)

            # Parse tool command
            if (command := config.get(COMMAND)) is None:
                report_config_error(tool_name, COMMAND, config_file_path)

            assert command is not None

            if (executable := command.get(EXECUTABLE)) is None:
                report_config_error(tool_name, EXECUTABLE, config_file_path)

            if (default_args := command.get(DEFAULT_ARGUMENTS)) is None:
                report_config_error(
                    tool_name, DEFAULT_ARGUMENTS, config_file_path
                )

            if (default_timeout := command.get(DEFAULT_TIMEOUT)) is None:
                report_config_error(tool_name, DEFAULT_TIMEOUT, config_file_path)

            tool_constructor: Optional[Callable] = None
            if tool_base_name == "confuzzius":
                tool_constructor = Confuzzius
            elif tool_base_name == "ilf":
                tool_constructor = Ilf
            elif tool_base_name == "mythril":
                tool_constructor = Mythril
            elif tool_base_name == "sfuzz":
                tool_constructor = Sfuzz
            elif tool_base_name == "slither":
                tool_constructor = Slither
            elif tool_base_name == "smartian":
                tool_constructor = Smartian
            elif tool_base_name == "smartfuzz":
                tool_constructor = SmartFuzz
            elif tool_base_name == "verismart":
                tool_constructor = VeriSmart
            elif tool_base_name == "efcf":
                tool_constructor = EFCF

            if tool_constructor is None:
                error_traceback(f"Unknown analysis tool: {tool_name}")
                return None
            else:
                return tool_constructor(
                    tool_name,
                    tool_base_name,
                    tool_name,
                    executable,
                    default_args,
                    default_timeout,
                )
        except AttributeError:
            warning("Error in configuration of tool: " + str(tool_name))
            return None


def configure_analysis_tools(tools: str) -> List[Tool]:
    """
    Configure all analysis tools.
    Input is a comma-separated list of tools.
    """

    tool_names = [s.strip() for s in tools.split(",")]
    safe_print(f"Configure analysis tools: {', '.join(tool_names)}")

    all_tool_configs = []
    for tool_name in tool_names:
        config = load_tool_configuration(tool_name)
        if config is None:
            error("Failed to read configuration of: " + tool_name)
        else:
            all_tool_configs.append(config)

    return all_tool_configs
