#!/bin/bash

source ./helper_functions.sh

main() {
    validate_input "$@"
    
    if [[ "$1" == "--install" ]]; then
        install_service
    elif [[ "$1" == "--uninstall" ]]; then
        uninstall_service
    fi
}

main "$@"
