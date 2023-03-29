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
from smartbench.tools.slither import slither
from smartbench.tools.smartfuzz import smartfuzz


# List of keywords in configuration files
INFO = "info"
ID = "id"
NAME = "name"
HOMEPAGE = "homepage"
CATEGORY = "category"
COMMAND = "command"
PATH = "path"
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
        additional_arguments: Optional[str] = None,
        timeout: Optional[int] = None,
        seed: int = 0
    ):
        """Constructor"""
        self.id: str = str(id)
        self.name: str = str(name)
        self.homepage: str = str(homepage)
        self.category: str = str(category)
        self.path: str = str(path)
        self.default_arguments: str = default_arguments
        self.additional_arguments: Optional[str] = additional_arguments
        self.timeout: Optional[int] = None if timeout is None else int(timeout)
        self.output_file: str = f"{id}_result.json"
        self.log_file: str = f"{id}_execution.log"
        self.seed: int = seed # increasing random seed for reproducible results

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

    def is_ilf(self):
        """Check if the current tool is ILF."""
        return self.id.casefold() == ilf.TOOL_NAME.casefold()

    def make_analysis_command(self, test_file, result_dir, solc_path):
        """Make an analysis command for a tool."""
        # Prepare output directory for all results
        make_command = None
        self.seed += 1 # determinstically increase from seed. Reproducible randomness
        # TODO add random seed for fuzzing tools if they support it
        arguments = self.default_arguments
        if self.is_slither():
            make_command = slither.make_analysis_command
        elif self.is_confuzzius():
            make_command = confuzzius.make_confuzzius_analysis_command
        elif self.is_mythril():
            make_command = mythril.make_mythril_analysis_command
        elif self.is_ilf():
            make_command = ilf.make_analysis_command
        elif self.is_smartfuzz():
            make_command = smartfuzz.make_analysis_command
            arguments += " --seed " + str(self.seed)
        elif self.is_confuzzius():
            raise Exception("TODO: implement")

        if make_command is None:
            return None

        if self.additional_arguments:
            arguments = arguments + " " + self.additional_arguments

        output_file = self.configure_output_file(result_dir)

        return make_command(
            self.path, arguments, test_file, output_file, solc_path
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
    # Get path of the configuration file
    tool_name = tool_name.casefold()
    config_file_name = tool_name + ".toml"
    config_file_path = os.path.join(TOOLS_DIR, tool_name, config_file_name)

    # Read configuration file
    with open(config_file_path, "r", encoding="utf-8") as file:
        file_content = file.read()
        config = tomli.loads(file_content)

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

            return Tool(
                tool_id,
                tool_name,
                homepage,
                category,
                path,
                default_arguments,
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
