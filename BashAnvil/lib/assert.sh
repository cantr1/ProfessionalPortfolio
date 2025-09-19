#!/bin/bash

# Assert equality
assert_eq() {
    local expected="$1"
    local actual="$2"
    local msg="${3:-}"

    if [[ "$expected" == "$actual" ]]; then
        echo -e "${GREEN}PASS${NC} $msg"
        return 0
    else
        echo -e "${RED}FAIL${NC} $msg"
        echo -e "   expected: $expected"
        echo -e "   got:      $actual"
        return 1
    fi
}

# Assert truthy
assert_true() {
    local cond="$1"
    local msg="${2:-}"
    if eval "$cond"; then
        echo -e "${GREEN}PASS${NC} $msg"
    else
        echo -e "${RED}FAIL${NC} $msg"
    fi
}
