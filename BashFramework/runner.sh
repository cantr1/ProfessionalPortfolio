#!/bin/bash
set -e

# Load framework libs
source lib/colors.sh
source lib/assert.sh

echo -e "${YELLOW}Running tests...${NC}"

TOTAL=0
FAILED=0

for testfile in tests/*.sh; do
    echo -e "\n${YELLOW}==> Running $testfile${NC}"
    
    # Source test file
    source "$testfile"

    # Find test functions defined in this file only
    testfuncs=$(grep -oE '^test_[a-zA-Z0-9_]+' "$testfile")

    for testfunc in $testfuncs; do
        ((TOTAL++))
        if ! $testfunc; then
            ((FAILED++))
        fi
    done

    # Cleanup: unset functions so they don't leak into the next file
    for testfunc in $testfuncs; do
        unset -f "$testfunc"
    done
done

echo -e "\n${YELLOW}Summary:${NC} $((TOTAL - FAILED))/$TOTAL passed, $FAILED failed."

# Exit non-zero if failures
exit $FAILED
