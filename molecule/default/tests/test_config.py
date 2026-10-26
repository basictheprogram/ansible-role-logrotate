"""Config-file tests for the ansible-role-logrotate Molecule scenario.

prepare.yml gives every instance /etc/logrotate.d/wtmp and btmp, so the role
must leave those two logs to their drop-ins. converge.yml sets global options
and the mysql-backup application.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ._data import CONFIG_FILES, LOGROTATE_BIN, LOGROTATE_CONF

if TYPE_CHECKING:
    from testinfra.host import Host


@pytest.mark.parametrize("path", CONFIG_FILES)
def test_config_file_exists(host: Host, path: str) -> None:
    assert host.file(path).is_file


@pytest.mark.parametrize("path", CONFIG_FILES)
def test_config_file_is_owned_by_root(host: Host, path: str) -> None:
    assert host.file(path).user == "root"


@pytest.mark.parametrize("path", CONFIG_FILES)
def test_config_file_mode(host: Host, path: str) -> None:
    assert host.file(path).mode == 0o644


def test_conf_includes_the_drop_in_directory(host: Host) -> None:
    assert "include /etc/logrotate.d" in host.file(LOGROTATE_CONF).content_string.splitlines()


def test_conf_has_the_global_options_from_converge(host: Host) -> None:
    assert "rotate 32" in host.file(LOGROTATE_CONF).content_string.splitlines()


def test_conf_does_not_redefine_wtmp(host: Host) -> None:
    assert "/var/log/wtmp" not in host.file(LOGROTATE_CONF).content_string


def test_conf_does_not_redefine_btmp(host: Host) -> None:
    assert "/var/log/btmp" not in host.file(LOGROTATE_CONF).content_string


def test_wtmp_is_defined_in_exactly_one_file(host: Host) -> None:
    result = host.run("grep -l '^/var/log/wtmp' %s /etc/logrotate.d/*", LOGROTATE_CONF)
    assert len(result.stdout.splitlines()) == 1


def test_btmp_is_defined_in_exactly_one_file(host: Host) -> None:
    result = host.run("grep -l '^/var/log/btmp' %s /etc/logrotate.d/*", LOGROTATE_CONF)
    assert len(result.stdout.splitlines()) == 1


def test_mysql_backup_drop_in_defines_its_log(host: Host) -> None:
    assert "/var/backup/mysql/*.log {" in host.file("/etc/logrotate.d/mysql-backup").content_string


def test_logrotate_accepts_the_configuration(host: Host) -> None:
    assert host.run("%s --debug %s", LOGROTATE_BIN, LOGROTATE_CONF).rc == 0
