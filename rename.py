import os
import sys
import argparse
import subprocess

# --- Configuration ---
# Only modify content in files with these extensions
TARGET_EXTENSIONS = ['.rs', '.toml']
# Exclude these directories from traversal and modification
EXCLUDED_DIRS = ['.git', 'vendor', 'build', 'target']

def get_replacements(old_term, new_term):
    """Generate a list of replacements for different casings."""
    return [
        (f"{old_term}-agentd", f"{new_term}-service"),
        (f"{old_term.upper()}-AGENTD", f"{new_term.upper()}-SERVICE"),
        (f"{old_term.capitalize()}-Agentd", f"{new_term.capitalize()}-Service"),
        (f"{old_term.lower()}-agentd", f"{new_term.lower()}-service"),
        (f"{old_term.capitalize()}-agentd", f"{new_term.capitalize()}-service"),
        (f"{old_term} Agent", new_term),
        (f"{old_term.upper()} AGENT", new_term.upper()),
        (f"{old_term.capitalize()} Agent", new_term.capitalize()),
        (old_term, new_term),
        (old_term.upper(), new_term.upper()),
        (old_term.capitalize(), new_term.capitalize()),
    ]

def replace_in_file(file_path, replacements, dry_run=False):
    """Replace content in a single file if it has a target extension."""
    _, extension = os.path.splitext(file_path)
    if extension not in TARGET_EXTENSIONS:
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                content = file.read()
        except Exception as e:
            print(f"Could not read file {file_path}: {e}")
            return

    original_content = content
    new_content = content
    for old, new in replacements:
        new_content = new_content.replace(old, new)

    if new_content != original_content:
        if dry_run:
            print(f"[DRY RUN] Would update content in: {file_path}")
        else:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print(f"Updated content in: {file_path}")
            except Exception as e:
                print(f"Could not write to file {file_path}: {e}")

def is_git_repository(path):
    """Check if the given path is a Git repository."""
    return os.path.isdir(os.path.join(path, '.git'))

def find_git_root(path):
    """Find the git repository root for a given path."""
    current_path = os.path.abspath(path)
    while current_path != os.path.dirname(current_path):
        if os.path.exists(os.path.join(current_path, '.git')):
            return current_path
        current_path = os.path.dirname(current_path)
    return None

def rename_item(git_root, old_path, new_path, dry_run=False, use_git=False):
    """Rename a file or directory, optionally using 'git mv'."""
    if os.path.exists(new_path):
        print(f"Error: Cannot rename '{old_path}' to '{new_path}' because the destination already exists.")
        return old_path

    if dry_run:
        print(f"[DRY RUN] Would rename: {old_path} to {new_path}")
        return new_path
    else:
        try:
            if use_git and git_root:
                git_item_path = os.path.relpath(old_path, git_root)
                git_new_path = os.path.relpath(new_path, git_root)
                subprocess.run(['git', 'mv', git_item_path, git_new_path], check=True, cwd=git_root)
            else:
                os.rename(old_path, new_path)
            print(f"Renamed: {old_path} to {new_path}")
            return new_path
        except (subprocess.CalledProcessError, OSError) as e:
            print(f"Could not rename {old_path}: {e}")
            return old_path

def rename_and_replace(root_dir, old_term, new_term, dry_run=False, use_git=False):
    """Walk through the directory, rename files/dirs, and replace content."""
    if use_git and not is_git_repository(root_dir):
        print("Error: --use-git flag passed, but the directory is not a Git repository.")
        sys.exit(1)

    replacements = get_replacements(old_term, new_term)

    # Use a single, robust bottom-up traversal
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Prune excluded directories
        if any(excluded in dirpath.split(os.sep) for excluded in EXCLUDED_DIRS):
            continue

        # 1. Handle files
        for filename in filenames:
            old_file_path = os.path.join(dirpath, filename)

            # First, replace content in the file
            replace_in_file(old_file_path, replacements, dry_run)

            # Then, rename the file if needed
            new_filename = filename
            for old, new in replacements:
                new_filename = new_filename.replace(old, new)

            if new_filename != filename:
                new_file_path = os.path.join(dirpath, new_filename)
                git_root = find_git_root(old_file_path)
                rename_item(git_root, old_file_path, new_file_path, dry_run, use_git)

        # 2. Handle directories
        for dirname in dirnames:
            old_dir_path = os.path.join(dirpath, dirname)
            if dirname in EXCLUDED_DIRS:
                continue

            new_dirname = dirname
            for old, new in replacements:
                new_dirname = new_dirname.replace(old, new)

            if new_dirname != dirname:
                new_dir_path = os.path.join(dirpath, new_dirname)
                # For submodule directories, the git_root is the parent's git repo
                if os.path.isfile(os.path.join(old_dir_path, '.git')):
                    git_root = find_git_root(dirpath)
                else:
                    git_root = find_git_root(old_dir_path)
                rename_item(git_root, old_dir_path, new_dir_path, dry_run, use_git)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recursively rename files, directories, and replace content.")
    parser.add_argument("directory", help="The root directory to start from.")
    parser.add_argument("old_term", help="The term to be replaced.")
    parser.add_argument("new_term", help="The term to replace with.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without actually making changes.")
    parser.add_argument("--use-git", action="store_true", help="Use 'git mv' for renaming files. The project must be a Git repository.")
    
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: Directory '{args.directory}' not found.")
        sys.exit(1)

    rename_and_replace(args.directory, args.old_term, args.new_term, args.dry_run, args.use_git)
    print("\nScript finished.")
