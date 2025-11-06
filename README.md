# SuperSed

`supersed` is a Python script that automates the process of renaming a project. It recursively renames files and directories and replaces content within files, intelligently handling various casing conventions. The script is designed to be safe and flexible, with features like dry runs and optional Git integration.

## Features

- **Recursive Renaming**: Traverses the project directory to rename files and directories that contain the old project name.
- **Content Replacement**: Replaces occurrences of the old project name within files, supporting multiple casings (e.g., `lowercase`, `UPPERCASE`, `Capitalized`).
- **Git Integration**: Optionally uses `git mv` to rename files, ensuring that the file history is preserved in Git repositories.
- **Submodule Support**: Correctly handles Git submodules, running rename operations within the submodule's own Git context.
- **Configurable**: Allows customization of target file extensions and excluded directories.
- **Safe**: Includes a `--dry-run` option to preview changes before they are applied.

## Usage

To use the script, run it from the command line with the following arguments:

```bash
python3 rename.py <directory> <old_term> <new_term> [options]
```

### Arguments

- `directory`: The root directory of the project you want to rename.
- `old_term`: The current name of the project to be replaced.
- `new_term`: The new name for the project.

### Options

- `--dry-run`: Show what would be changed without actually making any modifications.
- `--use-git`: Use `git mv` for renaming files. The project must be a Git repository.

### Example

Suppose you have a project named `initialname` located in the `test_dir` directory, and you want to rename it to `newname`.

```bash
python3 rename.py ./test_dir initialname newname --use-git
```

This command will:

1. Rename directories like `test_dir/initialname_dir` to `test_dir/newname_dir`.
2. Rename files like `test_dir/initialname_file.rs` to `test_dir/newname_file.rs`.
3. Replace content such as `initialname` with `newname` inside the files.
4. Use `git mv` for all renames, preserving the Git history.

## Configuration

The script can be configured by modifying the following lists at the top of `rename.py`:

- `TARGET_EXTENSIONS`: A list of file extensions to be included in content replacement. By default, it includes `.rs` and `.toml`.
- `EXCLUDED_DIRS`: A list of directories to be excluded from the renaming process. By default, it excludes directories like `.git`, `vendor`, and `target`.

## Casing Variations

The script automatically handles a variety of casing formats for the terms being replaced. The supported variations include:

- `old_term` -> `new_term`
- `OLD_TERM` -> `NEW_TERM`
- `Old_term` -> `New_term`
- `old_term-agentd` -> `new_term-service`
- `OLD_TERM-AGENTD` -> `NEW_TERM-SERVICE`

This ensures that different naming conventions used throughout a project are consistently updated.

## Git Submodules

When running with the `--use-git` flag, the script correctly handles Git submodules. It will:

1.  **Recursively process submodules:** The script descends into submodule directories and performs renames and content replacements within them.
2.  **Use the correct Git context:** For any changes made inside a submodule, `git mv` commands are run from within the submodule's own repository.
3.  **Rename the submodule directory:** The top-level directory of the submodule is renamed from the context of the parent repository.
