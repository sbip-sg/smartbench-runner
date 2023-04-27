#!/usr/bin/env python3

# Standard Library
import os
import shlex
import subprocess

from subprocess import CalledProcessError
from typing import Dict, List, Optional

# Third Party
import docker

# Library
from smartbench import printer
from smartbench.printer import debug, error, error_traceback, safe_print


# Init some paths
SMARTBENCH_ROOT = os.path.dirname(os.path.dirname(__file__))
DOCKER_INSTALLER = "install-tool-docker.sh"


class DockerContainer:
    """Class modelling a docker container for a job"""

    def __init__(self, name: str):
        self.name = name.lower()

    def __str__(self) -> str:
        return f"{self.name}"

    def start(self) -> None:
        """Start the docker container"""
        command = f"docker start {self.name}"
        try:
            safe_print(f"Starting docker container: {self}")
            subprocess.run(
                shlex.split(command),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
        except CalledProcessError as err:
            error(f"Failed to start Docker container: {self}!\n")
            raise err

    def stop(self) -> None:
        """Stop the docker container"""
        command = f"docker stop {self.name}"
        try:
            safe_print(f"Stopping docker container: {self}")
            subprocess.run(
                shlex.split(command),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
        except CalledProcessError as err:
            error(f"Failed to stop Docker container: {self}!\n")
            raise err


def install_local_docker_containers(tool_id: str, num_containers: int) -> bool:
    """Build and install docker containers locally. Return `True` if the
    installation succeeds."""

    # Prepare command to install docker containers
    cmd = os.path.join(SMARTBENCH_ROOT, DOCKER_INSTALLER)
    cmd += f" -t {tool_id} -n {num_containers} --force-install"

    debug(f"Command: {cmd}")

    try:
        with subprocess.Popen(
            shlex.split(cmd),
            # stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE,
            shell=False,
        ) as proc:
            # Install Docker
            (stdout, _) = proc.communicate()
            return True
    except Exception:
        error_traceback(f"Failed to install docker container: {cmd}")
        return False


def install_remote_docker_containers(tool_id: str, num_containers: int) -> bool:
    """Pull and install docker containers from remote. Return `True` if the
    installation succeeds."""
    client = docker.from_env()

    # Pull Docker image
    image_name = f"taquangtrung/{tool_id}"

    printer.print_medium_double_separator_line()
    safe_print(f"Pulling Docker image: {image_name}")
    try:
        client.images.pull(image_name)
    except Exception:
        error_traceback(f"Failed to pull Docker image: {image_name}")
        return False

    # Install Docker containers
    for idx in range(1, num_containers + 1):
        container_name = f"{tool_id}-{idx}"
        printer.print_short_dashed_separator_line()
        safe_print(f"Creating new Docker container: {container_name}")

        try:
            container = client.containers.get(container_name)
            safe_print(
                f"Container {container_name} already exists. Removing it..."
            )
            container.remove(force=True)
        except Exception:
            pass

        # TODO: refactor code to use Python Docker later
        cmd = (
            f"docker run -itd --name {container_name}"
            f" -v {SMARTBENCH_ROOT}/benchmarks:/root/benchmarks"
            f" -v {SMARTBENCH_ROOT}/results:/root/results"
            f" {image_name}"
        )

    try:
        with subprocess.Popen(
            shlex.split(cmd),
            shell=False,
        ) as proc:
            (stdout, _) = proc.communicate()
            return True
    except Exception:
        error_traceback(f"Failed to create Docker container: {cmd}")
        return False
