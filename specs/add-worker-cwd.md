# Custom Working Directory Flags for cape CLI & worker

## What and Why

### Intent (one-liner)

- Enable operators to run `cape-worker` and `cape run` from the workspace root (or any folder) while the processes themselves and their child workflows use the appropriate directories.

### Value (why)

- Simplifies local and service setups by removing ad-hoc wrapper scripts just to change working directories.
- Reduces operator confusion between `CAPE_APP_ROOT` (used for `cape-adw`) and each command’s own working directory.

### Signals of success

- Worker CLI exposes a `--working-dir` flag documented in `cape/app/README.md`.
- `uv run cape run … --working-dir C:\Users\bpong\git\cape` (or equivalent option) launches successfully, logs/echoes the directory switch, and still executes workflows correctly.
- Running `uv run cape-worker --working-dir C:\Users\bpong\git\cape` launches successfully, logs the directory switch, and still invokes `cape-adw` from `cape/app`.

---
# Custom Working Directory Flags for cape CLI & worker

## How: Implementation Plan

### Constraints & principles

- Keep changes localized to the worker CLI/config; maintain the existing `CAPE_APP_ROOT` behavior for spawning `cape-adw`.
- Follow AGENTS.md guidance: minimal, clear modifications with documentation updates and no premature optimization.

### Unknowns & assumptions

- Assumption: Both CLI flags should accept absolute paths only (e.g., `C:\Users\bpong\git\cape`), and we’ll reject relative paths.
- Assumption: `CAPE_APP_ROOT` remains independent—`CAPE_APP_ROOT` tells the worker where to run `cape-adw`, while each command’s `--working-dir` sets that process’s own `cwd`.

### Approach sketch

Introduce an optional `working_dir` field in `WorkerConfig` and a matching `--working-dir` CLI flag that accepts an absolute `Path`. Validate it’s absolute, resolve it, and call `os.chdir(working_dir)` before configuring logging and entering the main loop, logging the change for transparency. Mirror the same behavior in the main Typer CLI (`cape run` path) by adding a `--working-dir` option that changes directories before invoking workflow logic. Update `README.md` with instructions and examples showing how to use `--working-dir` alongside `CAPE_APP_ROOT`.

### Execution cadence

Generic phases: confirm requirements → implement CLI/config changes (worker + CLI) → document usage → validate with `uv run --directory cape/app cape run --working-dir …` and `uv run --directory cape/app cape-worker --working-dir …`.

### Logistics

- Task ID(s): TBD
- Owner(s): TBD
- Links: TBD
- Type/Scope: Feature; cape/app worker CLI + documentation

### Risks & mitigations (Optional)

- Misconfigured paths causing failures → validate the provided path early and emit clear errors before the worker starts.

### Notes & links (Optional)

- `CAPE_APP_ROOT` note in `cape/app/README.md` clarifies it controls `cape-adw` spawn location.
