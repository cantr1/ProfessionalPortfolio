#!/bin/bash
SERVICE_NAME="c_vault"
SERVICE_DIRECTORY="/opt/vault"
SERVICE_USER="kelz"

SERVICE_FILE="[Unit]
Description=API in C to Manage Password Vault
After=multi-user.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$SERVICE_DIRECTORY
ExecStart=$SERVICE_DIRECTORY/api
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target"

SERVICE_FILE_LOCATION="/etc/systemd/system/$SERVICE_NAME.service"

WORKING_DIRECTORY="/home/kelz/workspace"

validate_input() {
    # Add help option
    if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
        echo -e "Options:\n--install: Setup service\n--uninstall: Disable and remove service"
        exit 0
    fi

    # Main script requires args
    if [[ -z "$1" ]]; then
        echo "$0 requires positional arguments"
        echo "Valid arguments: --install | --uninstall"
        exit 1
    fi

    # Check that only one arg is passed
    if [[ "$#" -gt 1 ]]; then
        echo "$0 only takes one argument"
        exit 1
    fi

    # Check that arg is valid
    if [[ "$1" != "--install" ]] && [[ "$1" != "--uninstall" ]]; then
        echo "Unrecognized option '$1'"
        echo "Usage: $0 --install | $0 --uninstall"
    fi
}

setup_cjson() {
    git clone https://github.com/DaveGamble/cJSON.git
    cd cJSON || exit 1
    mkdir build
    cd build || exit 1
    cmake ..
    make
    sudo make install
    echo "/usr/local/lib64" | sudo tee /etc/ld.so.conf.d/cjson.conf
    sudo ldconfig
}

install_service() {
    if sudo systemctl is-active "$SERVICE_NAME" -q; then
        echo "$SERVICE_NAME is already active, exiting"
        exit 0
    fi

    sudo mkdir -p "$SERVICE_DIRECTORY"

    sudo chown "$SERVICE_USER":"$SERVICE_USER" "$SERVICE_DIRECTORY"

    cp cli_vault.c "$SERVICE_DIRECTORY"/.

    setup_cjson

    # Ensure back in working directory
    cd "$WORKING_DIRECTORY" || true

    gcc "$SERVICE_DIRECTORY"/cli_vault.c -o "$SERVICE_DIRECTORY"/api -I/usr/local/include -L/usr/local/lib -lcjson

    if ! [[ -f "$SERVICE_FILE_LOCATION" ]]; then
        echo "$SERVICE_FILE" | sudo tee "$SERVICE_FILE_LOCATION"
    fi

    sudo systemctl daemon-reexec
    sudo systemctl enable --now "$SERVICE_NAME"
    if sudo systemctl is-active "$SERVICE_NAME" -q; then
        echo "$SERVICE_NAME successfully installed"
        # Open firewall
        sudo firewall-cmd --permanent --add-port 8080/tcp
        sudo firewall-cmd --reload
    else
        echo "Issues during installation of service"
        exit 1
    fi
}

uninstall_service() {
    if ! sudo systemctl is-active "$SERVICE_NAME" -q; then
        echo "$SERVICE_NAME is already uninstalled / inactive"
        exit 0
    fi

    sudo systemctl disable --now "$SERVICE_NAME"

    sudo rm -r "$SERVICE_DIRECTORY"

    sudo rm "$SERVICE_FILE_LOCATION"

    sudo systemctl daemon-reexec

    if ! sudo systemctl is-active "$SERVICE_NAME" -q; then
        echo "$SERVICE_NAME successfully uninstalled"
        # Disable firewall port
        sudo firewall-cmd --permanent --remove-port 8080/tcp
        sudo firewall-cmd --reload
        exit 0
    else
        echo "Issues during uninstallation of service"
        exit 1
    fi
}
