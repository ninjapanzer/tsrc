from typing import List, Tuple  # noqa
from path import Path
import ui

import tsrc
import tsrc.executor
import tsrc.git


class BadBranches(tsrc.Error):
    pass


class Syncer(tsrc.executor.Task[tsrc.Repo]):
    def __init__(self, workspace_path: Path) -> None:
        self.workspace_path = workspace_path
        self.bad_branches = list()  # type: List[Tuple[str, str, str]]

    def description(self) -> str:
        return "Synchronize workspace"

    def display_item(self, repo: tsrc.Repo) -> str:
        return repo.src

    def process(self, repo: tsrc.Repo) -> None:
        ui.info(repo.src)
        repo_path = self.workspace_path / repo.src
        self.fetch(repo_path)
        ref = None

        if repo.tag:
            ref = repo.tag
        elif repo.sha1:
            ref = repo.sha1

        if ref:
            self.sync_repo_to_ref(repo_path, ref)
        else:
            self.check_branch(repo, repo_path)
            self.sync_repo_to_branch(repo_path)

    def check_branch(self, repo: tsrc.Repo, repo_path: Path) -> None:
        current_branch = None
        try:
            current_branch = tsrc.git.get_current_branch(repo_path)
        except tsrc.Error:
            raise tsrc.Error("Not on any branch")

        # FIXME: is repo.branch allowed to be None ?
        if current_branch and current_branch != repo.branch:
            self.bad_branches.append((repo.src, current_branch, repo.branch))  # type: ignore

    @staticmethod
    def fetch(repo_path: Path) -> None:
        try:
            tsrc.git.run_git(repo_path, "fetch", "--tags", "--prune", "origin")
        except tsrc.Error:
            raise tsrc.Error("fetch failed")

    @staticmethod
    def sync_repo_to_ref(repo_path: Path, ref: str) -> None:
        ui.info_2("Resetting to", ref)
        status = tsrc.git.get_status(repo_path)
        if status.dirty:
            raise tsrc.Error("%s dirty, skipping")
        try:
            tsrc.git.run_git(repo_path, "reset", "--hard", ref)
        except tsrc.Error:
            raise tsrc.Error("updating ref failed")

    @staticmethod
    def sync_repo_to_branch(repo_path: Path) -> None:
        try:
            tsrc.git.run_git(repo_path, "merge", "--ff-only", "@{u}")
        except tsrc.Error:
            raise tsrc.Error("updating branch failed")

    def display_bad_branches(self) -> None:
        if not self.bad_branches:
            return
        ui.error("Some projects were not on the correct branch")
        headers = ("project", "actual", "expected")
        data = [
            ((ui.bold, name), (ui.red, actual), (ui.green, expected)) for
            (name, actual, expected) in self.bad_branches
        ]
        ui.info_table(data, headers=headers)
        raise BadBranches()
