#!/bin/bash

SCRIPT_DIR="$(readlink -f $(dirname "${BASH_SOURCE[0]}"))"
SERVICEFILE_DIR="$(readlink -f "${SCRIPT_DIR}/systemd/user")"
SYSTEMD_DIR="$(readlink -f ~/.config/systemd/user)"

mkdir -p $SYSTEMD_DIR

for file in $SERVICEFILE_DIR
do
    ln -s "$file" "$SYSTEMD_DIR"
done

systemctl --user enable rustserver.service rustserver-update.timer rustserver-lgsm-update.timer rustserver-monitor.timer
systemctl --user start rustserver.service rustserver-update.timer rustserver-lgsm-update.timer rustserver-monitor.timer
