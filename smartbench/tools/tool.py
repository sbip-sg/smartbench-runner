#!/usr/bin/env python3

"""Module handling analysis tools.

This is the shared interface for all tools.
"""

# Standard Library
import os
import sys

# Library
import smartbench

from smartbench import debug


class Tool:
    """Configuration of an analysis tool."""

    def __init__(
        self,
        id,
        name,
        homepage,
        category,
        path,
        default_arguments,
        json_output=None,
        log_output=None,
        timeout=None,
    ):
        self.id = id
        self.name = name
        self.homepage = homepage
        self.category = category
        self.path = path
        self.default_arguments = default_arguments
        self.json_output = json_output
        self.log_output = log_output
        self.timeout = timeout

    def __str__(self):
        return (
            '{ Tool: "'
            + self.name
            + '", Path: "'
            + self.path
            + '", Arguments: "'
            + self.additional_arguments
            + '"}'
        )

    def is_slither(self):
        """Check if the current tool is Slither."""
        return self.id.casefold() == SLITHER.casefold()

    def is_confuzzius(self):
        """Check if the current tool is Confuzzius."""
        raise Exception("TODO: implement")

    def is_smartfuzz(self):
        """Check if the current tool is SmartFuzz."""
        raise Exception("TODO: implement")

    def make_analysis_command(self, test_file, result_dir):
        """Make an analysis command for a tool."""
        # Prepare output directory for all results
        if self.is_slither():
            return slither.make_analysis_command(self, test_file, result_dir)

        if self.is_confuzzius():
            raise Exception("TODO: implement")

        if self.is_smartfuzz():
            raise Exception("TODO: implement")

        return "Unknown"
