#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STW Hub v1.1.0 — Fortnite: Save The World Hub
Creado por: Pedro Espinal  Todos los derechos reservados (c) 2026
"""

import flet as ft
import json
import os
import hashlib
import threading
import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

try:
    import requests
    _REQ_OK = True
except ImportError:
    _REQ_OK = False

# ── App constants ─────────────────────────────────────────────────────────────
APP_NAME    = "STW Hub"
APP_VERSION = "1.1.0"
APP_AUTHOR  = "Pedro Espinal"
APP_RIGHTS  = "Todos los derechos reservados"
APP_YEAR    = str(date.today().year)
COPYRIGHT   = f"Creado por: {APP_AUTHOR}   ·   {APP_RIGHTS}   ©{APP_YEAR}"

DATA_DIR    = Path(os.environ.get("APPDATA", Path.home())) / "STWHub"
PREFS_FILE  = DATA_DIR / "prefs.json"
CACHE_FILE  = DATA_DIR / "cache.json"
DB_FILE     = DATA_DIR / "stwhub.db"

GITHUB_REPO     = "pedroespinal/STWHub"
GITHUB_API      = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
GITHUB_RELEASES = f"https://github.com/{GITHUB_REPO}/releases/latest"

# ── Authorship fingerprint ────────────────────────────────────────────────────
_GENESIS_COMMIT = "stwhub-genesis-20260521"
_GENESIS_DATE   = "2026-05-21T00:00:00"
_GENESIS_AUTHOR = "Pedro Espinal"
_GENESIS_APP    = "STW Hub"
_GENESIS_SEAL   = "bdeedb31e7c0e361f24a71fa9f7a14eb584d1d867bbd0f36e5b755b122166aff"

def _verify_genesis() -> bool:
    data = f"{_GENESIS_COMMIT}|{_GENESIS_DATE}|{_GENESIS_AUTHOR}|{_GENESIS_APP}"
    return hashlib.sha256(data.encode("utf-8")).hexdigest() == _GENESIS_SEAL

# ── Epic Games API (public client credentials) ────────────────────────────────
_EPIC_CLIENT_ID     = "ec684b8c687f479fadea3cb2ad83f5c6"
_EPIC_CLIENT_SECRET = "e1f31c211f28413186262d37a13fc84d"
_EPIC_TOKEN_URL     = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token"
_EPIC_WORLD_URL     = "https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/world/info"
_NEWS_URL           = "https://fortnite-api.com/v2/news/stw"

_VBUCKS_TYPE = "AccountResource:currency_mtxswap"
_REGIONS     = ["NAE", "NAW", "EU", "BR", "OC", "AS"]

# ── Meta builds data ─────────────────────────────────────────────────────────
BUILDS = {
    "Constructor": [
        {
            "name": "BASE Constructor / BASE Constructora",
            "hero": "BASE Kyle / Megabase Kyle",
            "skills": ["B.A.S.E.", "Plasma Pulse", "Bull Rush", "Decoy"],
            "desc_es": "Potencia tus estructuras con la B.A.S.E. y protege con Señuelo. Ideal para defender el objetivo.",
            "desc_en": "Boost structures with B.A.S.E. and protect with Decoy. Ideal for defending the objective.",
        },
        {
            "name": "Tank Constructor / Constructor Tanque",
            "hero": "Penny / Sentinel",
            "skills": ["Kinetic Overload", "Shockwave", "Bull Rush", "Plasma Pulse"],
            "desc_es": "Alta resistencia y control de masas. Perfecto para zonas de alta densidad de husks.",
            "desc_en": "High durability and crowd control. Perfect for high husk density zones.",
        },
    ],
    "Ninja": [
        {
            "name": "Melee Ninja / Ninja Cuerpo a Cuerpo",
            "hero": "Dragon Scorch / Dim Mak Mari",
            "skills": ["Dragon Slash", "Smoke Bomb", "Shadow Stance", "Crescent Kick"],
            "desc_es": "Velocidad y daño extremo cuerpo a cuerpo. Muy eficaz en misiones de olas cortas.",
            "desc_en": "Speed and extreme melee damage. Very effective in short wave missions.",
        },
        {
            "name": "Ranged Ninja / Ninja a Distancia",
            "hero": "Brawler Kyle / Autumn Queen",
            "skills": ["Throwing Stars", "Smoke Bomb", "Crescent Kick", "Shadow Stance"],
            "desc_es": "Movilidad con daño a distancia. Ideal para kiting y misiones de eliminación.",
            "desc_en": "Mobility with ranged damage. Ideal for kiting and elimination missions.",
        },
    ],
    "Outlander": [
        {
            "name": "TEDDY Outlander / Explorador TEDDY",
            "hero": "Phase Scout Jess / Enforcer Grizzly",
            "skills": ["T.E.D.D.Y.", "Anti-Material Charge", "Seismic Smash", "In the Zone"],
            "desc_es": "TEDDY hace el trabajo pesado. Perfecto para misiones de recoleccion y defensa.",
            "desc_en": "TEDDY does the heavy lifting. Perfect for collection and defense missions.",
        },
        {
            "name": "Support Outlander / Explorador Soporte",
            "hero": "Ranger Deadeye / Pathfinder Jess",
            "skills": ["Anti-Material Charge", "In the Zone", "T.E.D.D.Y.", "Seismic Smash"],
            "desc_es": "Soporte al equipo con recursos y control de area. Excelente en grupos.",
            "desc_en": "Team support with resources and area control. Excellent in groups.",
        },
    ],
    "Soldier": [
        {
            "name": "Gunslinger / Pistolero",
            "hero": "Raider Headhunter / Commando Ramirez",
            "skills": ["Frag Grenade", "Lefty and Righty", "War Cry", "Goin Commando"],
            "desc_es": "Maximo DPS con armas de fuego. El mejor para misiones de eliminacion rapida.",
            "desc_en": "Maximum DPS with firearms. The best for quick elimination missions.",
        },
        {
            "name": "Support Soldier / Soldado Soporte",
            "hero": "Urban Assault Headhunter / Sergeant Jonesy",
            "skills": ["War Cry", "Frag Grenade", "Goin Commando", "Shockwave"],
            "desc_es": "Potencia a todo el equipo con War Cry. Imprescindible en partidas de grupo.",
            "desc_en": "Powers the whole team with War Cry. Essential in group matches.",
        },
    ],
}

HERO_CLASSES = ["all", "Constructor", "Ninja", "Outlander", "Soldier"]

# ── Trap loadouts ─────────────────────────────────────────────────────────────
TRAP_LOADOUTS = {
    "Ride the Lightning": {
        "es": {
            "desc": "Mision de tren: coloca trampas a lo largo del camino del tren para eliminar husks en movimiento.",
            "traps": [
                ("Ceiling Electric Field", "Daño electrico continuo a husks bajo el techo del tunel."),
                ("Wall Dynamo", "Electrocuta y paraliza husks contra la pared lateral."),
                ("Wooden Floor Spike", "Daño pasivo a husks que caminan sobre el suelo."),
                ("Launcher Pad", "Lanza husks fuera del camino del objetivo."),
            ],
        },
        "en": {
            "desc": "Train mission: place traps along the train path to eliminate husks on the move.",
            "traps": [
                ("Ceiling Electric Field", "Continuous electric damage to husks under the tunnel ceiling."),
                ("Wall Dynamo", "Electrocutes and stuns husks against the side wall."),
                ("Wooden Floor Spike", "Passive damage to husks walking on the floor."),
                ("Launcher Pad", "Launches husks off the objective path."),
            ],
        },
    },
    "Retrieve the Data": {
        "es": {
            "desc": "Defiende el dron hasta que cargue. Crea un embudo de trampas en las entradas principales.",
            "traps": [
                ("Wall Launcher", "Empuja husks de vuelta al area de trampas."),
                ("Gas Trap", "Daño de veneno en area, perfecto para grupos densos."),
                ("Ceiling Electric Field", "Cobertura aerea constante sobre el dron."),
                ("Freeze Trap", "Ralentiza husks permitiendo mas tiempo de daño."),
            ],
        },
        "en": {
            "desc": "Defend the drone while it charges. Create a trap funnel at the main entrances.",
            "traps": [
                ("Wall Launcher", "Pushes husks back into the trap area."),
                ("Gas Trap", "Area poison damage, perfect for dense groups."),
                ("Ceiling Electric Field", "Constant aerial coverage above the drone."),
                ("Freeze Trap", "Slows husks allowing more damage time."),
            ],
        },
    },
    "Shelter Evacuation": {
        "es": {
            "desc": "Escolta a los supervivientes. Asegura el camino con trampas de slow y retroceso.",
            "traps": [
                ("Freeze Trap", "Ralentiza grupos de husks que bloquean la ruta."),
                ("Wall Dynamo", "Elimina husks pegados a las paredes del pasillo."),
                ("Wooden Floor Spike", "Daño continuo en el camino de los supervivientes."),
                ("Ceiling Zapper", "Daño rapido para grupos pequenos en espacios cerrados."),
            ],
        },
        "en": {
            "desc": "Escort survivors. Secure the path with slow and knockback traps.",
            "traps": [
                ("Freeze Trap", "Slows husk groups blocking the route."),
                ("Wall Dynamo", "Eliminates husks stuck to corridor walls."),
                ("Wooden Floor Spike", "Continuous damage on the survivor path."),
                ("Ceiling Zapper", "Quick damage for small groups in enclosed spaces."),
            ],
        },
    },
    "Destroy the Storm King": {
        "es": {
            "desc": "Fase de minions: usa trampas de alto DPS. En la fase de orbes, movilidad total.",
            "traps": [
                ("Gas Trap", "Maximo DPS contra los minions del Storm King."),
                ("Ceiling Electric Field", "Cubre amplias areas durante las oleadas."),
                ("Wall Launcher", "Separa grupos de minions para facil eliminacion."),
                ("Launcher Pad", "Movilidad rapida entre zonas del Storm King."),
            ],
        },
        "en": {
            "desc": "Minion phase: use high DPS traps. In the orb phase, full mobility.",
            "traps": [
                ("Gas Trap", "Maximum DPS against Storm King minions."),
                ("Ceiling Electric Field", "Covers large areas during waves."),
                ("Wall Launcher", "Separates minion groups for easy elimination."),
                ("Launcher Pad", "Quick mobility between Storm King zones."),
            ],
        },
    },
    "Zone Catalogue": {
        "es": {
            "desc": "Defiende multiples zonas. Distribuye trampas eficientemente por cada punto de defensa.",
            "traps": [
                ("Gas Trap", "Cobertura de area maxima por trampa colocada."),
                ("Ceiling Electric Field", "Ideal para cubrir entradas amplias."),
                ("Freeze Trap", "Compra tiempo mientras te mueves entre zonas."),
                ("Wooden Floor Spike", "Defensa pasiva en zonas sin jugador activo."),
            ],
        },
        "en": {
            "desc": "Defend multiple zones. Efficiently distribute traps across each defense point.",
            "traps": [
                ("Gas Trap", "Maximum area coverage per placed trap."),
                ("Ceiling Electric Field", "Ideal for covering wide entrances."),
                ("Freeze Trap", "Buys time while moving between zones."),
                ("Wooden Floor Spike", "Passive defense in zones without an active player."),
            ],
        },
    },
}

# ── Translations ──────────────────────────────────────────────────────────────
T = {
    "es": {
        "home": "Inicio", "builds": "Builds", "news": "Noticias",
        "guide": "Guia", "settings": "Config",
        "daily_alerts": "Alertas Diarias", "refresh": "Actualizar",
        "vbucks_only": "Solo V-Bucks", "region": "Region",
        "loading": "Cargando...", "no_alerts": "Sin alertas disponibles.",
        "no_news": "Sin noticias disponibles.", "news_tab": "Noticias STW",
        "meta_builds": "Meta Builds", "my_builds": "Mis Builds",
        "traps": "Trampas",
        "class_filter": "Clase", "skills": "Habilidades",
        "guide_title": "Guia Completa STW",
        "settings_title": "Configuracion",
        "theme": "Tema", "dark": "Oscuro", "light": "Claro",
        "language": "Idioma", "spanish": "Espanol", "english": "English",
        "about": "Acerca de",
        "genesis_valid": "Firma digital valida",
        "genesis_invalid": "FIRMA INVALIDA",
        "created_by": "Creado por", "rights": "Todos los derechos reservados",
        "region_lbl": "Region de alertas",
        "notif_hour": "Hora de notificacion diaria (0-23h)",
        "save_settings": "Guardar ajustes",
        "check_update": "Buscar actualizacion",
        "update_available": "Nueva version disponible",
        "up_to_date": "Aplicacion al dia",
        "download": "Descargar",
        "dismiss": "Ignorar",
        "new_build": "Nuevo Build",
        "build_name": "Nombre del build",
        "build_class": "Clase de heroe",
        "build_hero": "Heroe principal",
        "build_skills": "Habilidades (separadas por coma)",
        "build_desc": "Descripcion (opcional)",
        "save": "Guardar",
        "cancel": "Cancelar",
        "edit": "Editar",
        "delete": "Eliminar",
        "no_my_builds": "No tienes builds guardados.\nPresiona + para crear uno.",
        "utc_reset": "Reset UTC en",
        "trap_loadouts": "Cargas de Trampas",
        "mission_type": "Tipo de mision",
        "recommended_traps": "Trampas recomendadas",
        "alerts_cached": "Usando cache offline",
        "error_api": "Error al conectar con la API.",
    },
    "en": {
        "home": "Home", "builds": "Builds", "news": "News",
        "guide": "Guide", "settings": "Settings",
        "daily_alerts": "Daily Alerts", "refresh": "Refresh",
        "vbucks_only": "V-Bucks Only", "region": "Region",
        "loading": "Loading...", "no_alerts": "No alerts available.",
        "no_news": "No news available.", "news_tab": "STW News",
        "meta_builds": "Meta Builds", "my_builds": "My Builds",
        "traps": "Traps",
        "class_filter": "Class", "skills": "Skills",
        "guide_title": "Full STW Guide",
        "settings_title": "Settings",
        "theme": "Theme", "dark": "Dark", "light": "Light",
        "language": "Language", "spanish": "Espanol", "english": "English",
        "about": "About",
        "genesis_valid": "Valid digital signature",
        "genesis_invalid": "INVALID SIGNATURE",
        "created_by": "Created by", "rights": "All rights reserved",
        "region_lbl": "Alert region",
        "notif_hour": "Daily notification hour (0-23h)",
        "save_settings": "Save settings",
        "check_update": "Check for update",
        "update_available": "New version available",
        "up_to_date": "App is up to date",
        "download": "Download",
        "dismiss": "Dismiss",
        "new_build": "New Build",
        "build_name": "Build name",
        "build_class": "Hero class",
        "build_hero": "Main hero",
        "build_skills": "Skills (comma-separated)",
        "build_desc": "Description (optional)",
        "save": "Save",
        "cancel": "Cancel",
        "edit": "Edit",
        "delete": "Delete",
        "no_my_builds": "No saved builds yet.\nTap + to create one.",
        "utc_reset": "UTC reset in",
        "trap_loadouts": "Trap Loadouts",
        "mission_type": "Mission type",
        "recommended_traps": "Recommended traps",
        "alerts_cached": "Using offline cache",
        "error_api": "Error connecting to the API.",
    },
}

# ── Guide sections ────────────────────────────────────────────────────────────
GUIDE = {
    "es": [
        ("Que es STW?", "Fortnite: Save The World es el modo PvE cooperativo de Fortnite donde hasta 4 jugadores defienden objetivos contra oleadas de husks (zombies). El objetivo principal es recolectar recursos, construir fortines y completar misiones para avanzar en la historia y ganar recompensas."),
        ("V-Bucks gratuitos", "Completa misiones de alerta con el icono de V-Bucks cada dia. Las misiones de alerta se reinician a las 00:00 UTC. Filtra por 'Solo V-Bucks' en la pantalla de inicio para verlas todas rapidamente."),
        ("Clases de heroes", "Constructor: Especialista en estructuras y B.A.S.E.\nNinja: Velocidad y daño cuerpo a cuerpo.\nExplorador (Outlander): Recoleccion de recursos y TEDDY.\nSoldado: DPS a distancia y War Cry para el equipo."),
        ("Sistema de zonas", "El mapa del mundo esta dividido en zonas de diferente nivel de dificultad. Desbloquea zonas completando misiones de historia. Las alertas aparecen en zonas ya desbloqueadas con recompensas extra."),
        ("Regiones de servidores", "NAE: Este de NA | NAW: Oeste de NA | EU: Europa | BR: Brasil | OC: Oceania | AS: Asia. Elige la region mas cercana para menos latencia. Las alertas pueden variar por region."),
        ("Construccion y trampas", "Construye muros, suelos, techo y rampas con materiales recolectados. Las trampas se colocan en estructuras construidas. Usa el modo de edicion para crear embudos que guien a los husks hacia tus trampas."),
        ("Mision de Storm King", "El Storm King es el jefe final. Destruye los puntos brillantes (orbes) en sus hombros y caderas. Cuando cae, aparecen minions: usa War Cry y TEDDY. La fase final requiere dano masivo coordinado al corazon."),
        ("Consejos para nuevos jugadores", "1. Completa la historia principal primero para desbloquear el mapa completo.\n2. No destruyas estructuras del mapa sin necesidad.\n3. Construye antes del inicio de la oleada.\n4. Comunicate con tu equipo para dividir roles.\n5. Usa el filtro de V-Bucks diariamente para maximizar recompensas."),
    ],
    "en": [
        ("What is STW?", "Fortnite: Save The World is the cooperative PvE mode of Fortnite where up to 4 players defend objectives against waves of husks (zombies). The main goal is to collect resources, build forts, and complete missions to advance the story and earn rewards."),
        ("Free V-Bucks", "Complete alert missions with the V-Bucks icon each day. Alert missions reset at 00:00 UTC. Filter by 'V-Bucks Only' on the home screen to see them all quickly."),
        ("Hero Classes", "Constructor: Structures and B.A.S.E. specialist.\nNinja: Speed and melee damage.\nOutlander: Resource collection and TEDDY.\nSoldier: Ranged DPS and War Cry for the team."),
        ("Zone System", "The world map is divided into zones of different difficulty. Unlock zones by completing story missions. Alerts appear in already unlocked zones with extra rewards."),
        ("Server Regions", "NAE: North America East | NAW: North America West | EU: Europe | BR: Brazil | OC: Oceania | AS: Asia. Choose the closest region for lower latency. Alerts can vary by region."),
        ("Building & Traps", "Build walls, floors, ceilings, and ramps with collected materials. Traps are placed on built structures. Use edit mode to create funnels that guide husks toward your traps."),
        ("Storm King Mission", "The Storm King is the final boss. Destroy the glowing points (orbs) on its shoulders and hips. When it falls, minions appear: use War Cry and TEDDY. The final phase requires massive coordinated damage to the heart."),
        ("Tips for New Players", "1. Complete the main story first to unlock the full map.\n2. Don't destroy map structures unnecessarily.\n3. Build before the wave starts.\n4. Communicate with your team to split roles.\n5. Use the V-Bucks filter daily to maximize rewards."),
    ],
}

# ── Theme palettes ────────────────────────────────────────────────────────────
_DARK = {
    "bg":       "#07071a",
    "surface":  "#0d0d2b",
    "card":     "#12123a",
    "border":   "#1e1e5a",
    "text":     "#e8e8ff",
    "sub":      "#9090c0",
    "orange":   "#ff6d00",
    "cyan":     "#00e5ff",
    "yellow":   "#ffd700",
    "purple":   "#7c3aed",
    "green":    "#00e676",
    "red":      "#ff1744",
    "footer":   "#ff8800",
    "nav_sel":  "#ff6d00",
    "banner":   "#1a0a00",
}
_LIGHT = {
    "bg":       "#f0f0f8",
    "surface":  "#e8e8f5",
    "card":     "#ffffff",
    "border":   "#ccccee",
    "text":     "#111133",
    "sub":      "#444466",
    "orange":   "#cc4400",
    "cyan":     "#007acc",
    "yellow":   "#a07000",
    "purple":   "#5b21b6",
    "green":    "#007a33",
    "red":      "#c00020",
    "footer":   "#cc5500",
    "nav_sel":  "#cc4400",
    "banner":   "#fff3e0",
}
THEME = ["dark"]
LANG  = ["es"]

def _c(key: str) -> str:
    return (_DARK if THEME[0] == "dark" else _LIGHT)[key]

def t(key: str) -> str:
    return T[LANG[0]].get(key, key)

# ── Prefs I/O ─────────────────────────────────────────────────────────────────
def _load_prefs() -> dict:
    try:
        return json.loads(PREFS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _save_prefs(p: dict):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PREFS_FILE.write_text(json.dumps(p, ensure_ascii=False, indent=2), encoding="utf-8")

# ── Cache I/O ─────────────────────────────────────────────────────────────────
def _load_cache() -> dict:
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _save_cache(c: dict):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(c, ensure_ascii=False), encoding="utf-8")

# ── SQLite — My Builds ────────────────────────────────────────────────────────
def _init_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_FILE) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS my_builds (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                name    TEXT NOT NULL,
                cls     TEXT NOT NULL,
                hero    TEXT NOT NULL DEFAULT '',
                skills  TEXT NOT NULL DEFAULT '[]',
                desc    TEXT NOT NULL DEFAULT '',
                created TEXT NOT NULL DEFAULT ''
            )
        """)
        con.commit()

def _db_get_my_builds() -> list:
    try:
        with sqlite3.connect(DB_FILE) as con:
            con.row_factory = sqlite3.Row
            rows = con.execute("SELECT * FROM my_builds ORDER BY id DESC").fetchall()
            return [dict(r) for r in rows]
    except Exception:
        return []

def _db_get_build(bid: int) -> dict | None:
    try:
        with sqlite3.connect(DB_FILE) as con:
            con.row_factory = sqlite3.Row
            row = con.execute("SELECT * FROM my_builds WHERE id=?", (bid,)).fetchone()
            return dict(row) if row else None
    except Exception:
        return None

def _db_save_build(b: dict) -> int:
    with sqlite3.connect(DB_FILE) as con:
        cur = con.execute(
            "INSERT INTO my_builds (name,cls,hero,skills,desc,created) VALUES (?,?,?,?,?,?)",
            (b["name"], b["cls"], b.get("hero",""), json.dumps(b.get("skills",[])),
             b.get("desc",""), datetime.now().strftime("%Y-%m-%d %H:%M")),
        )
        con.commit()
        return cur.lastrowid

def _db_update_build(bid: int, b: dict):
    with sqlite3.connect(DB_FILE) as con:
        con.execute(
            "UPDATE my_builds SET name=?,cls=?,hero=?,skills=?,desc=? WHERE id=?",
            (b["name"], b["cls"], b.get("hero",""), json.dumps(b.get("skills",[])),
             b.get("desc",""), bid),
        )
        con.commit()

def _db_delete_build(bid: int):
    with sqlite3.connect(DB_FILE) as con:
        con.execute("DELETE FROM my_builds WHERE id=?", (bid,))
        con.commit()

# ── GitHub update checker ─────────────────────────────────────────────────────
def _check_github_update() -> dict | None:
    if not _REQ_OK:
        return None
    try:
        r = requests.get(GITHUB_API, timeout=6,
                         headers={"Accept": "application/vnd.github+json"})
        if r.status_code != 200:
            return None
        data = r.json()
        latest = data.get("tag_name", "").lstrip("v")
        if latest and latest != APP_VERSION:
            return {"version": latest, "url": GITHUB_RELEASES,
                    "notes": data.get("body", "")[:200]}
        return None
    except Exception:
        return None

# ── UTC daily reset countdown ─────────────────────────────────────────────────
def _utc_reset_str() -> str:
    now = datetime.now(timezone.utc)
    nxt = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    diff = nxt - now
    h, rem = divmod(int(diff.total_seconds()), 3600)
    m, s   = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

# ── Android background notification ───────────────────────────────────────────
def _schedule_notification_if_android(hour: int):
    try:
        from jnius import autoclass
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Context         = autoclass("android.content.Context")
        AlarmManager    = autoclass("android.app.AlarmManager")
        Intent          = autoclass("android.content.Intent")
        PendingIntent   = autoclass("android.app.PendingIntent")
        Calendar        = autoclass("java.util.Calendar")

        ctx = PythonActivity.mActivity
        am  = ctx.getSystemService(Context.ALARM_SERVICE)

        intent = Intent(ctx, PythonActivity)
        intent.setAction("com.pedroespinal.stwhub.DAILY_ALERT")
        pi = PendingIntent.getBroadcast(ctx, 0, intent,
                                        PendingIntent.FLAG_UPDATE_CURRENT | 0x02000000)

        cal = Calendar.getInstance()
        cal.set(Calendar.HOUR_OF_DAY, hour)
        cal.set(Calendar.MINUTE, 0)
        cal.set(Calendar.SECOND, 0)
        if cal.getTimeInMillis() < Calendar.getInstance().getTimeInMillis():
            cal.add(Calendar.DAY_OF_YEAR, 1)

        am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, cal.getTimeInMillis(), pi)
    except Exception:
        pass

# ── Epic Games API helpers ────────────────────────────────────────────────────
def _epic_token() -> str | None:
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

def _fetch_alerts(region: str) -> list:
    token = _epic_token()
    if not token:
        return []
    try:
        r = requests.get(
            _EPIC_WORLD_URL,
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        if r.status_code != 200:
            return []
        theatres = r.json().get("theaters", [])
        missions  = r.json().get("missions", [])
        alerts = []
        for m in missions:
            if m.get("theaterId", "").upper().find(region) == -1:
                if region != "NAE" or "Stonewood" not in m.get("theaterId", ""):
                    pass
            for alert in m.get("missionAlert", {}).get("availableAlerts", []):
                rewards = []
                for r2 in alert.get("missionAlertRewards", {}).get("items", []):
                    rewards.append({
                        "type": r2.get("itemType", ""),
                        "quantity": r2.get("quantity", 0),
                    })
                if rewards:
                    alerts.append({
                        "name": m.get("missionType", {}).get("missionType", "Mission"),
                        "zone": m.get("theaterId", ""),
                        "rewards": rewards,
                        "vbucks": any(_VBUCKS_TYPE in rw["type"] for rw in rewards),
                    })
        return alerts
    except Exception:
        return []

def _fetch_news() -> list:
    if not _REQ_OK:
        return []
    try:
        r = requests.get(_NEWS_URL, timeout=10)
        if r.status_code != 200:
            return []
        items = r.json().get("data", {}).get("motds", [])
        return [{"title": i.get("title",""), "body": i.get("body","")} for i in items[:8]]
    except Exception:
        return []

# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════
def main(page: ft.Page):
    _init_db()

    # ── Load prefs ────────────────────────────────────────────────────────────
    prefs = _load_prefs()
    if prefs.get("theme"):
        THEME[0] = prefs["theme"]
    if prefs.get("lang"):
        LANG[0] = prefs["lang"]

    state = {
        "screen":           "home",
        "vbucks_only":      False,
        "region":           prefs.get("region", "NAE"),
        "notif_hour":       prefs.get("notif_hour", 8),
        "alerts":           [],
        "news":             [],
        "my_builds":        _db_get_my_builds(),
        "builds_cls":       "all",
        "builds_tab":       "meta",
        "trap_mission":     list(TRAP_LOADOUTS.keys())[0],
        "last_refresh":     "",
        "loading":          False,
        "news_loading":     False,
        "update_info":      None,
        "update_dismissed": False,
        "edit_build_id":    None,
        "using_cache":      False,
    }

    # ── Page setup ────────────────────────────────────────────────────────────
    def _apply_theme():
        page.bgcolor            = _c("bg")
        page.navigation_bar.bgcolor = _c("surface") if page.navigation_bar else None

    page.title          = f"{APP_NAME} v{APP_VERSION}"
    page.bgcolor        = _c("bg")
    page.padding        = 0
    page.window_width   = 400
    page.window_height  = 800

    # ── UI helpers ────────────────────────────────────────────────────────────
    def _card(*children, padding=12, margin=6):
        return ft.Container(
            content=ft.Column(list(children), spacing=6, tight=True),
            bgcolor=_c("card"),
            border=ft.border.all(1, _c("border")),
            border_radius=10,
            padding=padding,
            margin=margin,
        )

    def _btn(label, on_click, color=None, width=None, icon=None):
        return ft.ElevatedButton(
            text=label,
            icon=icon,
            on_click=on_click,
            color="#ffffff",
            bgcolor=color or _c("orange"),
            width=width,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        )

    def _toggle_btn(label, active: bool, on_click):
        return ft.OutlinedButton(
            text=label,
            on_click=on_click,
            style=ft.ButtonStyle(
                color=_c("orange") if active else _c("sub"),
                side=ft.BorderSide(2 if active else 1,
                                   _c("orange") if active else _c("border")),
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

    def _chip(label, active: bool, on_click):
        return ft.FilterChip(
            label=ft.Text(label, size=12),
            selected=active,
            on_select=on_click,
            selected_color=_c("orange"),
            check_color="#ffffff",
        )

    def _hdr(text, size=18, color=None):
        return ft.Text(text, size=size, weight=ft.FontWeight.BOLD,
                       color=color or _c("orange"))

    def _sub(text, size=13):
        return ft.Text(text, size=size, color=_c("sub"))

    def _txt(text, size=14, color=None):
        return ft.Text(text, size=size, color=color or _c("text"))

    def _footer():
        return ft.Container(
            content=ft.Text(COPYRIGHT, size=10, color=_c("footer"),
                            text_align=ft.TextAlign.CENTER),
            padding=ft.padding.symmetric(vertical=6),
            alignment=ft.alignment.center,
        )

    def _divider():
        return ft.Divider(height=1, color=_c("border"))

    # ── Navigation ────────────────────────────────────────────────────────────
    TAB_ORDER = ["home", "builds", "news", "guide", "settings"]

    def navigate(screen: str):
        state["screen"] = screen
        idx = TAB_ORDER.index(screen) if screen in TAB_ORDER else 0
        page.navigation_bar.selected_index = idx
        render()

    def _nav_bar():
        icons = [
            ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED,
                                        selected_icon=ft.Icons.HOME, label=t("home")),
            ft.NavigationBarDestination(icon=ft.Icons.CONSTRUCTION_OUTLINED,
                                        selected_icon=ft.Icons.CONSTRUCTION, label=t("builds")),
            ft.NavigationBarDestination(icon=ft.Icons.ARTICLE_OUTLINED,
                                        selected_icon=ft.Icons.ARTICLE, label=t("news")),
            ft.NavigationBarDestination(icon=ft.Icons.MENU_BOOK_OUTLINED,
                                        selected_icon=ft.Icons.MENU_BOOK, label=t("guide")),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS_OUTLINED,
                                        selected_icon=ft.Icons.SETTINGS, label=t("settings")),
        ]
        cur = TAB_ORDER.index(state["screen"]) if state["screen"] in TAB_ORDER else 0

        def on_nav(e):
            navigate(TAB_ORDER[e.control.selected_index])

        return ft.NavigationBar(
            destinations=icons,
            selected_index=cur,
            on_change=on_nav,
            bgcolor=_c("surface"),
            indicator_color=_c("orange"),
        )

    def _appbar(title_txt: str):
        def flip_lang(e):
            LANG[0] = "en" if LANG[0] == "es" else "es"
            prefs["lang"] = LANG[0]
            _save_prefs(prefs)
            render()

        def toggle_theme(e):
            THEME[0] = "light" if THEME[0] == "dark" else "dark"
            prefs["theme"] = THEME[0]
            _save_prefs(prefs)
            render()

        return ft.AppBar(
            title=ft.Text(title_txt, size=16, weight=ft.FontWeight.BOLD,
                          color=_c("orange")),
            bgcolor=_c("surface"),
            actions=[
                ft.IconButton(icon=ft.Icons.TRANSLATE, tooltip="ES/EN",
                              icon_color=_c("cyan"), on_click=flip_lang),
                ft.IconButton(
                    icon=ft.Icons.DARK_MODE if THEME[0] == "dark" else ft.Icons.LIGHT_MODE,
                    tooltip=t("theme"), icon_color=_c("yellow"), on_click=toggle_theme),
            ],
        )

    # ── Alert loading ─────────────────────────────────────────────────────────
    def _load_alerts():
        state["loading"] = True
        state["using_cache"] = False
        render()
        alerts = _fetch_alerts(state["region"])
        if alerts:
            state["alerts"] = alerts
            state["last_refresh"] = datetime.now().strftime("%H:%M")
            _save_cache({"alerts": alerts, "region": state["region"],
                         "ts": state["last_refresh"]})
        else:
            cached = _load_cache()
            if cached.get("alerts"):
                state["alerts"] = cached["alerts"]
                state["using_cache"] = True
                state["last_refresh"] = cached.get("ts", "?")
        state["loading"] = False
        render()

    def _load_news():
        state["news_loading"] = True
        render()
        state["news"] = _fetch_news()
        state["news_loading"] = False
        render()

    def _bg_check_update():
        info = _check_github_update()
        if info:
            state["update_info"] = info
            state["update_dismissed"] = False
            render()

    # ── HOME screen ───────────────────────────────────────────────────────────
    def _screen_home():
        rows = []

        # Update banner
        if state["update_info"] and not state["update_dismissed"]:
            info = state["update_info"]
            def dismiss_update(e):
                state["update_dismissed"] = True
                render()
            def open_download(e):
                page.launch_url(info["url"])

            rows.append(ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.NEW_RELEASES, color=_c("yellow"), size=20),
                    ft.Column([
                        _txt(f"{t('update_available')}: v{info['version']}",
                             size=13, color=_c("yellow")),
                    ], expand=True, spacing=2),
                    _btn(t("download"), open_download, color=_c("green")),
                    ft.IconButton(ft.Icons.CLOSE, on_click=dismiss_update,
                                  icon_color=_c("sub"), icon_size=16),
                ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=_c("banner"),
                border=ft.border.all(1, _c("yellow")),
                border_radius=8,
                padding=8,
                margin=ft.margin.only(bottom=4),
            ))

        # Header row
        def do_refresh(e):
            threading.Thread(target=_load_alerts, daemon=True).start()

        def toggle_vbucks(e):
            state["vbucks_only"] = not state["vbucks_only"]
            render()

        vbucks_active = state["vbucks_only"]
        rows.append(ft.Row([
            _hdr(t("daily_alerts")),
            ft.Row([
                ft.Text(f"{t('utc_reset')}: {_utc_reset_str()}",
                        size=11, color=_c("cyan")),
            ], expand=True, main_alignment=ft.MainAxisAlignment.END),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN))

        # Controls row
        def on_region(e):
            state["region"] = e.control.value
            prefs["region"] = state["region"]
            _save_prefs(prefs)
            threading.Thread(target=_load_alerts, daemon=True).start()

        rows.append(ft.Row([
            _toggle_btn(t("vbucks_only"), vbucks_active, toggle_vbucks),
            ft.Dropdown(
                value=state["region"],
                options=[ft.dropdown.Option(r) for r in _REGIONS],
                on_change=on_region,
                width=100,
                text_size=13,
                border_color=_c("border"),
                color=_c("text"),
            ),
            _btn(t("refresh"), do_refresh, icon=ft.Icons.REFRESH),
        ], spacing=8, wrap=True))

        if state["using_cache"]:
            rows.append(_sub(f"({t('alerts_cached')} {state['last_refresh']})"))
        elif state["last_refresh"]:
            rows.append(_sub(f"({t('refresh')}: {state['last_refresh']})"))

        if state["loading"]:
            rows.append(ft.ProgressRing(width=32, height=32, stroke_width=3,
                                        color=_c("orange")))
        elif not state["alerts"]:
            rows.append(_card(_txt(t("no_alerts"), color=_c("sub"))))
        else:
            shown = [a for a in state["alerts"] if not vbucks_active or a.get("vbucks")]
            for a in shown[:30]:
                reward_chips = []
                for rw in a.get("rewards", []):
                    typ = rw["type"]
                    qty = rw["quantity"]
                    if _VBUCKS_TYPE in typ:
                        reward_chips.append(
                            ft.Container(
                                content=ft.Text(f"V-Bucks x{qty}", size=11,
                                                color="#000000",
                                                weight=ft.FontWeight.BOLD),
                                bgcolor=_c("yellow"), border_radius=6,
                                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                            )
                        )
                    else:
                        short = typ.split(":")[-1][:18]
                        reward_chips.append(
                            ft.Container(
                                content=ft.Text(f"{short} x{qty}", size=10,
                                                color=_c("sub")),
                                bgcolor=_c("surface"), border_radius=6,
                                border=ft.border.all(1, _c("border")),
                                padding=ft.padding.symmetric(horizontal=5, vertical=2),
                            )
                        )
                rows.append(_card(
                    ft.Row([
                        ft.Icon(ft.Icons.BOLT if a.get("vbucks") else ft.Icons.FLAG_OUTLINED,
                                color=_c("yellow") if a.get("vbucks") else _c("orange"),
                                size=18),
                        _txt(a.get("name",""), size=13, color=_c("text")),
                    ], spacing=6),
                    _sub(a.get("zone",""), size=11),
                    ft.Row(reward_chips, wrap=True, spacing=4),
                ))

        return ft.Column(rows, spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    # ── BUILDS screen ─────────────────────────────────────────────────────────
    def _screen_builds():
        rows = []

        # Sub-tab selector
        def set_btab(tab):
            def _h(e):
                state["builds_tab"] = tab
                render()
            return _h

        rows.append(ft.Row([
            _toggle_btn(t("meta_builds"), state["builds_tab"]=="meta", set_btab("meta")),
            _toggle_btn(t("my_builds"),   state["builds_tab"]=="my",   set_btab("my")),
            _toggle_btn(t("traps"),       state["builds_tab"]=="traps", set_btab("traps")),
        ], spacing=6, wrap=True))
        rows.append(_divider())

        if state["builds_tab"] == "meta":
            rows.extend(_builds_meta())
        elif state["builds_tab"] == "my":
            rows.extend(_builds_my())
        else:
            rows.extend(_builds_traps())

        return ft.Column(rows, spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    def _builds_meta():
        rows = []
        # Class filter chips
        def set_cls(cls):
            def _h(e):
                state["builds_cls"] = cls
                render()
            return _h

        rows.append(ft.Row(
            [_chip(c if c != "all" else ("Todas" if LANG[0]=="es" else "All"),
                   state["builds_cls"]==c, set_cls(c))
             for c in HERO_CLASSES],
            wrap=True, spacing=4,
        ))
        cls_filter = state["builds_cls"]
        for cls_name, blist in BUILDS.items():
            if cls_filter != "all" and cls_filter != cls_name:
                continue
            rows.append(_hdr(cls_name, size=15))
            for b in blist:
                desc = b["desc_es"] if LANG[0]=="es" else b["desc_en"]
                rows.append(_card(
                    _hdr(b["name"], size=14),
                    _sub(b["hero"], size=12),
                    ft.Wrap(
                        [ft.Container(
                            content=ft.Text(sk, size=11, color=_c("text")),
                            bgcolor=_c("surface"),
                            border=ft.border.all(1, _c("cyan")),
                            border_radius=6,
                            padding=ft.padding.symmetric(horizontal=6, vertical=2),
                         ) for sk in b["skills"]],
                        spacing=4, run_spacing=4,
                    ),
                    _txt(desc, size=12, color=_c("sub")),
                ))
        return rows

    def _builds_my():
        rows = []
        builds = _db_get_my_builds()
        state["my_builds"] = builds

        def go_create(e):
            state["screen"] = "build_create"
            state["edit_build_id"] = None
            render()

        rows.append(ft.Row([
            _hdr(t("my_builds")),
            _btn(t("new_build"), go_create, icon=ft.Icons.ADD),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN))

        if not builds:
            rows.append(_card(_txt(t("no_my_builds"), color=_c("sub"))))
            return rows

        for b in builds:
            skills = json.loads(b.get("skills","[]"))
            bid = b["id"]

            def go_edit(bid=bid):
                def _h(e):
                    state["screen"] = "build_edit"
                    state["edit_build_id"] = bid
                    render()
                return _h

            def do_delete(bid=bid):
                def _h(e):
                    _db_delete_build(bid)
                    state["my_builds"] = _db_get_my_builds()
                    render()
                return _h

            rows.append(_card(
                ft.Row([
                    ft.Column([
                        _hdr(b["name"], size=14),
                        _sub(f"{b['cls']}  ·  {b.get('hero','')}", size=12),
                    ], expand=True, spacing=2),
                    ft.Row([
                        ft.IconButton(ft.Icons.EDIT, on_click=go_edit(),
                                      icon_color=_c("cyan"), icon_size=18),
                        ft.IconButton(ft.Icons.DELETE, on_click=do_delete(),
                                      icon_color=_c("red"), icon_size=18),
                    ], spacing=0),
                ], vertical_alignment=ft.CrossAxisAlignment.START),
                ft.Wrap(
                    [ft.Container(
                        content=ft.Text(sk, size=11, color=_c("text")),
                        bgcolor=_c("surface"),
                        border=ft.border.all(1, _c("purple")),
                        border_radius=6,
                        padding=ft.padding.symmetric(horizontal=6, vertical=2),
                     ) for sk in skills],
                    spacing=4, run_spacing=4,
                ) if skills else ft.Text(""),
                _txt(b.get("desc",""), size=12, color=_c("sub")) if b.get("desc") else ft.Text(""),
                _sub(b.get("created",""), size=10),
            ))
        return rows

    def _builds_traps():
        rows = []
        missions = list(TRAP_LOADOUTS.keys())

        def set_mission(m):
            def _h(e):
                state["trap_mission"] = m
                render()
            return _h

        rows.append(ft.Row(
            [_chip(m, state["trap_mission"]==m, set_mission(m)) for m in missions],
            wrap=True, spacing=4,
        ))
        rows.append(_divider())

        mission = state["trap_mission"]
        data = TRAP_LOADOUTS[mission][LANG[0]]
        rows.append(_hdr(mission, size=15))
        rows.append(_txt(data["desc"], size=13, color=_c("sub")))
        for i, (trap_name, trap_desc) in enumerate(data["traps"], 1):
            rows.append(_card(
                ft.Row([
                    ft.Container(
                        content=ft.Text(str(i), size=13, weight=ft.FontWeight.BOLD,
                                        color="#000000"),
                        bgcolor=_c("orange"), width=26, height=26,
                        border_radius=13, alignment=ft.alignment.center,
                    ),
                    ft.Column([
                        _hdr(trap_name, size=13),
                        _txt(trap_desc, size=12, color=_c("sub")),
                    ], expand=True, spacing=2),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ))
        return rows

    # ── BUILD CREATE/EDIT screen ──────────────────────────────────────────────
    def _screen_build_form():
        is_edit = state["screen"] == "build_edit"
        existing = _db_get_build(state["edit_build_id"]) if is_edit else None
        existing_skills = json.loads(existing.get("skills","[]")) if existing else []

        name_field  = ft.TextField(label=t("build_name"),
                                   value=existing["name"] if existing else "",
                                   border_color=_c("border"), color=_c("text"),
                                   label_style=ft.TextStyle(color=_c("sub")))
        class_dd    = ft.Dropdown(
                          label=t("build_class"),
                          value=existing["cls"] if existing else list(BUILDS.keys())[0],
                          options=[ft.dropdown.Option(k) for k in BUILDS.keys()],
                          border_color=_c("border"), color=_c("text"),
                      )
        hero_field  = ft.TextField(label=t("build_hero"),
                                   value=existing.get("hero","") if existing else "",
                                   border_color=_c("border"), color=_c("text"),
                                   label_style=ft.TextStyle(color=_c("sub")))
        skills_field= ft.TextField(label=t("build_skills"),
                                   value=", ".join(existing_skills) if existing_skills else "",
                                   multiline=True, min_lines=2,
                                   border_color=_c("border"), color=_c("text"),
                                   label_style=ft.TextStyle(color=_c("sub")))
        desc_field  = ft.TextField(label=t("build_desc"),
                                   value=existing.get("desc","") if existing else "",
                                   multiline=True, min_lines=3,
                                   border_color=_c("border"), color=_c("text"),
                                   label_style=ft.TextStyle(color=_c("sub")))

        def do_save(e):
            skills_raw = [s.strip() for s in skills_field.value.split(",") if s.strip()]
            b = {
                "name":   name_field.value.strip() or "Build",
                "cls":    class_dd.value or list(BUILDS.keys())[0],
                "hero":   hero_field.value.strip(),
                "skills": skills_raw,
                "desc":   desc_field.value.strip(),
            }
            if is_edit:
                _db_update_build(state["edit_build_id"], b)
            else:
                _db_save_build(b)
            state["my_builds"] = _db_get_my_builds()
            state["screen"] = "builds"
            state["builds_tab"] = "my"
            render()

        def do_cancel(e):
            state["screen"] = "builds"
            state["builds_tab"] = "my"
            render()

        title = t("edit") + " Build" if is_edit else t("new_build")
        return ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=do_cancel,
                              icon_color=_c("orange")),
                _hdr(title),
            ], spacing=4),
            _divider(),
            name_field,
            class_dd,
            hero_field,
            skills_field,
            desc_field,
            ft.Row([
                _btn(t("save"), do_save, color=_c("green")),
                _btn(t("cancel"), do_cancel, color=_c("sub")),
            ], spacing=8),
        ], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

    # ── NEWS screen ───────────────────────────────────────────────────────────
    def _screen_news():
        rows = [_hdr(t("news_tab"))]
        if state["news_loading"]:
            rows.append(ft.ProgressRing(width=32, height=32, stroke_width=3,
                                        color=_c("orange")))
        elif not state["news"]:
            rows.append(_card(_txt(t("no_news"), color=_c("sub"))))
        else:
            for item in state["news"]:
                rows.append(_card(
                    _hdr(item.get("title",""), size=14),
                    _txt(item.get("body",""), size=12, color=_c("sub")),
                ))
        return ft.Column(rows, spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    # ── GUIDE screen ──────────────────────────────────────────────────────────
    def _screen_guide():
        lang_key = LANG[0]
        rows = [_hdr(t("guide_title"))]
        for section_title, section_body in GUIDE[lang_key]:
            rows.append(_card(
                _hdr(section_title, size=14, color=_c("cyan")),
                _txt(section_body, size=12),
            ))
        return ft.Column(rows, spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    # ── SETTINGS screen ───────────────────────────────────────────────────────
    def _screen_settings():
        rows = [_hdr(t("settings_title"))]

        # Theme
        def set_theme(theme_val):
            def _h(e):
                THEME[0] = theme_val
                prefs["theme"] = THEME[0]
                _save_prefs(prefs)
                render()
            return _h

        rows.append(_card(
            _sub(t("theme")),
            ft.Row([
                _toggle_btn(t("dark"),  THEME[0]=="dark",  set_theme("dark")),
                _toggle_btn(t("light"), THEME[0]=="light", set_theme("light")),
            ], spacing=8),
        ))

        # Language
        def set_lang(lang_val):
            def _h(e):
                LANG[0] = lang_val
                prefs["lang"] = LANG[0]
                _save_prefs(prefs)
                render()
            return _h

        rows.append(_card(
            _sub(t("language")),
            ft.Row([
                _toggle_btn(t("spanish"), LANG[0]=="es", set_lang("es")),
                _toggle_btn(t("english"), LANG[0]=="en", set_lang("en")),
            ], spacing=8),
        ))

        # Region
        def on_region_change(e):
            state["region"] = e.control.value
            prefs["region"] = state["region"]
            _save_prefs(prefs)

        rows.append(_card(
            _sub(t("region_lbl")),
            ft.Dropdown(
                value=state["region"],
                options=[ft.dropdown.Option(r) for r in _REGIONS],
                on_change=on_region_change,
                border_color=_c("border"), color=_c("text"),
            ),
        ))

        # Notification hour
        notif_tf = ft.TextField(
            label=t("notif_hour"),
            value=str(state["notif_hour"]),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=_c("border"), color=_c("text"),
            label_style=ft.TextStyle(color=_c("sub")),
        )

        def save_settings(e):
            try:
                h = int(notif_tf.value or 8)
                h = max(0, min(23, h))
            except ValueError:
                h = 8
            state["notif_hour"] = h
            prefs["notif_hour"] = h
            prefs["region"] = state["region"]
            _save_prefs(prefs)
            _schedule_notification_if_android(h)
            page.snack_bar = ft.SnackBar(ft.Text(t("save_settings")), bgcolor=_c("green"))
            page.snack_bar.open = True
            page.update()

        rows.append(_card(notif_tf, _btn(t("save_settings"), save_settings)))

        # Check for update
        update_status = ft.Text("", size=13, color=_c("sub"))

        def manual_check_update(e):
            update_status.value = t("loading")
            page.update()
            info = _check_github_update()
            if info:
                state["update_info"] = info
                state["update_dismissed"] = False
                update_status.value = f"{t('update_available')}: v{info['version']}"
                update_status.color = _c("yellow")
            else:
                update_status.value = t("up_to_date")
                update_status.color = _c("green")
            page.update()

        rows.append(_card(
            _sub(t("check_update")),
            ft.Row([
                _btn(t("check_update"), manual_check_update, icon=ft.Icons.SYSTEM_UPDATE),
                update_status,
            ], spacing=10, wrap=True),
        ))

        # About
        genesis_ok = _verify_genesis()
        rows.append(_card(
            _hdr(t("about"), size=14),
            _sub(f"{APP_NAME} v{APP_VERSION}"),
            _sub(f"{t('created_by')}: {APP_AUTHOR}"),
            _divider(),
            ft.Row([
                ft.Icon(ft.Icons.VERIFIED if genesis_ok else ft.Icons.WARNING,
                        color=_c("green") if genesis_ok else _c("red"), size=16),
                _txt(t("genesis_valid") if genesis_ok else t("genesis_invalid"),
                     size=12,
                     color=_c("green") if genesis_ok else _c("red")),
            ], spacing=6),
            _sub(f"Seal: {_GENESIS_SEAL[:32]}...", size=10),
            _sub(f"Commit: {_GENESIS_COMMIT}", size=10),
        ))

        return ft.Column(rows, spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    # ── Master render ─────────────────────────────────────────────────────────
    def render():
        _apply_theme()
        page.bgcolor = _c("bg")

        screen = state["screen"]
        if screen == "home":
            content = _screen_home()
            title   = f"{APP_NAME} v{APP_VERSION}"
        elif screen == "builds":
            content = _screen_builds()
            title   = t("builds")
        elif screen in ("build_create", "build_edit"):
            content = _screen_build_form()
            title   = APP_NAME
        elif screen == "news":
            content = _screen_news()
            title   = t("news_tab")
        elif screen == "guide":
            content = _screen_guide()
            title   = t("guide_title")
        elif screen == "settings":
            content = _screen_settings()
            title   = t("settings_title")
        else:
            content = _screen_home()
            title   = APP_NAME

        navbar = _nav_bar()
        page.navigation_bar = navbar

        page.controls.clear()
        page.appbar = _appbar(title)
        page.add(
            ft.Container(
                content=ft.Column([
                    content,
                    _footer(),
                ], spacing=0, expand=True),
                bgcolor=_c("bg"),
                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                expand=True,
            )
        )
        page.update()

    # ── Startup ───────────────────────────────────────────────────────────────
    render()
    threading.Thread(target=_load_alerts,       daemon=True).start()
    threading.Thread(target=_load_news,         daemon=True).start()
    threading.Thread(target=_bg_check_update,   daemon=True).start()
    _schedule_notification_if_android(state["notif_hour"])


ft.app(target=main)
