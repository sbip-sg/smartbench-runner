#!/usr/bin/env python3

"""Module handling Smartian analyzer."""

# Standard Library
import json
import math
import os
import re

from typing import List, Optional, Tuple

# Third Party
from solc_json_parser.parser import SolidityAst

# Library
from smartbench import logger
from smartbench.annotation import BugAnnot
from smartbench.docker import DockerContainer
from smartbench.issue import Checker, Confidence, Issue, IssueKind, Severity
from smartbench.printer import debug, error, warning
from smartbench.solidity import solc
from smartbench.solidity.loc import Location
from smartbench.tools.tool import Tool


class Smartian(Tool):
    def __init__(
        self,
        id: str,
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
        solc_version: str,
        container: DockerContainer,
        timeout: Optional[int] = None,
        **kwargs,
    ) -> str:
        """Function to make analysis command for `Smartian`. This function should
        have the same signature with other tools."""

        # Executable file
        cmd = f"docker exec -it {container.name} /root/{self.executable}"

        # Input file and contract names
        cmd = cmd + " -f " + test_file
        if len(contracts) > 0:
            cmd = cmd + " -c " + " ".join(contracts)

        # Solc version
        if solc_version is not None:
            cmd = cmd + " --solc-version " + solc_version

        # Output directory
        cmd = cmd + " -o " + test_output_dir

        # Timeout for each contract
        timeout = self.default_timeout if timeout is None else timeout
        contract_timeout = math.ceil(timeout / len(contracts))
        cmd = cmd + " -t " + str(contract_timeout)

        # Finally, pass default and additional arguments
        if self.default_arguments:
            cmd = cmd + " " + self.default_arguments
        if self.additional_args:
            cmd = cmd + " " + self.additional_args

        return cmd

    def parse_issue_function_name(self, file) -> Optional[str]:
        """Parse issue location in sequence of transactions printed to the log
        file by Smartian. Each transaction contains the name of the function
        trigger it. This sequence of transaction ends with an empty line."""

        func_name = None
        while line := file.readline():
            line = line.strip()
            if line == "":
                break
            elif match := re.search(
                r"TX .* Function: ([a-zA-Z$_][a-zA-Z0-9$_]*)", line
            ):
                func_name = match.groups(1)[0]

        return func_name

    def parse_issue_kind(self, log_line) -> Optional[Tuple[IssueKind, str]]:
        match = None

        if match := re.search(r"Tx#.* found AssertionFailure .*", log_line):
            issue_kind = IssueKind.ASSERTION_FAILURE
        elif match := re.search(r"Tx#.* found ArbitraryWrite .*", log_line):
            issue_kind = IssueKind.WRITE_TO_ARBITRARY_STORAGE_LOCATION
        elif match := re.search(
            r"Tx#.* found BlockstateDependency .*", log_line
        ):
            issue_kind = IssueKind.BLOCK_VALUE_DEPENDENCY
        elif match := re.search(r"Tx#.* found ControlHijack .*", log_line):
            # TODO: Review this classification
            issue_kind = IssueKind.UNSAFE_DELEGATECALL
        elif match := re.search(r"Tx#.* found EtherLeak .*", log_line):
            issue_kind = IssueKind.LEAKING_ETHER
        elif match := re.search(r"Tx#.* found IntegerBug .*", log_line):
            issue_kind = IssueKind.INTEGER_BUG
        elif match := re.search(
            r"Tx#.* found MishandledException .*", log_line
        ):
            issue_kind = IssueKind.UNHANDLED_EXCEPTION
        elif match := re.search(r"Tx#.* found Reentrancy .*", log_line):
            issue_kind = IssueKind.REENTRANCY
        elif match := re.search(r"Tx#.* found SuicidalContract .*", log_line):
            issue_kind = IssueKind.UNSAFE_SELFDESTRUCT
        elif match := re.search(
            r"Tx#.* found TransactionOriginUse .*", log_line
        ):
            issue_kind = IssueKind.TRANSACTION_ORDER_DEPENDENCY
        elif match := re.search(r"Tx#.* found FreezingEther .*", log_line):
            issue_kind = IssueKind.LOCKING_ETHER
        elif match := re.search(
            r"Tx#.* found RequirementViolation .*", log_line
        ):
            issue_kind = IssueKind.REQUIREMENT_VIOLATION

        if match is None:
            return None
        else:
            description = match.group(0)
            return (issue_kind, description)

    def parse_analysis_output(
        self, test_output_dir: str
    ) -> Optional[List[Issue]]:
        """Parse analysis result of Smartian. Return a list of detected issues,
        or `None` if the result parsing fails.

        Descriptions of some bugs are described in Smartian's paper:
        https://dl.acm.org/doi/abs/10.1109/ASE51524.2021.9678888"""

        # Smartian does not write output to any JSON file, so we parse its
        # result from the log file.
        log_file = self.configure_log_file(test_output_dir)
        debug("Smartian log file: ", log_file)

        test_file = logger.get_input_test_file(log_file)
        assert (
            test_file is not None
        ), f"Failed to get test file from: {log_file}"

        issues_info = []
        with open(log_file, "r", encoding="utf-8") as file:
            contract_name = None
            while line := file.readline():
                line = line.strip()

                if match := re.search(
                    r"Fuzzing contract: ([a-zA-Z$_][a-zA-Z0-9$_]*)", line
                ):
                    contract_name = match.groups(1)[0]
                elif issue_kind_description := self.parse_issue_kind(line):
                    (kind, descr) = issue_kind_description
                    # Parse name of function causing the bug
                    func_name = self.parse_issue_function_name(file)
                    issues_info.append((kind, descr, contract_name, func_name))

        ast = None
        try:
            best_solc_versions = solc.detect_best_solc_versions(test_file)
            best_solc_versions = solc.detect_best_solc_versions(test_file)
            for solc_version in best_solc_versions:
                try:
                    ast = SolidityAst(test_file, version=solc_version)
                    if ast is not None:
                        break
                except Exception as err:
                    warning(
                        f"Smaritan result: failed to compile {test_file}\n\n"
                        f"{err}"
                    )
                    pass
        except Exception:
            pass

        all_issues = []
        for issue_info in issues_info:
            kind, descr, contract_name, func_name = issue_info
            start_line = end_line = None

            if ast is not None:
                debug(f"FUNCTION: {func_name}")
                try:
                    if func_name == "fallback":
                        func = ast.function_by_name(contract_name, "")
                    else:
                        func = ast.function_by_name(contract_name, func_name)
                    (start_line, end_line) = func.line_num
                except Exception as err:
                    debug(f"Failed to find function: {func_name}\n\n" f"{err}")

            loc = Location(test_file, start_line, None, end_line, None)
            issue = Issue(
                kind,
                descr,
                Severity.UNKNOWN,
                Confidence.UNKNOWN,
                loc,
                Checker("Smartian", "fuzzing"),
            )
            all_issues.append(issue)

        return all_issues

    def match_location_of_issue_to_annotation(
        self, issue: Issue, annot: BugAnnot
    ):
        """Function to check whether an reported issue is related to a bug
        annotation."""
        # TODO: implement
        return False

    def parse_instruction_coverage(self, test_output_dir: str):
        """Parse code coverage of Smartian"""
        log_file = self.configure_log_file(test_output_dir)
        coverage_file = os.path.join(test_output_dir, self.coverage_json_file)

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
