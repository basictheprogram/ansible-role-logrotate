# TODO — ansible-role-logrotate

Items flagged during the 2026-10-25 `ansible-sync-role` run and since, that
were not resolved.

- [ ] **Molecule has not run since the EL/SUSE removal.** The trimmed role
  passed lint, `molecule syntax` and a preflight check, but `molecule test`
  was not run locally (the images were cleaned out of Docker and not
  re-pulled). The next push to `ansible-core-2.20` runs all five jobs in CI
  (default on ubuntu-jammy, noble, resolute, debian-trixie; unowned on
  ubuntu-noble); confirm they pass.
- [ ] **No automated negative test for preflight.** Both scenarios only prove
  preflight passes on valid input. The failure messages were checked by hand
  (bad `logrotate_applications` shapes, empty `logrotate_wtmp.logs`, relative
  `logrotate_include_dir`), not in molecule.
- [ ] **Debian bookworm, the Red Hat family and SUSE are unsupported.**
  Bookworm was dropped from the support statement, and EL and SUSE support
  was removed outright (task and vars files deleted, preflight fails on any
  non-Debian OS family). Check the inventory for hosts still running any of
  them before they next run this role.
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
