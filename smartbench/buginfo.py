#!/usr/bin/env python3


class BugInfo:
    """Class representing a bug found in smart contracts."""

    def __init__(
        self,
        filename,
        start_line,
        start_column,
        end_line,
        end_column,
        bug_type,
        description,
    ):
        self.filename = filename
        self.start_line = start_line
        self.start_column = start_column
        self.end_line = end_line
        self.end_column = end_column
        self.bug_type = bug_type
        self.description = description
