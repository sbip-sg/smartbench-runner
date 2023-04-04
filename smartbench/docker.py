#!/usr/bin/env python3


class DockerJob:
    """Class modelling an analysis job running using Docker."""

    def __init__(self, index: int, total_jobs: int):
        self.index = int(index)
        self.total_jobs = int(total_jobs)

    def __str__(self):
        return f"{self.index}/{self.total_jobs}"
