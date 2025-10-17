#!/bin/bash
set -e
echo "== Mattermost Spotify Status Setup =="

# --- Step 1: Create .env if missing ---
if [ ! -f ".env" ]; then
  echo "Copying .env.example to .env..."
  cp .env.example .env
  echo "Edit .env with your credentials before running the script."
fi

# --- Step 2: Install dependencies ---
echo "Installing dependencies..."
sudo apt install -y python3-gi gir1.2-appindicator3-0.1
pip install -r requirements.txt

# --- Step 3: Offer systemd autostart ---
read -p "Do you want to enable automatic startup via systemd (user mode)? [y/N]: " ENABLE_SYSTEMD
if [[ "$ENABLE_SYSTEMD" =~ ^[Yy]$ ]]; then
  mkdir -p ~/.config/systemd/user

  SERVICE_PATH=~/.config/systemd/user/mm-spotify-tray.service
  echo "Creating $SERVICE_PATH ..."

  cat > "$SERVICE_PATH" <<EOF
[Unit]
Description=Mattermost Spotify Tray App

[Service]
Type=simple
EnvironmentFile=$(pwd)/.env
ExecStart=$(which python3) $(pwd)/mm_spotify_status.py
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
EOF

  echo "Reloading systemd daemon..."
  systemctl --user daemon-reload

  read -p "Start and enable the service now? [Y/n]: " START_SERVICE
  if [[ "$START_SERVICE" =~ ^[Nn]$ ]]; then
    echo "Service created but not started."
  else
    systemctl --user enable --now mm-spotify-tray.service
    echo "Service enabled and started!"
  fi

  echo
  echo "To view logs later, run:"
  echo "  journalctl --user -u mm-spotify-tray -f"
fi

# --- Step 4: Done ---
echo
echo "Setup complete!"
echo "Run manually with: python3 mm_spotify_status.py &"
echo "Or start the systemd service with: systemctl --user start mm-spotify-tray.service"
echo "Enjoy your Mattermost Spotify status tray app!"