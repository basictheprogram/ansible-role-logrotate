"""Config tests for the unowned scenario.

prepare.yml removes /etc/logrotate.d/wtmp and btmp, so no drop-in owns those
logs and the role must define them in logrotate.conf itself.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._data import LOGROTATE_BIN, LOGROTATE_CONF

if TYPE_CHECKING:
    from testinfra.host import Host


def test_conf_defines_wtmp(host: Host) -> None:
    assert "/var/log/wtmp {" in host.file(LOGROTATE_CONF).content_string


def test_conf_defines_btmp(host: Host) -> None:
    assert "/var/log/btmp {" in host.file(LOGROTATE_CONF).content_string


def test_no_drop_in_defines_wtmp(host: Host) -> None:
    assert host.run("grep -rl '^/var/log/wtmp' /etc/logrotate.d").rc != 0


def test_logrotate_accepts_the_configuration(host: Host) -> None:
    assert host.run("%s --debug %s", LOGROTATE_BIN, LOGROTATE_CONF).rc == 0
