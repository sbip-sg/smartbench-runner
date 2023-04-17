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
from smartbench.issue import Issue
from smartbench.solidity.loc import Location
from smartbench.tools.ilf import ilf
from smartbench.tools.smartfuzz import smartfuzz


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

    def __str__(self):
        """Printing to string."""
        return (
            f"{{ Tool: {self.name}, Path: {self.executable}, "
            f"Arguments: {self.additional_args}}}"
        )

    def configure_output_file(self, result_dir: str) -> Optional[str]:
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

    def is_smartfuzz(self):
        """Check if the current tool is SmartFuzz."""
        return self.id.casefold() == smartfuzz.TOOL_NAME.casefold()

    def is_ilf(self):
        """Check if the current tool is ILF."""
        return self.id.casefold() == ilf.TOOL_NAME.casefold()

    # FIXME: make this function abstract, implement in each tool instead.
    def make_analysis_command(
        self,
        test_file: str,
        contract_names: List[str],
        test_output_dir: str,
        timeout: Optional[int] = None,
        use_docker=True,
    ) -> str:
        """Make an analysis command for a tool."""
        # Deterministically increase from seed. Reproducible randomness
        # TODO: add random seed for fuzzing tools if they support it.
        self.random_seed += 1

        arguments = self.default_arguments
        timeout = timeout if timeout is not None else self.default_timeout

        make_command = None
        if self.is_smartfuzz():
            make_command = smartfuzz.make_analysis_command
            arguments += " --seed " + str(self.random_seed)
        else:
            raise Exception(f"TODO: implement for tool: {self.id}")

        if self.additional_args:
            arguments = arguments + " " + self.additional_args

        output_file = self.configure_output_file(test_output_dir)

        cmd = make_command(
            self.executable, arguments, test_file, output_file, timeout
        )

        return cmd

    @abstractmethod
    def make_deployment_command(self, test_file, result_dir) -> str:
        """Make deployment command for an analyzer."""

    @abstractmethod
    def parse_analysis_output(self, test_output_dir: str) -> List[Issue]:
        """Process analysis result of each tool."""

    def match_location_of_issue_to_annotation(
        self, issue: Issue, annot: BugAnnot
    ) -> bool:
        """Default function to check whether the location of an issue reported
        by an analysis tool is related to the location of a bug annotation.
        """

        iloc: Location = issue.location
        # Check whether the issue location is covered by the annotation location.
        if iloc.start_line is None or iloc.end_line is None:
            return False
        if iloc.start_line < annot.start_line + 1:
            return False
        if iloc.end_line > annot.end_line + 1:
            return False

        # Pass all criteria to match an issue with a bug annotation
        return True

    @abstractmethod
    def parse_instruction_coverage(self, test_output_dir: str):
        """Parse instruction coverage of analysis results.
        This function should be implemented by each analysis tool."""
