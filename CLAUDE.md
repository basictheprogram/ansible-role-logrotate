# Claude Code project notes — ansible-role-logrotate

Fork of [arillso/ansible.logrotate](https://github.com/arillso/ansible.logrotate)
by arillso. This fork lives at
https://github.com/basictheprogram/ansible-role-logrotate. Bugs and pull
requests go to the fork repo, not upstream (upstream was archived
read-only on 2025-11-19).

Ansible role to install and configure logrotate on Debian/Ubuntu,
Red Hat/Rocky/Alma, and SUSE/openSUSE. Fork of arillso/ansible.logrotate,
taken over 2026-05-21 following upstream archival. Consolidated from two
roles (`realtime.logrotate` + `realtime.logrotate_core`) into this single
role.

---

## Behavioral guidelines

These four rules govern how to work in this repo. They bias toward
caution over speed — for trivial one-liner changes, use judgment.

### 1. Think before writing tasks

**Don't assume. Surface tradeoffs. Ask when uncertain.**

Before adding or changing anything:

* State assumptions explicitly. If a variable could live in `defaults/`,
  `vars/`, or `host_vars`, say which and why before choosing.
* If multiple approaches exist (e.g. `ansible.builtin.command` vs a
  purpose-built module), present the tradeoff — don't pick silently.
  This role uses templates exclusively; `lineinfile` is explicitly not
  used for logrotate config.
* If the request is ambiguous (which task file? which template block?),
  name the ambiguity and ask. Don't guess and implement.
* If a simpler approach solves the problem, say so and push back.
* If something conflicts with `DESIGN.md`, flag it before proceeding.

### 2. Simplicity first

**Minimum tasks, variables, and template logic that solve the problem.**

* No new default variables beyond what the task being added requires.
* No Jinja2 abstraction for logic used in only one template.
* No `when:` conditions for scenarios that have no test coverage.
* No "future-proofing" of the public interface that wasn't asked for.
* If a template block is 30 lines and could be 10, rewrite it.

Ask: would a senior Ansible engineer call this overcomplicated? If yes,
simplify.

### 3. Surgical changes

**Touch only what the request requires. Clean up only your own mess.**

When editing existing tasks, templates, or defaults:

* Don't reformat adjacent YAML, fix unrelated comments, or clean up
  upstream code that wasn't broken by your change.
* Match the existing style — indentation, quoting, bullet character —
  even if you'd do it differently from scratch.
* If you notice unrelated dead code or stale variables, mention it;
  don't delete it without being asked.

When your change creates orphans:

* Remove `vars`, `when` conditions, or template blocks that YOUR change
  made unreachable.
* Don't remove pre-existing orphans unless explicitly asked.

Every changed line should trace directly to the request.

### 4. Goal-driven execution

**Define the success criteria before starting. Verify before declaring done.**

Transform requests into verifiable outcomes:

* "Add a new distro" → `meta/main.yml` updated, `vars/<Distro>.yml`
  exists, `molecule converge` passes, `pre-commit run --all-files` clean.
* "Add an application config variable" → rendered template matches
  expected logrotate.d syntax, `molecule verify` passes.
* "Add a preflight assertion" → `molecule converge` passes,
  `molecule verify` passes, `pre-commit run --all-files` is clean.
* "Fix an idempotency bug" → second `molecule converge` reports zero
  changed tasks.
* "Refactor a template" → rendered output is byte-for-byte identical
  to pre-refactor output on a converged instance.

For multi-step changes, state a brief plan before starting:

    1. Edit template → verify: rendered logrotate.conf is valid
    2. Add task       → verify: molecule converge green
    3. Add test       → verify: molecule verify green
    4. Lint           → verify: pre-commit run --all-files clean

Strong success criteria allow independent verification. Weak criteria
("make it work") require constant clarification.

---

## Role-specific notes

### Source of truth

`DESIGN.md` is the authoritative spec once one exists. This role has no
`DESIGN.md` yet (see Design notes). When it does, read it before any
non-trivial change; if code disagrees with it, `DESIGN.md` is right —
flag the discrepancy and ask before fixing the design to match the code.

### Design notes

No DESIGN.md found — add one. Until then the architecture below is the
reference.

#### Role architecture

The role is self-contained — no role dependencies.

    defaults/main.yml          User-facing variables (lowest precedence)
    vars/<Distribution>.yml    Distro-specific logrotate.conf defaults,
                               loaded by the include_vars task in
                               tasks/main.yml using lookup('first_found')
    tasks/main.yml             Orchestrates: preflight → include_vars → distro
                               install → find drop-ins owning wtmp/btmp →
                               deploy logrotate.conf → deploy logrotate.d
                               configs → verify → hourly symlink
    tasks/debian.yml           apt install (include_tasks, Debian/Ubuntu)
    tasks/redhat.yml           dnf install (include_tasks, RedHat family)
    tasks/suse.yml             zypper install (include_tasks, SUSE family)
    templates/etc/
      logrotate.conf.j2        Global /etc/logrotate.conf
      logrotate.d/
        application.j2         Per-app drop-in, rendered per entry in
                               logrotate_applications

#### Variable loading order

1. `defaults/main.yml` loaded automatically by Ansible (lowest precedence).
   Sets `logrotate_distribution_options: []` as fallback.
2. The `include_vars` task loads `vars/<Distribution>.yml` (e.g.
   `vars/Ubuntu.yml`) which sets `logrotate_distribution_options` to
   the distro canonical defaults.
3. Inventory/playbook variables override anything from steps 1–2.

Users configure global options via `logrotate_options` (overrides
`logrotate_distribution_options` entirely in the template) and
per-app configs via `logrotate_applications`.

#### Config management — templates only

All logrotate configuration is managed via Jinja2 templates.
`ansible.builtin.lineinfile` is explicitly not used. Do not introduce
lineinfile tasks; they produce non-idempotent, hard-to-audit config.

### Secrets

Role-specific secret variable names:

None found. No variable in `defaults/`, `vars/` or `tasks/` matches
`_key`, `_token`, `_password` or `_secret`, and the role uses no `no_log`.

### Commit scopes

Role-specific subsystem scopes: `debian`, `redhat`, `suse` (per-family
task files), `conf` (`templates/etc/logrotate.conf.j2`), `application`
(`templates/etc/logrotate.d/application.j2`)

### Settled decisions

* **Template-only config management.** No `lineinfile`. The Jinja2
  templates render a complete, auditable `/etc/logrotate.conf`.
* **Single role.** The two-role split (`realtime.logrotate` +
  `realtime.logrotate_core`) was collapsed into this role on
  2026-05-21. Do not re-introduce a dependency structure.
* **Per-distro vars in `vars/`, not `defaults/`.** Distro-canonical
  logrotate options live in `vars/<Distribution>.yml` and are loaded
  explicitly. User-facing variables belong in `defaults/main.yml`.
* **`lookup('first_found', …)` with `errors: ignore`.** Not
  `with_first_found` + `loop_control` (deprecated). Not a hard fail
  when no distro file is found — `logrotate_distribution_options`
  defaults to `[]`.
* **MIT license.** Original work by arillso. Modifications by
  Bob Tanner. Both credited in `LICENSE`.
* **No CI/CD in this repo yet.** Jenkins removed; GitLab CI is a
  future effort. Do not add CI config without being asked.

### Open questions

If a task touches one of these, leave a `# TODO(open-q):` comment:

<!-- TODO: fill in open questions -->

### Implementation order

Work one section at a time. Each item = one focused session and one
commit. Stop and verify between items.

1. `defaults/main.yml` — done. Public interface: `logrotate_packages`,
   `logrotate_options`, `logrotate_include_dir`, `logrotate_global_config`,
   `logrotate_use_hourly_rotation`, `logrotate_wtmp_*`, `logrotate_btmp_*`,
   `logrotate_applications`.
2. `vars/<Distribution>.yml` — done for CentOS, Debian, RedHat, Suse, Ubuntu.
3. `tasks/` — done: `main.yml`, `debian.yml`, `redhat.yml`, `suse.yml`.
4. `templates/` — done: `etc/logrotate.conf.j2`,
   `etc/logrotate.d/application.j2`.
5. `handlers/main.yml` — empty; the role defines no handlers.
6. `molecule/` — `default` (six platforms, drop-ins own wtmp/btmp) and
   `unowned` (ubuntu-noble, rockylinux-9) scenarios, testinfra verifier.
   Written 2026-10-25 but not yet run on the full matrix.
7. `tasks/preflight.yml` — done (runs first, wired from `tasks/main.yml`).
8. testinfra suite and `molecule/requirements.txt` — done.

### Consumer side notes

See the Example playbook section of `README.md`. Consumers set global
options with `logrotate_options` and per-application drop-ins with
`logrotate_applications`. SUSE support needs the `community.general`
collection from `requirements.yml`.

---

## Conventions

* **FQCN**: all module calls use fully-qualified collection names
  (`ansible.builtin.template`, `ansible.builtin.apt`,
  `ansible.builtin.dnf`, `community.general.zypper`). The
  `.ansible-lint` config enforces this via `fqcn-builtins`.
* **`ansible_facts` dict syntax**: always `ansible_facts['key']`,
  never bare `ansible_distribution` or `ansible_os_family`.
* **`become: true`**: set explicitly on every privileged task, never
  at play level.
* **Package install pattern**: all install tasks use `register` +
  `until: … is succeeded` + `retries: 3`.
* **Lint**: `.ansible-lint`, `.yamllint`, `.pre-commit-config.yaml`
  define the rules. Run `pre-commit run --all-files` before declaring
  work done.
* **Secrets**: this role manages no secrets or credentials.
* **Idempotency**: every task must be safe to re-run. The template
  tasks are inherently idempotent; the install tasks use `until/retries`
  which is also safe.

## Supported platforms (as of 2026-05-21)

| Platform | Versions |
|----------|----------|
| Ubuntu   | jammy (22.04), noble (24.04), resolute (26.04) |
| Debian   | trixie (13) |
| EL       | 9 (Rocky, Alma, RHEL) |
| SUSE     | current (openSUSE Leap / SUSE Linux Enterprise) |

Minimum ansible-core: **2.20**

When adding a new platform:
1. Add the distro to `meta/main.yml` platforms.
2. Create `vars/<Distribution>.yml` with `logrotate_distribution_options`.
3. Add or update the appropriate `tasks/<family>.yml` if the package
   manager differs.
4. Update `README.md` platform table.
5. Add a molecule platform to `molecule/default/molecule.yml`.

## Testing locally

* `pre-commit run --all-files` — fast lint/format pass. Run before
  every commit.
* `molecule converge` then `molecule verify` — fast iteration during
  template/task work; skips the destroy/create cycle.
* `molecule test` — full role exercise. Run before declaring a change
  done.

### Molecule verifier

The verifier is **pytest-testinfra** (`molecule/<scenario>/tests/`), pinned
in `molecule/requirements.txt`. Each scenario has its own `pytest.ini`
(see its comments: it turns off the `pytest_molecule` and `pytest-ansible`
plugins that break under Python 3.14 and clash with testinfra).

* `default` runs on ubuntu-jammy, ubuntu-noble, ubuntu-resolute,
  debian-trixie, rockylinux-9 and opensuse-leap15. `prepare.yml` installs
  logrotate and seeds `/etc/logrotate.d/wtmp` and `btmp` when the package
  does not ship them, so the role always meets drop-ins that own both logs.
  Tests: `test_packages.py` (logrotate installed) and `test_config.py`
  (`/etc/logrotate.conf` and the `mysql-backup` drop-in exist, are root
  owned, mode `0644`; `logrotate.conf` does not redefine wtmp or btmp; each
  is defined in exactly one file; `logrotate --debug` exits zero).
* `unowned` (`molecule test -s unowned`) runs on ubuntu-noble and
  rockylinux-9. `prepare.yml` removes the wtmp and btmp drop-ins, and the
  tests assert `logrotate.conf` defines both itself and that no drop-in does.

When adding a new feature, add single-purpose test functions to
`tests/test_config.py` (or a new `test_<subsystem>.py`): one concern per
test, no compound assertions, `host.file` / `host.run` for state.

---

## When in doubt

Read this file (and `DESIGN.md` once it exists), then ask. The settled
decisions above are load-bearing.

---

## Commit message guide

You are an expert DevOps engineer and professional git commit message
writer. When generating a commit message, follow these steps exactly.

### Step 1 — Retrieve changes

Run:

    git diff --cached

Analyze the full staged diff. This is the **single source of truth**
for what will be committed.

### Step 2 — Understand the change

Determine:

* The **primary purpose** of the change
* The **type of change** (feature, bug fix, refactor, etc.)
* The **most relevant scope** within the role
* Whether the change introduces a **breaking change** for role consumers
* Whether multiple changes should be summarized together

Pay special attention to:

* Changes to `defaults/main.yml` — these define the role's public interface
* Changes to handler names, task names, and tags — consumers may pin to them
* Changes to template variables that consumers override
* Changes to config or env file templates that affect service behavior
* Changes to `meta/main.yml` — galaxy metadata, min Ansible version, platforms

If multiple files are modified, identify the **dominant intent** rather
than listing every file.

### Step 3 — Select commit type

Use Conventional Commits:

* `feat` — new task, handler, variable, template, or capability
* `fix` — bug fix or idempotency correction
* `docs` — README, role metadata documentation, inline comments
* `style` — YAML formatting, whitespace, ansible-lint cleanup
* `refactor` — restructure tasks/templates without behavior change
* `perf` — performance improvement (e.g., reduced task runs, fewer handlers)
* `test` — molecule scenarios, lint config, CI tests
* `chore` — galaxy metadata, dependencies, tooling
* `ci` — GitHub Actions, GitLab CI, pre-commit hooks

### Step 4 — Determine scope

Infer a scope from the role layout or the subsystem being changed.

Common Ansible role scopes: `tasks`, `handlers`, `templates`,
`defaults`, `vars`, `meta`, `molecule`, `docker`.

Role-specific subsystem scopes: `debian`, `redhat`, `suse` (per-family
task files), `conf` (`templates/etc/logrotate.conf.j2`), `application`
(`templates/etc/logrotate.d/application.j2`)

Only include a scope when it adds clarity. Prefer a subsystem scope
for feature-driven changes (e.g., `feat(tls): ...`) and a role-layout
scope for structural changes (e.g., `refactor(tasks): ...`).

### Step 5 — Write the commit message

Format exactly as:

    <type>[optional scope]: <short summary (<=50 chars)>

    <body wrapped at 72 characters>

    [optional footer(s)]

**Subject line rules:**

* Use **imperative mood** ("Add", "Fix", "Update", "Remove")
* Maximum **50 characters**
* Describe the **result**, not the implementation
* Prefer role-specific or Ansible terminology over generic phrasing

**Body rules** (required):

Explain **why the change was made**, focusing on:

* What deployment scenario or upstream behavior motivated it
* What downstream role consumers need to know to upgrade safely
* Any Ansible version constraints involved

When helpful, summarize key changes using bullet points.

**Bullet rules:**

* Use `*` (asterisk) for all bullets — never `-` or `•`
* Nested bullets indented with two spaces
* No Markdown formatting of any kind

**Ansible role expectations:**

* Call out new, renamed, or removed default variables
* Note when handler names, tag names, or public task names change
* Mention idempotency improvements when relevant
* Reference supported platforms when adding OS-specific tasks
* Flag changes to `meta/main.yml` (min Ansible version, platforms)
* Note molecule scenario additions or removals

**logrotate-specific expectations:**

* Distinguish between global config (`/etc/logrotate.conf`) changes
  and per-application drop-in (`/etc/logrotate.d/`) changes
* Note when `logrotate_applications` schema gains or loses keys —
  consumers build data structures against it
* Call out changes to `logrotate_distribution_options` per distro
* Note when the template rendering changes in a way that alters
  logrotate behavior (rotation frequency, compression, retention)

### Breaking changes

A change is breaking when it:

* Renames or removes a default variable
* Renames or removes a handler, tag, or public task name
* Changes a default value in a way that alters runtime behavior
* Drops support for an Ansible version or OS platform
* Restructures generated configuration in a way consumers' overrides
  cannot accommodate

If the diff introduces a breaking change:

* Add `!` after the type/scope in the subject
* Include a footer: `BREAKING CHANGE: <description>`

Examples:

    feat(tasks): add preflight variable assertion block
    fix(handlers): correct service restart trigger condition
    refactor(tasks): split install and configure into files
    chore(meta): bump minimum Ansible version to 2.20
    test(molecule): add scenario for Ubuntu 24.04

    feat(defaults)!: rename primary configuration variable

    BREAKING CHANGE: old_variable_name is now new_variable_name;
    update playbook vars before upgrading.

### Step 6 — Output rules

Return **only the commit message**. Do NOT include:

* explanations or analysis
* the diff
* markdown formatting
* code fences

The output must be a clean commit message ready for `git commit`.
It will be pasted directly into a git commit editor — optimize for
copy/paste fidelity over styling.
