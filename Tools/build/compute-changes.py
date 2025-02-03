from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from collections.abc import Set
from pathlib import Path

GITHUB_WORKFLOWS_PATH = Path(".github/workflows")
GITHUB_CODEOWNERS_PATH = Path(".github/CODEOWNERS")
CONFIGURATION_FILE_NAMES = frozenset(
    {".ruff.toml", "mypy.ini", ".pre-commit-config.yaml"}
)
SUFFIXES_DOCUMENTATION = frozenset({".rst", ".md"})
SUFFIXES_C_OR_CPP = frozenset({".c", ".h", ".cpp"})


@dataclass(kw_only=True, slots=True)
class Outputs:
    run_ci_fuzz: bool = False
    run_docs: bool = False
    run_hypothesis: bool = False
    run_tests: bool = False
    run_win_msi: bool = False


def compute_changes():
    target_branch = get_git_base_branch()
    changed_files = get_changed_files()
    outputs = process_changed_files(changed_files)
    outputs = process_target_branch(outputs, target_branch)

    if outputs.run_tests:
        print("Run tests")

    if outputs.run_hypothesis:
        print("Run hypothesis tests")

    if outputs.run_ci_fuzz:
        print("Run CIFuzz tests")
    else:
        print("Branch too old for CIFuzz tests; or no C files were changed")

    if outputs.run_docs:
        print("Build documentation")

    if outputs.run_win_msi:
        print("Build Windows MSI")

    print(outputs)

    write_github_output(outputs)


def get_changed_files(ref_a: str = "main", ref_b: str = "HEAD") -> Set[Path]:
    """List the files changed between two Git refs, filtered by change type."""
    changed_files_result = subprocess.run(
        ("git", "diff", "--name-only", f"{ref_a}...{ref_b}", "--"),
        capture_output=True,
        check=True,
        encoding="utf-8",
    )
    changed_files = changed_files_result.stdout.strip().splitlines()
    return frozenset(map(Path, filter(None, map(str.strip, changed_files))))


def get_git_base_branch() -> str:
    git_branch = os.environ.get("GITHUB_BASE_REF", "")
    git_branch = git_branch.removeprefix("refs/heads/")
    print(f"target branch: {git_branch!r}")
    return git_branch


def process_changed_files(changed_files: Set[Path]) -> Outputs:
    run_tests = False
    run_ci_fuzz = False
    run_docs = False
    run_win_msi = False

    for file in changed_files:
        file_name = file.name
        file_suffix = file.suffix
        file_parts = file.parts

        # Documentation files
        doc_or_misc = file_parts[0] in {"Doc", "Misc"}
        doc_file = file_suffix in SUFFIXES_DOCUMENTATION or doc_or_misc

        if file.parent == GITHUB_WORKFLOWS_PATH:
            if file_name == "build.yml":
                run_tests = run_ci_fuzz = True
            if file_name == "reusable-docs.yml":
                run_docs = True
            if file_name == "reusable-windows-msi.yml":
                run_win_msi = True

        if not (
            doc_file
            or file == GITHUB_CODEOWNERS_PATH
            or file_name in CONFIGURATION_FILE_NAMES
        ):
            run_tests = True

        # The fuzz tests are pretty slow so they are executed only for PRs
        # changing relevant files.
        if file_suffix in SUFFIXES_C_OR_CPP:
            run_ci_fuzz = True
        if file_parts[:2] in {
            ("configure",),
            ("Modules", "_xxtestfuzz"),
        }:
            run_ci_fuzz = True

        # Get a list of the changed documentation-related files
        # Check for docs changes
        # We only want to run this on PRs when related files are changed,
        # or when user triggers manual workflow run.
        if doc_file:
            run_docs = True

        # Get a list of the MSI installer-related files
        # Check for changes in MSI installer-related files
        # We only want to run this on PRs when related files are changed,
        # or when user triggers manual workflow run.
        if file_parts[:2] == ("Tools", "msi"):
            run_win_msi = True

    return Outputs(
        run_ci_fuzz=run_ci_fuzz,
        run_docs=run_docs,
        run_tests=run_tests,
        run_win_msi=run_win_msi,
    )


def process_target_branch(outputs: Outputs, git_branch: str) -> Outputs:
    if not os.environ.get("GITHUB_BASE_REF", ""):
        outputs.run_tests = True

    # Check if we should run hypothesis tests
    if git_branch in {"3.8", "3.9", "3.10", "3.11"}:
        print("Branch too old for hypothesis tests")
        outputs.run_hypothesis = False
    else:
        outputs.run_hypothesis = outputs.run_tests

    # oss-fuzz maintains a configuration for fuzzing the main branch of
    # CPython, so CIFuzz should be run only for code that is likely to be
    # merged into the main branch; compatibility with older branches may
    # be broken.
    if git_branch != "main":
        outputs.run_ci_fuzz = False

    return outputs


def write_github_output(outputs: Outputs) -> None:
    # https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/store-information-in-variables#default-environment-variables
    # https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/workflow-commands-for-github-actions#setting-an-output-parameter
    if "GITHUB_OUTPUT" not in os.environ:
        print("GITHUB_OUTPUT not defined!")
        return

    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
        f.write(f"run-cifuzz={bool_lower(outputs.run_ci_fuzz)}")
        f.write(f"run-docs={bool_lower(outputs.run_docs)}")
        f.write(f"run-hypothesis={bool_lower(outputs.run_hypothesis)}")
        f.write(f"run-tests={bool_lower(outputs.run_tests)}")
        f.write(f"run-win-msi={bool_lower(outputs.run_win_msi)}")


def bool_lower(value: bool, /) -> str:
    return "true" if value else "false"


if __name__ == "__main__":
    compute_changes()
