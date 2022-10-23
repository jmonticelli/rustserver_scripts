#!/bin/bash

SCRIPT_DIR="$(readlink -f $(dirname "${BASH_SOURCE[0]}"))"

# Call getopt to validate the provided input. 
options=$(getopt -o u: -- "$@")
[ $? -eq 0 ] || { 
    echo "Incorrect options provided"
    exit 1
}
eval set -- "$options"
while true; do
    case "$1" in
    -u)
	shift
	SERVER_USERNAME=$1
	;;
    --)
        shift
        break
        ;;
    esac
    shift
done

set -euo pipefail

echo "Adding user $SERVER_USERNAME"
adduser $SERVER_USERNAME

# This is required for running systemd services
echo "Enabling linger for $SERVER_USERNAME"
loginctl enable-linger $SERVER_USERNAME

# TODO: actually do this for the right version, for now I assume Debian 10
dpkg --add-architecture i386 && \
apt update && \
apt install curl wget file tar bzip2 gzip unzip bsdmainutils python3 util-linux ca-certificates binutils bc jq tmux netcat lib32gcc1 lib32stdc++6 lib32z1

# Install the rustserver
sudo su -c 'cd ~ && wget -O linuxgsm.sh https://linuxgsm.sh && chmod +x linuxgsm.sh && bash linuxgsm.sh rustserver && ./rustserver install'

# Right now, I have no access token that I require but I might in the future.
sudo su -c 'cd ~ && git clone https://github.com/jmonticelli/rustserver_scripts && ./rustserver_scripts/install_services.sh'
