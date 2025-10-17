#!/bin/bash
echo "== Mattermost Spotify Status Setup =="

if [ ! -f ".env" ]; then
  echo "Copying .env.example to .env..."
  cp .env.example .env
  echo "Edit .env with your credentials before running the script."
fi

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Setup complete. Start with:"
echo "  python3 mm_spotify_status.py &"
