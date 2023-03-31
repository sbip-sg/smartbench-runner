#!/usr/bin/env python3

"""Module handling analysis tools.

This is the shared interface for all tools.
"""

# Standard Library
import os
import sys

from abc import abstractmethod
from typing import List, Optional, Tuple

# Third Party
import tomli

# Library
import smartbench

from smartbench import debug
from smartbench.bug_annot import BugAnnot
from smartbench.issue import Checker, Confidence, Issue, IssueKind, Severity
from smartbench.loc import Location
from smartbench.tools.ilf import ilf
from smartbench.tools.smartfuzz import smartfuzz


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

    def is_smartfuzz(self):
        """Check if the current tool is SmartFuzz."""
        return self.id.casefold() == smartfuzz.TOOL_NAME.casefold()

    def is_ilf(self):
        """Check if the current tool is ILF."""
        return self.id.casefold() == ilf.TOOL_NAME.casefold()

    def make_analysis_command(
        self,
        test_file,
        test_output_dir,
        timeout=None,
        use_docker=True,
    ) -> Tuple[str, Optional[dict]]:
        """Make an analysis command for a tool."""
        # Deterministically increase from seed. Reproducible randomness
        # TODO: add random seed for fuzzing tools if they support it.
        self.random_seed += 1

        arguments = self.default_arguments
        timeout = timeout if timeout is not None else self.default_timeout

        make_command = None
        if self.is_ilf():
            make_command = ilf.make_analysis_command
        elif self.is_smartfuzz():
            make_command = smartfuzz.make_analysis_command
            arguments += " --seed " + str(self.random_seed)
        else:
            raise Exception(f"TODO: implement for tool: {self.id}")

        if self.additional_arguments:
            arguments = arguments + " " + self.additional_arguments

        output_file = self.configure_output_file(test_output_dir)

        cmd = make_command(
            self.path, arguments, test_file, output_file, timeout
        )

        return (cmd, None)

    @abstractmethod
    def make_deployment_command(self, test_file, result_dir) -> str:
        """Make deployment command for an analyzer."""

    @abstractmethod
    def process_analysis_result(self, test_output_dir: str) -> List[Issue]:
        """Process analysis result of each tool."""

    def match_location_of_issue_to_annotation(
        self, issue: Issue, annot: BugAnnot
    ) -> bool:
        """Default function to check whether an issue reported by the
        tool is related to a bug annotation.
        """

        # Check for issue kind
        if issue.issue_kind != annot.annot_kind:
            return False

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

    def parse_instruction_coverage(self, test_output_dir: str):
        """Default function to parse instruction coverage of analysis results."""

        # When the tool does not support generating instruction coverage
        return []
