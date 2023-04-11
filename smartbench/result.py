#!/usr/bin/env python3

"""Module for parsing results."""


# Standard Library
import bisect
import os
import pathlib

from typing import Dict, List, Optional, Tuple

# Library
from smartbench import annotation, logger, validator
from smartbench.annotation import BugAnnot
from smartbench.issue import Issue, Severity
from smartbench.printer import warning
from smartbench.tools.config import load_tool_configuration
from smartbench.tools.confuzzius.confuzzius import Confuzzius
from smartbench.tools.mythril.mythril import Mythril
from smartbench.tools.sfuzz.sfuzz import Sfuzz
from smartbench.tools.slither.slither import Slither
from smartbench.tools.smartfuzz import smartfuzz
from smartbench.tools.smartian.smartian import Smartian
from smartbench.tools.tool import Tool
from smartbench.validator import Validation


class AnalysisResult:
    """Class capturing the validation result between detected issues and
    bug annotations in a smart contract."""

    def __init__(
        self,
        tool: Tool,
        test_file: str,
        issues: List[Issue],
        bug_annots: List[BugAnnot],
        validation: Optional[Validation],
    ):
        self.tool: Tool = tool
        self.test_file: str = test_file

        # All the issues that are reported
        self.issues: List[Issue] = list(issues)

        # Bug annotations specified for the test files.
        self.bug_annots: List[BugAnnot] = list(bug_annots)

        # Validation of detected issues
        self.validation = validation

    def __lt__(self, other):
        """Compare analysis result by the test file name, case insensitive.
        Used only for the ordering purpose."""
        test_file = self.test_file.casefold()
        other_file = other.test_file.casefold()
        return test_file.__lt__(other_file)

    def print_detailed_summary(self):
        """Print statistic summary of detected issues for a test file"""
        print("-------------------")
        print("ANALYSIS RESULT")
        print("-------------------")
        print(f"- Tool: {self.tool.name}")
        print(f"- Test file: {self.test_file}")
        print(f"- Annotated bugs: {len(self.bug_annots)}")
        print(f"- Detected issues: {len(self.issues)}")

        # Print severity information
        severity_stat: Dict[Severity, int] = {}
        for issue in self.issues:
            if issue.severity in severity_stat:
                severity_stat[issue.severity] += 1
            else:
                severity_stat[issue.severity] = 1
        severity_info = [f"  + {s}: {severity_stat[s]}" for s in severity_stat]
        if len(severity_stat) > 0:
            print("\n".join(severity_info))

        # Print validation results
        if self.validation is not None:
            self.validation.print_summary()

        print("")

    def print_benchmarking_summary(self):
        if self.validation is None:
            raise ValueError("Results were not validated for benchmarking!")

        validation = self.validation
        num_correct = len(validation.correct_bugs)
        num_missing = len(validation.missing_bugs)
        num_unlabelled = len(validation.unlabelled_issues)

        print(
            f"{self.test_file} {self.tool.name}, "
            f"{num_correct}, {num_missing}, {num_unlabelled}"
        )


def verify_tool_result_dir(tool: Tool, test_dir: str) -> bool:
    """Check whether `test_dir` containing analysis result of a tool for
    a test file."""

    test_dir = os.path.abspath(test_dir)
    output_file = os.path.join(test_dir, tool.output_file)
    return os.path.exists(output_file)


def parse_result_directory(
    results_dir: str,
    validate=False,
    benchmarking=False,
    benchmark_name=None,
) -> List[AnalysisResult]:
    """Function to parse result directory of a tool.

    The input `result_dir` is the directory containing results of all
    tools.
    """
    print(f"Parsing result directory: {results_dir}")

    path = pathlib.Path(results_dir)
    if not path.is_dir():
        warning(f"Directory does not exists: {results_dir}")
        return []

    all_results: List[Issue] = []

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

        print(f"{'=' * 55}\n")
        print(f"Parsing analysis result of: {tool.id}\n")

        tool_output_dir = os.path.join(results_dir, tool_id)
        test_output_dirs = sorted([p[0] for p in os.walk(tool_output_dir)])
        correct_bugs = 0
        annotations = 0
        for test_output_dir in test_output_dirs:
            if not verify_tool_result_dir(tool, test_output_dir):
                continue

            test_output_dir = os.path.abspath(test_output_dir)
            output_file = os.path.join(test_output_dir, tool.output_file)
            log_file = os.path.join(test_output_dir, tool.log_file)

            test_file = logger.get_input_test_file(log_file)
            print(f"{'-' * 45}\n")
            print(f"Test file: {test_file}\n")

            issues = tool.parse_analysis_output(test_output_dir)

            for issue in issues:
                print(f"- {issue}")

            bug_annots = []
            validation = None
            if validate or benchmarking:
                if test_file is None:
                    print(f"Unable to read test file: {test_file}")
                    print("Skip validating results!")
                else:
                    print("Bug annotations:")
                    bug_annots = annotation.parse_bug_annotations(
                        test_file, annot_format=benchmark_name
                    )
                    annotations += len(bug_annots)
                    for annot in bug_annots:
                        print(f"- {annot.print_concise()}")

                    validation = validator.validate_issues(
                        tool,
                        test_file,
                        issues,
                        bug_annots,
                        benchmark_name=benchmark_name or "",
                    )
                    correct_bugs += validation.num_correct_bugs()
                print("")

            ares = AnalysisResult(
                tool, test_file, issues, bug_annots, validation
            )
            ares.print_detailed_summary()
            all_results.append(ares)

        if validate:
            print(f"Result for {tool_id} is {correct_bugs}/{annotations}")

    print("Parsing result completed!")

    if benchmarking:
        print_benchmarking_results(results_dir, all_results)

    return all_results


def parse_instruction_coverage(results_dir: str):
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

        if not (
            isinstance(tool, Sfuzz)
            or isinstance(tool, Confuzzius)
            or isinstance(tool, Smartian)
        ):
            print(f"Parse coverage is not supported for: {tool.id}")
            continue

        print(f"{'=' * 55}\n")
        print(f"Parsing analysis result of: {tool.id}\n")

        tool_output_dir = os.path.join(results_dir, tool_id)
        test_output_dirs = sorted([p[0] for p in os.walk(tool_output_dir)])
        for test_output_dir in test_output_dirs:
            if not verify_tool_result_dir(tool, test_output_dir):
                continue

            if (
                isinstance(tool, Sfuzz)
                or isinstance(tool, Confuzzius)
                or isinstance(tool, Smartian)
            ):
                coverage = tool.parse_instruction_coverage(test_output_dir)
                print(f"test_output_dir: {test_output_dir}")
                print(f"coverage: {coverage}")

    print("Parsing coverage completed!")


def print_benchmarking_results(results_dir: str, results: List[AnalysisResult]):
    print("\n========================")
    print("BENCHMARKING RESULT")
    print("========================")

    tools_results = group_analysis_result_by_tools(results)

    for tool_id in tools_results.keys():
        print(f"\n** Result of {tool_id}\n")
        for result in tools_results[tool_id]:
            result.print_benchmarking_summary()

    export_benchmarking_results(results_dir, tools_results)


def group_analysis_result_by_tools(
    results: List[AnalysisResult],
) -> Dict[str, List[AnalysisResult]]:
    tools_results = {}

    for result in results:
        tool_id = result.tool.id
        if tool_id in tools_results:
            bisect.insort(tools_results[tool_id], result)
        else:
            tools_results[tool_id] = [result]

    return tools_results


def export_benchmarking_results(
    result_dir: str, tools_results: Dict[str, List[AnalysisResult]]
):
    """Record analysis log of all tools."""
    print(f"\n** Exporting benchmarking results...")
    for tool_name in tools_results.keys():
        results = tools_results[tool_name]

        result_file = os.path.join(result_dir, f"results_{tool_name}.csv")
        print(f"- {result_file}")
        with open(result_file, "w", encoding="utf-8") as file:
            file.write(f"Benchmarking result of {tool_name}\n")
            file.write("======================================\n\n")

            for result in results:
                validation = result.validation
                num_correct = len(validation.correct_bugs)
                num_missing = len(validation.missing_bugs)
                num_unlabelled = len(validation.unlabelled_issues)

                file.write(
                    f"{result.test_file}, {num_correct}, "
                    f"{num_missing}, {num_unlabelled}\n"
                )
