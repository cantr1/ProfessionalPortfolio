#!/bin/bash

test_addition() {
    local result=$((2 + 3))
    assert_eq "5" "$result" "2 + 3 should equal 5"
}

test_string_compare() {
    local str="hello"
    assert_eq "hello" "$str" "string should be hello"
}

test_addition
test_string_compare