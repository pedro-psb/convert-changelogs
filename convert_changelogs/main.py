from __future__ import annotations

import argparse
import re
from pathlib import Path
from string import Template
from textwrap import dedent

import pypandoc
import tomlkit


def main():
    parser = argparse.ArgumentParser("convert-changes")
    parser.add_argument("plugin_name", type=str)
    args = parser.parse_args()
    result = markdown_changelog_migration(args.plugin_name)
    print(result)


def markdown_changelog_migration(plugin_name: str):
    result = {"changelog_converted": False, "pyproject_updated": False}

    # pyproject update
    pyproject_file = Path("pyproject.toml")
    if (
        r'start_string = "[//]: # (towncrier release notes start)\n"'
        not in pyproject_file.read_text()
    ):
        update_pyproject_toml(pyproject_file)
        result["pyproject_updated"] = True

    # changelog conversion
    rst_changes = Path("CHANGES.rst")
    if rst_changes.exists():
        convert_changelog(rst_changes, plugin_name)
        rst_changes.unlink()
        result["changelog_converted"] = True

    return result


def update_pyproject_toml(pyproject_file: Path):
    pyproject_data = tomlkit.loads(pyproject_file.read_text())

    package_name = pyproject_data["tool"]["towncrier"]["package"]  # type: ignore
    TOWNCRIER_TOML_DATA = {
        "package": package_name,
        "filename": "CHANGES.md",
        "directory": "CHANGES/",
        "title_format": "## {version} ({project_date}) {{: #{version} }}",
        "template": "CHANGES/.TEMPLATE.md",
        "issue_format": Template(
            "[#{issue}](https://github.com/pulp/$plugin_name/issues/{issue})"
        ).substitute(plugin_name=package_name),
        "start_string": "[//]: # (towncrier release notes start)\n",
        "underlines": ["", "", ""],
    }
    # update towncrier section
    for k, v in TOWNCRIER_TOML_DATA.items():
        pyproject_data["tool"]["towncrier"][k] = v  # type: ignore

    # re-write file
    pyproject_file.write_text(tomlkit.dumps(pyproject_data))


def convert_changelog(changes_rst: Path, plugin_name: str) -> Path:
    """Convert an rst changelog file to markdown.

    Args:
        changelog_file: The path to a rst changelog.
    Return:
        Path to new markdown changelog.
    """
    # pre-process
    with open(changes_rst, "r") as f:
        cleaned = pre_process(f.read())
    changes_rst.write_text(cleaned)

    # convert
    changes_md = changes_rst.parent / "CHANGES.md"
    changes_md_fn = str(changes_md.absolute())
    changes_rst_fn = str(changes_rst.absolute())
    pypandoc.convert_file(
        source_file=changes_rst_fn,
        outputfile=changes_md_fn,
        to="markdown",
        extra_args=["--wrap=preserve"],
    )

    # pos-process
    with open(changes_md, "r") as f:
        cleaned = post_process(f.read(), plugin_name)
    changes_md.write_text(cleaned)
    return changes_md


def pre_process(data) -> str:
    replaces = [
        (
            "Convert :github: directive",
            r":github:`(\d+)`",
            r"`#\1 <https://github.com/pulp/%this_plugin%/issues/\1>`__",
        ),
        (
            "Convert :redmine: directive",
            r":redmine:`(\d+)`",
            r"`#\1 <https://pulp.plan.io/issues/\1>`__",
        ),
        (
            "Convert :ref: directive w/ <...>",
            r":ref:`([a-zA-Z_\s\.]+)\s<[a-zA-Z_\s\.]+>`",
            r"*\1*",
        ),
        (
            "Convert :meth: directive w/ <...>",
            r":meth:(`[a-zA-Z_\s\.]+`)",
            r"\1",
        ),
        (
            "Convert :ref: directive without <...>",
            r":ref:`([a-zA-Z_\s\.]+)`",
            r"*\1*",
        ),
        (
            "Ensure double backticks: `someword` -> ``someword``",
            r"(?<![`:])(`[a-zA-Z_\.]+`)(?!`)",
            r"`\1`",
        ),
    ]
    f_new = data
    for _, pattern, repl in replaces:
        f_new = re.sub(pattern, repl, f_new)
    return f_new


def post_process(data, plugin_name: str) -> str:
    replaces = [
        (
            "Remove # Changelog to include header later",
            r"#\sChangelog",
            r"",
        ),
        (
            "Replace $this_plugin$ with the plugin name",
            "%this_plugin%",
            plugin_name,
        ),
        (
            "Use nice anchor links",
            r"## ([0-9]+\.[0-9]+\.[0-9]+) (\([0-9-]+\))",
            r"## \1 \2 {: #\1 }",
        ),
        (
            r"Remove backslahes before backticks",  # \' \* -> ' *
            r"\\(['\*`])",
            r"\1",
        ),
        (
            r"Normalize dash separators",
            r"\n-+\n",
            r"\n---\n",
        ),
        (
            "Remove double line breaks",
            r"^\n\n+",
            r"",
        ),
    ]
    f_new = data
    for _, pattern, repl in replaces:
        f_new = re.sub(pattern, repl, f_new)

    header = dedent(
        """\
        # Changelog

        [//]: # (You should *NOT* be adding new change log entries to this file, this)
        [//]: # (file is managed by towncrier. You *may* edit previous change logs to)
        [//]: # (fix problems like typo corrections or such.)
        [//]: # (To add a new change log entry, please see)
        [//]: # (https://docs.pulpproject.org/contributing/git.html#changelog-update)
        [//]: # (WARNING: Don't drop the towncrier directive!)

        [//]: # (towncrier release notes start)

        """
    )
    f_new = header + f_new
    return f_new


if __name__ == "__main__":
    main()
