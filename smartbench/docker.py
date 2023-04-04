#!/usr/bin/env python3

# Standard Library
import shlex
import subprocess

from subprocess import CalledProcessError

# Library
from smartbench.printer import error


class DockerJob:
    """Class modelling an analysis job running using Docker."""

    def __init__(self, index: int, total_jobs: int):
        self.index = int(index)
        self.total_jobs = int(total_jobs)

    def __str__(self):
        return f"{self.index}/{self.total_jobs}"


class DockerContainer:
    """Class modelling a docker container for a job"""

    def __init__(self, name):
        self.name = name

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
