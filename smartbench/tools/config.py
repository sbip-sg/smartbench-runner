#!/usr/bin/env python3

# Standard Library
import os
import sys

from typing import Callable, List, Optional

# Third Party
import tomli

# Library
from smartbench import debug
from smartbench.tools.confuzzius.confuzzius import Confuzzius
from smartbench.tools.mythril.mythril import Mythril
from smartbench.tools.sfuzz.sfuzz import Sfuzz
from smartbench.tools.slither.slither import Slither
from smartbench.tools.smartian.smartian import Smartian
from smartbench.tools.tool import Tool


# List of keywords in configuration files
INFO = "info"
ID = "id"
NAME = "name"
HOMEPAGE = "homepage"
CATEGORY = "category"
COMMAND = "command"
PATH = "path"
DEFAULT_TIMEOUT = "default_timeout"
DEFAULT_ARGUMENTS = "default_arguments"

# Initiate some global varibles
TOOLS_DIR = os.path.dirname(__file__)
SMARTBENCH_ROOT_DIR = os.path.dirname(os.path.dirname(TOOLS_DIR))
# print(f"SMARTBENCH_ROOT_DIR: {SMARTBENCH_ROOT_DIR}")
RESULTS_DIR = os.path.join(SMARTBENCH_ROOT_DIR, "results")
# print(f"RESULTS_DIR: {RESULTS_DIR}")
DEPLOY_DIR = os.path.join(os.path.dirname(SMARTBENCH_ROOT_DIR), "deploy")


def load_tool_configuration(tool_name: str) -> Optional[Tool]:
    """Parse configuration of an analysis tool"""

    # Helper function to report configuration error
    def report_config_error(config_key, config_file):
        raise ValueError(
            f"{tool_name}: '{config_key}' is not specified in: {config_file}"
        )

    # Get path of the configuration file
    tool_name = tool_name.casefold()
    cfg_fname = tool_name + ".toml"
    cfg_fpath = os.path.join(TOOLS_DIR, tool_name, cfg_fname)

    # Read configuration file
    with open(cfg_fpath, "r", encoding="utf-8") as file:
        file_content = file.read()
        config = tomli.loads(file_content)

        try:
            # Parse tool info
            if (info := config.get(INFO)) is None:
                report_config_error(INFO, cfg_fpath)

            assert info is not None

            if (tool_id := info.get(ID)) is None:
                report_config_error(ID, cfg_fpath)

            if (tool_name := info.get(NAME)) is None:
                report_config_error(NAME, cfg_fpath)

            if (homepage := info.get(HOMEPAGE)) is None:
                report_config_error(HOMEPAGE, cfg_fpath)

            if (category := info.get(CATEGORY)) is None:
                report_config_error(CATEGORY, cfg_fpath)

            # Parse tool command
            if (command := config.get(COMMAND)) is None:
                report_config_error(COMMAND, cfg_fpath)

            assert command is not None

            if (path := command.get(PATH)) is None:
                report_config_error(PATH, cfg_fpath)

            if (default_args := command.get(DEFAULT_ARGUMENTS)) is None:
                report_config_error(DEFAULT_ARGUMENTS, cfg_fpath)

            if (default_timeout := command.get(DEFAULT_TIMEOUT)) is None:
                report_config_error(DEFAULT_TIMEOUT, cfg_fpath)

            ToolConstructor: Callable = Tool
            if tool_id == "slither":
                ToolConstructor = Slither
            elif tool_id == "confuzzius":
                ToolConstructor = Confuzzius
            elif tool_id == "mythril":
                ToolConstructor = Mythril
            elif tool_id == "sFuzz":
                ToolConstructor = Sfuzz
            elif tool_id == "smartian":
                ToolConstructor = Smartian

            return ToolConstructor(
                tool_id,
                tool_name,
                homepage,
                category,
                path,
                default_args,
                default_timeout,
            )
        except AttributeError:
            debug.warning("Error in configuration of tool: " + str(tool_name))
            return None


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
