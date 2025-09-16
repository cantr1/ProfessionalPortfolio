#!/bin/bash
# Checks expected users were setup

declare -a USERS=("kelz" "haley" "admin")

test_users() {
    for USER_NAME in "${USERS[@]}"; do
        result=$(id $USER_NAME 2>/dev/null)
        if [[ -n "$result" ]]; then 
            assert_true "[[ -n \"$result\" ]]" "User $USER_NAME setup"
        else
            assert_true "[[ -n \"$result\" ]]" "User $USER_NAME not setup"
        fi
    done
}

test_users