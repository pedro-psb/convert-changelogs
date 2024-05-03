import os
from pathlib import Path

import pytest
import tomlkit

from convert_changelogs.main import update_pyproject_toml

pyproject_sample = r"""[tool.towncrier]
package = "pulp_gem"
filename = "CHANGES.rst"
directory = "CHANGES/"
title_format = "{version} ({project_date})"
template = "CHANGES/.TEMPLATE.rst"
issue_format = "`#{issue} <https://github.com/pulp/pulp_gem/issues/{issue}>`__"

    [[tool.towncrier.type]]
        directory = "feature"
        name = "Features"
        showcontent = true

    [[tool.towncrier.type]]
        directory = "bugfix"
        name = "Bugfixes"
        showcontent = true

[tool.black]
line-length = 100
target-version = ["py36", "py37"]
exclude = '''
/(
    \.eggs
  | \.git
  | \.venv
  | _build
  | build
  | dist
  | migrations
  | docs
)/
'''
"""

pyproject_sample_result = r"""[tool.towncrier]
package = "pulp_gem"
filename = "CHANGES.md"
directory = "CHANGES/"
title_format = "## {version} ({project_date}) {{: #{version} }}"
template = "CHANGES/.TEMPLATE.md"
issue_format = "[#{issue}](https://github.com/pulp/pulp_gem/issues/{issue})"
start_string = "[//]: # (towncrier release notes start)\n"
underlines = ["", "", ""]

    [[tool.towncrier.type]]
        directory = "feature"
        name = "Features"
        showcontent = true

    [[tool.towncrier.type]]
        directory = "bugfix"
        name = "Bugfixes"
        showcontent = true

[tool.black]
line-length = 100
target-version = ["py36", "py37"]
exclude = '''
/(
    \.eggs
  | \.git
  | \.venv
  | _build
  | build
  | dist
  | migrations
  | docs
)/
'''
"""


def tests_pyproject_update(tmp_path):
    pyproject_file = Path(tmp_path / "pyproject.toml")
    pyproject_file.write_text(pyproject_sample)
    update_pyproject_toml(pyproject_file)
    assert pyproject_file.read_text() == pyproject_sample_result
