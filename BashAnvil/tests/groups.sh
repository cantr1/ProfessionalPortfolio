#!/bin/bash
# Checks expected groups were created during the playbook

declare -a GROUPS=("devops" "security" "developers")

test_groups() {
    for GROUP in "${GROUPS[@]}"; do
        result=$(getent group "$GROUP")
        if [[ -n "$result" ]]; then 
            assert_true "[[ -n \"$result\" ]]" "Group $GROUP setup"
        else
            assert_true "[[ -n \"$result\" ]]" "Group $GROUP not installed"
        fi
    done
}

test_groups