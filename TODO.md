# TODO — ansible-role-logrotate

Items flagged during the 2026-10-25 `ansible-sync-role` run that were not
resolved in that session.

- [ ] **Run the rest of the molecule matrix.** On 2026-10-25 `default` and
  `unowned` were run and passed (15 and 8 testinfra tests, including
  idempotence) on ubuntu-noble and rockylinux-9 only, to save Docker disk.
  Not yet run: ubuntu-jammy, ubuntu-resolute, debian-trixie and
  opensuse-leap15 in `default`. opensuse-leap15 is the one most worth
  running, since the zypper install task and the `su root root` fixture have
  never run under molecule. Pull the images on the macOS terminal (the
  devcontainer's credential store breaks `docker pull`), then
  `make molecule ROLE=roles/git_repository/ansible-role-logrotate CMD="test --platform-name opensuse-leap15"`.
- [ ] **No automated negative test for preflight.** Both scenarios only prove
  preflight passes on valid input. The failure messages were checked by hand
  (bad `logrotate_applications` shapes, empty `logrotate_wtmp.logs`, relative
  `logrotate_include_dir`), not in molecule.
- [ ] **Debian bookworm and EL 8 are dropped from the support statement**
  (`meta/main.yml`, README, CLAUDE.md, molecule). Nothing in the role blocks
  them, but check the inventory for hosts still running either before they
  next run this role.
- [ ] **Skill/repo conflict on the company name.** `ansible-sync-role` Steps 5
  and 5b say to set `company: Real Time Enterprises, Inc.` in `meta/main.yml`
  and to add that name to the LICENSE copyright line. Commit `d688e54` removed
  the company name from this role on purpose, so both were skipped at your
  direction. Update the skill, or the next sync will ask again.
- [ ] **No `DESIGN.md`.** `CLAUDE.md` says "No DESIGN.md found — add one", and
  its Open questions section is a TODO comment. The settled decisions carried
  over from the previous CLAUDE.md; nothing new was invented.
- [ ] **No `meta/argument_specs.yml`.** Step 4 only asks to fix one that holds
  placeholder content, and none exists. Adding a real one (every key in
  `defaults/main.yml`) would give consumers argument validation.
- [ ] **`.gitignore` is now the template's 9 lines** (sorted by the pre-commit
  hook). `.DS_Store`, `.idea/`, `.vscode/`, `.pytest_cache/` and `*.retry` are
  no longer ignored by the role itself.
