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


EXECUTION_LOG_SUFFIX = "_execution.log"


class Tool:
    """Configuration of an analysis tool."""

    def __init__(
        self,
        id: str,
        root_id: str,
        name: str,
        executable: str,
        default_arguments: str,
        default_timeout: int,
        additional_args: Optional[str] = None,
        random_seed: int = 0,
    ):
        """Constructor"""
        self.id: str = str(id)
        self.root_id: str = str(root_id)
        self.name: str = str(name)
        self.executable: str = str(executable)
        self.default_arguments: str = default_arguments
        self.additional_args: Optional[str] = additional_args
        self.default_timeout = int(default_timeout)
        # increasing random seed for reproducible results
        self.random_seed: int = int(random_seed)

        # Result file in JSON format, some tools may not support this output
        self.json_result_file = (
            None
            if self.id in ["smartian", "sfuzz"]
            else f"{self.id if '-' not in self.id else self.id.split('-')[0]}_result.json"
        )

        # Code coverage file in JSON format, some tools may not support this
        # output
        self.json_coverage_file = (
            f"{self.id if '-' not in self.id else self.id.split('-')[0]}_coverage.json"
            if self.id
            in ["sfuzz", "confuzzius", "smartian", "ilf", "smartfuzz", "confuzzius-patch"]
            else None
        )

        # Log file for capturing execution log
        self.log_file: str = f"{self.id if '-' not in self.id else self.id.split('-')[0]}{EXECUTION_LOG_SUFFIX}"

    def __str__(self):
        """Printing to string."""
        return (
            f"{{ Tool: {self.name}, Path: {self.executable}, "
            f"Arguments: {self.additional_args}}}"
        )

    def configure_json_result_file(self, result_dir: str) -> Optional[str]:
        """Configure result file in JSON format of the tool for a test file."""

        if self.json_result_file is None:
            return None

        # Prepare output directory
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)

        return os.path.join(result_dir, self.json_result_file)

    def configure_json_coverage_file(self, result_dir: str) -> Optional[str]:
        """Configure code coverage file in JSON format of the tool for a test
        file."""

        if self.json_coverage_file is None:
            return None

        # Prepare output directory
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)

        return os.path.join(result_dir, self.json_coverage_file)

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
