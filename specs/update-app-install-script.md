# Plan: Update `install-app.py` for `cape-cli` and `.env` Preservation

Switch installs to `cape-cli/` and change overwrite behavior so an existing install warns before proceeding and preserves a single top-level `.env` file (not variants like `.env.local`).

## Steps

1. **Update install directory naming in `install-app.py`**  
   - Change `INSTALL_DIR_NAME` from `"cape"` to `"cape-cli"` so `target_path = base_target / INSTALL_DIR_NAME` becomes `target_dir/cape-cli`.  
   - Update the module docstring to say it copies into a `cape-cli/` subdirectory instead of `cape/`.

2. **Add clear overwrite warning when target exists**  
   - In `remove_existing_target(target_path: Path, force: bool)`, keep the early return when `target_path` does not exist and the error when it exists but is not a directory.  
   - Before prompting (or proceeding with `force=True`), print a yellow warning that an existing `cape-cli` installation at `target_path` will be overwritten.  
   - Keep the current confirmation prompt for non-`force` runs and the "Copy cancelled by user." message on refusal.

3. **Refactor removal into helpers and introduce `.env` backup**  
   - Extract the current `shutil.rmtree(..., onerror=_on_rm_error)` logic from `remove_existing_target` into a private helper (e.g., `_remove_tree(path: Path) -> None`) defined at module level, along with its `onerror` callback, so recursive removal is reusable.  
   - Add a new helper (e.g., `backup_env_file(target_path: Path) -> Path | None`) that:  
     - Looks for `env_path = target_path / ".env"`.  
     - If it does not exist, returns `None` and does nothing.  
     - If it exists and is a regular file, moves it to a safe temp location (for example `target_path.parent / ".env.cape-backup"`) and returns that new path.  
     - If `.env` exists but is not a regular file (directory or symlink), prints a red error explaining the unexpected `.env` type and exits with `typer.Exit(code=1)` to avoid unsafe behavior.

4. **Implement `.env`-preserving overwrite flow**  
   - In `remove_existing_target`, after confirmation (or immediately when `force=True`):  
     - Call `backup_env_file(target_path)` and remember the returned backup path (if any).  
     - Use `_remove_tree(target_path)` to delete the existing install directory entirely.  
   - After this, the main flow proceeds as today: `copy_app(source_path, target_path)` recreates `target_path` using `shutil.copytree`.  
   - After `copy_app` returns successfully, restore `.env` if a backup exists by moving the backup file into `target_path / ".env"`. If restoring fails, print a clear red error indicating where the backup file lives and exit non-zero.

5. **Make messaging and behavior precise and consistent**  
   - Change the message in `remove_existing_target` from "Removing existing directory: {target_path}" to something like "Overwriting existing installation at {target_path} (preserving .env if present)".  
   - Do not treat `.env.local` or any `.env.*` file specially: they are deleted as part of the tree removal. Add a short comment near `backup_env_file` clarifying that only the exact top-level `.env` is preserved.  
   - Ensure both interactive and `--force` flows use the same backup/remove/restore sequence so behavior is consistent; the only difference remains whether the user is prompted.

6. **Update any script-related documentation**  
   - In any README or docs that describe `scripts/install-app.py` (for example `cape/README.md` or `scripts/README.md` if present), update references from `target/cape` to `target/cape-cli`.  
   - Add a brief note that reinstalls into an existing `cape-cli` directory will warn before overwriting and will preserve only a single top-level `.env` file, not `.env.local` or other variants.

## Further Considerations

1. This plan assumes `.env` lives directly under `target_dir/cape-cli` (not nested); if you ever need nested configs, the backup helper would need to be extended.  
2. The backup helper can use a single fixed filename (like `.env.cape-backup`) for now; if repeated failed runs ever make multiple backups a concern, it can be extended later to generate unique names instead.
