#!/usr/bin/env python3
import os, time, json, threading, requests
from datetime import datetime, timedelta, timezone
import gi
from dotenv import load_dotenv
load_dotenv()

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3

# ==== CONFIG ====
MM_URL = os.environ["MM_URL"].rstrip("/")
MM_USER = os.environ["MM_USER"]
MM_PASS = os.environ["MM_PASS"]
SPOTIFY_CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
SPOTIFY_REFRESH_TOKEN = os.environ["SPOTIFY_REFRESH_TOKEN"]

POLL_SECONDS = 5
EMOJI = "musical_note"
ICON_PATH = os.environ.get("ICON_PATH", "icon.ico")

# ==== Mattermost API ====
def mm_login():
    print("[INFO] Logge bei Mattermost ein...")
    r = requests.post(
        f"{MM_URL}/api/v4/users/login",
        headers={"Content-Type": "application/json"},
        data=json.dumps({"login_id": MM_USER, "password": MM_PASS}),
        timeout=20
    )
    r.raise_for_status()
    token = r.headers.get("Token", "")
    cookie = r.headers.get("Set-Cookie", "").split(";")[0]
    h = {}
    if token:
        h["Authorization"] = f"Bearer {token}"
    if cookie:
        h["Cookie"] = cookie
    print("[OK] Login erfolgreich, Token erhalten.")
    return h

def mm_set_custom_status(headers, text, expires_at_iso):
    print(f"[INFO] Setze MM-Status: '{text}' bis {expires_at_iso}")
    body = {"emoji": EMOJI, "text": text, "expires_at": expires_at_iso}
    r = requests.put(
        f"{MM_URL}/api/v4/users/me/status/custom",
        headers={**headers, "Content-Type": "application/json"},
        data=json.dumps(body),
        timeout=20
    )
    print(f"[DEBUG] Antwort Code: {r.status_code}")
    if r.status_code == 401:
        print("[WARN] Token ungültig, neuer Login...")
        headers.update(mm_login())
        return mm_set_custom_status(headers, text, expires_at_iso)

def mm_clear_custom_status(headers):
    print("[INFO] Lösche MM-Status.")
    body = {"emoji": "", "text": "", "expires_at": None}
    r = requests.put(
        f"{MM_URL}/api/v4/users/me/status/custom",
        headers={**headers, "Content-Type": "application/json"},
        data=json.dumps(body),
        timeout=20
    )
    print(f"[DEBUG] Antwort Code: {r.status_code}")
    if r.status_code == 401:
        print("[WARN] Token ungültig, neuer Login...")
        headers.update(mm_login())
        return mm_clear_custom_status(headers)

# ==== Spotify API ====
def spotify_access_token():
    print("[INFO] Hole Spotify Access Token...")
    r = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "refresh_token", "refresh_token": SPOTIFY_REFRESH_TOKEN},
        auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
        timeout=20
    )
    r.raise_for_status()
    token = r.json()["access_token"]
    print("[OK] Spotify Access Token erhalten.")
    return token

def spotify_current(access_token):
    print("[INFO] Frage aktuellen Song bei Spotify ab...")
    r = requests.get(
        "https://api.spotify.com/v1/me/player/currently-playing",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=20
    )
    if r.status_code == 204 or not r.text:
        print("[INFO] Keine Wiedergabe erkannt.")
        return None
    r.raise_for_status()
    data = r.json()
    if not data.get("is_playing"):
        print("[INFO] Wiedergabe pausiert.")
        return None

    item = data.get("item") or {}
    name = item.get("name")
    artists = ", ".join(a.get("name","") for a in item.get("artists", []))
    track_id = item.get("id") or item.get("uri") or f"{artists} – {name}"

    duration_ms = item.get("duration_ms") or 0
    progress_ms = data.get("progress_ms") or 0
    remaining_ms = max(0, duration_ms - progress_ms)

    # Startzeit der aktuellen Wiedergabe berechnen. Sekundenauflösung reicht und ist stabil
    started_at = datetime.now(timezone.utc) - timedelta(milliseconds=progress_ms)
    started_iso = started_at.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Eindeutige Wiedergabe-ID. Ändert sich auch bei Repeat desselben Songs
    uid = f"{track_id}:{started_iso}"

    expires = datetime.now(timezone.utc) + timedelta(milliseconds=remaining_ms + 3000)
    expires_iso = expires.strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"[OK] Aktueller Song: {artists} – {name} uid={uid}")
    return {
        "text": f"{artists} – {name}",
        "expires_at": expires_iso,
        "uid": uid
    }

# ==== Hintergrundthread ====
running = False
last_uid = None
last_text = None

def sync_loop():
    global last_uid, last_text
    headers = mm_login()
    while running:
        try:
            at = spotify_access_token()
            cur = spotify_current(at)
            if cur:
                if cur["uid"] != last_uid:
                    mm_set_custom_status(headers, cur["text"], cur["expires_at"])
                    last_uid = cur["uid"]
                    last_text = cur["text"]
            else:
                if last_uid is not None:
                    mm_clear_custom_status(headers)
                    last_uid = None
                    last_text = None
        except Exception as e:
            print("[ERROR] Loop Fehler:", e)
        time.sleep(POLL_SECONDS)

# ==== Tray UI mit Toggle ====
class TrayApp:
    def __init__(self):
        self.indicator = AppIndicator3.Indicator.new(
            "mm-spotify-tray",
            ICON_PATH,
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.build_menu()

    def build_menu(self):
        menu = Gtk.Menu()

        self.toggle_item = Gtk.CheckMenuItem(label="Spotify Status aktiv")
        self.toggle_item.connect("toggled", self.toggle_sync)
        menu.append(self.toggle_item)

        quit_item = Gtk.MenuItem(label="Beenden")
        quit_item.connect("activate", self.quit)
        menu.append(quit_item)

        menu.show_all()
        self.indicator.set_menu(menu)

    def toggle_sync(self, widget):
        global running
        if widget.get_active():
            if not running:
                running = True
                threading.Thread(target=sync_loop, daemon=True).start()
                print("[OK] Spotify sync gestartet.")
        else:
            running = False
            print("[OK] Spotify sync gestoppt.")

    def quit(self, _):
        global running
        running = False
        Gtk.main_quit()

if __name__ == "__main__":
    app = TrayApp()
    Gtk.main()

