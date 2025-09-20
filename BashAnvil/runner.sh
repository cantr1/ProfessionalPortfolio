#!/bin/bash

# Load framework libs
source lib/colors.sh
source lib/assert.sh

# Change to working dir
cd /home/kelz/ProfessionalPortfolio/BashAnvil || echo "Unable to enter proper dir"

echo -e "${YELLOW}Running tests...${NC}"

for testfile in tests/*.sh; do
    echo -e "\n${YELLOW}==> Running $testfile${NC}"
    
    # Source test file
    source "$testfile"

    # Cleanup: unset functions so they don't leak into the next file
    for testfunc in $testfuncs; do
        unset -f "$testfunc"
    done
done
