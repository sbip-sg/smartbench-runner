#!/usr/bin/env python3

"""Module handling ILF."""

# Standard Library
import json
import math
import os
import re

from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Third Party
from solc_json_parser.standard_json_parser import StandardJsonParser

# Library
from smartbench import issue, logger
from smartbench.annotation import AnnotFormat, BugAnnot
from smartbench.docker import DockerContainer
from smartbench.issue import Checker, Issue, IssueKind
from smartbench.printer import debug, error, warning
from smartbench.solidity import solc
from smartbench.solidity.loc import Location
from smartbench.tools.tool import Tool


class Ilf(Tool):
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
        """Function to make analysis command for ILF. This function should have
        the same signature with other tools."""

        # Configure command
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

    def parse_issue_kind(self, bug_name: str) -> IssueKind:
        """Parse issue kind from issue description reported by ILF."""
        if bug_name == "BlockStateDep":
            return IssueKind.BLOCK_VALUE_DEPENDENCY

        if bug_name == "DangerousDelegatecall":
            return IssueKind.UNSAFE_DELEGATECALL

        if bug_name == "Leaking":
            return IssueKind.LEAKING_ETHER

        if bug_name == "Locking":
            return IssueKind.LOCKING_ETHER

        if bug_name == "Suicidal":
            return IssueKind.UNSAFE_SELFDESTRUCT

        if bug_name == "UnhandledException":
            return IssueKind.UNHANDLED_EXCEPTION

        if bug_name == "Reentrancy":
            return IssueKind.REENTRANCY

        return IssueKind.UNKNOWN

    def parse_analysis_output(
        self, test_output_dir: str
    ) -> Optional[List[Issue]]:
        """Parse output of ILF"""
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
                    if not has_fuzzing_result and '"tx_count"' in line:
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
                    ast = StandardJsonParser(test_file, version=solc_version)
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
        contract = None
        contract_info = []
        prev_line = None
        while i < len(log_lines):
            log_line = log_lines[i]
            i += 1

            # Parse contract name
            if match := re.search(
                r"Fuzzing contract: ([a-zA-Z$_][a-zA-Z0-9$_]*)", log_line
            ):
                if contract is not None and prev_line is not None:
                    contract_info.append((contract, prev_line))
                    prev_line = None

                contract = match.groups(1)[0]
                continue

            # Skip parsing if not fuzzing any contract yet
            if contract is None:
                continue

            # Search for the JSON data containing analysis information
            # Skip if the log line is not a JSON object
            match = re.search(r" ({.*})$", log_line)
            if match is None:
                continue

            prev_line = log_line

        # Add the information of the last contract
        if contract is not None and prev_line is not None:
            contract_info.append((contract, prev_line))

        for (contract, log_line) in contract_info:
            match = re.search(r" ({.*})$", log_line)

            # Parsing bug information
            analysis_data = json.loads(match.group(1))
            reported_bugs = analysis_data[contract]["bugs"]
            if reported_bugs is None:
                continue

            for bug_kind in reported_bugs:
                issue_kind = self.parse_issue_kind(bug_kind)
                functions = reported_bugs[bug_kind]
                for func_name in functions:
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

                    all_issues = issue.record_new_issue_and_deduplicate(
                        all_issues,
                        issue_kind,
                        log_line,
                        [loc],
                        Checker("ILF", "fuzzing"),
                    )

        return all_issues

    def match_location_of_issue_to_annotation(
        self, issue: Issue, annot: BugAnnot
    ):
        """Function to check whether the location of an reported issue is
        related to a bug annotation."""

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
                # ILF reports issue location as a range of the whole function.
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

    def parse_time(self, line: str):
        parts = line.split()
        if len(parts) >= 3:
            date = parts[0]
            time = parts[1].split(",")[0]
            date_time = date + " " + time
            date_time = date_time.removeprefix("[")
            try:
                time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
                return time

            except Exception:
                return None

        else:
            return None

    def parse_instruction_coverage(self, test_output_dir: str):
        """Parse instruction coverage of ILF"""
        lines = None
        log_file = self.configure_log_file(test_output_dir)
        debug("ILF log_file: ", log_file)
        try:
            with open(log_file, "r", encoding="utf-8") as file:
                lines = [line.rstrip() for line in file]
        except Exception as err:
            error(f"Failed to parse ILF log file: {log_file}\n\n{err}")
            return []

        contract_name = ""
        result_lines = []
        contract_result_info = []
        for line in lines:
            if "Fuzzing contract:" in line:
                if result_lines != [] and contract_name != "":
                    contract_result_info.append((contract_name, result_lines))
                    result_lines = []

                contract_name = line.removeprefix("Fuzzing contract: ")

            else:
                result_lines.append(line)

        if result_lines != []:
            contract_result_info.append((contract_name, result_lines))

        contract_coverage_list = []
        for contract_name, result_lines in contract_result_info:
            contract_coverage = []
            current_time = None
            counter = 0
            for line in result_lines:
                if "fuzzing start" in line:
                    time = self.parse_time(line)
                    if time is not None:
                        current_time = time
                        contract_coverage.append((counter, 0))

                parts = line.split()
                if len(parts) >= 3 and current_time is not None:
                    time = self.parse_time(line)
                    line = line.removeprefix(parts[0] + " ")
                    line = line.removeprefix(parts[1] + " ")

                    try:
                        data = json.loads(line)
                        instr = data[contract_name]["covered_insns"]
                        duration = (time - current_time).total_seconds()
                        if duration >= 1:
                            counter += duration
                            contract_coverage.append((counter, instr))
                            current_time = time

                    except Exception:
                        continue

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

        coverage_file = os.path.join(test_output_dir, self.json_coverage_file)
        with open(coverage_file, "w", encoding="utf-8") as file:
            file.write(results_json_obj_str)
            file.close()

        return coverage_file
