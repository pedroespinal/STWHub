[app]

# ─── App identity ──────────────────────────────────────────────────────────────
title           = STW Hub
package.name    = stwhub
package.domain  = com.pedroespinal

source.dir      = .
source.include_exts = py,png,jpg,kv,atlas,json

version         = 1.1.0

# ─── Entry point ──────────────────────────────────────────────────────────────
source.main     = main.py

# ─── Dependencies ─────────────────────────────────────────────────────────────
requirements = python3,kivy==2.3.0,requests,certifi,plyer,pyjnius

# ─── UI orientation ───────────────────────────────────────────────────────────
orientation = portrait

# ─── Icons & splash ───────────────────────────────────────────────────────────
icon.filename        = %(source.dir)s/assets/icon.png
presplash.filename   = %(source.dir)s/assets/presplash.png

android.presplash_color = #07071a

# ─── Android settings ─────────────────────────────────────────────────────────
android.permissions     = INTERNET,RECEIVE_BOOT_COMPLETED,SCHEDULE_EXACT_ALARM,USE_EXACT_ALARM,POST_NOTIFICATIONS
android.api             = 33
android.minapi          = 24
android.ndk             = 25b
android.sdk             = 33
android.private_storage = True
android.accept_sdk_license = True
android.services = AlertChecker:service/alert_checker.py:foreground

# ─── Build settings ───────────────────────────────────────────────────────────
[buildozer]
log_level = 2
warn_on_root = 1
