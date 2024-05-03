import os
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent

import pytest

from convert_changelogs.main import convert_changelog


@dataclass
class _TestCase:
    id: str
    input: str
    expected: str

    def __post_init__(self):
        self.input = dedent(self.input)
        self.expected = dedent(self.expected)


test_cases = [
    _TestCase(
        id="header-and-misc-unconverted-directives",
        input="""\
        =========
        Changelog
        =========

        ..
            You should *NOT* be adding new change log entries to this file, this
            file is managed by towncrier. You *may* edit previous change logs to
            fix problems like typo corrections or such.
            To add a new change log entry, please see
            https://docs.pulpproject.org/contributing/git.html#changelog-update

            WARNING: Don't drop the next directive!

        .. towncrier release notes start

        3.25.3 (2024-04-18)
        ===================

        Bugfixes
        --------

        - Fix publications created by mirror_complete syncs not having checksum_type set properly.
          `#3484 <https://github.com/pulp/pulp_rpm/issues/3484>`__
        - Added support for preventing unquoted NSVCA numerical values (e.g. ``"stream": 2.10``) of having zeros stripped on modulemd YAML files.
        - Fixed a warning that gets raised when cache is enabled: ``RuntimeWarning: coroutine
          'AsyncCache.delete' was never awaited``.
        - Fixed bug about malformed tuple introduced on the removal of sqlite-metadata support (PR #3328).
        - Fixed `gpgcheck` and `repo_gpgcheck`;`core.upload_create`;`pulp_last_updated`;`django-lifecycle`
        - :github:`4592`, :github:`5010`
        - :ref:`telemetry docs <analytics>`;:ref:`telemetry docs`;
        - :redmine:`1234`
        - :meth:`pulpcore.content.handler.Handler.list_directory`

        ----
        """,
        expected="""\
        # Changelog
        
        [//]: # (You should *NOT* be adding new change log entries to this file, this)
        [//]: # (file is managed by towncrier. You *may* edit previous change logs to)
        [//]: # (fix problems like typo corrections or such.)
        [//]: # (To add a new change log entry, please see)
        [//]: # (https://docs.pulpproject.org/contributing/git.html#changelog-update)
        [//]: # (WARNING: Don't drop the towncrier directive!)

        [//]: # (towncrier release notes start)

        ## 3.25.3 (2024-04-18) {: #3.25.3 }

        ### Bugfixes

        -   Fix publications created by mirror_complete syncs not having checksum_type set properly.
            [#3484](https://github.com/pulp/pulp_rpm/issues/3484)
        -   Added support for preventing unquoted NSVCA numerical values (e.g. `"stream": 2.10`) of having zeros stripped on modulemd YAML files.
        -   Fixed a warning that gets raised when cache is enabled: `RuntimeWarning: coroutine 'AsyncCache.delete' was never awaited`.
        -   Fixed bug about malformed tuple introduced on the removal of sqlite-metadata support (PR #3328).
        -   Fixed `gpgcheck` and `repo_gpgcheck`;`core.upload_create`;`pulp_last_updated`;`django-lifecycle`
        -   [#4592](https://github.com/pulp/pulp_rpm/issues/4592), [#5010](https://github.com/pulp/pulp_rpm/issues/5010)
        -   *telemetry docs*;*telemetry docs*;
        -   [#1234](https://pulp.plan.io/issues/1234)
        -   `pulpcore.content.handler.Handler.list_directory`

        ---
        """,
    ),
    _TestCase(
        id="pulpcore-sample",
        input="""\
        =========
        Changelog
        =========

        ..
            You should *NOT* be adding new change log entries to this file, this
            file is managed by towncrier. You *may* edit previous change logs to
            fix problems like typo corrections or such.
            To add a new change log entry, please see
            https://docs.pulpproject.org/contributing/git.html#changelog-update

            WARNING: Don't drop the towncrier directive!

        .. towncrier release notes start

        3.53.0 (2024-04-30)
        ===================
        REST API
        --------

        Features
        ~~~~~~~~

        - Added integration with Sentry/GlitchTip.
          :github:`5285`


        Bugfixes
        ~~~~~~~~

        - Update jquery version from 3.5.1 to 3.7.1 in API.html template
          :github:`5306`


        Plugin API
        ----------

        No significant changes.


        Pulp File
        ---------

        No significant changes.


        Pulp Cert Guard
        ---------------

        No significant changes.


        ----


        3.52.0 (2024-04-23)
        ===================
        REST API
        --------
        """,
        expected="""\
        # Changelog
        
        [//]: # (You should *NOT* be adding new change log entries to this file, this)
        [//]: # (file is managed by towncrier. You *may* edit previous change logs to)
        [//]: # (fix problems like typo corrections or such.)
        [//]: # (To add a new change log entry, please see)
        [//]: # (https://docs.pulpproject.org/contributing/git.html#changelog-update)
        [//]: # (WARNING: Don't drop the towncrier directive!)

        [//]: # (towncrier release notes start)

        ## 3.53.0 (2024-04-30) {: #3.53.0 }

        ### REST API

        #### Features

        -   Added integration with Sentry/GlitchTip.
            [#5285](https://github.com/pulp/pulp_rpm/issues/5285)

        #### Bugfixes

        -   Update jquery version from 3.5.1 to 3.7.1 in API.html template
            [#5306](https://github.com/pulp/pulp_rpm/issues/5306)

        ### Plugin API

        No significant changes.

        ### Pulp File

        No significant changes.

        ### Pulp Cert Guard

        No significant changes.

        ---

        ## 3.52.0 (2024-04-23) {: #3.52.0 }

        ### REST API
        """,
    ),
]

pytest_cases = [pytest.param(tc.input, tc.expected, id=tc.id) for tc in test_cases]


@pytest.fixture(autouse=True)
def tempcwd(tmp_path):
    os.chdir(tmp_path)
    yield


@pytest.mark.parametrize("rst_data,expected_md", pytest_cases)
def tests_convert_changelog(tmp_path, rst_data, expected_md):
    changes_rst = Path(tmp_path / "CHANGES.rst")
    changes_rst.write_text(rst_data)
    changes_md = convert_changelog(changes_rst, "pulp_rpm")
    assert changes_md.read_text() == expected_md
