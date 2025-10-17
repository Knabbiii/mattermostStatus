#!/usr/bin/env bash
set -e

# === Colors ===
GREEN="\e[32m"
YELLOW="\e[33m"
BLUE="\e[36m"
BOLD="\e[1m"
RESET="\e[0m"

clear
echo -e "${BLUE}${BOLD}╔══════════════════════════════════════════╗${RESET}"
echo -e "${BLUE}${BOLD}║     Mattermost Spotify Status Setup      ║${RESET}"
echo -e "${BLUE}${BOLD}╚══════════════════════════════════════════╝${RESET}"
echo

# --- Step 1: Create .env if missing ---
if [ ! -f ".env" ]; then
  echo -e "${YELLOW}[INFO]${RESET} Creating ${BOLD}.env${RESET} file from example..."
  cp .env.example .env
  echo -e "${GREEN}[OK]${RESET} .env file created!"
  echo
  echo -e "${YELLOW}${BOLD}⚠️  Important:${RESET} Open the file ${BOLD}.env${RESET} and fill in your Mattermost and Spotify credentials before continuing."
  echo -e "${YELLOW}   Example: nano .env${RESET}"
  echo
else
  echo -e "${GREEN}[OK]${RESET} Existing ${BOLD}.env${RESET} found."
fi

# --- Step 2: Install system dependencies ---
echo -e "${YELLOW}[INFO]${RESET} Installing system dependencies (this may take a moment)..."
{
  sudo apt update -qq
  sudo apt install -y -qq \
    python3 python3-pip python3-venv \
    python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1 \
    pkg-config libcairo2-dev libgirepository1.0-dev libglib2.0-dev cmake
} &>/dev/null
echo -e "${GREEN}[OK]${RESET} System dependencies installed."
echo

# --- Step 3: Create & prepare virtual environment ---
if [ ! -d "venv" ]; then
  echo -e "${YELLOW}[INFO]${RESET} Creating virtual environment..."
  python3 -m venv venv &>/dev/null
  echo -e "${GREEN}[OK]${RESET} Virtual environment created."
else
  echo -e "${GREEN}[OK]${RESET} Virtual environment already exists."
fi

echo -e "${YELLOW}[INFO]${RESET} Installing Python packages..."
{
  source venv/bin/activate
  pip install --quiet --upgrade pip
  pip install --quiet -r requirements.txt
  deactivate
} &>/dev/null
echo -e "${GREEN}[OK]${RESET} Python packages installed."
echo

# --- Step 4: Offer systemd autostart ---
read -p "$(echo -e "${YELLOW}[?]${RESET} Do you want to enable automatic startup via systemd (user mode)? [y/N]: ")" ENABLE_SYSTEMD
if [[ "$ENABLE_SYSTEMD" =~ ^[Yy]$ ]]; then
  mkdir -p ~/.config/systemd/user
  SERVICE_PATH=~/.config/systemd/user/mm-spotify-tray.service

  echo -e "${YELLOW}[INFO]${RESET} Creating systemd service..."
  cat > "$SERVICE_PATH" <<EOF
[Unit]
Description=Mattermost Spotify Tray App

[Service]
Type=simple
EnvironmentFile=$(pwd)/.env
ExecStart=$(pwd)/venv/bin/python $(pwd)/mm_spotify_status.py
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
EOF

  {
    systemctl --user daemon-reload
  } &>/dev/null

  read -p "$(echo -e "${YELLOW}[?]${RESET} Start and enable the service now? [Y/n]: ")" START_SERVICE
  if [[ "$START_SERVICE" =~ ^[Nn]$ ]]; then
    echo -e "${YELLOW}[INFO]${RESET} Service created but not started."
  else
    {
      systemctl --user enable --now mm-spotify-tray.service
    } &>/dev/null
    echo -e "${GREEN}[OK]${RESET} Service enabled and started."
  fi

  echo
  echo -e "${BLUE}To view logs later, run:${RESET}"
  echo "  journalctl --user -u mm-spotify-tray -f"
  echo
fi

# --- Step 5: Done ---
echo -e "${GREEN}${BOLD}✔ Setup complete!${RESET}"
echo
echo -e "${BLUE}Run manually:${RESET}"
echo "  ./venv/bin/python mm_spotify_status.py &"
echo
echo -e "${BLUE}Or start the service:${RESET}"
echo "  systemctl --user start mm-spotify-tray.service"
echo
echo -e "${YELLOW}${BOLD}Remember:${RESET} Edit your ${BOLD}.env${RESET} file before first run if you haven’t already!"
echo
echo -e "${GREEN}${BOLD}Enjoy your Mattermost Spotify status tray app!${RESET}"
echo
