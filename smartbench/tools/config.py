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


def load_tool_configuration(tool_id: str) -> Optional[Tool]:
    """Parse configuration of an analysis tool"""
    # Normalize tool ID
    tool_id = tool_id.casefold()

    # Find tool root ID. This is to handle the case where a tool can
    # have multiple variants, like confuzzius, confuzzius-sbip,
    tool_root_id = tool_id
    if (idx := tool_id.find("-")) >= 0:
        tool_root_id = tool_id[:idx]
    elif (idx := tool_id.find("_")) >= 0:
        tool_root_id = tool_id[:idx]

    if tool_root_id not in SUPPORTED_TOOLS:
        warning(f"Invalid or unspported tool ID: {tool_id}")
        return None

    # Get path of the configuration file
    config_file_name = tool_root_id + ".toml"
    config_file_path = os.path.join(TOOLS_DIR, tool_root_id, config_file_name)

    # Read configuration file
    with open(config_file_path, "r", encoding="utf-8") as file:
        file_content = file.read()
        config = tomli.loads(file_content)

        try:
            # Parse tool info
            if (info := config.get(INFO)) is None:
                report_config_error(tool_id, INFO, config_file_path)

            assert info is not None

            if (tool_name := info.get(NAME)) is None:
                report_config_error(tool_id, NAME, config_file_path)

            # Parse tool command
            if (command := config.get(COMMAND)) is None:
                report_config_error(tool_id, COMMAND, config_file_path)

            assert command is not None

            if (executable := command.get(EXECUTABLE)) is None:
                report_config_error(tool_id, EXECUTABLE, config_file_path)

            if (default_args := command.get(DEFAULT_ARGUMENTS)) is None:
                report_config_error(
                    tool_id, DEFAULT_ARGUMENTS, config_file_path
                )

            if (default_timeout := command.get(DEFAULT_TIMEOUT)) is None:
                report_config_error(tool_id, DEFAULT_TIMEOUT, config_file_path)

            tool_constructor: Optional[Callable] = None
            if tool_root_id == "confuzzius":
                tool_constructor = Confuzzius
            elif tool_root_id == "ilf":
                tool_constructor = Ilf
            elif tool_root_id == "mythril":
                tool_constructor = Mythril
            elif tool_root_id == "sfuzz":
                tool_constructor = Sfuzz
            elif tool_root_id == "slither":
                tool_constructor = Slither
            elif tool_root_id == "smartian":
                tool_constructor = Smartian
            elif tool_root_id == "smartfuzz":
                tool_constructor = SmartFuzz
            elif tool_root_id == "verismart":
                tool_constructor = VeriSmart

            if tool_constructor is None:
                error_traceback(f"Unknown analysis tool: {tool_id}")
                return None
            else:
                return tool_constructor(
                    tool_id,
                    tool_root_id,
                    tool_name,
                    executable,
                    default_args,
                    default_timeout,
                )
        except AttributeError:
            warning("Error in configuration of tool: " + str(tool_id))
            return None


def configure_analysis_tools(tool_ids: List[str]) -> List[Tool]:
    """Configure all analysis tools."""
    safe_print("Configure analysis tools...")

    if len(tool_ids) == 0:
        sys.exit("No analysis tool is selected!")

    all_tool_configs = []
    for tool_id in tool_ids:
        config = load_tool_configuration(tool_id)
        if config is None:
            error("Failed to read configuration of: " + tool_id)
        else:
            all_tool_configs.append(config)

    return all_tool_configs
