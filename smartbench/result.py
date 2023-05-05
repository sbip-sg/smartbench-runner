#!/usr/bin/env python3

"""Module for parsing results."""


# Standard Library
import bisect
import os
import pathlib

from typing import Dict, List, Optional, no_type_check

# Library
from smartbench import annotation, logger, printer, validator
from smartbench.annotation import AnnotFormat, BugAnnot
from smartbench.issue import Issue
from smartbench.printer import (
    debug,
    error,
    print_unless,
    safe_print,
    safe_print_underline,
    warning,
)
from smartbench.tools.config import load_tool_configuration
from smartbench.tools.confuzzius.confuzzius import Confuzzius
from smartbench.tools.ilf.ilf import Ilf
from smartbench.tools.sfuzz.sfuzz import Sfuzz
from smartbench.tools.smartian.smartian import Smartian
from smartbench.tools.tool import Tool
from smartbench.validator import ValidationResult


class AnalysisResult:
    """Class capturing the validation result between detected issues and
    bug annotations in a smart contract."""

    def __init__(
        self,
        tool: Tool,
        test_file: str,
        test_output_dir: str,
        bug_annots: List[BugAnnot],
        annot_format: Optional[AnnotFormat],
        is_successful: bool,
        issues: List[Issue] = [],
        validation_result: Optional[ValidationResult] = None,
    ):
        self.tool: Tool = tool

        # Paths of test file and output directory
        self.test_file: str = test_file
        self.test_output_dir: str = test_output_dir

        # Concise path of test file, which is the longest common suffix of
        # the test file path and output directory path
        self.concise_test_file = os.path.commonprefix(
            [self.test_file[::-1], self.test_output_dir[::-1]]
        )[::-1]
        if self.concise_test_file.startswith("/"):
            self.concise_test_file = self.concise_test_file[1:]

        # Whether the test file is successfully analyzed
        self.is_successful: bool = is_successful

        # All the issues that are reported
        self.issues: List[Issue] = list(issues) if issues else []

        # Bug annotations specified for the test files.
        self.bug_annots: List[BugAnnot] = list(bug_annots)
        self.annot_format = annot_format

        # Validation of detected issues
        self.validation_result = validation_result

    @no_type_check
    def __lt__(self, other) -> bool:
        """Compare analysis result by the test file name, case insensitive.
        Used only for the ordering purpose."""
        test_file = self.test_file.casefold()
        other_file = other.test_file.casefold()
        return test_file.__lt__(other_file)

    def print_detailed_summary(self) -> None:
        """Print statistic summary of detected issues for a test file"""
        safe_print("")
        safe_print_underline("ANALYSIS RESULT")
        safe_print(f"- Tool: {self.tool.name}")
        safe_print(f"- Test file: {self.test_file}")
        safe_print(
            f"- Status: {'Succeeded' if self.is_successful else 'Failed'}"
        )
        if self.is_successful:
            safe_print(f"- Annotated bugs: {len(self.bug_annots)}")
            safe_print(f"- Detected issues: {len(self.issues)}")

        # # Print severity information
        # severity_dict: Dict[Severity, int] = {}
        # for issue in self.issues:
        #     if issue.severity in severity_dict:
        #         severity_dict[issue.severity] += 1
        #     else:
        #         severity_dict[issue.severity] = 1
        # severity_info = [f"  + {s}: {severity_dict[s]}" for s in severity_dict]
        # if len(severity_dict) > 0:
        #     safe_print("\n".join(severity_info))

        # Print validation results
        if self.validation_result is not None:
            self.validation_result.print_summary()


def is_tool_output_dir(tool: Tool, test_dir: str) -> bool:
    """Check whether `test_dir` containing analysis log of a tool for
    a test file."""
    test_dir = os.path.abspath(test_dir)
    log_file = os.path.join(test_dir, tool.log_file)
    return os.path.exists(log_file)


def parse_test_file_output_dir(
    tool: Tool,
    test_file: str,
    test_output_dir: str,
    benchmark_names: Optional[List[str]] = None,
    validate: Optional[bool] = False,
    export_summary: Optional[str] = None,
    annot_format: Optional[AnnotFormat] = None,
    print_bug_details: bool = True,
) -> Optional[AnalysisResult]:
    """Parsing and printing analysis results"""
    # Parse and print bug annotations in test file
    bug_annots = annotation.parse_bug_annotations(test_file, annot_format)
    if print_bug_details:
        safe_print_underline("Bug annotations")
        if len(bug_annots) > 0:
            safe_print("\n".join([format(f"- {x}") for x in bug_annots]))
            safe_print("")
        else:
            safe_print("- No bug annotation is found!\n")

    # Parse and print detected bugs
    tool.prepare_parsing_analysis_output()
    issues = tool.parse_analysis_output(test_output_dir)
    validation = None
    if issues is None:
        is_successful = False
        issues = []
    else:
        is_successful = True
        if print_bug_details:
            safe_print_underline("Detected issues")
            if len(issues) > 0:
                safe_print("\n\n".join([format(f"- {x}") for x in issues]))
            else:
                safe_print("- No issue is detected!\n")

        if validate:
            validation = validator.validate_issues(tool, issues, bug_annots)

    return AnalysisResult(
        tool,
        test_file,
        test_output_dir,
        bug_annots,
        annot_format,
        is_successful,
        issues,
        validation,
    )


def parse_tool_results(
    tool: Tool,
    tool_results_dir: str,
    benchmark_names: Optional[List[str]] = None,
    validate: Optional[bool] = False,
    export_summary: Optional[str] = None,
    annot_format: Optional[AnnotFormat] = None,
    print_bug_details: bool = True,
) -> List[AnalysisResult]:
    printer.print_long_double_separator_line()
    safe_print(f"Parsing analysis result of: {tool.id}")

    # Find all output directories for each test file
    test_output_dirs = [p[0] for p in os.walk(tool_results_dir)]

    # Filter them by the benchmark names, and sort alphabetically
    if benchmark_names is not None:
        benchmark_paths = []
        for b in benchmark_names:
            if not b.endswith("/"):
                b += "/"
                benchmark_paths.append(os.path.join(tool_results_dir, b))

        test_output_dirs = [
            d
            for d in test_output_dirs
            if any([d.startswith(b) for b in benchmark_paths])
        ]
        test_output_dirs = sorted(test_output_dirs)

    all_results: List[AnalysisResult] = []
    for test_output_dir in test_output_dirs:
        if not is_tool_output_dir(tool, test_output_dir):
            continue

        printer.print_medium_dashed_separator_line()

        # Get test file
        test_output_dir = os.path.abspath(test_output_dir)
        log_file = os.path.join(test_output_dir, tool.log_file)
        debug(f"Log file: {log_file}")

        test_file = logger.get_input_test_file(log_file)
        safe_print(f"Test file: {test_file}\n")

        if test_file is None:
            warning(f"Unable to get test file: {test_file}")
            continue

        res = parse_test_file_output_dir(
            tool,
            test_file,
            test_output_dir,
            benchmark_names,
            validate,
            export_summary,
            annot_format,
            print_bug_details,
        )

        if res is not None:
            if not res.is_successful:
                warning(f"Failed to parse result of test file: {test_file}")
            elif print_bug_details:
                res.print_detailed_summary()
            else:
                safe_print("Parsed analysis results successfully!")

            all_results.append(res)

    return all_results


def parse_result_directory(
    results_dir: str,
    only_tools: Optional[List[Tool]] = None,
    benchmark_names: Optional[List[str]] = None,
    validate: Optional[bool] = False,
    export_summary: Optional[str] = None,
    annot_format: Optional[AnnotFormat] = None,
    print_bug_details: bool = True,
) -> List[AnalysisResult]:
    """Function to parse result directory of a tool.

    The input `result_dir` is the directory containing results of all
    tools.
    """
    safe_print(f"Parsing result directory: {results_dir}")

    path = pathlib.Path(results_dir)
    if not path.is_dir():
        warning(f"Directory does not exists: {results_dir}")
        return []

    all_results: List[AnalysisResult] = []

    # Parse results of each analysis tool
    tool_result_dirs = list(os.listdir(results_dir))
    for tool_output_dir in tool_result_dirs:
        tool_output_dir_path = os.path.join(results_dir, tool_output_dir)
        if not os.path.isdir(tool_output_dir_path):
            continue

        # Tool ID is assumed to be the same as tool_result_dir
        tool_id = tool_output_dir
        tool = load_tool_configuration(tool_id)

        if tool is None:
            warning(f"Invalid result directory of all tools: {results_dir}")
            continue

        if only_tools is not None and all(tool.id != t.id for t in only_tools):
            continue

        tool_results = parse_tool_results(
            tool,
            tool_output_dir_path,
            benchmark_names,
            validate,
            export_summary,
            annot_format,
            print_bug_details,
        )

        all_results.extend(tool_results)

    safe_print("Parsing result completed!")
    print_benchmarking_results(results_dir, all_results)

    return all_results


def parse_instruction_coverage(results_dir: str) -> None:
    """Function to parse code coverage from analysis results of a tool.

    The input `result_dir` is the directory containing results of all
    tools.
    """

    path = pathlib.Path(results_dir)
    if not path.is_dir():
        warning(f"Directory does not exists: {results_dir}")
        return

    # Parse results of each analysis tool
    items = list(os.listdir(results_dir))
    for item in items:
        item_path = os.path.join(results_dir, item)
        if not os.path.isdir(item_path):
            continue

        # Tool ID is assumed to be the same as tool_dir
        tool_id = item
        tool = load_tool_configuration(tool_id)

        if tool is None:
            warning(f"Unable to load tool configuration: {tool_id}")
            continue

        if not isinstance(tool, (Sfuzz, Confuzzius, Smartian, Ilf)):
            safe_print(f"Parse coverage is not supported for: {tool.id}")
            continue

        safe_print(f"{'=' * 55}\n")
        safe_print(f"Parsing analysis result of: {tool.id}\n")

        tool_output_dir = os.path.join(results_dir, tool_id)
        test_output_dirs = sorted([p[0] for p in os.walk(tool_output_dir)])
        for test_output_dir in test_output_dirs:
            if not is_tool_output_dir(tool, test_output_dir):
                continue

            if isinstance(tool, (Sfuzz, Confuzzius, Smartian, Ilf)):
                coverage = tool.parse_instruction_coverage(test_output_dir)
                safe_print(f"test_output_dir: {test_output_dir}")
                safe_print(f"coverage: {coverage}")

    safe_print("Parsing coverage completed!")


def group_analysis_result_by_tools(
    results: List[AnalysisResult],
) -> Dict[str, List[AnalysisResult]]:
    """Group all analysis results by tool name"""
    tools_results: Dict[str, List[AnalysisResult]] = {}

    for result in results:
        tool_id = result.tool.id
        if tool_id in tools_results:
            bisect.insort(tools_results[tool_id], result)
        else:
            tools_results[tool_id] = [result]

    return tools_results


def print_benchmarking_results(
    results_dir: str,
    results: List[AnalysisResult],
) -> None:
    printer.print_long_double_separator_line()
    safe_print("BENCHMARKING SUMMARY")

    tools_results = group_analysis_result_by_tools(results)

    for tool_id in tools_results.keys():
        printer.print_short_dashed_separator_line()
        safe_print(f"Detailed result of: {tool_id}\n")

        # Count number of successful and failed cases
        num_succeeded = num_failed = 0

        for result in tools_results[tool_id]:
            test_file = result.concise_test_file

            num_annots = len(result.bug_annots)
            if not result.is_successful:
                num_failed += 1
                safe_print(f"- {test_file}: Failed, {num_annots}")
                continue

            num_succeeded += 1
            num_issues = len(result.issues)

            validation = result.validation_result
            if validation is None:
                safe_print(
                    f"- {test_file}: Succeeded, {num_annots}, "
                    f"{num_issues}, [results were not validated]"
                )
                continue

            num_missing = len(validation.missing_bugs)
            if result.annot_format == AnnotFormat.SOLIDIFI:
                # In Solidifi benchmarks, multiple correct bugs under
                # the same injected buggy function are only count as
                # one, so the final number of correct is computed by
                # excluding the number of missing bugs
                num_correct = num_annots - num_missing
            else:
                num_correct = len(validation.correct_bugs)
            num_unlabelled = len(validation.unlabelled_issues)

            safe_print(
                f"- {test_file}: Succeeded, {num_annots}, "
                f"{num_issues}, {num_correct}, {num_missing}, {num_unlabelled}"
            )

        safe_print(
            f"\nOverall result: {tool_id}: "
            f"{num_succeeded} succeeded, {num_failed} failed."
        )

    export_benchmarking_results_to_csv_format(results_dir, tools_results)


def export_benchmarking_results_to_csv_format(
    result_dir: str,
    tools_results: Dict[str, List[AnalysisResult]],
) -> None:
    """Export benchmarking results to CSV files."""
    printer.print_short_dashed_separator_line()
    safe_print("Exporting benchmarking results to CSV files...")

    for tool_id in tools_results.keys():
        results: List[AnalysisResult] = tools_results[tool_id]
        result_file = f"results_{tool_id}.csv"
        result_file = os.path.join(result_dir, result_file)

        safe_print(f"- {result_file}")

        with open(result_file, "w", encoding="utf-8") as file:
            file.write(f"Benchmarking result of {tool_id}\n")
            file.write("======================================\n\n")

            # Count number of successful and failed cases
            num_succeeded = num_failed = 0

            for result in results:
                test_file = result.concise_test_file

                num_annots = len(result.bug_annots)
                file.write(f"- {test_file}: ")

                if not result.is_successful:
                    num_failed += 1
                    file.write(f"Failed, {num_annots}\n")
                    continue

                num_succeeded += 1
                num_issues = len(result.issues)
                file.write(f"Succeeded, {num_annots}, {num_issues}")

                validation = result.validation_result
                if validation is None:
                    file.write(",  [results were not validated]\n")
                else:
                    num_missing = len(validation.missing_bugs)

                    if result.annot_format == AnnotFormat.SOLIDIFI:
                        # In Solidifi benchmarks, multiple correct bugs under
                        # the same injected buggy function are only count as
                        # one, so the final number of correct is computed by
                        # excluding the number of missing bugs
                        num_correct = num_annots - num_missing
                    else:
                        num_correct = len(validation.correct_bugs)

                    num_unlabelled = len(validation.unlabelled_issues)
                    file.write(
                        f", {num_correct}, {num_missing}, {num_unlabelled}\n"
                    )

            file.write(
                f"\nOverall result: {tool_id}: "
                f"{num_succeeded} succeeded, {num_failed} failed."
            )


def export_benchmarking_results_to_json_format(
    result_dir: str,
    tools_results: Dict[str, List[AnalysisResult]],
    detailed_summary: bool = False,
) -> None:
    """Export benchmarking results to JSON files."""
    printer.print_short_dashed_separator_line()
    safe_print("Exporting benchmarking results to JSON files...")

    for tool_id in tools_results.keys():
        tool_results = tools_results[tool_id]

        json_tool_results = []

        # Count number of successful and failed cases
        num_succeeded = num_failed = 0

        for result in tool_results:
            test_file = (
                result.test_file
                if detailed_summary
                else result.concise_test_file
            )

            json_result = {}
            json_result["test_file"] = test_file

            if not result.is_successful:
                num_failed += 1
                json_result["analysis_status"] = "Failed"
                json_tool_results.append(json_result)
                continue

            num_succeeded += 1
            num_issues = len(result.issues)
            json_result["analysis_status"] = "Succeeded"
            json_result["num_issues"] = str(num_issues)

            validation = result.validation_result

            if validation is None:
                json_result["validation_status"] = "Invalidated"
                json_tool_results.append(json_result)
                continue

            json_result["validation_status"] = "Validated"

            num_correct = len(validation.correct_bugs)
            num_missing = len(validation.missing_bugs)
            num_unlabelled = len(validation.unlabelled_issues)

            json_result["correct_bugs"] = str(num_correct)
            json_result["missing_bugs"] = str(num_missing)
            json_result["unlabelled_bugs"] = str(num_unlabelled)
            json_tool_results.append(json_result)
