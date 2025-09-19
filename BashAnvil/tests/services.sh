#!/bin/bash

declare -a SERVICES=("sshd" "mosquitto" "nginx")

test_services() {
    for SERVICE in "${SERVICES[@]}"; do
        result=$(sudo systemctl is-active "$SERVICE")
        case "$result" in
            "active")
                assert_true "[[ \"$result\" == \"active\" ]]" "Service $SERVICE active"
                ;;
            "inactive")
                assert_true "[[ \"$result\" == \"active\" ]]" "Service $SERVICE inactive"
                ;;
            *)
                echo "Service in unknown state..."
        esac
    done
}

test_services