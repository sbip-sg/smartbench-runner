#!/usr/bin/env python3

"""Module handling analysis tools.

This is the shared interface for all tools.
"""

# Standard Library
import os
import sys

from typing import List, Optional

# Third Party
import tomli

# Library
import smartbench

from smartbench import debug
from smartbench.tools.confuzzius import confuzzius
from smartbench.tools.ilf import ilf
from smartbench.tools.mythril import mythril
from smartbench.tools.sfuzz import sfuzz
from smartbench.tools.slither import slither
from smartbench.tools.smartfuzz import smartfuzz
from smartbench.tools.smartian import smartian


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
SMARTBENCH_ROOT_DIR = os.path.dirname(smartbench.__file__)
RESULTS_DIR = os.path.join(os.path.dirname(SMARTBENCH_ROOT_DIR), "results")
DEPLOY_DIR = os.path.join(os.path.dirname(SMARTBENCH_ROOT_DIR), "deploy")


class Tool:
    """Configuration of an analysis tool."""

    def __init__(
        self,
        id: str,
        name: str,
        homepage: str,
        category: str,
        path: str,
        default_arguments: str,
        default_timeout: int,
        additional_arguments: Optional[str] = None,
        random_seed: int = 0,
    ):
        """Constructor"""
        self.id: str = str(id)
        self.name: str = str(name)
        self.homepage: str = str(homepage)
        self.category: str = str(category)
        self.path: str = str(path)
        self.default_arguments: str = default_arguments
        self.additional_arguments: Optional[str] = additional_arguments
        self.default_timeout = int(default_timeout)
        self.output_file: str = f"{id}_result.json"
        self.log_file: str = f"{id}_execution.log"
        # increasing random seed for reproducible results
        self.random_seed: int = int(random_seed)

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
        return self.id.casefold() == confuzzius.TOOL_NAME.casefold()

    def is_mythril(self):
        """Check if the current tool is Mythril."""
        return self.id.casefold() == mythril.TOOL_NAME.casefold()

    def is_smartfuzz(self):
        """Check if the current tool is SmartFuzz."""
        return self.id.casefold() == smartfuzz.TOOL_NAME.casefold()

    def is_smartian(self):
        """Check if the current tool is Smartian."""
        return self.id.casefold() == smartian.TOOL_NAME.casefold()

    def is_sfuzz(self):
        """Check if the current tool is sFuzz."""
        return self.id.casefold() == sfuzz.TOOL_NAME.casefold()

    def is_ilf(self):
        """Check if the current tool is ILF."""
        return self.id.casefold() == ilf.TOOL_NAME.casefold()

    def make_analysis_command(
        self,
        test_file,
        result_dir,
        solc_path,
        timeout=None,
        use_docker=True,
    ):
        """Make an analysis command for a tool."""
        # Deterministically increase from seed. Reproducible randomness
        # TODO: add random seed for fuzzing tools if they support it.
        self.random_seed += 1

        arguments = self.default_arguments
        timeout = timeout if timeout is not None else self.default_timeout

        make_command = None
        if self.is_slither():
            make_command = slither.make_analysis_command
        elif self.is_sfuzz():
            make_command = sfuzz.make_analysis_command
        elif self.is_confuzzius():
            make_command = confuzzius.make_analysis_command
        elif self.is_mythril():
            make_command = mythril.make_analysis_command
        elif self.is_ilf():
            make_command = ilf.make_analysis_command
        elif self.is_smartian():
            make_command = smartian.make_analysis_command
        elif self.is_smartfuzz():
            make_command = smartfuzz.make_analysis_command
            arguments += " --seed " + str(self.random_seed)
        else:
            raise Exception(f"TODO: implement for tool: {self.id}")

        if self.additional_arguments:
            arguments = arguments + " " + self.additional_arguments

        output_file = self.configure_output_file(result_dir)

        return make_command(
            self.path, arguments, test_file, output_file, solc_path, timeout
        )

    def make_deployment_command(self, test_file, result_dir, solc_path):
        # TODO: impleemnt
        pass

    def configure_output_file(self, result_dir: str) -> str:
        """
        Configure output file of the tool for a test file.
        """
        # Prepare output directory
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
        return os.path.join(result_dir, self.output_file)

    def configure_log_file(self, result_dir: str) -> str:
        """
        Configure log file of a tool for a test file.
        """
        # Prepare output directory
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
        return os.path.join(result_dir, self.log_file)


def load_tool_configuration(tool_name: str) -> Optional[Tool]:
    """Parse configuration of an analysis tool"""

    # Helper function to report configuraiton error
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

            return Tool(
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
