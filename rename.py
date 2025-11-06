import os
import sys
import argparse

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

def rename_item(item_path, replacements, dry_run=False):
    """Rename a file or directory."""
    directory, name = os.path.split(item_path)
    new_name = name
    for old, new in replacements:
        new_name = new_name.replace(old, new)

    if new_name != name:
        new_path = os.path.join(directory, new_name)
        if dry_run:
            print(f"[DRY RUN] Would rename: {item_path} to {new_path}")
        else:
            try:
                os.rename(item_path, new_path)
                print(f"Renamed: {item_path} to {new_path}")
                return new_path
            except Exception as e:
                print(f"Could not rename {item_path}: {e}")
    return item_path

def rename_and_replace(root_dir, old_term, new_term, dry_run=False):
    """Walk through the directory, rename files/dirs, and replace content."""
    replacements = get_replacements(old_term, new_term)

    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=True):
        # Prune the list of directories to visit
        def path_contains_excluded(path):
            parts = os.path.normpath(path).split(os.sep)
            return any(part in EXCLUDED_DIRS for part in parts)

        # Prune directories whose path contains any excluded directory
        dirnames[:] = [d for d in dirnames if not path_contains_excluded(os.path.join(dirpath, d))]

        # Process files in the current (non-excluded) directory
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            replace_in_file(file_path, replacements, dry_run)
            rename_item(file_path, replacements, dry_run)

    # We need a second, bottom-up pass for renaming directories safely
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # We only need to check the immediate subdirectories for exclusion
        # as the traversal into them was already pruned in the first pass.
        for dirname in dirnames:
            # Skip directories whose path contains any excluded directory
            parts = os.path.normpath(os.path.join(dirpath, dirname)).split(os.sep)
            if any(part in EXCLUDED_DIRS for part in parts):
                continue
            dir_path = os.path.join(dirpath, dirname)
            rename_item(dir_path, replacements, dry_run)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recursively rename files, directories, and replace content.")
    parser.add_argument("directory", help="The root directory to start from.")
    parser.add_argument("old_term", help="The term to be replaced.")
    parser.add_argument("new_term", help="The term to replace with.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without actually making changes.")
    
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: Directory '{args.directory}' not found.")
        sys.exit(1)

    rename_and_replace(args.directory, args.old_term, args.new_term, args.dry_run)
    print("\nScript finished.")
