# ansible-role-logrotate

Ansible role to install and configure [logrotate](https://github.com/logrotate/logrotate)
on Debian/Ubuntu, Red Hat/CentOS/Rocky/Alma, and SUSE/openSUSE systems.

## Fork notice

This role is a fork of [arillso/ansible.logrotate](https://github.com/arillso/ansible.logrotate),
originally authored by [arillso](https://github.com/arillso) and licensed under
the MIT License. The upstream repository was archived read-only on 2025-11-19.

Fork taken over on 2026-05-21 by Bob Tanner.

Changes from upstream: see [CHANGELOG.md](CHANGELOG.md).

## Requirements

- ansible-core >= 2.20
- `community.general` collection (for SUSE/openSUSE support — install via
  `ansible-galaxy collection install -r requirements.yml`)

## Supported platforms

| Platform | Versions |
|----------|----------|
| Ubuntu   | jammy (22.04), noble (24.04), resolute (26.04) |
| Debian   | trixie (13) |
| EL (Rocky/Alma/RHEL/CentOS) | 9 |
| SUSE / openSUSE Leap | current |

## Role variables

All variables have defaults and can be overridden in your inventory or playbook.

### Package

```yaml
# Package(s) to install. Override to add extras (e.g. cronie on EL).
logrotate_packages:
  - logrotate
```

### Global logrotate.conf

```yaml
# Whether to deploy and manage /etc/logrotate.conf via template.
logrotate_global_config: true

# Global options written into /etc/logrotate.conf.
# When empty, distribution-appropriate defaults are used (see vars/).
logrotate_options: []

# Directory where per-application drop-in configs are placed.
logrotate_include_dir: /etc/logrotate.d

# Create a symlink from cron.hourly to cron.daily for sub-daily rotation.
logrotate_use_hourly_rotation: false
```

### wtmp / btmp

```yaml
logrotate_wtmp_enable: true
logrotate_wtmp:
  logs:
    - /var/log/wtmp
  options:
    - missingok
    - monthly
    - create 0664 root utmp
    - rotate 1

logrotate_btmp_enable: true
logrotate_btmp:
  logs:
    - /var/log/btmp
  options:
    - missingok
    - monthly
    - create 0660 root utmp
    - rotate 1
```

Newer Debian and Ubuntu packages ship `/etc/logrotate.d/wtmp` and `btmp`.
logrotate exits 1 with `duplicate log entry` when a log is defined in
both `logrotate.conf` and a drop-in, so the role writes each block only
when the matching `*_enable` is true **and** no file in
`logrotate_include_dir` already defines that log. Every template is
checked with `logrotate --debug` before it is written, and the final
configuration is checked again after the role finishes, so a bad
config fails the play instead of the nightly `logrotate.service`.

### Per-application configs

```yaml
# List of application logrotate configs to deploy under /etc/logrotate.d/.
logrotate_applications: []
```

Each entry supports the following keys:

```yaml
logrotate_applications:
  - name: myapp                   # filename in /etc/logrotate.d/
    definitions:
      - logs:
          - /var/log/myapp/*.log
        options:
          - rotate 14
          - daily
          - missingok
          - notifempty
          - compress
          - delaycompress
          - sharedscripts
        postrotate:
          - systemctl reload myapp || true
        preremove: []
        lastaction: []
        firstaction: []
```

Multiple `definitions` blocks are supported per application entry, which allows
a single drop-in file to cover several log path patterns with different options.

### OS overrides (`vars/`)

These are loaded by `include_vars` from `vars/<Distribution>.yml` and are not
meant to be overridden directly; set `logrotate_options` instead, which
replaces them entirely.

| File | `logrotate_distribution_options` |
|------|----------------------------------|
| `Debian.yml`, `RedHat.yml`, `CentOS.yml`, `Suse.yml` | `weekly`, `rotate 4`, `create`, `dateext` |
| `Ubuntu.yml` | the above plus `su root syslog` |

## Task flow

1. **Preflight** (`tasks/preflight.yml`, first task, tag `always`): asserts
   ansible-core >= 2.20, an OS family of Debian, RedHat or Suse,
   `logrotate_options` and `logrotate_applications` are lists,
   `logrotate_include_dir` is an absolute path, `logrotate_wtmp` and
   `logrotate_btmp` define `logs` and `options`, and every
   `logrotate_applications` entry has a `name` and `definitions` that each
   carry `logs` and `options`.
2. Load `vars/<Distribution>.yml` (`logrotate_distribution_options`).
3. Install the package (`debian.yml`, `redhat.yml` or `suse.yml`).
4. Find drop-ins in `logrotate_include_dir` that already rotate wtmp or btmp.
5. Write `/etc/logrotate.conf`, validated with `logrotate --debug`.
6. Write the per-application drop-ins, each validated the same way.
7. Run `logrotate --debug /etc/logrotate.conf` on the result (skipped in
   check mode).
8. Optionally link `/etc/cron.hourly/logrotate` to `/etc/cron.daily/logrotate`.

## Example playbook

```yaml
- hosts: all
  become: true

  vars:
    logrotate_options:
      - weekly
      - su root adm
      - rotate 4
      - create
      - dateext
      - compress

    logrotate_applications:
      - name: nginx
        definitions:
          - logs:
              - /var/log/nginx/*.log
            options:
              - rotate 52
              - weekly
              - missingok
              - notifempty
              - compress
              - delaycompress
              - sharedscripts
            postrotate:
              - invoke-rc.d nginx rotate >/dev/null 2>&1 || true

  roles:
    - role: realtime.logrotate
```

## License

MIT — see [LICENSE](LICENSE).

Original work by [arillso](https://github.com/arillso).
Modifications and ongoing maintenance by Bob Tanner.

## Author information

- Bob Tanner
