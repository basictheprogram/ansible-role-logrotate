"""Package installation tests for the ansible-role-logrotate Molecule scenario."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ._data import PACKAGES

if TYPE_CHECKING:
    from testinfra.host import Host


@pytest.mark.parametrize("package_name", PACKAGES)
def test_package_installed(host: Host, package_name: str) -> None:
    assert host.package(package_name).is_installed
