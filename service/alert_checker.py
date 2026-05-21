#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STW Hub — Background alert notification service.
Runs as an Android service via python-for-android.
Fires a daily notification at the user-configured hour with V-Bucks alert count.
"""

import json
import time
import hashlib
from datetime import datetime, timezone
from pathlib import Path
import os

try:
    import requests
    _REQ_OK = True
except ImportError:
    _REQ_OK = False

# ── Constants (must match main.py) ────────────────────────────────────────────
_EPIC_CLIENT_ID     = "ec684b8c687f479fadea3cb2ad83f5c6"
_EPIC_CLIENT_SECRET = "e1f31c211f28413186262d37a13fc84d"
_EPIC_TOKEN_URL     = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token"
_EPIC_WORLD_URL     = "https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/world/info"
_VBUCKS_TYPE        = "AccountResource:currency_mtxswap"

DATA_DIR   = Path(os.environ.get("APPDATA", Path.home())) / "STWHub"
PREFS_FILE = DATA_DIR / "prefs.json"

NOTIF_TITLE = "STW Hub — Alertas del dia"
NOTIF_ID    = 1001
CHANNEL_ID  = "stwhub_daily"

# ── Android notification helper ───────────────────────────────────────────────
def _send_android_notification(title: str, body: str):
    try:
        from jnius import autoclass
        PythonActivity      = autoclass("org.kivy.android.PythonActivity")
        NotificationBuilder = autoclass("androidx.core.app.NotificationCompat$Builder")
        NotificationManager = autoclass("android.app.NotificationManager")
        NotificationChannel = autoclass("android.app.NotificationChannel")
        Context             = autoclass("android.content.Context")

        ctx = PythonActivity.mActivity
        nm  = ctx.getSystemService(Context.NOTIFICATION_SERVICE)

        # Create channel once
        channel = NotificationChannel(
            CHANNEL_ID, "STW Hub Daily Alerts",
            NotificationManager.IMPORTANCE_DEFAULT,
        )
        nm.createNotificationChannel(channel)

        notif = (
            NotificationBuilder(ctx, CHANNEL_ID)
            .setSmallIcon(ctx.getApplicationInfo().icon)
            .setContentTitle(title)
            .setContentText(body)
            .setAutoCancel(True)
            .build()
        )
        nm.notify(NOTIF_ID, notif)
    except Exception:
        pass

# ── Epic token ────────────────────────────────────────────────────────────────
def _epic_token():
    if not _REQ_OK:
        return None
    try:
        import base64
        creds = base64.b64encode(
            f"{_EPIC_CLIENT_ID}:{_EPIC_CLIENT_SECRET}".encode()
        ).decode()
        r = requests.post(
            _EPIC_TOKEN_URL,
            headers={"Authorization": f"Basic {creds}",
                     "Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "client_credentials"},
            timeout=10,
        )
        return r.json().get("access_token") if r.status_code == 200 else None
    except Exception:
        return None

# ── Fetch V-Bucks alert count ─────────────────────────────────────────────────
def _count_vbucks_alerts(region: str) -> int:
    token = _epic_token()
    if not token:
        return 0
    try:
        r = requests.get(
            _EPIC_WORLD_URL,
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        if r.status_code != 200:
            return 0
        count = 0
        for m in r.json().get("missions", []):
            for alert in m.get("missionAlert", {}).get("availableAlerts", []):
                for rw in alert.get("missionAlertRewards", {}).get("items", []):
                    if _VBUCKS_TYPE in rw.get("itemType", ""):
                        count += 1
                        break
        return count
    except Exception:
        return 0

# ── Load prefs ────────────────────────────────────────────────────────────────
def _load_prefs() -> dict:
    try:
        return json.loads(PREFS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

# ── Service main loop ─────────────────────────────────────────────────────────
def service_main():
    last_date = ""
    while True:
        prefs       = _load_prefs()
        notif_hour  = int(prefs.get("notif_hour", 8))
        region      = prefs.get("region", "NAE")
        lang        = prefs.get("lang", "es")

        now = datetime.now(timezone.utc)
        today = now.strftime("%Y-%m-%d")

        if now.hour == notif_hour and today != last_date:
            count = _count_vbucks_alerts(region)
            if lang == "es":
                body = (f"{count} misiones con V-Bucks disponibles hoy en {region}."
                        if count else "Abre STW Hub para ver las alertas del dia.")
            else:
                body = (f"{count} V-Bucks missions available today in {region}."
                        if count else "Open STW Hub to see today's alerts.")
            _send_android_notification(NOTIF_TITLE, body)
            last_date = today

        time.sleep(60)


if __name__ == "__main__":
    service_main()
