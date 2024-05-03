import os
from pathlib import Path

import pytest

from convert_changelogs.main import markdown_changelog_migration

pyproject_sample = r"""[tool.towncrier]
package = "pulp_gem"
filename = "CHANGES.rst"
directory = "CHANGES/"
title_format = "{version} ({project_date})"
template = "CHANGES/.TEMPLATE.rst"
issue_format = "`#{issue} <https://github.com/pulp/pulp_gem/issues/{issue}>`__"


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

pyproject_sample_updated = r"""[tool.towncrier]
package = "pulp_gem"
filename = "CHANGES.md"
directory = "CHANGES/"
title_format = "## {version} ({project_date}) {{: #{version} }}"
template = "CHANGES/.TEMPLATE.md"
issue_format = "[#{issue}](https://github.com/pulp/pulp_gem/issues/{issue})"
start_string = "[//]: # (towncrier release notes start)\n"
underlines = ["", "", ""]
"""

@pytest.fixture(autouse=True)
def tempcwd(tmp_path):
    os.chdir(tmp_path)
    yield


def test_migration_applying(tmp_path):
    Path(tmp_path / "CHANGES.rst").write_text("hello")
    Path(tmp_path / "pyproject.toml").write_text(pyproject_sample)
    result = markdown_changelog_migration("pulp_gem")
    assert result["changelog_converted"] is True
    assert result["pyproject_updated"] is True


def test_migration_not_applying_when_already_converted(tmp_path):
    Path(tmp_path / "CHANGES.md").write_text("hello")
    Path(tmp_path / "pyproject.toml").write_text(pyproject_sample_updated)
    result = markdown_changelog_migration("pulp_gem")
    assert result["changelog_converted"] is False
    assert result["pyproject_updated"] is False
