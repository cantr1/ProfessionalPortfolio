#!/bin/bash
# Checks expected users were setup with sudo perms applied
source lib/colors.sh

declare -a USERS=("millie" "haley" "admin")

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

test_perms() {
    for USER_NAME in "${USERS[@]}"; do
        if [[ -f "/etc/sudoers.d/$USER_NAME" ]]; then
            assert_true "[[ -f "/etc/sudoers.d/$USER_NAME" ]]" "Sudo perms setup for $USER_NAME"
        else
            assert_true "[[ -f "/etc/sudoers.d/$USER_NAME" ]]" "Sudo perms not setup for $USER_NAME"
        fi
    done
}

test_users
echo -e "${PURPLE}==> Checking sudo perms"
test_perms
