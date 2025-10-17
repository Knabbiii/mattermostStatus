# 🎵 Mattermost Spotify Status

A lightweight tray app that automatically updates your Mattermost custom status with your currently playing Spotify song.

---

## ✨ Features

* Shows your current Spotify song as your Mattermost status
* Clears the status automatically when paused or stopped
* Tray icon toggle for quick enable/disable
* Works cross-platform (Linux, tested on GNOME/Ubuntu)

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/<yourname>/mm_spotify_status.git
cd mm_spotify_status
```

### 2. Run setup

```bash
./setup.sh
```

This installs all dependencies and creates a `.env` file.
Then edit `.env` with your credentials.

---

## 🗾 Mattermost Setup

1. Log in to your Mattermost instance.
2. Go to **Account Settings → Security → Personal Access Tokens**.
3. (If tokens are disabled, ask your admin to enable them.)
4. Fill your Mattermost URL, username and password (or token if you modify the script to use it) in `.env`.

Example:

```env
MM_URL=https://chat.company.com
MM_USER=johndoe
MM_PASS=mysecurepassword
```

---

## 🎷 Spotify API Setup

To get your Spotify tokens, follow these steps:

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
2. Log in and click **Create an App**.
3. Give it a name (e.g., “Mattermost Status Sync”).
4. In **Redirect URI**, enter `http://localhost:8888/callback` (you can change it later).
5. Save your **Client ID** and **Client Secret** — put them into `.env`.

Then, to get a **Refresh Token**:

* Run a small helper tool like [Spotify Token Generator](https://spotify-refresh-token-generator.netlify.app/)
* Or follow a manual tutorial:
  [https://developer.spotify.com/documentation/web-api/tutorials/refreshing-tokens](https://developer.spotify.com/documentation/web-api/tutorials/refreshing-tokens)

You’ll receive a `refresh_token`. Add it to your `.env`.

Example:

```env
SPOTIFY_CLIENT_ID=abcd1234
SPOTIFY_CLIENT_SECRET=efgh5678
SPOTIFY_REFRESH_TOKEN=long_refresh_token_here
```

---

## 🚀 Run

```bash
python3 mm_spotify_status.py &
```

A tray icon will appear.
Toggle “Spotify Status aktiv” to start or stop syncing.

---

## 🧩 Troubleshooting

* **GTK / AppIndicator missing:**
  Install manually:

  ```bash
  sudo apt install python3-gi gir1.2-appindicator3-0.1
  ```
* **Spotify not showing anything:**
  Make sure Spotify is playing on the same account linked in `.env`.
* **Mattermost 401 errors:**
  Check your credentials or regenerate your access token.

---

## 🧐 Dependencies

* Python 3.9+
* PyGObject
* requests
* python-dotenv
* GTK / AppIndicator (system packages)

---

## 📝 License

MIT © 2025 Knabbiii
