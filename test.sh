#!/bin/bash

# Function to check the exit code of the last command
check_exit_code() {
    if [ $? -ne 0 ]; then
        echo "Error: Test failed."
        exit 1
    fi
}

# --- Test Setup ---
TEST_DIR="test_dir"
OLD_NAME="initialname"
NEW_NAME="newname"

# Clean up previous test runs
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR/$OLD_NAME"_dir "$TEST_DIR"/another_dir
check_exit_code

# Create dummy files and directories
echo "This is a file about $OLD_NAME. $OLD_NAME is a great tool." > "$TEST_DIR/$OLD_NAME"_dir/"$OLD_NAME"_file.rs
echo "This file does not contain the term." > "$TEST_DIR/$OLD_NAME"_dir/another_file.rs
echo "This is a root file about $OLD_NAME." > "$TEST_DIR"/root_"$OLD_NAME"_file.rs
echo "$OLD_NAME-agentd" > "$TEST_DIR"/another_dir/service.toml
check_exit_code

# Initialize a Git repository for the 'git mv' test
(cd "$TEST_DIR" && git init && git add . && git commit -m "Initial commit")
check_exit_code

# --- Run the Script ---
python3 rename.py "$TEST_DIR" "$OLD_NAME" "$NEW_NAME" --use-git
check_exit_code

# --- Assertions ---
echo "Running assertions for successful rename..."

# 1. Check for renamed directory
if [ ! -d "$TEST_DIR/$NEW_NAME"_dir ]; then
    echo "Assertion failed: Directory '$TEST_DIR/$NEW_NAME'_dir was not created."
    exit 1
fi
echo "✔ Directory renamed successfully."

# 2. Check for renamed file in the renamed directory
if [ ! -f "$TEST_DIR/$NEW_NAME"_dir/"$NEW_NAME"_file.rs ]; then
    echo "Assertion failed: File '$TEST_DIR/$NEW_NAME'_dir/'$NEW_NAME'_file.rs was not created."
    exit 1
fi
echo "✔ File in renamed directory renamed successfully."

# 3. Check for renamed file in the root directory
if [ ! -f "$TEST_DIR"/root_"$NEW_NAME"_file.rs ]; then
    echo "Assertion failed: File '$TEST_DIR'/root_'$NEW_NAME'_file.rs was not created."
    exit 1
fi
echo "✔ Root file renamed successfully."

# 4. Check that old directory is gone
if [ -d "$TEST_DIR/$OLD_NAME"_dir ]; then
    echo "Assertion failed: Directory '$TEST_DIR/$OLD_NAME'_dir still exists."
    exit 1
fi
echo "✔ Old directory removed."

# 5. Check content replacement in the first file
if ! grep -q "$NEW_NAME is a great tool" "$TEST_DIR/$NEW_NAME"_dir/"$NEW_NAME"_file.rs; then
    echo "Assertion failed: Content in '$TEST_DIR/$NEW_NAME'_dir/'$NEW_NAME'_file.rs was not replaced correctly."
    exit 1
fi
echo "✔ Content in first file replaced successfully."

# 6. Check content replacement in the root file
if ! grep -q "This is a root file about $NEW_NAME." "$TEST_DIR"/root_"$NEW_NAME"_file.rs; then
    echo "Assertion failed: Content in '$TEST_DIR'/root_'$NEW_NAME'_file.rs was not replaced correctly."
    exit 1
fi
echo "✔ Content in root file replaced successfully."

# 7. Check special -agentd to -service replacement
if ! grep -q "$NEW_NAME-service" "$TEST_DIR"/another_dir/service.toml; then
    echo "Assertion failed: Special case '-agentd' to '-service' replacement failed in 'service.toml'."
    exit 1
fi
echo "✔ Special case replacement successful."

# --- Cleanup for first test ---
rm -rf "$TEST_DIR"
echo ""
echo "All rename tests passed!"
echo "-------------------------------------"
echo "Testing name conflict scenario..."

# --- Test Setup for Conflict ---
mkdir -p "$TEST_DIR/$OLD_NAME"_dir
mkdir -p "$TEST_DIR/$NEW_NAME"_dir # Create the conflicting directory
echo "dummy file" > "$TEST_DIR/$OLD_NAME"_dir/dummy.txt
(cd "$TEST_DIR" && git init && git add . && git commit -m "Initial commit")
check_exit_code

# --- Run the Script and Capture Output ---
output=$(python3 rename.py "$TEST_DIR" "$OLD_NAME" "$NEW_NAME" --use-git 2>&1)
echo "Script output:"
echo "$output"

# --- Assertions for Conflict ---
# 1. Check that the script printed an error
if ! echo "$output" | grep -q "Error: Cannot rename"; then
    echo "Assertion failed: Script did not print an error message for the name conflict."
    exit 1
fi
echo "✔ Script correctly identified the name conflict."

# 2. Check that the original directory still exists
if [ ! -d "$TEST_DIR/$OLD_NAME"_dir ]; then
    echo "Assertion failed: Original directory was removed despite the conflict."
    exit 1
fi
echo "✔ Original directory was not removed."

# --- Cleanup for second test ---
rm -rf "$TEST_DIR"
echo ""
echo "Name conflict test passed!"
echo "-------------------------------------"
echo "Testing submodule scenario..."

# --- Test Setup for Submodule ---
# Allow local file clones for the test
git config --global protocol.file.allow always
check_exit_code

# Create a dummy repo to act as the submodule
SUBMODULE_REPO="submodule_repo"
rm -rf "$SUBMODULE_REPO"
mkdir -p "$SUBMODULE_REPO"
(cd "$SUBMODULE_REPO" && git init && echo "submodule content" > "$OLD_NAME"_file.txt && git add . && git commit -m "Initial submodule commit")
check_exit_code

# Create the main test directory and add the submodule
mkdir -p "$TEST_DIR"
(cd "$TEST_DIR" && git init && git submodule add "../$SUBMODULE_REPO" "$OLD_NAME"_submodule && git commit -m "Add submodule")
check_exit_code

# --- Run the Script ---
python3 rename.py "$TEST_DIR" "$OLD_NAME" "$NEW_NAME" --use-git
check_exit_code

# --- Assertions for Submodule ---
# 1. Check that the submodule directory was renamed
if [ ! -d "$TEST_DIR/$NEW_NAME"_submodule ]; then
    echo "Assertion failed: Submodule directory was not renamed."
    exit 1
fi
echo "✔ Submodule directory renamed successfully."

# 2. Check that the file inside the submodule was renamed
if [ ! -f "$TEST_DIR/$NEW_NAME"_submodule/"$NEW_NAME"_file.txt ]; then
    echo "Assertion failed: File inside submodule was not renamed."
    exit 1
fi
echo "✔ File inside submodule renamed successfully."


# --- Final Cleanup ---
rm -rf "$TEST_DIR"
rm -rf "$SUBMODULE_REPO"
# Revert the git config change
git config --global --unset protocol.file.allow
echo ""
echo "All tests passed!"
exit 0
