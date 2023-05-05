#!/usr/bin/env python3

"""Module handling analysis tools.

This is the shared interface for all tools.
"""

# Standard Library
import os

from abc import abstractmethod
from typing import List, Optional

# Library
from smartbench.annotation import BugAnnot
from smartbench.docker import DockerContainer
from smartbench.issue import Issue
from smartbench.solidity.loc import Location


class Tool:
    """Configuration of an analysis tool."""

    def __init__(
        self,
        tool_id: str,
        name: str,
        executable: str,
        default_arguments: str,
        default_timeout: int,
        additional_args: Optional[str] = None,
        random_seed: int = 0,
    ):
        """Constructor"""
        tool_id = tool_id.lower()
        self.id: str = str(tool_id)
        self.name: str = str(name)
        self.executable: str = str(executable)
        self.default_arguments: str = default_arguments
        self.additional_args: Optional[str] = additional_args
        self.default_timeout = int(default_timeout)
        # increasing random seed for reproducible results
        self.random_seed: int = int(random_seed)

        # Output file in JSON format, some tools may not support this output
        self.json_output_file = (
            None
            if tool_id in ["smartian", "sfuzz"]
            else f"{tool_id}_result.json"
        )

        # Log file for capturing execution log
        self.log_file: str = f"{tool_id}_execution.log"

        # Output code coverage file in JSON format, some tools may not support
        # this output
        self.coverage_json_file = (
            f"{tool_id}_coverage.json"
            if tool_id in ["sfuzz", "confuzzius", "smartian", "ilf"]
            else None
        )

    def __str__(self):
        """Printing to string."""
        return (
            f"{{ Tool: {self.name}, Path: {self.executable}, "
            f"Arguments: {self.additional_args}}}"
        )

    def configure_json_output(self, result_dir: str) -> Optional[str]:
        """
        Configure output file of the tool for a test file.
        """
        if self.json_output_file is None:
            return None

        # Prepare output directory
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
        return os.path.join(result_dir, self.json_output_file)

    def configure_log_file(self, result_dir: str) -> str:
        """
        Configure log file of a tool for a test file.
        """
        # Prepare output directory
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
        return os.path.join(result_dir, self.log_file)

    @abstractmethod
    def make_analysis_command(
        self,
        test_file: str,
        contracts: List[str],
        test_output_dir: str,
        container: DockerContainer,
        solc_version: str,
        timeout: Optional[int] = None,
        **kwargs,
    ) -> str:
        """Make an analysis command for a tool."""

    def prepare_parsing_analysis_output(self) -> None:
        """Reset the environment before parsing analysis results."""
        # Reset issue index counter
        Issue.index_counter = 1
        return None

    @abstractmethod
    def parse_analysis_output(
        self, test_output_dir: str
    ) -> Optional[List[Issue]]:
        """Process analysis result of each tool. Returns a list of detected
        issues, or `None` if the corresponding tool failed to analyze the test
        file."""

    @abstractmethod
    def match_location_of_issue_to_annotation(
        self, issue: Issue, annot: BugAnnot
    ) -> bool:
        """This function must be implemented by each tool, since the bug
        location reported by each tool are in different format."""

    @abstractmethod
    def parse_instruction_coverage(self, test_output_dir: str):
        """Parse instruction coverage of analysis results.
        This function should be implemented by each analysis tool."""
