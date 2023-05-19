#!/usr/bin/env python3

"""Module handling VeriSmart analyzer."""

# Standard Library
import math
import re

from typing import List, Optional, Tuple

# Library
from smartbench import issue, logger
from smartbench.annotation import BugAnnot
from smartbench.docker import DockerContainer
from smartbench.issue import Checker, Issue, IssueKind
from smartbench.printer import error
from smartbench.solidity.loc import Location
from smartbench.tools.tool import Tool


class VeriSmart(Tool):
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
        Tool.__init__(
            self,
            id,
            root_id,
            name,
            executable,
            default_arguments,
            default_timeout,
            additional_args,
            random_seed,
        )

    def make_analysis_command(
        self,
        test_file: str,
        contracts: List[str],
        test_output_dir: str,
        container: DockerContainer,
        solc_version: str,
        timeout: Optional[int] = None,
    ) -> str:
        """Function to make analysis command for `VeriSmart`. This function
        should have the same signature with other tools."""

        # Executable file
        cmd = f"docker exec -it {container.name} /root/{self.executable}"

        # Input file and contract names
        cmd += f" -f {test_file}"
        if len(contracts) > 0:
            cmd += f" -c {' '.join(contracts)}"

        # Solc version
        if solc_version is not None:
            cmd += f" --solc-version {solc_version}"

        # Output directory
        cmd += f" -o {test_output_dir}"

        # Timeout for each contract
        timeout = self.default_timeout if timeout is None else timeout
        contract_timeout = math.ceil(timeout / len(contracts))
        cmd += f" -t {str(contract_timeout)}"

        # Finally, pass default and additional arguments
        if self.default_arguments:
            cmd += f" {self.default_arguments}"
        if self.additional_args:
            cmd += f" {self.additional_args}"

        return cmd

    def parse_issue_kind(
        self, log_line: str
    ) -> Optional[Tuple[IssueKind, int]]:
        match = None

        if match := re.search(r"\[IO\] line ([0-9]+).* unproven", log_line):
            issue_kind = IssueKind.INTEGER_OVERFLOW
        elif match := re.search(r"\[DZ\] line ([0-9]+).* unproven", log_line):
            issue_kind = IssueKind.DIVISION_BY_ZERO
        elif match := re.search(
            r"\[ASSERT] line ([0-9]+).* unproven", log_line
        ):
            issue_kind = IssueKind.ASSERTION_FAILURE
        elif match := re.search(r"\[KA] line ([0-9]+).* unproven", log_line):
            issue_kind = IssueKind.UNKNOWN
        elif match := re.search(
            r"\[ETH_LEAK] line ([0-9]+).* unproven", log_line
        ):
            issue_kind = IssueKind.LEAKING_ETHER
        elif match := re.search(r"\[RE_EL] line ([0-9]+).* unproven", log_line):
            issue_kind = IssueKind.REENTRANCY
        elif match := re.search(r"\[RE] line ([0-9]+).* unproven", log_line):
            issue_kind = IssueKind.REENTRANCY
        elif match := re.search(
            r"\[TX_ORG] line ([0-9]+).* unproven", log_line
        ):
            issue_kind = IssueKind.AUTHORIZATION_THROUGH_TX_ORIGIN

        if match is None:
            return None
        else:
            location = int(match.group(1))
            return (issue_kind, location)

    def parse_analysis_output(
        self, test_output_dir: str
    ) -> Optional[List[Issue]]:
        """Parse analysis result of VeriSmart. Return a list of detected issues,
        or `None` if the result parsing fails."""

        # Read analysis output from log file of VeriSmart
        log_file = self.configure_log_file(test_output_dir)
        test_file = logger.get_input_test_file(log_file)
        if test_file is None:
            error(f"Failed to get test file from: {log_file}")

        log_lines = []
        has_fuzzing_result = False
        try:
            with open(log_file, "r", encoding="utf-8") as file:
                while line := file.readline():
                    if not has_fuzzing_result and "[CHECKER]" in line:
                        has_fuzzing_result = True
                    log_lines.append(line.strip())
        except Exception as err:
            error(f"Failed to parse log file: {log_file}\n\n{err}")
            return None

        if not has_fuzzing_result:
            return None

        # Parsing bug information in log data
        i = 0
        all_issues: List[Issue] = []
        contract = ""
        while i < len(log_lines):
            log_line = log_lines[i]
            i += 1

            if match := re.search(
                r"Fuzzing contract: ([a-zA-Z$_][a-zA-Z0-9$_]*)", log_line
            ):
                contract = match.group(1)
            elif issue_kind_location := self.parse_issue_kind(log_line):
                description = log_line
                (issue_kind, line_loc) = issue_kind_location

                loc = Location(
                    test_file,
                    contract,
                    start_line=line_loc,
                    end_line=line_loc,
                )

                all_issues = issue.record_new_issue_and_deduplicate(
                    all_issues,
                    issue_kind,
                    description,
                    [loc],
                    Checker("VeriSmart", "fuzzing"),
                )

        return all_issues

    def match_location_of_issue_to_annotation(
        self, issue: Issue, annot: BugAnnot
    ) -> bool:
        """Function to check whether an reported issue is related to a bug
        annotation."""

        for iloc in issue.locations:
            # The bug line number must be reported explicitly by VeriSmart
            if iloc.start_line is None or iloc.end_line is None:
                return False

            # VeriSmart report a bug location at the line level so, the bug
            # annotation location must cover the issue location.

            if (
                iloc.start_line >= annot.start_line
                and iloc.end_line <= annot.end_line
            ):
                return True

        return False

    def parse_instruction_coverage(self, test_output_dir: str):
        """Parse code coverage of VeriSmart"""
        raise ValueError("Instruction coverage is not supported by VeriSmart!")
