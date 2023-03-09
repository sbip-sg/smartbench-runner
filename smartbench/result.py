#!/usr/bin/env python3

"""Module for parsing results."""


# Standard Library
from typing import List

# Library
from smartbench.issue import Issue
from smartbench.tools.slither import slither
from smartbench.tools.tool import Tool


def parse_analysis_result(
    tool: Tool, test_file: str, result_dir
) -> List[Issue]:
    parse_result = None

    if tool.is_slither():
        parse_result = slither.parse_slither_json_output

    if parse_result:
        return parse_result(tool.id, test_file, result_dir, tool.output_file)

    return []
