#!/usr/bin/env python3

"""Module handling sFuzz."""

# Standard Library
import json
import math
import os
import re

from typing import Dict, List, Optional, Tuple

# Third Party
from solc_json_parser.parser import SolidityAst

# Library
from smartbench import issue, logger
from smartbench.annotation import AnnotFormat, BugAnnot
from smartbench.docker import DockerContainer
from smartbench.issue import Checker, Issue, IssueKind
from smartbench.printer import debug, error, safe_print, warning
from smartbench.solidity import solc
from smartbench.solidity.loc import Location
from smartbench.tools.tool import Tool


class Sfuzz(Tool):
    def __init__(
        self,
        id: str,
        name: str,
        executable: str,
        default_arguments: str,
        default_timeout: int,
        additional_args: Optional[str] = None,
    ):
        Tool.__init__(
            self,
            id,
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
        **kwargs,
    ) -> str:
        """
        Function to make analysis command for Slither.
        This function should have the same signature with other tools.
        """

        # Configure command
        cmd = f"docker exec -it {container.name} /root/{self.executable}"

        # Input file and contract names
        cmd = cmd + " -f " + test_file
        if len(contracts) == 1:
            cmd = cmd + " -c " + contracts[0]

        # Solc version
        if solc_version is not None:
            cmd = cmd + " --solc-version " + solc_version

        # Pass contract names to sFuzz
        if len(contracts) > 0:
            cmd = cmd + " -c " + " ".join(contracts)

        # Timeout
        timeout = self.default_timeout if timeout is None else timeout
        contract_timeout = math.ceil(timeout / len(contracts))
        cmd = cmd + " -t " + str(contract_timeout)

        # Pass arguments
        if self.default_arguments:
            cmd = cmd + " " + self.default_arguments
        if self.additional_args:
            cmd = cmd + " " + self.additional_args

        return cmd

    def parse_issue_kind(self, description: str) -> IssueKind:
        if "exception disorder : found" in description:
            return IssueKind.UNHANDLED_EXCEPTION

        if "reentrancy : found" in description:
            return IssueKind.REENTRANCY

        if "integer overflow : found" in description:
            return IssueKind.INTEGER_OVERFLOW

        if "integer underflow : found" in description:
            return IssueKind.INTEGER_UNDERFLOW

        if "dangerous delegatecall : found" in description:
            return IssueKind.UNSAFE_DELEGATECALL

        if "freezing ether : found" in description:
            return IssueKind.LOCKING_ETHER

        if "block number dependency : found" in description:
            return IssueKind.BLOCK_VALUE_DEPENDENCY

        if "timestamp dependency : found" in description:
            return IssueKind.BLOCK_VALUE_DEPENDENCY

        return IssueKind.UNKNOWN

    def parse_analysis_output(
        self, test_output_dir: str
    ) -> Optional[List[Issue]]:
        """Parse output of sFuzz"""
        log_file = self.configure_log_file(test_output_dir)
        test_file = logger.get_input_test_file(log_file)
        if test_file is None:
            warning(f"Failed to get input test file from: {log_file}")

        # Read analysis output from log file of ILF
        log_lines = []
        has_fuzzing_result = False
        try:
            with open(log_file, "r", encoding="utf-8") as file:
                while line := file.readline():
                    if not has_fuzzing_result and "coverage :" in line:
                        has_fuzzing_result = True
                    log_lines.append(line.strip())
        except Exception as err:
            error(f"Failed to parse sFuzz log file: {log_file}\n\n{err}")
            return None

        if not has_fuzzing_result:
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
            if "Fuzzing contract:" in log_line:
                contract_name = log_line.removeprefix("Fuzzing contract: ")
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
                        contract = ast.function_by_name(contract_name)
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
                    Checker("sFuzz", "fuzzing"),
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
                annot.annot_format == AnnotFormat.SMARTBUGS_FORMAT
                or annot.annot_format == AnnotFormat.SOLIDIFI_FORMAT
            ):
                # SFuzz reports issue location as a range of the whole function.
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
        """Parse instruction coverage of sFuzz"""
        lines = None
        log_file = self.configure_log_file(test_output_dir)
        coverage_file = os.path.join(test_output_dir, self.coverage_json_file)
        try:
            with open(log_file, "r", encoding="utf-8") as file:
                lines = [line.rstrip() for line in file]
        except Exception as err:
            error(f"Failed to parse sFuzz log file: {log_file}\n\n{err}")
            return None

        contract_coverage_list = []
        contract_name = ""
        first_coverage = 0
        contract_coverage = [first_coverage]

        for line in lines:
            match_str = re.search(r"coverage : [0-9]+", line)
            fuzz_match = re.search(r">> Fuzz [a-zA-Z0-9$_]+", line)
            if fuzz_match:
                contract = fuzz_match.group()
                contract_name = contract.removeprefix(">> Fuzz ")
                safe_print(f"contract: {contract_name}")
                if len(contract_coverage) != 1:
                    contract_coverage_list.append(
                        (contract_name, contract_coverage)
                    )
                    contract_coverage = [first_coverage]

            if match_str:
                coverage = match_str.group()
                coverage = coverage.removeprefix("coverage : ")
                contract_coverage.append(int(coverage))

        # Add the results of the last contract

        if contract_coverage != [0]:
            contract_coverage_list.append((contract_name, contract_coverage))

        if contract_coverage_list == []:
            return None

        results_json_obj = {
            "coverage-interval": 1,
        }
        for contract_name, contract_coverage in contract_coverage_list:
            results_json_obj[contract_name] = contract_coverage

        results_json_obj_str = json.dumps(results_json_obj, indent=2)
        debug(f"coverage: {results_json_obj_str}")

        with open(coverage_file, "w", encoding="utf-8") as file:
            file.write(results_json_obj_str)
            file.close()

        return coverage_file
