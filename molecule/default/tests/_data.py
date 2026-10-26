"""Shared test constants for the ansible-role-logrotate Molecule scenario."""

from __future__ import annotations

# One package, named the same on every OS family the role supports.
PACKAGES: list[str] = ["logrotate"]

# Config files the role renders: the global config and the mysql-backup
# drop-in that converge.yml defines through logrotate_applications.
CONFIG_FILES: list[str] = [
    "/etc/logrotate.conf",
    "/etc/logrotate.d/mysql-backup",
]

LOGROTATE_CONF = "/etc/logrotate.conf"
LOGROTATE_BIN = "/usr/sbin/logrotate"
