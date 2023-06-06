#!/usr/bin/env python3

"""Module for parsing results."""


# Standard Library
import bisect
import os
import pathlib
import json

from enum import Enum
from typing import Dict, List, Optional, Tuple, no_type_check

# Library
from smartbench import annotation, logger, printer, validator
from smartbench.annotation import AnnotFormat, BugAnnot
from smartbench.issue import Issue
from smartbench.printer import (
    debug,
    error,
    error_traceback,
    safe_print,
    safe_print_underline,
    warning,
)
from smartbench.tools.config import load_tool_configuration
from smartbench.tools.confuzzius.confuzzius import Confuzzius
from smartbench.tools.ilf.ilf import Ilf
from smartbench.tools.sfuzz.sfuzz import Sfuzz
from smartbench.tools.smartian.smartian import Smartian
from smartbench.tools.tool import EXECUTION_LOG_SUFFIX, Tool
from smartbench.validator import ValidationResult


class SummaryPrinting(str, Enum):
    """Class representing the summary printing mode"""

    CONCISE_PRINTING = "Concise Printing"
    DETAILED_PRINTING = "Detailed Printing"
    DISABLE_PRINTING = "Disable Printing"


class AnalysisResult:
    """Class capturing the validation result between detected issues and
    bug annotations in a smart contract."""

    def __init__(
        self,
        tool: Tool,
        test_file: Optional[str],
        test_output_dir: str,
        bug_annots: Optional[List[BugAnnot]],
        annot_format: Optional[AnnotFormat],
        issues: Optional[List[Issue]] = None,
        validation_result: Optional[ValidationResult] = None,
    ):
        self.tool: Tool = tool

        # Paths of test file and output directory
        self.test_file: Optional[str] = test_file
        self.test_output_dir: str = test_output_dir

        # Concise path of test file, which is the longest common suffix of
        # the test file path and output directory path
        if self.test_file is not None:
            self.concise_test_file = os.path.commonprefix(
                [self.test_file[::-1], self.test_output_dir[::-1]]
            )[::-1]
            if self.concise_test_file.startswith("/"):
                self.concise_test_file = self.concise_test_file[1:]

        # All the issues that are reported
        self.issues: Optional[List[Issue]] = issues

        # Bug annotations specified for the test files.
        self.bug_annots: Optional[List[BugAnnot]] = bug_annots
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

    def simplify(self) -> Dict:
        result = {}
        # print (self, self.tool, self.test_file, self.test_output_dir, self.bug_annots, self.annot_format, self.issues, self.validation_result)
        result["test_file"] = self.test_file
        if self.validation_result:
            result["missing_annots"] = self.validation_result.missing_bugs
            result["detected_annots"] = [f[1] for f in self.validation_result.correct_bugs]
            result["unlabelled_issues"] = self.validation_result.unlabelled_issues
        return result
    def print_detailed_summary(self) -> None:
        """Print statistic summary of detected issues for a test file"""
        safe_print("")
        safe_print_underline("ANALYSIS RESULT")
        safe_print(f"- Tool: {self.tool.name}")
        safe_print(f"- Test file: {self.test_file}")
        if self.issues is None:
            safe_print("- Status: Failed")
        else:
            safe_print("- Status: Succeeded")
            safe_print(f"- Bug annotations: {len(self.bug_annots)}")
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


def is_tool_output_dir(tool: Tool, test_output_dir: str) -> bool:
    """Check whether `test_dir` containing analysis log of a tool for
    a test file."""
    log_file = tool.configure_log_file(test_output_dir)
    return os.path.exists(log_file)


def parse_test_file_bug_annots(
    test_file: str,
    annot_format: Optional[AnnotFormat] = None,
    summary_printing: SummaryPrinting = SummaryPrinting.CONCISE_PRINTING,
) -> List[BugAnnot]:
    bug_annots = annotation.parse_bug_annotations(test_file, annot_format)
    if summary_printing != SummaryPrinting.DISABLE_PRINTING:
        safe_print_underline("Bug annotations")
        if len(bug_annots) > 0:
            safe_print("\n".join([format(f"- {x}") for x in bug_annots]))
            safe_print("")
        else:
            safe_print("- No bug annotation is found!\n")
    return bug_annots


def parse_test_file_output_dir(
    tool: Tool,
    bug_annots: Optional[List[BugAnnot]],
    test_output_dir: str,
    annot_format: Optional[AnnotFormat] = None,
    summary_printing: SummaryPrinting = SummaryPrinting.CONCISE_PRINTING,
    file_suffix: Optional[str] = "",
) -> Optional[List[Issue]]:
    """Parsing and printing analysis results"""

    tool.prepare_parsing_analysis_output()
    issues = tool.parse_analysis_output(test_output_dir, file_suffix)
    if (
        issues is not None
        and summary_printing != SummaryPrinting.DISABLE_PRINTING
    ):
        safe_print_underline("Detected issues")
        if len(issues) > 0:
            print_smartbugs_kind = False
            print_solidifi_kind = False
            if bug_annots is not None:
                for annot in bug_annots:
                    if annot.annot_format == AnnotFormat.SMARTBUGS:
                        print_smartbugs_kind = True
                    if annot.annot_format == AnnotFormat.SOLIDIFI:
                        print_solidifi_kind = True
                    if print_smartbugs_kind and print_solidifi_kind:
                        break
            issues_strs = [
                x.pretty_print(
                    True,
                    print_smartbugs_kind,
                    print_solidifi_kind,
                    summary_printing == SummaryPrinting.CONCISE_PRINTING,
                )
                for x in issues
            ]
            safe_print("\n\n".join([format(f"- {s}") for s in issues_strs]))
        else:
            safe_print("- No issue is detected!\n")

    return issues


def parse_test_file_result(
    tool: Tool,
    test_output_dir: str,
    validate: Optional[bool] = False,
    export_summary: Optional[str] = None,
    annot_format: Optional[AnnotFormat] = None,
    summary_printing: SummaryPrinting = SummaryPrinting.CONCISE_PRINTING,
    file_suffix: Optional[str] = "",
) -> Optional[AnalysisResult]:
    printer.print_medium_dashed_separator_line()

    safe_print(f"Output directory: {test_output_dir}\n")

    safe_print(f"Analysis tool: {tool.id}\n")

    # Get test file
    test_output_dir = os.path.abspath(test_output_dir)
    log_file = tool.configure_log_file(test_output_dir)
    test_file = logger.get_input_test_file(log_file)
    safe_print(f"Test file: {test_file}\n")

    bug_annots = None
    issues = None
    validation = None

    if test_file is None:
        error(f"Unable to get input test file: {test_file}")
    elif not os.path.exists(test_file):
        error(f"Input test file does not exists: {test_file}")
    else:
        # Parse bug annotation in input test file
        bug_annots = parse_test_file_bug_annots(test_file, annot_format)

        # Parse issues detected by an analysis tool
        issues = parse_test_file_output_dir(
            tool,
            bug_annots,
            test_output_dir,
            annot_format,
            summary_printing,
            file_suffix,
        )

        # Validate detected issues against the bug annotations
        if validate and issues is not None and bug_annots is not None:
            validation = validator.validate_issues(test_file, tool, issues, bug_annots)

    res = AnalysisResult(
        tool,
        test_file,
        test_output_dir,
        bug_annots,
        annot_format,
        issues,
        validation,
    )

    if res.issues is None:
        warning(f"Failed to parse analysis result for: {test_file}")
    elif summary_printing:
        res.print_detailed_summary()
    else:
        safe_print("Parsed analysis results successfully!")

    return res


def guess_analysis_tools(test_output_dir: str) -> List[Tool]:
    """Guess analysis tools corresponding to a test output directory."""
    tools = []

    # Find tool IDs by looking at execution log files
    for file_name in os.listdir(test_output_dir):
        if file_name.endswith(EXECUTION_LOG_SUFFIX):
            tool_id = file_name[0 : -len(EXECUTION_LOG_SUFFIX)]
            try:
                if tool := load_tool_configuration(tool_id):
                    tools.append(tool)
            except Exception:
                error_traceback(f"Failed to load tool configuration: {tool_id}")

    return tools


def parse_result_directory(
    results_dir: str,
    only_tools: Optional[List[str]] = None,
    validate: Optional[bool] = False,
    export_summary: Optional[str] = None,
    annot_format: Optional[AnnotFormat] = None,
    summary_printing: SummaryPrinting = SummaryPrinting.CONCISE_PRINTING,
    file_suffix: Optional[str] = "",
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

    # Find output directory of all test files
    test_output_dirs = [p[0] for p in os.walk(results_dir)]

    for test_output_dir in test_output_dirs:
        if not os.path.isdir(test_output_dir):
            continue

        tools = guess_analysis_tools(test_output_dir)

        if only_tools is not None:
            tools = [t for t in tools if any(t.id == s for s in only_tools)]

        for tool in tools:
            tool_result = parse_test_file_result(
                tool,
                test_output_dir,
                validate,
                export_summary,
                annot_format,
                summary_printing,
                file_suffix=file_suffix,
            )
            if tool_result is not None:
                all_results.append(tool_result)

    safe_print("Parsing result completed!")
    print_benchmarking_results(results_dir, all_results, file_suffix=file_suffix)

    return all_results


def parse_instruction_coverage(results_dir: str, tool: str="") -> None:
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
    if len(tool) > 0:
        items = tool
        print ("itemss", items)
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
    file_suffix: str = "",
) -> None:
    printer.print_long_double_separator_line()
    safe_print("BENCHMARKING SUMMARY")

    tools_results = group_analysis_result_by_tools(results)

    for tool_id in tools_results.keys():
        printer.print_short_dashed_separator_line()
        safe_print(f"Detailed result of: {tool_id}\n")

        # Count number of successful and failed cases
        num_succeeded = num_failed_annots = num_failed_result = 0

        for result in tools_results[tool_id]:
            test_file = result.concise_test_file

            if result.test_file is None:
                result_dir = result.test_output_dir
                safe_print(f"!! Input test file not found: {result_dir}")
                continue

            if result.bug_annots is None:
                safe_print(f"- {test_file}: Failed, unable to parse bug annots")
                num_failed_annots += 1
                continue

            num_annots = len(result.bug_annots)
            if result.issues is None:
                num_failed_result += 1
                safe_print(f"- {test_file}: Failed, {num_annots}")
                continue

            num_succeeded += 1
            num_issues = len(result.issues)

            validation = result.validation_result
            if validation is None:
                safe_print(
                    f"- {test_file}: Succeeded, {num_annots}, "
                    f"{num_issues}, no validation"
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
            f"\nOverall result: {tool_id}\n"
            f"- {num_succeeded} succeeded\n"
            f"- {num_failed_annots} failed to parse bug annots\n"
            f"- {num_failed_result} failed to parse results"
        )

    export_benchmarking_results_to_csv_format(results_dir, tools_results, file_suffix=file_suffix)
    export_raw_results_to_json_format(results_dir, tools_results, file_suffix=file_suffix)

def json_decoder(obj:object):
    if isinstance(obj, BugAnnot) or isinstance(obj, Issue):
        return obj.to_json()
    else:
        return obj.__dict__

def export_raw_results_to_json_format(
    result_dir: str,
    tools_results: Dict[str, List[AnalysisResult]],
    file_suffix: str = "",
) -> None:
    """Export raw results to JSON files."""
    printer.print_short_dashed_separator_line()
    safe_print("Exporting raw results to JSON files...")

    for tool_id in tools_results.keys():
        results: List[AnalysisResult] = tools_results[tool_id]
        simplified_results = [result.simplify() for result in results]
        result_file = f"raw_results_{tool_id}.json{file_suffix}"
        result_file = os.path.join(result_dir, result_file)

        safe_print(f"- {result_file}")

        with open(result_file, "w", encoding="utf-8") as file:
            json.dump(simplified_results, file, default=json_decoder)

    safe_print("Exporting raw results to JSON files completed!")


def export_benchmarking_results_to_csv_format(
    result_dir: str,
    tools_results: Dict[str, List[AnalysisResult]],
    file_suffix: str = "",
) -> None:
    """Export benchmarking results to CSV files."""
    printer.print_short_dashed_separator_line()
    safe_print("Exporting benchmarking results to CSV files...")

    for tool_id in tools_results.keys():
        results: List[AnalysisResult] = tools_results[tool_id]
        result_file = f"results_{tool_id}.csv{file_suffix}"
        result_file = os.path.join(result_dir, result_file)

        safe_print(f"- {result_file}")
        total_correct = total_missing = total_unlabelled = 0
        with open(result_file, "w", encoding="utf-8") as file:
            file.write(f"Benchmarking result of {tool_id}\n")
            file.write("======================================\n\n")

            # Count number of successful and failed cases
            num_succeeded = num_failed_annots = num_failed_results = 0

            for result in results:
                if result.concise_test_file is None:
                    result_dir = result.test_output_dir
                    file.write(f"!! Input test file not found: {result_dir}")
                    continue

                test_file = result.concise_test_file
                file.write(f"- {test_file}: ")

                if result.bug_annots is None:
                    num_failed_annots += 1
                    file.write("Failed, unable to parse annots\n")
                    continue
                else:
                    num_annots = len(result.bug_annots)
                    if result.issues is None:
                        num_failed_results += 1
                        file.write(f"Failed, {num_annots}\n")
                        continue

                num_succeeded += 1
                num_issues = len(result.issues)
                file.write(f"Succeeded, {num_annots}, {num_issues}")

                validation = result.validation_result
                if validation is None:
                    file.write(",  no validation\n")
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
                    total_correct += num_correct
                    total_missing += num_missing
                    total_unlabelled += num_unlabelled
            safe_print(f"\ntotal_results: {total_correct} {total_missing} {total_unlabelled}")

            file.write(
                f"\nOverall result: {tool_id}\n"
                f"- {num_succeeded} succeeded\n"
                f"- {num_failed_annots} failed to parse annots\n"
                f"- {num_failed_results} failed to parse result\n"
            )
