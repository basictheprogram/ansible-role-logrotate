# Changelog

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
and [human-readable changelog](https://keepachangelog.com/en/1.0.0/).

---

## Unreleased (realtime fork — Bob Tanner)

### Fixed

- `logrotate.conf` no longer defines the wtmp and btmp blocks when a drop-in
  in `logrotate_include_dir` already does. Newer Debian/Ubuntu ship
  `/etc/logrotate.d/wtmp` and `btmp`, and the duplicate made logrotate exit 1
  with `duplicate log entry` on every nightly run.
- `logrotate.conf` and the per-application drop-ins are validated with
  `logrotate --debug` before they are written, and the final configuration is
  verified after the role runs (skipped in check mode).
- Molecule: `cgroupns_mode: host` and a read-write cgroup mount so the
  systemd test image starts on Docker Desktop. Added the `unowned` scenario
  and a seeded-drop-in case in `default`.

### Changed — Fork Takeover (2026-05-21)

Upstream repository `arillso/ansible.logrotate` was archived read-only on
2026-11-19. This fork was taken over and is now the maintained version under
the `realtime` namespace.

- Consolidated `realtime.logrotate` and `realtime.logrotate_core` into a
  single unified role. The two-role split only existed to track the upstream
  community release cycle; with upstream abandoned the abstraction adds
  complexity with no benefit.
- Replaced all bare module names with fully-qualified collection names (FQCN)
  throughout (`ansible.builtin.*`, `community.general.zypper`).
- Replaced `ansible_distribution`, `ansible_os_family`, `ansible_lsb` bare
  variable references with `ansible_facts['*']` dict syntax required by
  ansible-core 2.13+ and enforced in 2.20+.
- Replaced deprecated `with_first_found` + `loop_control` loop pattern with
  `lookup('first_found', ...)` in `include_vars` task.
- Removed `import_tasks`/`include_tasks` in favour of explicit `when:` guards
  on `ansible.builtin.include_tasks`.
- Replaced all `lineinfile` config management tasks with the Jinja2 template
  approach (`templates/etc/logrotate.conf.j2`). Config is now fully idempotent
  and auditable.
- Removed all Ubuntu < 14.04 compatibility code (`ansible_lsb.release`
  comparisons). Ubuntu 14.04 reached end-of-life in April 2019.
- Added `until: … is succeeded` / `retries: 3` to all package install tasks.
- Added `become: true` explicitly on all privileged tasks.
- Updated `meta/main.yml`: namespace → `realtime`, author → Bob Tanner,
  `min_ansible_version` → `"2.20"`, platform list trimmed to active releases
  only: Ubuntu jammy/noble/resolute, Debian bookworm/trixie, EL 8/9.
- Dropped EoL platforms: Ubuntu bionic (EoL Apr 2023), focal (EoL Apr 2025),
  Debian buster (EoL Jun 2024), bullseye (EoL Jun 2026).
- Added `requirements.yml` declaring `community.general` collection (needed
  for `community.general.zypper` on SUSE).
- Added `vars/Suse.yml` with distribution defaults for SUSE/openSUSE.
- Updated Molecule default scenario: Ubuntu 24.04 (noble) image, correct role
  name, FQCN modules throughout converge/prepare/verify.
- Updated `.pre-commit-config.yaml` to ansible-lint v26.4.0, ruff v0.15.10.
- Removed `.travis.yml` (CI abandoned upstream).
- Removed `Jenkinsfile` — CI/CD will move to GitLab.
- Removed `defaults/Debian.yml` and `defaults/Suse.yml` — orphaned files not
  loaded by any task; package name is uniform across distros and lives in
  `defaults/main.yml`.
- Removed `meta/.galaxy_install_info` (upstream Galaxy artifact).

---

## arillso/ansible.logrotate history (upstream, archived 2025-11-19)

> The following entries represent the changelog of the upstream role prior to
> this fork taking over maintenance.

## 1.6.1

### Fixed

- Fix typos (imclude -> include)
- Fix role name

### Changed

- Extended example

## 1.6.0

### Fixed

- Travis CI and molecule setup.
- The src option requires state to be 'link' or 'hard' (breaking in Ansible
  2.10) (Fixes: #14).

### Changed

- `logrotate_use_hourly_rotation` will no longer clean the symlink in
  `cron.daily`.
- Bumped tested distros versions.

### Added

- Options to enable or not wtmp/btmp config by [smutel](https://github.com/smutel)
  via PR #25 (Fixes: #23).
- Option to skip global configuration file by [fhsctv](https://github.com/fhsctv)
  via PR #28.

## 1.5.2

### Fixed

- Fix custom definition of logrotate_options via inventory

## 1.5.1

### Fixed

- Incorrect documentation adapted.

## 1.5.0

### Changed

- Updated min ansible version to 2.8
- Changelog has been moved to its own file
- Travis file has been updated
- Documentation has been improved

### Added

- molecule testing
- hourly rotation option

## 1.4.1

### Added

- add Red Hat Support

## 1.4.0

### Changed

- update loop_vars

### Added

- add defaults vars

## 1.3.0

### Changed

- new role tests

## 1.2.0

### Changed

- rename role

## 1.1.0

### Added

- add become support

## 1.0.0

### Added

- initial Release
