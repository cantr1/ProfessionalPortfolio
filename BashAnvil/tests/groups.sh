#!/bin/bash
# Checks expected groups were created during the playbook

test_groups() {
    for GROUP in "devops" "security" "developers"; do
        result=$(getent group "$GROUP")
        if [[ -n "$result" ]]; then 
            assert_true "[[ -n \"$result\" ]]" "Group $GROUP setup"
        else
            assert_true "false" "Group $GROUP not installed"
        fi
    done
}

test_groups