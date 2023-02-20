#!/usr/bin/env python3

"""Module handling Slither."""


# Library
from smartbench.tools import tool

def read_slither_configuration():
    config = tool.parse_tool_configuration("slither")
    print("Command:", config.analyzer_path)
