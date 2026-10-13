#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="$SCRIPT_DIR/oju-ui.service"

if [ ! -f "$SERVICE_FILE" ]; then
  echo "Error: oju-ui.service not found in $SCRIPT_DIR"
  exit 1
fi

echo "Installing Oju UI service..."
echo "Make sure you've edited oju-ui.service with your username and paths first!"
echo ""

# The service was called odysseus-ui before the rename; stop it so the two
# don't fight over the same port.
if [ -f /etc/systemd/system/odysseus-ui.service ]; then
  echo "Disabling the old odysseus-ui service..."
  sudo systemctl disable --now odysseus-ui || true
fi

sudo cp "$SERVICE_FILE" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable oju-ui
sudo systemctl start oju-ui
sudo systemctl status oju-ui
