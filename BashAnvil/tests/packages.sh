#!/bin/bash
# Checks expected packages were installed during the playbook

declare -a PACKAGES=("golang" "python3" "vim" "curl" "tmux")

test_packages() {
    for PACKAGE_NAME in "${PACKAGES[@]}"; do
        result=$(dpkg -l "$PACKAGE_NAME" 2>/dev/null | grep -E "^ii\s+$PACKAGE_NAME" || true)
        if [[ -n "$result" ]]; then 
            assert_true "[[ -n \"$result\" ]]" "Package $PACKAGE_NAME installed"
        else
            assert_true "[[ -n \"$result\" ]]" "Package $PACKAGE_NAME not installed"
        fi
    done
}

test_packages