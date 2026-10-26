# Claude Code project notes — ansible-role-logrotate

This is an Ansible role that installs and configures logrotate on
Debian/Ubuntu, Red Hat/Rocky/Alma, and SUSE/openSUSE systems.

Forked from arillso/ansible.logrotate
(https://github.com/arillso/ansible.logrotate), which was archived
read-only on 2025-11-19. Fork taken over on 2026-05-21 by Bob Tanner,
Consolidated from two roles
(`realtime.logrotate` + `realtime.logrotate_core`) into this single
role.

---

## Behavioral guidelines

These four rules govern how to work in this repo. They bias toward
caution over speed — for trivial one-liner changes, use judgment.

### 1. Think before writing tasks

**Don't assume. Surface tradeoffs. Ask when uncertain.**

Before adding or changing anything:

* State assumptions explicitly. If a variable could live in `defaults/`,
  `vars/`, or a per-distro file, say which and why before choosing.
* If multiple approaches exist (e.g. `ansible.builtin.lineinfile` vs
  the Jinja2 template approach), present the tradeoff — don't pick
  silently. This role uses templates exclusively; lineinfile is
  explicitly not used for logrotate config.
* If the request is ambiguous (which task file? which template block?),
  name the ambiguity and ask. Don't guess and implement.
* If a simpler approach solves the problem, say so and push back.

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
* "Fix an idempotency bug" → second `molecule converge` reports zero
  changed tasks.
* "Refactor a template" → rendered output is byte-for-byte identical
  to pre-refactor output on a converged instance.

For multi-step changes, state a brief plan before starting:

    1. Edit template  → verify: rendered logrotate.conf is valid
    2. Add task       → verify: molecule converge green
    3. Add test       → verify: molecule verify green
    4. Lint           → verify: pre-commit run --all-files clean

---

## Role architecture

The role is self-contained — no role dependencies.

    defaults/main.yml          User-facing variables (lowest precedence)
    vars/<Distribution>.yml    Distro-specific logrotate.conf defaults,
                               loaded by the include_vars task in
                               tasks/main.yml using lookup('first_found')
    tasks/main.yml             Orchestrates: include_vars → distro
                               install → deploy logrotate.conf →
                               deploy logrotate.d configs → hourly symlink
    tasks/debian.yml           apt install (include_tasks, Debian/Ubuntu)
    tasks/redhat.yml           dnf install (include_tasks, RedHat family)
    tasks/suse.yml             zypper install (include_tasks, SUSE family)
    templates/etc/
      logrotate.conf.j2        Global /etc/logrotate.conf
      logrotate.d/
        application.j2         Per-app drop-in, rendered per entry in
                               logrotate_applications

### Variable loading order

1. `defaults/main.yml` loaded automatically by Ansible (lowest precedence).
   Sets `logrotate_distribution_options: []` as fallback.
2. The `include_vars` task loads `vars/<Distribution>.yml` (e.g.
   `vars/Ubuntu.yml`) which sets `logrotate_distribution_options` to
   the distro canonical defaults.
3. Inventory/playbook variables override anything from steps 1–2.

Users configure global options via `logrotate_options` (overrides
`logrotate_distribution_options` entirely in the template) and
per-app configs via `logrotate_applications`.

### Config management — templates only

All logrotate configuration is managed via Jinja2 templates.
`ansible.builtin.lineinfile` is explicitly not used. Do not introduce
lineinfile tasks; they produce non-idempotent, hard-to-audit config.

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
| Debian   | bookworm (12), trixie (13) |
| EL       | 8, 9 (Rocky, Alma, RHEL) |
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

The verifier is the **Ansible verifier** (`molecule/default/verify.yml`).
Tests are written as Ansible tasks using `ansible.builtin.assert` and
`ansible.builtin.stat`. The verify playbook currently checks:

* `logrotate` package is installed (via `package_facts`)
* `/etc/logrotate.conf` exists, is owned by root, mode `0644`
* `logrotate --debug /etc/logrotate.conf` exits zero

When adding a new feature, extend `verify.yml` with assertions that
confirm the feature rendered correctly. Use `ansible.builtin.command`
to inspect rendered files, `ansible.builtin.stat` for filesystem state,
and `ansible.builtin.assert` for all conditions.

---

## Settled decisions — don't re-litigate

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
* Changes to `logrotate_applications` schema — consumers build data
  structures against it
* Changes to handler names, task names, and tags — consumers may pin
  to them
* Changes to template output — rendered logrotate.conf or logrotate.d
  files must remain valid logrotate syntax

If multiple files are modified, identify the **dominant intent** rather
than listing every file.

### Step 3 — Select commit type

Use Conventional Commits:

* `feat` — new task, variable, template capability, or distro support
* `fix` — bug fix or idempotency correction
* `docs` — README, role metadata, inline comments
* `style` — YAML formatting, whitespace, ansible-lint cleanup
* `refactor` — restructure tasks/templates without behavior change
* `perf` — performance improvement (e.g., reduced task runs)
* `test` — molecule scenarios, verify playbook, lint config
* `chore` — galaxy metadata, dependencies, tooling
* `ci` — GitLab CI, pre-commit hooks

### Step 4 — Determine scope

Infer a scope from the role layout.

Common scopes: `tasks`, `handlers`, `templates`, `defaults`, `vars`,
`meta`, `molecule`, `debian`, `redhat`, `suse`.

Only include a scope when it adds clarity. Prefer the functional scope
for feature-driven changes (e.g., `feat(templates): ...`) and the
structural scope for housekeeping (e.g., `chore(meta): ...`).

### Step 5 — Write the commit message

Format exactly as:

    <type>[optional scope]: <short summary (<=50 chars)>

    <body wrapped at 72 characters>

    [optional footer(s)]

**Subject line rules:**

* Use **imperative mood** ("Add", "Fix", "Update", "Remove")
* Maximum **50 characters**
* Describe the **result**, not the implementation

**Body rules** (required for non-trivial changes):

Explain **why the change was made**, focusing on:

* What deployment scenario or upstream behavior motivated it
* What downstream role consumers need to know to upgrade safely
* Any ansible-core or platform version constraints involved

When helpful, summarize key changes using bullet points.

**Bullet rules:**

* Use `*` (asterisk) for all bullets — never `-` or `•`
* Nested bullets indented with two spaces
* No Markdown formatting of any kind

Example:

    * Add vars/Ubuntu.yml with distribution defaults
    * Wire into include_vars lookup in tasks/main.yml

**Ansible-specific expectations:**

* Call out new, renamed, or removed default variables
* Note when handler names, tag names, or public task names change
* Mention idempotency improvements when relevant
* Reference supported platforms when adding distro-specific tasks
* Flag changes to `meta/main.yml` (galaxy metadata, min Ansible
  version, supported platforms)
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
* Changes a default value in a way that alters rotation behavior
* Changes the `logrotate_applications` item schema
* Drops support for an Ansible version or platform
* Renames or removes a tag or task name consumers pin to

If the diff introduces a breaking change:

* Add `!` after the type/scope in the subject
* Include a footer: `BREAKING CHANGE: <description>`

Examples:

    feat(debian): add Ubuntu resolute (26.04) support
    fix(templates): correct wtmp block when btmp disabled
    refactor(tasks): split install and configure steps
    chore(meta): drop EoL platforms bionic and focal
    test(molecule): add assertions for logrotate.d output

    feat(defaults)!: rename logrotate_conf to logrotate_global_config

    BREAKING CHANGE: logrotate_conf is now logrotate_global_config;
    update playbook vars before upgrading.

### Step 6 — Output rules

Return **only the commit message** — no explanation, no analysis,
no diff, no markdown formatting, no code fences. The output will be
pasted directly into a git commit editor.
