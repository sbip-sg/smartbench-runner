#!/usr/bin/env python3

# Standard Library
import shlex
import subprocess

from subprocess import CalledProcessError
from typing import List

# Library
from smartbench.printer import error
from smartbench.tools.tool import Tool


class DockerContainer:
    """Class modelling a docker container for a job"""

    def __init__(self, name):
        self.name = name.lower()

    def __str__(self):
        return f"{self.name}"

    def start(self):
        """Start the docker container"""
        command = f"docker start {self.name}"
        try:
            print(f"Starting docker container: {self}")
            subprocess.run(
                shlex.split(command),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
        except CalledProcessError as err:
            error(f"Failed to start Docker container: {self}!\n" f"Log: {err}")

    def stop(self):
        """Stop the docker container"""
        command = f"docker stop {self.name}"
        try:
            print(f"Stopping docker container: {self}")
            subprocess.run(
                shlex.split(command),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
        except CalledProcessError as err:
            error(f"Failed to stop Docker container: {self}!\n" f"Log: {err}")


class DockerJob:
    """Class modelling an analysis job running using Docker."""

    def __init__(
        self,
        container: DockerContainer,
        tool: Tool,
        test_files: List[str],
        job_output_dir: str,
        timeout=None,
    ):
        self.container = container
        self.tool = tool

        # List of test file, which are relative path to the `/root/`
        # folder in a Docker container
        self.test_files = list(test_files)

        # Output directory of a job to store results of all test files
        self.job_output_dir = job_output_dir
        self.timeout = timeout

    def __str__(self):
        return f"{self.container.name}: {len(self.test_files)} tasks"
