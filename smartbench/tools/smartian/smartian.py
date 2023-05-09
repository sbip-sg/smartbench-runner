#!/usr/bin/env python3

"""Module handling Smartian analyzer."""

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
from smartbench.annotation import BugAnnot
from smartbench.docker import DockerContainer
from smartbench.issue import Checker, Issue, IssueKind
from smartbench.printer import debug, error, warning
from smartbench.solidity import solc
from smartbench.solidity.loc import Location
from smartbench.tools.tool import Tool


class Smartian(Tool):
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
        """Function to make analysis command for `Smartian`. This function
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

    def parse_function_names_related_to_issue(
        self, log_lines: List[str], idx: int
    ) -> List[str]:
        """Parse issue location in sequence of transactions printed to the log
        file by Smartian. Each transaction contains the name of the function
        trigger it. This sequence of transaction ends with an empty line."""

        func_names = []

        for i in range(idx + 1, len(log_lines)):
            line = log_lines[i]
            if line == "":
                break
            elif match := re.search(
                r"TX.* Function: ([a-zA-Z$_][a-zA-Z0-9$_]*)", line
            ):
                func_names.append(match.group(1))

        return func_names

    def parse_issue_kind(
        self, log_line
    ) -> Optional[Tuple[IssueKind, str, str]]:
        match = None

        if match := re.search(r"Tx#([0-9]+) found AssertionFailure ", log_line):
            issue_kind = IssueKind.ASSERTION_FAILURE
        elif match := re.search(r"Tx#([0-9]+) found ArbitraryWrite ", log_line):
            issue_kind = IssueKind.WRITE_TO_ARBITRARY_STORAGE_LOCATION
        elif match := re.search(
            r"Tx#([0-9]+) found BlockstateDependency ", log_line
        ):
            issue_kind = IssueKind.BLOCK_VALUE_DEPENDENCY
        elif match := re.search(r"Tx#([0-9]+) found ControlHijack ", log_line):
            # TODO: Review this classification
            issue_kind = IssueKind.UNSAFE_DELEGATECALL
        elif match := re.search(r"Tx#([0-9]+) found EtherLeak ", log_line):
            issue_kind = IssueKind.LEAKING_ETHER
        elif match := re.search(r"Tx#([0-9]+) found IntegerBug ", log_line):
            issue_kind = IssueKind.INTEGER_BUG
        elif match := re.search(
            r"Tx#([0-9]+) found MishandledException ", log_line
        ):
            issue_kind = IssueKind.UNHANDLED_EXCEPTION
        elif match := re.search(r"Tx#([0-9]+) found Reentrancy ", log_line):
            issue_kind = IssueKind.REENTRANCY
        elif match := re.search(
            r"Tx#([0-9]+) found SuicidalContract ", log_line
        ):
            issue_kind = IssueKind.UNSAFE_SELFDESTRUCT
        elif match := re.search(
            r"Tx#([0-9]+) found TransactionOriginUse ", log_line
        ):
            issue_kind = IssueKind.TRANSACTION_ORDER_DEPENDENCY
        elif match := re.search(r"Tx#([0-9]+) found FreezingEther ", log_line):
            issue_kind = IssueKind.LOCKING_ETHER
        elif match := re.search(
            r"Tx#([0-9]+) found RequirementViolation ", log_line
        ):
            issue_kind = IssueKind.REQUIREMENT_VIOLATION

        if match is None:
            return None
        else:
            description = match.group(0)
            transaction_idx = match.group(1)
            return (issue_kind, transaction_idx, description)

    def parse_analysis_output(
        self, test_output_dir: str
    ) -> Optional[List[Issue]]:
        """Parse analysis result of Smartian. Return a list of detected issues,
        or `None` if the result parsing fails."""

        # Read analysis output from log file of Smartian
        log_file = self.configure_log_file(test_output_dir)
        test_file = logger.get_input_test_file(log_file)
        if test_file is None:
            error(f"Failed to get test file from: {log_file}")

        log_lines = []
        has_fuzzing_result = False
        try:
            with open(log_file, "r", encoding="utf-8") as file:
                while line := file.readline():
                    if not has_fuzzing_result and "Fuzz target :" in line:
                        has_fuzzing_result = True
                    log_lines.append(line.strip())
        except Exception as err:
            error(f"Failed to parse log file: {log_file}\n\n{err}")
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
        func_loc_dict: Dict[Tuple[str, str], Tuple[int, int]] = {}
        contract = ""
        while i < len(log_lines):
            log_line = log_lines[i]
            i += 1

            if match := re.search(
                r"Fuzzing contract: ([a-zA-Z$_][a-zA-Z0-9$_]*)", log_line
            ):
                contract = match.group(1)
            elif issue_kind_txn_description := self.parse_issue_kind(log_line):
                issue_locs = []
                (issue_kind, txn_idx, descr) = issue_kind_txn_description

                # Parse function names relevant to the issue
                func_names = self.parse_function_names_related_to_issue(
                    log_lines, i
                )
                for func_name in func_names:
                    start_l = end_l = None
                    if (contract, func_name) in func_loc_dict:
                        (start_l, end_l) = func_loc_dict[(contract, func_name)]
                    elif ast is not None:
                        try:
                            function = ast.function_by_name(contract, func_name)
                            (start_l, end_l) = function.line_num
                            # Store function location for later use
                            func_loc_dict[(contract, func_name)] = (
                                start_l,
                                end_l,
                            )
                        except Exception:
                            continue

                    loc = Location(
                        test_file,
                        contract,
                        func_name,
                        start_line=start_l,
                        end_line=end_l,
                    )
                    if loc not in issue_locs:
                        issue_locs.append(loc)

                all_issues = issue.record_new_issue_and_deduplicate(
                    all_issues,
                    issue_kind,
                    descr,
                    issue_locs,
                    Checker("Smartian", "fuzzing"),
                )

        return all_issues

        # issues_info: List[Tuple[IssueKind, str, str]] = []
        # for i in range(0, len(log_lines)):
        #     line = log_lines[i].strip()
        #     if match := re.search(
        #         r"Fuzzing contract: ([a-zA-Z$_][a-zA-Z0-9$_]*)", line
        #     ):
        #         contract_name = match.groups(1)[0]
        #     elif issue_kind_txn_description := self.parse_issue_kind(line):
        #         (kind, txn_idx, descr) = issue_kind_txn_description
        #         # Parse name of function causing the bug
        #         # func_name = self.parse_function_names_related_to_issue(
        #         #     log_lines, i, txn_idx
        #         # )
        #         # debug(f"FUNCTION NAME: {func_name}")
        #         # issues_info.append((kind, descr, contract_name, func_name))
        #         issues_info.append((kind, descr, contract_name))

        # ast = None
        # if test_file is not None:
        #     best_solc_versions = solc.detect_best_solc_versions(test_file)
        #     for solc_version in best_solc_versions:
        #         try:
        #             ast = SolidityAst(test_file, version=solc_version)
        #             if ast is not None:
        #                 break
        #         except Exception:
        #             continue
        # if ast is None:
        #     warning(f"Failed to get AST of: {test_file}")

        # all_issues: List[Issue] = []
        # contract_loc_dict: Dict[str, Tuple[int, int]] = {}

        # for issue_info in issues_info:
        #     # kind, descr, contract_name, func_name = issue_info
        #     (kind, descr, contract_name) = issue_info

        #     # Smartian doesn't pinpoint the bug location to exactly
        #     # which function or line of code, so we consider location of
        #     # the corresponding contract as the bug location.
        #     start_line = end_line = None
        #     if contract_name in contract_loc_dict:
        #         (start_line, end_line) = contract_loc_dict[contract_name]
        #     elif ast is not None:
        #         try:
        #             contract = ast.contract_by_name(contract_name)
        #             (start_line, end_line) = contract.line_num

        #             # Store in a dictionary for later use
        #             contract_loc_dict[contract_name] = (start_line, end_line)
        #         except Exception:
        #             debug(f"Smartian: failed to find contract: {contract_name}")

        #     loc = Location(
        #         test_file, contract_name, None, start_line, None, end_line, None
        #     )

        #     # Do not deduplicate issues since the issue location is of the whole
        #     # contracts
        #     issue = Issue(
        #         kind,
        #         descr,
        #         [loc],
        #         Checker("Smartian", "fuzzing"),
        #     )
        #     all_issues.append(issue)

        # return all_issues

    def match_location_of_issue_to_annotation(
        self, issue: Issue, annot: BugAnnot
    ):
        """Function to check whether an reported issue is related to a bug
        annotation."""

        for iloc in issue.locations:
            # The bug line number must be reported explicitly by Smartian
            if iloc.start_line is None or iloc.end_line is None:
                return False

            # Smartian report a bug location at the function level: begin and end
            # line of the function containing bugs. So, the bug location must cover
            # the issue location.

            if (
                iloc.start_line <= annot.start_line
                and iloc.end_line >= annot.end_line
            ):
                return True

        return False

    def parse_instruction_coverage(self, test_output_dir: str):
        """Parse code coverage of Smartian"""
        log_file = self.configure_log_file(test_output_dir)
        coverage_file = os.path.join(test_output_dir, self.json_coverage_file)

        lines = None
        try:
            with open(log_file, "r", encoding="utf-8") as file:
                lines = [line.rstrip() for line in file]
        except Exception as err:
            error(f"Failed to parse Smartian log file: {log_file}\n\n{err}")
            return None

        current_time = 0
        contract_coverage_list = []
        contract_name = ""
        first_coverage = (0, 0)
        contract_coverage = [first_coverage]

        for line in lines:
            match_str = re.search(r"Covered Instructions: [0-9]+", line)
            time_str = re.search(
                "(\d{2})[/.:](\d{2})[/.:](\d{2})[/.:](\d{2})", line
            )
            fuzz_match = re.search(r"Fuzzing contract: [a-zA-Z0-9$_]+", line)

            if fuzz_match:
                contract = fuzz_match.group()
                contract_name = contract.removeprefix("Fuzzing contract: ")
                # Results of new contract
                if len(contract_coverage) != 1:
                    contract_coverage_list.append(
                        (contract_name, contract_coverage)
                    )

                contract_coverage = [first_coverage]
                current_time = 0

            if match_str and time_str:
                time = time_str.group()
                seconds = int(time[9:11])
                minutes = int(time[6:8])
                hours = int(time[3:5])
                duration = hours * 3600 + minutes * 60 + seconds

                # Add a new pair every second
                if duration - current_time >= 1:
                    current_coverage = match_str.group()
                    current_coverage = current_coverage.removeprefix(
                        "Covered Instructions: "
                    )
                    contract_coverage.append((duration, int(current_coverage)))
                    current_time = duration

        # Append the last list if it is not empty
        if len(contract_coverage) != 1:
            contract_coverage_list.append((contract_name, contract_coverage))

        if contract_coverage_list == []:
            return None

        results_json_obj = {
            "coverage-interval": -1,
        }
        for contract_name, contract_coverage in contract_coverage_list:
            results_json_obj[contract_name] = contract_coverage

        results_json_obj_str = json.dumps(results_json_obj, indent=2)
        debug(f"coverage: {results_json_obj_str}")

        with open(coverage_file, "w", encoding="utf-8") as file:
            file.write(results_json_obj_str)
            file.close()

        return coverage_file
