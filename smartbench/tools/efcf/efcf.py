#!/usr/bin/env python3

"""Module handling CF/EF."""

# Standard Library
import json
import os
import re

from typing import List, Optional

# Third Party
from solc_json_parser.parser import SolidityAst

# Library
from smartbench import issue, logger
from smartbench.annotation import AnnotFormat, BugAnnot
from smartbench.docker import DockerContainer
from smartbench.issue import Checker, Confidence, Issue, IssueKind, Severity
from smartbench.printer import debug, error, error_traceback, warning, safe_print
from smartbench.solidity import solc
from smartbench.solidity.loc import Localizer, Location
from smartbench.tools.tool import Tool


class EFCF(Tool):
    def __init__(
        self,
        id: str,
        root_id: str,
        name: str,
        executable: str,
        default_arguments: str,
        default_timeout: int,
        additional_args: Optional[str] = None,
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
        """Function to make analysis command for `Smartian`. This function
        should have the same signature with other tools."""

        # Executable file
        cmd = f"docker exec -it {container.name} /root/{self.executable}"

        # Input file and contract names
        cmd += f" -f {test_file}"

        # Solc version
        if solc_version is not None:
            cmd += f" --solc-version {solc_version}"

        # Output directory: Need to add a sub-directory `output`
        # Otherwise, the log file is deleted from the results directory
        if test_output_dir.endswith("/"):
            test_output_dir += "output"
        else:
            test_output_dir += "/output"

        cmd += f" -o {test_output_dir}"

        # Timeout for each contract
        timeout = self.default_timeout if timeout is None else timeout
        cmd += f" -t {str(timeout)}"

        # Finally, pass default and additional arguments
        if self.default_arguments:
            cmd += f" {self.default_arguments}"
        if self.additional_args:
            cmd += f" {self.additional_args}"

        return cmd

    def parse_issue_kind(self, description: str) -> Optional[IssueKind]:
        """Parse issue kind from issue description reported by EF/CF"""
        if "[BUG] Violated Assertion/Event" in description:
            return IssueKind.ASSERTION_FAILURE

        if "[BUG] balance gain" in description:
            return IssueKind.BALANCE_GAIN

        if "[BUG] leaking ether" in description:
            return IssueKind.LEAKING_ETHER

        if "[BUG] controlled delegatecall" in description:
            return IssueKind.UNSAFE_DELEGATECALL

        if "[BUG] controlled selfdestruct" in description or "[BUG] selfdestruct DoS" in description:
            return IssueKind.UNSAFE_SELFDESTRUCT

        return None

    def parse_analysis_output(
        self,
        test_output_dir: str,
    ) -> Optional[List[Issue]]:
        """Parse output of EF/CF. Return `None` if result parsing is not
        successful."""

        log_file = self.configure_log_file(test_output_dir)
        test_file = logger.get_input_test_file(log_file)
        if test_file is None:
            warning(f"Failed to get input test file from: {log_file}")

        # Read analysis output from log file of EF/CF
        log_lines = []
        try:
            with open(log_file, "r", encoding="utf-8") as file:
                while line := file.readline():
                    log_lines.append(line.strip())
        except Exception as err:
            error(f"Failed to parse EF/CF log file: {log_file}\n\n{err}")
            return None

        # Construct AST of test file to get bug location
        ast = None
        if test_file is not None:
            best_solc_versions = solc.detect_best_solc_versions(test_file)
            for solc_version in best_solc_versions:
                try:
                    ast = SolidityAst(test_file, version=solc_version)
                    if ast is not None:
                        break
                except Exception:
                    continue
        if ast is None:
            warning(f"Failed to get AST of: {test_file}")

        # Parsing bug information in log data
        i = 0
        all_issues: List[Issue] = []
        contract_loc_dict: Dict[str, Tuple[int, int]] = {}
        contract_name = ""
        while i < len(log_lines):
            log_line = log_lines[i]
            i += 1

            # Parse contract name
            if match := re.search(
                r"launch-aflfuzz.sh ([a-zA-Z$_][a-zA-Z0-9$_]*)", log_line
            ):
                contract_name = match.groups(1)[0]
                continue

            # Skip parsing if not fuzzing any contract yet
            if contract_name == "":
                continue

            if (issue_kind := self.parse_issue_kind(log_line)) is not None:
                start_l = end_l = None
                if contract_name in contract_loc_dict:
                    (start_l, end_l) = contract_loc_dict[contract_name]
                elif ast is not None:
                    try:
                        contract = ast.contract_by_name(contract_name)
                        (start_l, end_l) = contract.line_num
                        # Store function location for later use
                        contract_loc_dict[contract_name] = (
                            start_l,
                            end_l,
                        )
                    except Exception:
                        continue

                loc = Location(
                    test_file,
                    contract_name=contract_name,
                    start_line=start_l,
                    end_line=end_l,
                )
                all_issues = issue.record_new_issue_and_deduplicate(
                    all_issues,
                    issue_kind,
                    log_line,
                    [loc],
                    Checker("EF/CF", "fuzzing"),
                )

        return all_issues

    def match_location_of_issue_to_annotation(
        self, issue: Issue, annot: BugAnnot
    ) -> bool:
        """Function to check whether an reported issue is related to a bug
        annotation."""

        # Find if a bug location matches with the annotation location.
        for iloc in issue.locations:
            # The bug line number must be reported explicitly by Silther
            if iloc.start_line is None or iloc.end_line is None:
                return False

            if (
                annot.annot_format == AnnotFormat.SMARTBUGS
                or annot.annot_format == AnnotFormat.SOLIDIFI
                or annot.annot_format == AnnotFormat.SMARTBENCH
                or annot.annot_format == AnnotFormat.VERISMART
            ):
                # EF/CF reports issue location as a range of the whole function.
                # If an issue and a bug annotation are relevant, then the
                # issue's location should cover the bug annotation's location.
                if (
                    iloc.start_line <= annot.start_line
                    and iloc.end_line >= annot.end_line
                ):
                    return True
            else:
                warning(f"Need to validate location for {annot.annot_format}")

        return False

    def parse_instruction_coverage(self, test_output_dir: str):
        """Parse instruction coverage of CF/EF"""
        lines = None
        log_file = self.configure_log_file(test_output_dir)
        coverage_file = os.path.join(test_output_dir, self.json_coverage_file)
        try:
            with open(log_file, "r", encoding="utf-8") as file:
                lines = [line.rstrip() for line in file]
        except Exception as err:
            error(f"Failed to parse CF/EF log file: {log_file}\n\n{err}")
            return None

        coverage_num = None
        for line in lines:
            coverage_match = re.search(r"Code Coverage \(Basic Blocks\) => ([0-9]+[.])?[0-9]+", line)
            if coverage_match:
                coverage = coverage_match.group()
                coverage_num = coverage.removeprefix("Code Coverage (Basic Blocks) => ")

        # Add the results of the last contract
        debug(f"coverage: {coverage_num}")
        with open(coverage_file, "w", encoding="utf-8") as file:
            file.write(str(coverage_num or "NONE"))
            file.close()

        return coverage_file

