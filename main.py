#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STW Hub v2.0.0 — Fortnite: Save The World Hub
Creado por: Pedro Espinal   Todos los derechos reservados (c) 2026
Bilingual · Dark/Light · Auto-refresh · Builds with images · Genesis-sealed
"""

import flet as ft
import asyncio
import json
import os
import hashlib
import sqlite3
import base64
import traceback
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

try:
    import requests
    _REQ_OK = True
except ImportError:
    _REQ_OK = False

# ── Flet 0.85.1 Android compatibility (border/padding/margin/alignment helpers) ─
def _border_all(width, color):
    bs = ft.BorderSide(width, color)
    return ft.Border(top=bs, right=bs, bottom=bs, left=bs)

def _pad_sym(horizontal=0, vertical=0):
    return ft.Padding(left=horizontal, right=horizontal, top=vertical, bottom=vertical)

def _pad_only(left=0, top=0, right=0, bottom=0):
    return ft.Padding(left=left, top=top, right=right, bottom=bottom)

def _margin_b(bottom=0):
    return ft.Margin(left=0, top=0, right=0, bottom=bottom)

_ALIGN_CENTER = ft.Alignment(0, 0)

# ── App identity ───────────────────────────────────────────────────────────────
APP_NAME    = "STW Hub"
APP_VERSION = "2.1.1"
APP_AUTHOR  = "Pedro Espinal"
APP_RIGHTS  = "Todos los derechos reservados"
APP_YEAR    = str(date.today().year)
COPYRIGHT   = f"Creado por: {APP_AUTHOR}   ·   {APP_RIGHTS}   ©{APP_YEAR}"

# ── Writable data dir ──────────────────────────────────────────────────────────
def _resolve_data_dir() -> Path:
    for key in ("FLET_APP_STORAGE_DATA", "FLET_APP_DIR", "APPDATA"):
        v = os.environ.get(key)
        if v:
            p = Path(v) / "stwhub"
            try:
                p.mkdir(parents=True, exist_ok=True)
                probe = p / ".probe"
                probe.write_text("x")
                probe.unlink()
                return p
            except Exception:
                continue
    try:
        fb = Path.home() / ".stwhub"
        fb.mkdir(parents=True, exist_ok=True)
        return fb
    except Exception:
        import tempfile
        t = Path(tempfile.gettempdir()) / "stwhub"
        t.mkdir(parents=True, exist_ok=True)
        return t

DATA_DIR   = _resolve_data_dir()
PREFS_FILE = DATA_DIR / "prefs.json"
CACHE_FILE = DATA_DIR / "cache.json"
DB_FILE    = DATA_DIR / "stwhub.db"

# ── External endpoints ─────────────────────────────────────────────────────────
GITHUB_REPO     = "pedroespinal/STWHub"
GITHUB_API      = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
GITHUB_RELEASES = f"https://github.com/{GITHUB_REPO}/releases/latest"

_EPIC_CLIENT_ID     = "ec684b8c687f479fadea3cb2ad83f5c6"
_EPIC_CLIENT_SECRET = "e1f31c211f28413186262d37a13fc84d"
_EPIC_TOKEN_URL     = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token"
_EPIC_WORLD_URL     = "https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/world/info"
_NEWS_URL           = "https://fortnite-api.com/v2/news"
_BR_COSMETICS_URL   = "https://fortnite-api.com/v2/cosmetics/br"
# Community builds backend — JSON file in GitHub repo (no server needed)
_COMMUNITY_BUILDS_URL = "https://raw.githubusercontent.com/pedroespinal/STWHub/main/community_builds.json"

_VBUCKS_TYPE = "AccountResource:currency_mtxswap"
_REGIONS     = ["NAE", "NAW", "EU", "BR", "OC", "AS"]

# ── Genesis seal ───────────────────────────────────────────────────────────────
_GENESIS_COMMIT = "stwhub-genesis-20260521"
_GENESIS_DATE   = "2026-05-21T00:00:00"
_GENESIS_AUTHOR = "Pedro Espinal"
_GENESIS_APP    = "STW Hub"
_GENESIS_SEAL   = "bdeedb31e7c0e361f24a71fa9f7a14eb584d1d867bbd0f36e5b755b122166aff"

def _verify_genesis() -> bool:
    raw = f"{_GENESIS_COMMIT}|{_GENESIS_DATE}|{_GENESIS_AUTHOR}|{_GENESIS_APP}"
    return hashlib.sha256(raw.encode()).hexdigest() == _GENESIS_SEAL

# ── Theme palettes ─────────────────────────────────────────────────────────────
_DARK = {
    "bg":      "#07071a",
    "surface": "#0d0d2b",
    "card":    "#0e0e2e",
    "border":  "#1e1e5a",
    "text":    "#e8e8ff",
    "sub":     "#b8b8e8",
    "orange":  "#ff6d00",
    "cyan":    "#00e5ff",
    "yellow":  "#ffd700",
    "purple":  "#7c3aed",
    "green":   "#00ff88",
    "red":     "#ff3355",
    "pink":    "#f72585",
    "footer":  "#ff8800",
    "banner":  "#1a0500",
    "gold":    "#ffcc00",
    "vbucks":  "#d0a8f0",
}
_LIGHT = {
    "bg":      "#dfe3f0",   # azul-gris suave, no blanco puro
    "surface": "#d2d6e6",   # un tono más oscuro que bg
    "card":    "#eaecf5",   # blanco cálido, no puro
    "border":  "#b0b6cc",
    "text":    "#10102e",   # azul-marino oscuro — máximo contraste
    "sub":     "#3a3f68",   # gris-azul legible
    "orange":  "#c04800",   # naranja oscuro — legible sobre light
    "cyan":    "#0060a0",
    "yellow":  "#7a5800",
    "purple":  "#6b25c4",   # gamer purple
    "green":   "#006030",   # verde oscuro — texto blanco legible encima
    "red":     "#c8007a",   # magenta gamer — en lugar de rojo convencional
    "pink":    "#b0006a",
    "footer":  "#aa3000",
    "banner":  "#ffe8d6",
    "gold":    "#8b6914",
    "vbucks":  "#6b1fc4",   # gamer purple-violet
}
THEME = ["dark"]
LANG  = ["es"]

def _c(k: str) -> str:
    return (_DARK if THEME[0] == "dark" else _LIGHT)[k]

def t(k: str) -> str:
    return T[LANG[0]].get(k, k)

# ── Translations ───────────────────────────────────────────────────────────────
T = {
    "es": {
        "home": "Inicio", "news": "Noticias", "builds": "Builds",
        "guide": "Guia", "settings": "Config",
        "daily_alerts": "Alertas Diarias",
        "refresh": "Actualizar", "vbucks_only": "Solo V-Bucks",
        "region": "Region", "loading": "Cargando...",
        "no_alerts": "Sin alertas disponibles.",
        "utc_reset": "Reset UTC en", "last_refresh": "Actualizado",
        "alerts_cached": "Cache offline", "power": "Poder",
        "news_title": "Noticias STW", "no_news": "Sin noticias disponibles.",
        "meta_builds": "Meta Builds", "my_builds": "Mis Builds",
        "community_builds": "Comunidad",
        "heroes": "Heroes", "all_classes": "Todas",
        "new_build": "Nuevo Build",
        "build_name": "Nombre del build",
        "build_class": "Clase del heroe",
        "build_hero": "Heroe principal",
        "build_hero_img": "URL imagen heroe (opcional)",
        "build_weapon1": "Arma principal",
        "build_weapon1_img": "URL imagen arma (opcional)",
        "build_weapon2": "Arma secundaria (opcional)",
        "build_weapon2_img": "URL imagen arma 2 (opcional)",
        "build_skills": "Perks / Habilidades (separadas por coma)",
        "build_desc": "Descripcion — que hace este build",
        "build_purpose": "Para que sirve / Mejores usos",
        "build_tags": "Etiquetas",
        "save": "Guardar", "cancel": "Cancelar",
        "edit": "Editar", "delete": "Eliminar",
        "no_my_builds": "Sin builds guardados.\nPresiona + para crear uno.",
        "search_hero": "Buscar imagen",
        "hero_search_title": "Buscar Heroe / Personaje",
        "hero_placeholder": "Nombre del heroe (ej: Kyle, Scorch)...",
        "searching": "Buscando...",
        "no_hero_results": "Sin resultados. Prueba otro nombre.",
        "select": "Seleccionar",
        "guide_title": "Guia Completa STW",
        "settings_title": "Configuracion",
        "theme": "Tema", "dark": "Oscuro", "light": "Claro",
        "language": "Idioma", "spanish": "Espanol", "english": "English",
        "region_lbl": "Region de alertas",
        "notif_hour": "Hora notificacion (0-23h)",
        "save_settings": "Configuracion guardada",
        "check_update": "Buscar actualizacion",
        "update_available": "Nueva version disponible",
        "up_to_date": "App al dia",
        "download": "Descargar", "dismiss": "Ignorar",
        "about": "Acerca de",
        "genesis_valid": "Firma digital valida",
        "genesis_invalid": "FIRMA INVALIDA",
        "created_by": "Creado por",
        "rights": "Todos los derechos reservados",
        "checking": "Verificando...",
        "support_heroes": "Heroes soporte",
        "weapons": "Armas",
        "purpose": "Para que sirve",
        "tags": "Etiquetas",
        "skills": "Perks",
        "created": "Creado",
        "desc": "Descripcion",
        "no_img": "Sin imagen",
        "hero_img": "Imagen heroe",
        "weapon_img": "Imagen arma",
        "tag_afk": "AFK", "tag_farm": "Farm", "tag_vbucks": "V-Bucks",
        "tag_speed": "Rapido", "tag_endgame": "Endgame",
        "tag_beginner": "Principiante", "tag_expert": "Experto",
        "tag_team": "Equipo", "tag_dps": "DPS",
        "error_api": "Error al conectar con la API.",
    },
    "en": {
        "home": "Home", "news": "News", "builds": "Builds",
        "guide": "Guide", "settings": "Settings",
        "daily_alerts": "Daily Alerts",
        "refresh": "Refresh", "vbucks_only": "V-Bucks Only",
        "region": "Region", "loading": "Loading...",
        "no_alerts": "No alerts available.",
        "utc_reset": "UTC reset in", "last_refresh": "Updated",
        "alerts_cached": "Offline cache", "power": "Power",
        "news_title": "STW News", "no_news": "No news available.",
        "meta_builds": "Meta Builds", "my_builds": "My Builds",
        "community_builds": "Community",
        "heroes": "Heroes", "all_classes": "All",
        "new_build": "New Build",
        "build_name": "Build name",
        "build_class": "Hero class",
        "build_hero": "Main hero",
        "build_hero_img": "Hero image URL (optional)",
        "build_weapon1": "Main weapon",
        "build_weapon1_img": "Weapon image URL (optional)",
        "build_weapon2": "Secondary weapon (optional)",
        "build_weapon2_img": "Weapon 2 image URL (optional)",
        "build_skills": "Perks / Skills (comma-separated)",
        "build_desc": "Description — what this build does",
        "build_purpose": "Best uses / Purpose",
        "build_tags": "Tags",
        "save": "Save", "cancel": "Cancel",
        "edit": "Edit", "delete": "Delete",
        "no_my_builds": "No saved builds.\nTap + to create one.",
        "search_hero": "Search image",
        "hero_search_title": "Search Hero / Character",
        "hero_placeholder": "Hero name (eg: Kyle, Scorch)...",
        "searching": "Searching...",
        "no_hero_results": "No results. Try another name.",
        "select": "Select",
        "guide_title": "Full STW Guide",
        "settings_title": "Settings",
        "theme": "Theme", "dark": "Dark", "light": "Light",
        "language": "Language", "spanish": "Espanol", "english": "English",
        "region_lbl": "Alert region",
        "notif_hour": "Notification hour (0-23h)",
        "save_settings": "Settings saved",
        "check_update": "Check for update",
        "update_available": "New version available",
        "up_to_date": "App is up to date",
        "download": "Download", "dismiss": "Dismiss",
        "about": "About",
        "genesis_valid": "Valid digital signature",
        "genesis_invalid": "INVALID SIGNATURE",
        "created_by": "Created by",
        "rights": "All rights reserved",
        "checking": "Checking...",
        "support_heroes": "Support heroes",
        "weapons": "Weapons",
        "purpose": "Best uses",
        "tags": "Tags",
        "skills": "Perks",
        "created": "Created",
        "desc": "Description",
        "no_img": "No image",
        "hero_img": "Hero image",
        "weapon_img": "Weapon image",
        "tag_afk": "AFK", "tag_farm": "Farm", "tag_vbucks": "V-Bucks",
        "tag_speed": "Speed", "tag_endgame": "Endgame",
        "tag_beginner": "Beginner", "tag_expert": "Expert",
        "tag_team": "Team", "tag_dps": "DPS",
        "error_api": "Error connecting to the API.",
    },
}

# ── Meta Builds database ───────────────────────────────────────────────────────
BUILDS = {
    "Constructor": [
        {
            "name": "BASE Constructor",
            "hero": "Megabase Kyle",
            "support_es": "BASE Kyle · Electro-pulse Penny · Trailblaster Buzz",
            "support_en": "BASE Kyle · Electro-pulse Penny · Trailblaster Buzz",
            "weapons_es": "Hydraulic Shotgun · Siegebreaker",
            "weapons_en": "Hydraulic Shotgun · Siegebreaker",
            "skills": ["B.A.S.E.", "Plasma Pulse", "Bull Rush", "Decoy"],
            "desc_es": "B.A.S.E. de Megabase potencia 9 estructuras adyacentes haciendolas casi indestructibles. Decoy desvia husks mientras el equipo trabaja.",
            "desc_en": "Megabase's B.A.S.E. buffs 9 adjacent structures making them nearly indestructible. Decoy diverts husks while the team works.",
            "purpose_es": "Defensa de objetivo · Twine Peaks · Alta dificultad",
            "purpose_en": "Objective defense · Twine Peaks · High difficulty",
            "tags": ["endgame", "expert"],
        },
        {
            "name": "Tank Constructor",
            "hero": "Sentinel",
            "support_es": "Penny · Steel Wool Anthony · Hotdog Stan",
            "support_en": "Penny · Steel Wool Anthony · Hotdog Stan",
            "weapons_es": "Ground Pounder · Typewriter",
            "weapons_en": "Ground Pounder · Typewriter",
            "skills": ["Kinetic Overload", "Shockwave", "Bull Rush", "Plasma Pulse"],
            "desc_es": "Maximo aguante y control de masas. Kinetic Overload genera dano electrico al bloquear, Shockwave despeja zonas al instante.",
            "desc_en": "Maximum durability and crowd control. Kinetic Overload deals electric damage on block, Shockwave instantly clears areas.",
            "purpose_es": "Zonas densas · Soporte de equipo · Defensa larga",
            "purpose_en": "Dense husk zones · Team support · Long defense",
            "tags": ["endgame", "team"],
        },
    ],
    "Ninja": [
        {
            "name": "Dragon Ninja",
            "hero": "Dragon Scorch",
            "support_es": "Dim Mak Mari · Deadly Blade Crash · Brawler Kyle",
            "support_en": "Dim Mak Mari · Deadly Blade Crash · Brawler Kyle",
            "weapons_es": "Nocturno (Dragon) · Spectral Blade",
            "weapons_en": "Nocturno (Dragon) · Spectral Blade",
            "skills": ["Dragon Slash", "Smoke Bomb", "Shadow Stance", "Crescent Kick"],
            "desc_es": "Dragon Slash aplica fuego a todo en linea recta con dano masivo. Shadow Stance da invulnerabilidad breve. El mejor para oleadas cortas.",
            "desc_en": "Dragon Slash applies fire to everything in a straight line with massive damage. Shadow Stance gives brief invulnerability. Best for short waves.",
            "purpose_es": "Misiones de oleadas cortas · Speedrun · Eliminacion",
            "purpose_en": "Short wave missions · Speedrun · Elimination",
            "tags": ["speed", "expert", "dps"],
        },
        {
            "name": "Ranged Ninja",
            "hero": "Autumn Queen",
            "support_es": "Brawler Kyle · Deadly Blade Crash · Dire",
            "support_en": "Brawler Kyle · Deadly Blade Crash · Dire",
            "weapons_es": "Hydra · Vacuum Tube Bow",
            "weapons_en": "Hydra · Vacuum Tube Bow",
            "skills": ["Throwing Stars", "Smoke Bomb", "Crescent Kick", "Shadow Stance"],
            "desc_es": "Movilidad extrema con dano a distancia. Throwing Stars + Smoke Bomb para kiting perfecto. Ideal para misiones donde hay que moverse constantemente.",
            "desc_en": "Extreme mobility with ranged damage. Throwing Stars + Smoke Bomb for perfect kiting. Ideal for missions requiring constant movement.",
            "purpose_es": "Kiting · Misiones de eliminacion · Movilidad maxima",
            "purpose_en": "Kiting · Elimination missions · Maximum mobility",
            "tags": ["speed", "dps"],
        },
    ],
    "Outlander": [
        {
            "name": "TEDDY Outlander",
            "hero": "Enforcer Grizzly",
            "support_es": "Phase Scout Jess · Pathfinder Jess · Ranger Deadeye",
            "support_en": "Phase Scout Jess · Pathfinder Jess · Ranger Deadeye",
            "weapons_es": "Razorblade · Siegebreaker",
            "weapons_en": "Razorblade · Siegebreaker",
            "skills": ["T.E.D.D.Y.", "Anti-Material Charge", "Seismic Smash", "In the Zone"],
            "desc_es": "TEDDY hace el trabajo pesado. AMC destruye estructuras enemigas y da materiales extra. In the Zone maximiza la movilidad para recolectar sin parar.",
            "desc_en": "TEDDY does the heavy lifting. AMC destroys enemy structures and gives extra materials. In the Zone maximizes mobility for non-stop collection.",
            "purpose_es": "Farm de recursos · AFK parcial · Recoleccion",
            "purpose_en": "Resource farming · Semi-AFK · Collection missions",
            "tags": ["afk", "farm", "beginner"],
        },
        {
            "name": "V-Bucks Outlander",
            "hero": "Phase Scout Jess",
            "support_es": "Ranger Deadeye · Pathfinder Jess · Enforcer Grizzly",
            "support_en": "Ranger Deadeye · Pathfinder Jess · Enforcer Grizzly",
            "weapons_es": "Vacuum Tube Sniper · Grave Digger",
            "weapons_en": "Vacuum Tube Sniper · Grave Digger",
            "skills": ["T.E.D.D.Y.", "In the Zone", "Anti-Material Charge", "Seismic Smash"],
            "desc_es": "Optimizado para completar alertas de V-Bucks rapido. In the Zone acelera el movimiento para llegar a misiones antes del limite de tiempo.",
            "desc_en": "Optimized for completing V-Bucks alerts fast. In the Zone speeds up movement to reach missions before time limits.",
            "purpose_es": "Farm V-Bucks · Alertas diarias · Misiones con tiempo",
            "purpose_en": "V-Bucks farming · Daily alerts · Timed missions",
            "tags": ["vbucks", "speed", "farm"],
        },
    ],
    "Soldier": [
        {
            "name": "Gunslinger DPS",
            "hero": "Raider Headhunter",
            "support_es": "Commando Ramirez · Sergeant Jonesy · Enforcer Grizzly",
            "support_en": "Commando Ramirez · Sergeant Jonesy · Enforcer Grizzly",
            "weapons_es": "Nocturno · Siegebreaker · Ground Pounder",
            "weapons_en": "Nocturno · Siegebreaker · Ground Pounder",
            "skills": ["Frag Grenade", "Lefty and Righty", "War Cry", "Goin' Commando"],
            "desc_es": "El DPS mas alto del juego. War Cry potencia a todo el equipo. Lefty and Righty + Goin' Commando para oleadas masivas. El rey del endgame.",
            "desc_en": "Highest DPS in the game. War Cry buffs the entire team. Lefty and Righty + Goin' Commando for massive waves. The endgame king.",
            "purpose_es": "Maximo DPS · Endgame · Twine Peaks · Storm King",
            "purpose_en": "Maximum DPS · Endgame · Twine Peaks · Storm King",
            "tags": ["endgame", "dps", "expert"],
        },
        {
            "name": "Support Soldier",
            "hero": "Sergeant Jonesy",
            "support_es": "Urban Assault Headhunter · Commando Ramirez · Raider Headhunter",
            "support_en": "Urban Assault Headhunter · Commando Ramirez · Raider Headhunter",
            "weapons_es": "Typewriter · Hydra",
            "weapons_en": "Typewriter · Hydra",
            "skills": ["War Cry", "Frag Grenade", "Goin' Commando", "Shockwave"],
            "desc_es": "War Cry potencia a todos los aliados en rango. Imprescindible en partidas de 4 jugadores. Shockwave para control de emergencias.",
            "desc_en": "War Cry buffs all allies in range. Essential in 4-player matches. Shockwave for emergency crowd control.",
            "purpose_es": "Partidas grupales · Buff de equipo · Cooperativo",
            "purpose_en": "Group matches · Team buff · Cooperative",
            "tags": ["team", "beginner"],
        },
    ],
}
HERO_CLASSES = ["all", "Constructor", "Ninja", "Outlander", "Soldier"]
BUILD_TAGS   = ["afk", "farm", "vbucks", "speed", "endgame", "dps", "team", "beginner", "expert"]

# ── Guide sections ─────────────────────────────────────────────────────────────
GUIDE = {
    "es": [
        ("¿Que es Save The World?",
         "Fortnite: Save The World es el modo PvE cooperativo de Fortnite (hasta 4 jugadores). "
         "Tu objetivo: construir defensas, recolectar recursos y eliminar oleadas de husks para "
         "proteger el objetivo. ¡Desde 2024 Save The World es completamente GRATIS! "
         "Solo descarga Fortnite y accede desde el menú principal.\n\n"
         "La campaña principal se divide en 4 mundos: Stonewood → Plankerton → "
         "Canny Valley → Twine Peaks (endgame)."),
        ("V-Bucks Gratis",
         "Las alertas diarias se reinician a las 00:00 UTC exactamente. Cada alerta especial "
         "puede dar entre 50 y 100 V-Bucks.\n\n"
         "Como maximizarlos:\n"
         "• Usa el filtro 'Solo V-Bucks' en la pantalla de Inicio\n"
         "• Completa TODAS las alertas con V-Bucks cada dia\n"
         "• Las misiones de Storm Zones y Weekly Missions dan 100 V-Bucks\n"
         "• Avanzar en la historia desbloquea zonas con mas alertas disponibles\n"
         "• Puedes ganar entre 50 y 1000+ V-Bucks al dia segun tu progreso"),
        ("Clases de Heroes",
         "CONSTRUCTOR: Especialista en B.A.S.E. y estructuras. Sus edificaciones son "
         "mas resistentes y B.A.S.E. las potencia aun mas.\n\n"
         "NINJA: Velocidad y dano cuerpo a cuerpo extremo. Dragon Slash, Smoke Bomb "
         "y Shadow Stance son sus armas.\n\n"
         "EXPLORADOR (Outlander): Maestro de la recoleccion. TEDDY hace el trabajo "
         "mientras el Explorador recolecta recursos y detecta cofres a distancia.\n\n"
         "SOLDADO: Maximo DPS a distancia. War Cry es una de las mejores habilidades "
         "del juego, potenciando a todo el equipo por varios segundos."),
        ("Sistema de Alertas",
         "Las alertas son misiones especiales disponibles por tiempo limitado (24h) "
         "con recompensas extra como V-Bucks, heroes legendarios o esquemas raros.\n\n"
         "Como funcionan:\n"
         "• Se renuevan exactamente a 00:00 UTC\n"
         "• Filtra por tu region para ver las de tu servidor\n"
         "• Las alertas de mayor poder dan mejores recompensas\n"
         "• Debes tener desbloqueada la zona donde aparece la alerta\n"
         "• El contador de reset UTC en la pantalla de Inicio te dice cuanto falta"),
        ("Construccion y Trampas",
         "Materiales en orden de resistencia: Madera < Ladrillo < Metal.\n"
         "Metal es el mas resistente pero tarda mas en construirse — usalo en el "
         "endgame. En Stonewood/Plankerton, madera es suficiente.\n\n"
         "Trampas esenciales:\n"
         "• Gas Trap: Maximo DPS, cubre area\n"
         "• Ceiling Electric Field: Cobertura aerea constante\n"
         "• Wall Dynamo: Electrocuta husks lateralmente\n"
         "• Freeze Trap: Control de masas, ralentiza grupos\n"
         "• Wall Launcher: Empuja husks fuera del camino\n\n"
         "Tip clave: Crea embudos (funnels) que fuercen a los husks a pasar por "
         "tus trampas. Un buen embudo puede defender el objetivo solo."),
        ("El Storm King",
         "El boss final de STW. Solo disponible en Twine Peaks (endgame).\n\n"
         "Estrategia completa:\n"
         "Fase 1: Destruye los 4 orbes brillantes (2 en hombros, 2 en caderas).\n"
         "  → No dispares al cuerpo — es inmune.\n\n"
         "Fase 2: El Storm King cae y libera oleadas masivas de minions.\n"
         "  → Usa War Cry + TEDDY para eliminarlos rapido.\n\n"
         "Fase 3: Dano coordinado masivo al corazon brillante.\n"
         "  → Todo el equipo debe apuntar al mismo punto.\n\n"
         "Recomendacion de build: Soldado con Goin' Commando o Explorador con TEDDY."),
        ("Regiones de Servidores",
         "NAE: Este de Norteamerica\n"
         "NAW: Oeste de Norteamerica\n"
         "EU: Europa\n"
         "BR: Brasil\n"
         "OC: Oceania\n"
         "AS: Asia\n\n"
         "Siempre elige la region mas cercana a tu ubicacion fisica para menor "
         "latencia. Puedes cambiarla en la pantalla de Inicio o en Configuracion."),
        ("Consejos de Experto",
         "1. Completa toda la historia principal antes de enfocarte en alertas.\n"
         "2. Nunca destruyas estructuras del mapa existentes — puedes necesitarlas.\n"
         "3. SIEMPRE construye antes de que empiece la oleada, no durante.\n"
         "4. Comunica con tu equipo donde poner trampas antes de empezar.\n"
         "5. Usa el filtro V-Bucks en Inicio cada dia sin falta.\n"
         "6. Prioriza misiones con Power Level cercano al tuyo (±10).\n"
         "7. Sube el nivel de tu Comandante completando misiones de historia.\n"
         "8. En misiones con limite de tiempo, usa Outlander con In the Zone.\n"
         "9. El modo 4 jugadores da recompensas bonus — juega con amigos cuando puedas.\n"
         "10. Guarda tus mejores esquemas de armas — son difíciles de volver a conseguir."),
    ],
    "en": [
        ("What is Save The World?",
         "Fortnite: Save The World is Fortnite's PvE cooperative mode (up to 4 players). "
         "Your goal: build defenses, collect resources, and eliminate husk waves to protect "
         "the objective. Since 2024, Save The World is completely FREE! "
         "Just download Fortnite and access it from the main menu.\n\n"
         "The main campaign is split into 4 worlds: Stonewood → Plankerton → "
         "Canny Valley → Twine Peaks (endgame)."),
        ("Free V-Bucks",
         "Daily alerts reset exactly at 00:00 UTC. Each special alert can give 50 to 100 V-Bucks.\n\n"
         "How to maximize them:\n"
         "• Use the 'V-Bucks Only' filter on the Home screen\n"
         "• Complete ALL V-Bucks alerts every day\n"
         "• Storm Zone and Weekly Missions give 100 V-Bucks\n"
         "• Advancing in the story unlocks zones with more available alerts\n"
         "• You can earn 50 to 1000+ V-Bucks per day depending on your progress"),
        ("Hero Classes",
         "CONSTRUCTOR: B.A.S.E. and structure specialist. Buildings are more resistant "
         "and B.A.S.E. boosts them even further.\n\n"
         "NINJA: Speed and extreme melee damage. Dragon Slash, Smoke Bomb, and "
         "Shadow Stance are their weapons.\n\n"
         "OUTLANDER: Resource collection master. TEDDY does the work while the "
         "Outlander collects resources and detects chests from a distance.\n\n"
         "SOLDIER: Maximum ranged DPS. War Cry is one of the best abilities in the "
         "game, buffing the entire team for several seconds."),
        ("Alert System",
         "Alerts are special missions available for limited time (24h) with extra rewards "
         "like V-Bucks, legendary heroes, or rare schematics.\n\n"
         "How they work:\n"
         "• They refresh exactly at 00:00 UTC\n"
         "• Filter by your region to see your server's alerts\n"
         "• Higher power level alerts give better rewards\n"
         "• You must have unlocked the zone where the alert appears\n"
         "• The UTC reset counter on Home tells you how long until they refresh"),
        ("Building & Traps",
         "Materials in order of resistance: Wood < Brick < Metal.\n"
         "Metal is the most resistant but takes longer to build — use it in endgame. "
         "In Stonewood/Plankerton, wood is sufficient.\n\n"
         "Essential traps:\n"
         "• Gas Trap: Maximum DPS, covers area\n"
         "• Ceiling Electric Field: Constant aerial coverage\n"
         "• Wall Dynamo: Electrocutes husks from the sides\n"
         "• Freeze Trap: Crowd control, slows groups\n"
         "• Wall Launcher: Pushes husks off the path\n\n"
         "Key tip: Create funnels that force husks to pass through your traps. "
         "A good funnel can defend the objective on its own."),
        ("The Storm King",
         "STW's final boss. Only available in Twine Peaks (endgame).\n\n"
         "Full strategy:\n"
         "Phase 1: Destroy the 4 glowing orbs (2 on shoulders, 2 on hips).\n"
         "  → Don't shoot the body — it's immune.\n\n"
         "Phase 2: The Storm King falls and releases massive minion waves.\n"
         "  → Use War Cry + TEDDY to eliminate them fast.\n\n"
         "Phase 3: Coordinated massive damage to the glowing heart.\n"
         "  → The entire team must aim at the same point.\n\n"
         "Recommended build: Soldier with Goin' Commando or Outlander with TEDDY."),
        ("Server Regions",
         "NAE: North America East\n"
         "NAW: North America West\n"
         "EU: Europe\n"
         "BR: Brazil\n"
         "OC: Oceania\n"
         "AS: Asia\n\n"
         "Always choose the region closest to your physical location for lower latency. "
         "You can change it on the Home screen or in Settings."),
        ("Expert Tips",
         "1. Complete the entire main story before focusing on alerts.\n"
         "2. Never destroy existing map structures — you might need them.\n"
         "3. ALWAYS build before the wave starts, not during it.\n"
         "4. Communicate where to place traps before starting.\n"
         "5. Use the V-Bucks filter on Home every single day.\n"
         "6. Prioritize missions with a Power Level close to yours (±10).\n"
         "7. Level up your Commander by completing story missions.\n"
         "8. For timed missions, use Outlander with In the Zone.\n"
         "9. 4-player mode gives bonus rewards — play with friends when you can.\n"
         "10. Keep your best weapon schematics — they're hard to get again."),
    ],
}

# ── Prefs ──────────────────────────────────────────────────────────────────────
def _load_prefs() -> dict:
    try:
        return json.loads(PREFS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _save_prefs(p: dict):
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        PREFS_FILE.write_text(json.dumps(p, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

# ── Cache ──────────────────────────────────────────────────────────────────────
def _load_cache() -> dict:
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _save_cache(c: dict):
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(json.dumps(c, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

def _alerts_cache_stale(cache: dict) -> bool:
    ts = cache.get("alerts_ts", "")
    if not ts:
        return True
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return not ts.startswith(today)

# ── SQLite ─────────────────────────────────────────────────────────────────────
def _init_db():
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(DB_FILE)) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS my_builds (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    name        TEXT NOT NULL DEFAULT '',
                    cls         TEXT NOT NULL DEFAULT '',
                    hero        TEXT NOT NULL DEFAULT '',
                    hero_img    TEXT NOT NULL DEFAULT '',
                    weapon1     TEXT NOT NULL DEFAULT '',
                    weapon1_img TEXT NOT NULL DEFAULT '',
                    weapon2     TEXT NOT NULL DEFAULT '',
                    weapon2_img TEXT NOT NULL DEFAULT '',
                    skills      TEXT NOT NULL DEFAULT '[]',
                    desc        TEXT NOT NULL DEFAULT '',
                    purpose     TEXT NOT NULL DEFAULT '',
                    tags        TEXT NOT NULL DEFAULT '[]',
                    created     TEXT NOT NULL DEFAULT ''
                )
            """)
            con.commit()
    except Exception:
        pass

def _db_all_builds() -> list:
    try:
        with sqlite3.connect(str(DB_FILE)) as con:
            con.row_factory = sqlite3.Row
            return [dict(r) for r in
                    con.execute("SELECT * FROM my_builds ORDER BY id DESC").fetchall()]
    except Exception:
        return []

def _db_get_build(bid: int):
    try:
        with sqlite3.connect(str(DB_FILE)) as con:
            con.row_factory = sqlite3.Row
            row = con.execute("SELECT * FROM my_builds WHERE id=?", (bid,)).fetchone()
            return dict(row) if row else None
    except Exception:
        return None

def _db_save_build(b: dict) -> int:
    try:
        with sqlite3.connect(str(DB_FILE)) as con:
            cur = con.execute(
                "INSERT INTO my_builds "
                "(name,cls,hero,hero_img,weapon1,weapon1_img,weapon2,weapon2_img,"
                "skills,desc,purpose,tags,created) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (b["name"], b["cls"], b.get("hero",""), b.get("hero_img",""),
                 b.get("weapon1",""), b.get("weapon1_img",""),
                 b.get("weapon2",""), b.get("weapon2_img",""),
                 json.dumps(b.get("skills",[])), b.get("desc",""),
                 b.get("purpose",""), json.dumps(b.get("tags",[])),
                 datetime.now().strftime("%Y-%m-%d %H:%M")),
            )
            con.commit()
            return cur.lastrowid
    except Exception:
        return -1

def _db_update_build(bid: int, b: dict):
    try:
        with sqlite3.connect(str(DB_FILE)) as con:
            con.execute(
                "UPDATE my_builds SET name=?,cls=?,hero=?,hero_img=?,"
                "weapon1=?,weapon1_img=?,weapon2=?,weapon2_img=?,"
                "skills=?,desc=?,purpose=?,tags=? WHERE id=?",
                (b["name"], b["cls"], b.get("hero",""), b.get("hero_img",""),
                 b.get("weapon1",""), b.get("weapon1_img",""),
                 b.get("weapon2",""), b.get("weapon2_img",""),
                 json.dumps(b.get("skills",[])), b.get("desc",""),
                 b.get("purpose",""), json.dumps(b.get("tags",[])), bid),
            )
            con.commit()
    except Exception:
        pass

def _db_delete_build(bid: int):
    try:
        with sqlite3.connect(str(DB_FILE)) as con:
            con.execute("DELETE FROM my_builds WHERE id=?", (bid,))
            con.commit()
    except Exception:
        pass

# ── Network sync helpers ───────────────────────────────────────────────────────
def _sync_epic_token():
    if not _REQ_OK:
        return None
    try:
        creds = base64.b64encode(
            f"{_EPIC_CLIENT_ID}:{_EPIC_CLIENT_SECRET}".encode()
        ).decode()
        r = requests.post(
            _EPIC_TOKEN_URL,
            headers={"Authorization": f"Basic {creds}",
                     "Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "client_credentials"},
            timeout=12,
        )
        return r.json().get("access_token") if r.status_code == 200 else None
    except Exception:
        return None

# English AND Spanish zone-name keywords that mark non-campaign (venture/test) theaters
_SKIP_ZONES_EN = {"[test]", "venture", "adventure", "survive", "homebase", "horde", "scurvy", "shoal"}
_SKIP_ZONES_ES = {"aventura", "escorbuto", "estiaje", "horda", "punto de partida"}

def _theater_name(display, lang="en") -> str:
    """Extract zone name from displayName dict (multilingual) or plain string."""
    if isinstance(display, dict):
        return display.get(lang) or display.get("en") or next(iter(display.values()), "")
    return str(display) if display else ""

def _parse_mission_type(raw: str) -> str:
    """Convert 'MissionAlert_Retrieve_the_Data_T01' → 'Retrieve the Data'"""
    import re as _re
    s = raw.replace("MissionAlert_", "").replace("MissionAlert", "")
    s = _re.sub(r'_(T|PL|SW|TW|CV|SH)\d+$', '', s, flags=_re.IGNORECASE)
    s = _re.sub(r'_(Novice|Expert|Active|Storm|Phoenix)\w*$', '', s, flags=_re.IGNORECASE)
    s = s.replace("_", " ").strip()
    return s or raw

def _sync_fetch_alerts() -> list:
    """Fetch STW mission alerts from Epic world/info API.
    API structure (v2026):
      data["theaters"]     — list of theater defs with uniqueId + displayName (lang dict)
      data["missionAlerts"]— list of {theaterId, availableMissionAlerts:[{missionAlertRewards}]}
    """
    token = _sync_epic_token()
    if not token:
        return []
    try:
        r = requests.get(
            _EPIC_WORLD_URL,
            headers={"Authorization": f"Bearer {token}"},
            timeout=18,
        )
        if r.status_code != 200:
            return []
        data = r.json()

        # Build theater GUID → (display_name, english_name) map
        lang = LANG[0] if LANG[0] in ("es", "en") else "en"
        theater_map: dict = {}
        for theater in data.get("theaters", []):
            uid     = theater.get("uniqueId", "")
            display = theater.get("displayName", {})
            en_name   = _theater_name(display, "en")    # always English for filtering
            lang_name = _theater_name(display, lang)    # user language for display
            theater_map[uid] = (lang_name, en_name)

        alerts: list = []
        for entry in data.get("missionAlerts", []):
            tid = entry.get("theaterId", "")
            lang_zone, en_zone = theater_map.get(tid, (tid[:8], tid[:8]))
            # Skip test / venture / horde / homebase zones — filter on both EN and display name
            en_lower = en_zone.lower()
            es_lower = lang_zone.lower()
            if (any(kw in en_lower for kw in _SKIP_ZONES_EN) or
                    any(kw in es_lower for kw in _SKIP_ZONES_ES)):
                continue
            zone = lang_zone
            for alert in entry.get("availableMissionAlerts", []):
                items = alert.get("missionAlertRewards", {}).get("items", [])
                rewards: list = []
                has_vbucks = False
                for rw in items:
                    typ   = rw.get("itemType", "")
                    qty   = rw.get("quantity", 0)
                    is_vb = _VBUCKS_TYPE in typ
                    if is_vb:
                        has_vbucks = True
                    rewards.append({"type": typ, "quantity": qty, "vbucks": is_vb})
                if rewards:
                    mtype = _parse_mission_type(alert.get("name", "Mission"))
                    alerts.append({
                        "name":   mtype,
                        "zone":   zone,
                        "rewards": rewards,
                        "vbucks": has_vbucks,
                    })
        return alerts
    except Exception:
        return []

def _sync_fetch_news() -> list:
    """Fetch STW news. API changed: now /v2/news → data.stw.messages (not motds)."""
    if not _REQ_OK:
        return []
    try:
        r = requests.get(_NEWS_URL, timeout=12)
        if r.status_code != 200:
            return []
        data = r.json().get("data", {})
        # New structure: data.stw.messages
        stw = data.get("stw") or {}
        items = stw.get("messages") or stw.get("motds") or []
        # Fallback: try old structure
        if not items:
            items = data.get("motds", [])
        out = []
        for i in items[:15]:
            if i.get("hidden"):
                continue
            out.append({
                "title": i.get("title", ""),
                "body":  i.get("body", ""),
                "image": i.get("image", "") or i.get("titleImage", ""),
            })
        return out
    except Exception:
        return []

_BR_COSMETICS_CACHE: list = []   # in-memory cache of all BR cosmetics

def _sync_load_br_cosmetics() -> list:
    """Download and cache all BR cosmetics (used for hero image search)."""
    global _BR_COSMETICS_CACHE
    if _BR_COSMETICS_CACHE:
        return _BR_COSMETICS_CACHE
    if not _REQ_OK:
        return []
    try:
        r = requests.get(_BR_COSMETICS_URL, params={"language": "en"}, timeout=40)
        if r.status_code == 200:
            _BR_COSMETICS_CACHE = r.json().get("data", [])
    except Exception:
        pass
    return _BR_COSMETICS_CACHE

def _sync_search_heroes(query: str) -> list:
    """Search hero/character images from full BR cosmetics list (cached)."""
    if not query.strip():
        return []
    try:
        items = _sync_load_br_cosmetics()
        q = query.strip().lower()
        matches = [i for i in items if q in i.get("name", "").lower()]
        # Prefer outfits (skins) over other types
        outfits = [m for m in matches if m.get("type", {}).get("value") == "outfit"]
        results = outfits or matches
        out = []
        for item in results[:20]:
            name = item.get("name", "")
            imgs = item.get("images", {}) or {}
            img  = imgs.get("icon") or imgs.get("featured") or imgs.get("smallIcon") or ""
            if name and img:
                out.append({"name": name, "image": img})
        return out
    except Exception:
        return []

def _btn_text_color(bgcolor: str) -> str:
    """Return black or white text for maximum contrast against bgcolor."""
    try:
        h = bgcolor.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return "#000000" if luminance > 148 else "#ffffff"
    except Exception:
        return "#ffffff"

def _reward_label(item_type: str):
    """Convert raw Epic itemType → (emoji, short human-readable label).
    Returns a tuple (emoji_str, label_str).
    """
    t_low    = item_type.lower()
    parts    = item_type.split(":")
    category = parts[0].lower() if parts else ""
    # ── V-Bucks ──
    if "currency_mtxswap" in t_low:
        return "💎", "V-Bucks"
    # ── XP types ──
    if "phoenixxp" in t_low or "phoenix_xp" in t_low:
        return "🔥", "Phoenix XP"
    if "campaign_event_currency" in t_low or "acorns" in t_low or "candy" in t_low:
        return "🪙", "Event Currency"
    if "seasonxp" in t_low or "season_xp" in t_low:
        return "⚡", "Season XP"
    # ── Survivors / Heroes ──
    if category == "worker":
        return "👷", "Survivor"
    if category == "hero":
        return "⭐", "Hero"
    # ── Weapons / Traps ──
    if category == "schematic":
        return "🔧", "Schematic"
    # ── Materials ──
    if "ingredient" in t_low or "reagent" in t_low:
        return "🧪", "Material"
    # ── Base / Homebase ──
    if category == "homebasenode" or "homebase" in t_low:
        return "🏠", "Base Upgrade"
    # ── Tokens / Accolades ──
    if category == "token":
        return "🎫", "Token"
    if category == "accolade":
        return "🏆", "Accolade"
    # ── Catch-all XP ──
    if "xp" in t_low:
        return "⚡", "XP"
    # ── Fallback: make subtype human-readable ──
    subtype = parts[1] if len(parts) > 1 else item_type
    label   = subtype.replace("_", " ").split()[0].capitalize()
    return "📦", label[:14] if label else "Item"


def _newer_version(remote: str, local: str) -> bool:
    try:
        r = tuple(int(x) for x in remote.split("."))
        l = tuple(int(x) for x in local.split("."))
        return r > l
    except Exception:
        return remote != local

def _sync_check_update():
    if not _REQ_OK:
        return None
    try:
        r = requests.get(GITHUB_API, timeout=8,
                         headers={"Accept": "application/vnd.github+json"})
        if r.status_code != 200:
            return None
        data   = r.json()
        latest = data.get("tag_name", "").lstrip("v")
        if latest and _newer_version(latest, APP_VERSION):
            return {"version": latest, "url": GITHUB_RELEASES,
                    "notes": data.get("body", "")[:200]}
        return None
    except Exception:
        return None

# ── UTC countdown ──────────────────────────────────────────────────────────────
def _utc_reset_str() -> str:
    try:
        now = datetime.now(timezone.utc)
        nxt = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        diff = nxt - now
        h, rem = divmod(int(diff.total_seconds()), 3600)
        m, s   = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
    except Exception:
        return "--:--:--"

# ═════════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════════
async def _show_fatal(page: ft.Page, err: Exception):
    try:
        page.bgcolor = "#07071a"
        page.controls.clear()
        page.add(ft.Container(
            content=ft.Column([
                ft.Text("⚠ FATAL STARTUP ERROR", size=15, color="#ff3355",
                        weight=ft.FontWeight.BOLD),
                ft.Text(str(err), size=11, color="#ff9944", selectable=True),
                ft.Text(traceback.format_exc(), size=9, color="#aaaaaa",
                        selectable=True),
            ], spacing=6, scroll=ft.ScrollMode.AUTO),
            padding=16, expand=True, bgcolor="#07071a",
        ))
        page.update()
    except Exception:
        pass


async def main(page: ft.Page):
    try:
        _init_db()
    except Exception as _e:
        await _show_fatal(page, _e)
        return
    try:
        prefs = _load_prefs()
    except Exception as _e:
        await _show_fatal(page, _e)
        return
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
        "loading":          False,
        "news_loading":     False,
        "last_refresh":     "",
        "using_cache":      False,
        "update_info":      None,
        "update_dismissed": False,
        "builds_tab":       "meta",
        "builds_cls":       "all",
        "meta_imgs":            {},
        "community_builds":     [],
        "hero_search_results":  [],
        "hero_search_loading":  False,
        "hero_search_query":    "",
        "hero_search_origin":   "build_create",
        "hero_search_field":    "hero",
        "form_data": {
            "id": None, "name": "", "cls": "Soldier",
            "hero": "", "hero_img": "",
            "weapon1": "", "weapon1_img": "",
            "weapon2": "", "weapon2_img": "",
            "skills": "", "desc": "", "purpose": "", "tags": [],
        },
    }

    # ── Page setup ─────────────────────────────────────────────────────────────
    page.title   = f"{APP_NAME} v{APP_VERSION}"
    page.bgcolor = _c("bg")
    page.padding = 0
    try:
        page.window.width  = 400
        page.window.height = 820
    except Exception:
        pass

    # ── UI helpers ─────────────────────────────────────────────────────────────
    def _card(*children, padding=12, margin=4, border_color=None):
        return ft.Container(
            content=ft.Column(list(children), spacing=6, tight=True),
            bgcolor=_c("card"),
            border=_border_all(1, border_color or _c("border")),
            border_radius=12,
            padding=padding,
            margin=margin,
        )

    def _btn(label, on_click=None, color=None, width=None, icon=None, url=None):
        bg = color or _c("orange")
        return ft.FilledButton(
            content=ft.Text(label, color=_btn_text_color(bg), weight=ft.FontWeight.W_600),
            icon=icon, on_click=on_click, url=url,
            bgcolor=bg, width=width,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        )

    def _toggle_btn(label, active: bool, on_click):
        return ft.OutlinedButton(
            content=ft.Text(label, color=_c("orange") if active else _c("sub")),
            on_click=on_click,
            style=ft.ButtonStyle(
                side=ft.BorderSide(2 if active else 1,
                                   _c("orange") if active else _c("border")),
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

    def _chip(label, active: bool, on_select, color=None):
        return ft.Chip(
            label=ft.Text(label, size=12),
            selected=active,
            on_select=on_select,
            selected_color=color or _c("orange"),
            check_color="#ffffff",
        )

    def _hdr(text, size=18, color=None):
        return ft.Text(text, size=size, weight=ft.FontWeight.BOLD,
                       color=color or _c("orange"))

    def _sub(text, size=12):
        return ft.Text(text, size=size, color=_c("sub"))

    def _txt(text, size=14, color=None):
        return ft.Text(text, size=size, color=color or _c("text"))

    def _divider():
        return ft.Divider(height=1, color=_c("border"))

    def _footer():
        return ft.Container(
            content=ft.Text(
                COPYRIGHT, size=11,
                color=_c("footer"),
                weight=ft.FontWeight.W_600,
                text_align=ft.TextAlign.CENTER,
            ),
            padding=_pad_sym(vertical=10),
            alignment=_ALIGN_CENTER,
        )

    def _hero_img(url: str, size=72):
        if url:
            return ft.Image(
                src=url, width=size, height=size,
                fit=ft.BoxFit.CONTAIN, border_radius=8,
                error_content=ft.Container(
                    width=size, height=size, bgcolor=_c("surface"),
                    border_radius=8,
                    content=ft.Icon(ft.Icons.PERSON, size=size // 2,
                                    color=_c("sub")),
                    alignment=_ALIGN_CENTER,
                ),
            )
        return ft.Container(
            width=size, height=size, bgcolor=_c("surface"),
            border_radius=8,
            content=ft.Icon(ft.Icons.PERSON, size=size // 2, color=_c("sub")),
            alignment=_ALIGN_CENTER,
        )

    def _tag_chip(tag_key: str):
        colors = {
            "vbucks": _c("vbucks"), "endgame": _c("red"),
            "dps":    _c("cyan"),   "team":    _c("purple"),
            "speed":  _c("green"),  "farm":    _c("yellow"),
            "afk":    _c("sub"),    "beginner":_c("green"),
            "expert": _c("orange"),
        }
        color = colors.get(tag_key, _c("sub"))
        return ft.Container(
            content=ft.Text(t(f"tag_{tag_key}"), size=10,
                            color=_btn_text_color(color)),
            bgcolor=color, border_radius=10,
            padding=_pad_sym(horizontal=8, vertical=3),
        )

    # ── Navigation ─────────────────────────────────────────────────────────────
    TAB_ORDER = ["home", "news", "builds", "guide", "settings"]

    def navigate(screen: str):
        state["screen"] = screen
        render()

    def _nav_bar():
        cur = TAB_ORDER.index(state["screen"]) if state["screen"] in TAB_ORDER else 0

        def on_nav(e):
            navigate(TAB_ORDER[e.control.selected_index])

        # Use explicit ft.Icon with colors so inactive tabs are always legible
        # (Flutter default makes them near-invisible in light mode)
        _unsel = _c("sub")   # readable in both dark and light
        _sel   = "#ffffff"   # white inside the orange indicator pill
        return ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icon(ft.Icons.HOME_OUTLINED, color=_unsel),
                    selected_icon=ft.Icon(ft.Icons.HOME, color=_sel),
                    label=t("home")),
                ft.NavigationBarDestination(
                    icon=ft.Icon(ft.Icons.ARTICLE_OUTLINED, color=_unsel),
                    selected_icon=ft.Icon(ft.Icons.ARTICLE, color=_sel),
                    label=t("news")),
                ft.NavigationBarDestination(
                    icon=ft.Icon(ft.Icons.HANDYMAN_OUTLINED, color=_unsel),
                    selected_icon=ft.Icon(ft.Icons.HANDYMAN, color=_sel),
                    label=t("builds")),
                ft.NavigationBarDestination(
                    icon=ft.Icon(ft.Icons.MENU_BOOK_OUTLINED, color=_unsel),
                    selected_icon=ft.Icon(ft.Icons.MENU_BOOK, color=_sel),
                    label=t("guide")),
                ft.NavigationBarDestination(
                    icon=ft.Icon(ft.Icons.SETTINGS_OUTLINED, color=_unsel),
                    selected_icon=ft.Icon(ft.Icons.SETTINGS, color=_sel),
                    label=t("settings")),
            ],
            selected_index=cur,
            on_change=on_nav,
            bgcolor=_c("surface"),
            indicator_color=_c("orange"),
            label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
        )

    def _appbar(title_txt: str, back_screen: str = None):
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

        leading = None
        if back_screen:
            def go_back(e):
                navigate(back_screen)
            leading = ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=_c("orange"),
                on_click=go_back,
            )

        return ft.AppBar(
            leading=leading,
            title=ft.Text(title_txt, size=16, weight=ft.FontWeight.BOLD,
                          color=_c("orange")),
            bgcolor=_c("surface"),
            actions=[
                ft.IconButton(icon=ft.Icons.TRANSLATE,
                              tooltip="ES / EN",
                              icon_color=_c("cyan"),
                              on_click=flip_lang),
                ft.IconButton(
                    icon=ft.Icons.DARK_MODE if THEME[0] == "dark" else ft.Icons.LIGHT_MODE,
                    tooltip=t("theme"),
                    icon_color=_c("yellow"),
                    on_click=toggle_theme),
            ],
        )

    # ── Async tasks ────────────────────────────────────────────────────────────
    async def _task_load_alerts(force=False):
        cache = _load_cache()
        if not force and not _alerts_cache_stale(cache) and cache.get("alerts"):
            state["alerts"]      = cache["alerts"]
            state["using_cache"] = True
            state["last_refresh"] = cache.get("alerts_ts", "?")[:16]
            render()
            return
        state["loading"]     = True
        state["using_cache"] = False
        render()
        alerts = await asyncio.to_thread(_sync_fetch_alerts)
        if alerts:
            state["alerts"]       = alerts
            ts                    = datetime.now(timezone.utc).isoformat()
            state["last_refresh"] = ts[:16]
            state["using_cache"]  = False
            cache["alerts"]       = alerts
            cache["alerts_ts"]    = ts
            _save_cache(cache)
        else:
            if cache.get("alerts"):
                state["alerts"]       = cache["alerts"]
                state["using_cache"]  = True
                state["last_refresh"] = cache.get("alerts_ts", "?")[:16]
        state["loading"] = False
        render()

    async def _task_load_news(force=False):
        cache = _load_cache()
        if not force and cache.get("news"):
            state["news"] = cache["news"]
            render()
            return
        state["news_loading"] = True
        render()
        news = await asyncio.to_thread(_sync_fetch_news)
        if news:
            state["news"] = news
            cache["news"] = news
            _save_cache(cache)
        elif cache.get("news"):
            state["news"] = cache["news"]
        state["news_loading"] = False
        render()

    async def _task_check_update():
        info = await asyncio.to_thread(_sync_check_update)
        if info:
            state["update_info"]      = info
            state["update_dismissed"] = False
            render()

    async def _task_search_heroes(query: str):
        state["hero_search_loading"] = True
        state["hero_search_results"] = []
        render()
        results = await asyncio.to_thread(_sync_search_heroes, query)
        state["hero_search_results"] = results
        state["hero_search_loading"] = False
        render()

    async def _task_load_meta_imgs():
        # Pre-load BR cosmetics list (needed for hero image search)
        await asyncio.to_thread(_sync_load_br_cosmetics)
        # Collect unique hero names from all meta builds
        names = list({b["hero"] for builds in BUILDS.values() for b in builds})
        for name in names:
            if name in state["meta_imgs"]:
                continue
            results = await asyncio.to_thread(_sync_search_heroes, name)
            if results:
                state["meta_imgs"][name] = results[0].get("image", "")
            else:
                state["meta_imgs"][name] = ""
        render()

    async def _task_load_community_builds():
        if not _REQ_OK:
            return
        try:
            data = await asyncio.to_thread(
                lambda: requests.get(_COMMUNITY_BUILDS_URL, timeout=10).json()
            )
            if isinstance(data, list):
                state["community_builds"] = data
                render()
        except Exception:
            pass

    async def _auto_refresh_loop():
        while True:
            await asyncio.sleep(3600)
            await _task_load_alerts(force=True)

    # Dict to hold a live reference to the clock Text control
    _clock_ctrl: dict = {"ref": None}

    async def _task_clock_ticker():
        """Update countdown clock every second without full render."""
        while True:
            await asyncio.sleep(1)
            if state["screen"] == "home" and _clock_ctrl.get("ref"):
                try:
                    _clock_ctrl["ref"].value = f"⏱ {_utc_reset_str()}"
                    page.update()
                except Exception:
                    pass

    # ── HOME screen ────────────────────────────────────────────────────────────
    def _screen_home():
        rows = []

        if state["update_info"] and not state["update_dismissed"]:
            info = state["update_info"]

            def dismiss_update(e):
                state["update_dismissed"] = True
                render()

            rows.append(ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.NEW_RELEASES, color=_c("yellow"), size=20),
                    ft.Column([
                        _txt(f"{t('update_available')}: v{info['version']}",
                             size=13, color=_c("yellow")),
                    ], expand=True, spacing=2),
                    ft.FilledButton(
                        content=ft.Text(t("download"), color="#ffffff"),
                        url=info["url"],
                        bgcolor=_c("green"),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    ),
                    ft.IconButton(ft.Icons.CLOSE, on_click=dismiss_update,
                                  icon_color=_c("sub"), icon_size=16),
                ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=_c("banner"),
                border=_border_all(1, _c("yellow")),
                border_radius=8, padding=8,
                margin=_margin_b(bottom=4),
            ))

        def do_refresh(e):
            async def _r(): await _task_load_alerts(force=True)
            page.run_task(_r)

        def toggle_vbucks(e):
            state["vbucks_only"] = not state["vbucks_only"]
            render()

        def on_region(e):
            state["region"] = e.control.value
            prefs["region"] = state["region"]
            _save_prefs(prefs)
            async def _r(): await _task_load_alerts(force=True)
            page.run_task(_r)

        _clock_text = ft.Text(f"⏱ {_utc_reset_str()}", size=12, color=_c("cyan"))
        _clock_ctrl["ref"] = _clock_text

        rows.append(ft.Row([
            _hdr(t("daily_alerts")),
            _clock_text,
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN))

        rows.append(ft.Row([
            _toggle_btn(t("vbucks_only"), state["vbucks_only"], toggle_vbucks),
            ft.Dropdown(
                value=state["region"],
                options=[ft.dropdown.Option(r) for r in _REGIONS],
                on_select=on_region,
                width=115, text_size=13,
                border_color=_c("border"), color=_c("text"),
            ),
            _btn(t("refresh"), do_refresh, icon=ft.Icons.REFRESH),
        ], spacing=8, wrap=True))

        if state["using_cache"] and state["last_refresh"]:
            rows.append(_sub(f"({t('alerts_cached')} · {state['last_refresh']})"))
        elif state["last_refresh"]:
            rows.append(_sub(f"{t('last_refresh')}: {state['last_refresh']}"))

        if state["loading"]:
            rows.append(ft.ProgressRing(width=36, height=36, stroke_width=3,
                                        color=_c("orange")))
        elif not state["alerts"]:
            rows.append(_card(_txt(t("no_alerts"), color=_c("sub"))))
        else:
            shown = [a for a in state["alerts"]
                     if not state["vbucks_only"] or a.get("vbucks")]
            for a in shown[:35]:
                reward_chips = []
                for rw in a.get("rewards", []):
                    emoji, label = _reward_label(rw["type"])
                    qty = rw["quantity"]
                    if rw.get("vbucks"):
                        reward_chips.append(ft.Container(
                            content=ft.Row([
                                ft.Text(emoji, size=13),
                                ft.Text(f"{label} ×{qty}", size=11,
                                        color="#000000",
                                        weight=ft.FontWeight.BOLD),
                            ], spacing=3, tight=True),
                            bgcolor=_c("gold"), border_radius=8,
                            padding=_pad_sym(horizontal=7, vertical=3),
                        ))
                    else:
                        reward_chips.append(ft.Container(
                            content=ft.Row([
                                ft.Text(emoji, size=12),
                                ft.Text(f"{label} ×{qty}", size=10,
                                        color=_c("sub")),
                            ], spacing=3, tight=True),
                            bgcolor=_c("surface"), border_radius=6,
                            border=_border_all(1, _c("border")),
                            padding=_pad_sym(horizontal=5, vertical=2),
                        ))
                rows.append(_card(
                    ft.Row([
                        ft.Icon(
                            ft.Icons.BOLT if a.get("vbucks") else ft.Icons.FLAG,
                            color=_c("gold") if a.get("vbucks") else _c("orange"),
                            size=20,
                        ),
                        _txt(a.get("name", ""), size=13),
                    ], spacing=6),
                    _sub(a.get("zone", ""), size=11),
                    ft.Row(reward_chips, wrap=True, spacing=4),
                    border_color=_c("gold") if a.get("vbucks") else None,
                ))

        rows.append(_footer())
        return ft.Column(rows, spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    # ── NEWS screen ────────────────────────────────────────────────────────────
    def _screen_news():
        rows = []

        def do_refresh(e):
            async def _r(): await _task_load_news(force=True)
            page.run_task(_r)

        rows.append(ft.Row([
            ft.IconButton(ft.Icons.REFRESH, on_click=do_refresh,
                          icon_color=_c("cyan"), icon_size=20),
        ], alignment=ft.MainAxisAlignment.END))

        if state["news_loading"]:
            rows.append(ft.ProgressRing(width=36, height=36, stroke_width=3,
                                        color=_c("orange")))
        elif not state["news"]:
            rows.append(_card(_txt(t("no_news"), color=_c("sub"))))
        else:
            for item in state["news"]:
                card_children = []
                if item.get("image"):
                    card_children.append(ft.Container(
                        content=ft.Image(
                            src=item["image"],
                            fit=ft.BoxFit.COVER,
                            width=9999,
                            height=170,
                            error_content=ft.Container(
                                height=170, bgcolor=_c("surface"),
                                content=ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED,
                                                size=40, color=_c("sub")),
                                alignment=_ALIGN_CENTER,
                            ),
                        ),
                        border_radius=ft.BorderRadius(
                            top_left=10, top_right=10,
                            bottom_left=0, bottom_right=0),
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    ))
                if item.get("title"):
                    card_children.append(_hdr(item["title"], size=14))
                if item.get("body"):
                    card_children.append(_txt(item["body"], size=12,
                                              color=_c("sub")))
                rows.append(ft.Container(
                    content=ft.Column(card_children, spacing=8, tight=True),
                    bgcolor=_c("card"),
                    border=_border_all(1, _c("border")),
                    border_radius=12,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    margin=4,
                    padding=_pad_only(bottom=10),
                ))

        rows.append(_footer())
        return ft.Column(rows, spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    # ── BUILDS screen ──────────────────────────────────────────────────────────
    def _screen_builds():
        rows = []

        def set_tab(tab):
            def _h(e):
                state["builds_tab"] = tab
                render()
            return _h

        rows.append(ft.Row([
            _toggle_btn(t("meta_builds"),       state["builds_tab"] == "meta",
                        set_tab("meta")),
            _toggle_btn(t("my_builds"),         state["builds_tab"] == "my",
                        set_tab("my")),
            _toggle_btn(t("community_builds"),  state["builds_tab"] == "community",
                        set_tab("community")),
        ], spacing=8, wrap=True))
        rows.append(_divider())

        if state["builds_tab"] == "meta":
            rows.extend(_builds_meta())
        elif state["builds_tab"] == "community":
            rows.extend(_builds_community())
        else:
            rows.extend(_builds_my())

        rows.append(_footer())
        return ft.Column(rows, spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    def _builds_meta():
        rows = []

        def set_cls(cls):
            def _h(e):
                state["builds_cls"] = cls
                render()
            return _h

        chip_labels = {
            "all": t("all_classes"),
            "Constructor": "Constructor", "Ninja": "Ninja",
            "Outlander": "Outlander",     "Soldier": "Soldier",
        }
        rows.append(ft.Row(
            [_chip(chip_labels[c], state["builds_cls"] == c, set_cls(c))
             for c in HERO_CLASSES],
            wrap=True, spacing=4,
        ))

        for cls_name, blist in BUILDS.items():
            if state["builds_cls"] != "all" and state["builds_cls"] != cls_name:
                continue
            cls_colors = {
                "Constructor": _c("cyan"),   "Ninja": _c("pink"),
                "Outlander":   _c("yellow"), "Soldier": _c("green"),
            }
            rows.append(_hdr(cls_name, size=15,
                             color=cls_colors.get(cls_name, _c("orange"))))
            for b in blist:
                lang = LANG[0]
                desc    = b[f"desc_{lang}"]
                purpose = b[f"purpose_{lang}"]
                support = b[f"support_{lang}"]
                weapons = b[f"weapons_{lang}"]
                tags    = b.get("tags", [])
                hero_img_url = state["meta_imgs"].get(b["hero"], "")
                rows.append(_card(
                    ft.Row([
                        _hero_img(hero_img_url, size=56),
                        ft.Column([
                            _hdr(b["name"], size=14),
                            ft.Row([
                                ft.Container(
                                    content=ft.Text(cls_name[0], size=9,
                                                   weight=ft.FontWeight.BOLD,
                                                   color="#ffffff"),
                                    bgcolor=cls_colors.get(cls_name, _c("orange")),
                                    width=18, height=18, border_radius=9,
                                    alignment=_ALIGN_CENTER,
                                ),
                                _sub(b["hero"], size=12),
                            ], spacing=4,
                               vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        ], expand=True, spacing=2),
                    ], spacing=10,
                       vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    _divider(),
                    ft.Row([
                        ft.Icon(ft.Icons.PEOPLE, size=14, color=_c("purple")),
                        ft.Text(support, size=11, color=_c("sub"), expand=True),
                    ], spacing=6),
                    ft.Row([
                        ft.Icon(ft.Icons.SPORTS_ESPORTS, size=14,
                                color=_c("cyan")),
                        ft.Text(weapons, size=11, color=_c("sub"), expand=True),
                    ], spacing=6),
                    ft.Row(
                        [ft.Container(
                            content=ft.Text(sk, size=10, color=_c("text")),
                            bgcolor=_c("surface"),
                            border=_border_all(1, _c("border")),
                            border_radius=6,
                            padding=_pad_sym(horizontal=6, vertical=2),
                         ) for sk in b["skills"]],
                        wrap=True, spacing=4,
                    ),
                    _txt(desc, size=12),
                    ft.Row([
                        ft.Icon(ft.Icons.STAR, size=12, color=_c("yellow")),
                        _txt(purpose, size=11, color=_c("yellow")),
                    ], spacing=4),
                    ft.Row([_tag_chip(tg) for tg in tags], wrap=True, spacing=4),
                ))
        return rows

    def _builds_my():
        rows = []
        builds = _db_all_builds()

        def go_create(e):
            state["form_data"] = {
                "id": None, "name": "", "cls": "Soldier",
                "hero": "", "hero_img": "",
                "weapon1": "", "weapon1_img": "",
                "weapon2": "", "weapon2_img": "",
                "skills": "", "desc": "", "purpose": "", "tags": [],
            }
            navigate("build_create")

        rows.append(ft.Row([
            _hdr(t("my_builds")),
            _btn(t("new_build"), go_create, icon=ft.Icons.ADD),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN))

        if not builds:
            rows.append(_card(_txt(t("no_my_builds"), color=_c("sub"))))
            return rows

        for b in builds:
            bid = b["id"]
            skills = []
            try:
                skills = json.loads(b.get("skills", "[]"))
            except Exception:
                pass
            tags = []
            try:
                tags = json.loads(b.get("tags", "[]"))
            except Exception:
                pass

            def go_edit(bid=bid):
                def _h(e):
                    rec = _db_get_build(bid)
                    if not rec:
                        return
                    sk = []
                    try:
                        sk = json.loads(rec.get("skills", "[]"))
                    except Exception:
                        pass
                    tgs = []
                    try:
                        tgs = json.loads(rec.get("tags", "[]"))
                    except Exception:
                        pass
                    state["form_data"] = {
                        "id":          rec["id"],
                        "name":        rec.get("name", ""),
                        "cls":         rec.get("cls", "Soldier"),
                        "hero":        rec.get("hero", ""),
                        "hero_img":    rec.get("hero_img", ""),
                        "weapon1":     rec.get("weapon1", ""),
                        "weapon1_img": rec.get("weapon1_img", ""),
                        "weapon2":     rec.get("weapon2", ""),
                        "weapon2_img": rec.get("weapon2_img", ""),
                        "skills":      ", ".join(sk),
                        "desc":        rec.get("desc", ""),
                        "purpose":     rec.get("purpose", ""),
                        "tags":        tgs,
                    }
                    navigate("build_edit")
                return _h

            def do_delete(bid=bid):
                def _h(e):
                    _db_delete_build(bid)
                    render()
                return _h

            hero_img_url = b.get("hero_img", "")
            rows.append(_card(
                ft.Row([
                    _hero_img(hero_img_url, size=64),
                    ft.Column([
                        _hdr(b["name"], size=14),
                        _sub(f"{b['cls']}  ·  {b.get('hero','')}", size=12),
                        _sub(b.get("created", ""), size=10),
                    ], expand=True, spacing=2),
                    ft.Row([
                        ft.IconButton(ft.Icons.EDIT, on_click=go_edit(),
                                      icon_color=_c("cyan"), icon_size=18),
                        ft.IconButton(ft.Icons.DELETE, on_click=do_delete(),
                                      icon_color=_c("red"), icon_size=18),
                    ], spacing=0),
                ], spacing=10,
                   vertical_alignment=ft.CrossAxisAlignment.START),
                _divider() if (b.get("weapon1") or skills or b.get("desc")) else ft.Text(""),
                ft.Row([
                    ft.Icon(ft.Icons.SPORTS_ESPORTS, size=13, color=_c("cyan")),
                    _txt(b.get("weapon1", ""), size=12),
                ], spacing=6) if b.get("weapon1") else ft.Text(""),
                ft.Row(
                    [ft.Container(
                        content=ft.Text(sk, size=10, color=_c("text")),
                        bgcolor=_c("surface"),
                        border=_border_all(1, _c("purple")),
                        border_radius=6,
                        padding=_pad_sym(horizontal=6, vertical=2),
                     ) for sk in skills],
                    wrap=True, spacing=4,
                ) if skills else ft.Text(""),
                _txt(b.get("desc", ""), size=12, color=_c("sub"))
                    if b.get("desc") else ft.Text(""),
                ft.Row([_tag_chip(tg) for tg in tags], wrap=True, spacing=4)
                    if tags else ft.Text(""),
            ))
        return rows

    def _builds_community():
        rows = [_hdr(t("community_builds"))]
        builds = state.get("community_builds", [])
        if not builds:
            rows.append(_card(_sub(
                "Cargando builds de la comunidad..." if LANG[0] == "es"
                else "Loading community builds..."
            )))
            return rows
        for b in builds:
            lang_key = "es" if LANG[0] == "es" else "en"
            desc = b.get(f"desc_{lang_key}") or b.get("desc_es") or b.get("desc_en", "")
            purpose = b.get(f"purpose_{lang_key}") or b.get("purpose_es") or ""
            tags = b.get("tags", [])
            author = b.get("author", "")
            votes = b.get("votes", 0)
            skills = b.get("skills", [])
            cls = b.get("cls", "")
            hero_name = b.get("hero", "")
            hero_img_url = state["meta_imgs"].get(hero_name, "")
            cls_letter = cls[0].upper() if cls else "?"
            cls_colors = {"C": _c("cyan"), "N": _c("purple"), "O": _c("yellow"), "S": _c("green")}
            cls_color = cls_colors.get(cls_letter, _c("sub"))
            rows.append(_card(
                ft.Row([
                    _hero_img(hero_img_url, size=52),
                    ft.Column([
                        _hdr(b.get("name", ""), size=15),
                        ft.Row([
                            ft.Container(
                                content=ft.Text(cls_letter, size=10, color="#fff",
                                                weight=ft.FontWeight.BOLD),
                                bgcolor=cls_color, border_radius=99,
                                width=20, height=20, alignment=_ALIGN_CENTER,
                            ),
                            _txt(hero_name, size=12, color=_c("sub")),
                            _txt(f"👍 {votes}", size=11, color=_c("gold")),
                            _sub(f"@{author}", size=10) if author else ft.Text(""),
                        ], spacing=6),
                    ], spacing=3, expand=True),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.START),
                _divider(),
                ft.Row([
                    ft.Icon(ft.Icons.SPORTS_ESPORTS, size=13, color=_c("cyan")),
                    _txt(b.get("weapon1",""), size=12),
                ], spacing=6) if b.get("weapon1") else ft.Text(""),
                ft.Row(
                    [ft.Container(
                        content=ft.Text(sk, size=10, color=_c("text")),
                        bgcolor=_c("surface"),
                        border=_border_all(1, _c("purple")),
                        border_radius=6,
                        padding=_pad_sym(horizontal=6, vertical=2),
                    ) for sk in skills],
                    wrap=True, spacing=4,
                ) if skills else ft.Text(""),
                _txt(desc, size=12, color=_c("sub")) if desc else ft.Text(""),
                _sub(purpose, size=11) if purpose else ft.Text(""),
                ft.Row([_tag_chip(tg) for tg in tags], wrap=True, spacing=4)
                    if tags else ft.Text(""),
            ))
        return rows

    # ── BUILD FORM ─────────────────────────────────────────────────────────────
    def _screen_build_form():
        fd = state["form_data"]
        is_edit = state["screen"] == "build_edit"

        name_field   = ft.TextField(label=t("build_name"), value=fd["name"],
                                    border_color=_c("border"), color=_c("text"),
                                    label_style=ft.TextStyle(color=_c("sub")))
        class_dd     = ft.Dropdown(
            label=t("build_class"), value=fd["cls"],
            options=[ft.dropdown.Option(k) for k in BUILDS.keys()],
            border_color=_c("border"), color=_c("text"),
            label_style=ft.TextStyle(color=_c("sub")),
        )
        hero_field   = ft.TextField(label=t("build_hero"), value=fd["hero"],
                                    border_color=_c("border"), color=_c("text"),
                                    label_style=ft.TextStyle(color=_c("sub")))
        hero_img_field = ft.TextField(
            label=t("build_hero_img"), value=fd["hero_img"],
            hint_text="https://...",
            border_color=_c("border"), color=_c("text"),
            label_style=ft.TextStyle(color=_c("sub")), expand=True,
        )
        weapon1_field = ft.TextField(label=t("build_weapon1"), value=fd["weapon1"],
                                     border_color=_c("border"), color=_c("text"),
                                     label_style=ft.TextStyle(color=_c("sub")))
        weapon1_img_field = ft.TextField(
            label=t("build_weapon1_img"), value=fd["weapon1_img"],
            hint_text="https://...",
            border_color=_c("border"), color=_c("text"),
            label_style=ft.TextStyle(color=_c("sub")), expand=True,
        )
        weapon2_field = ft.TextField(label=t("build_weapon2"), value=fd["weapon2"],
                                     border_color=_c("border"), color=_c("text"),
                                     label_style=ft.TextStyle(color=_c("sub")))
        skills_field  = ft.TextField(label=t("build_skills"), value=fd["skills"],
                                     multiline=True, min_lines=2,
                                     border_color=_c("border"), color=_c("text"),
                                     label_style=ft.TextStyle(color=_c("sub")))
        desc_field    = ft.TextField(label=t("build_desc"), value=fd["desc"],
                                     multiline=True, min_lines=3,
                                     border_color=_c("border"), color=_c("text"),
                                     label_style=ft.TextStyle(color=_c("sub")))
        purpose_field = ft.TextField(label=t("build_purpose"), value=fd["purpose"],
                                     multiline=True, min_lines=2,
                                     border_color=_c("border"), color=_c("text"),
                                     label_style=ft.TextStyle(color=_c("sub")))

        selected_tags = list(fd["tags"])
        tag_row_ref = ft.Ref[ft.Row]()

        def _build_tag_row():
            def toggle_tag(tag):
                def _h(e):
                    if tag in selected_tags:
                        selected_tags.remove(tag)
                    else:
                        selected_tags.append(tag)
                    tag_row_ref.current.controls = _tag_chips()
                    page.update()
                return _h

            return [_chip(t(f"tag_{tg}"), tg in selected_tags, toggle_tag(tg))
                    for tg in BUILD_TAGS]

        def _tag_chips():
            return _build_tag_row()

        def _persist_form():
            fd["name"]        = name_field.value or ""
            fd["cls"]         = class_dd.value or "Soldier"
            fd["hero"]        = hero_field.value or ""
            fd["hero_img"]    = hero_img_field.value or ""
            fd["weapon1"]     = weapon1_field.value or ""
            fd["weapon1_img"] = weapon1_img_field.value or ""
            fd["weapon2"]     = weapon2_field.value or ""
            fd["skills"]      = skills_field.value or ""
            fd["desc"]        = desc_field.value or ""
            fd["purpose"]     = purpose_field.value or ""
            fd["tags"]        = list(selected_tags)

        def go_search_hero(field_key: str):
            def _h(e):
                _persist_form()
                state["hero_search_origin"] = state["screen"]
                state["hero_search_field"]  = field_key
                state["hero_search_results"] = []
                state["hero_search_query"]   = ""
                navigate("hero_search")
            return _h

        def do_save(e):
            _persist_form()
            skills_list = [s.strip() for s in fd["skills"].split(",")
                           if s.strip()]
            b = {
                "name":        fd["name"] or t("new_build"),
                "cls":         fd["cls"],
                "hero":        fd["hero"],
                "hero_img":    fd["hero_img"],
                "weapon1":     fd["weapon1"],
                "weapon1_img": fd["weapon1_img"],
                "weapon2":     fd["weapon2"],
                "weapon2_img": fd["weapon2_img"],
                "skills":      skills_list,
                "desc":        fd["desc"],
                "purpose":     fd["purpose"],
                "tags":        fd["tags"],
            }
            if is_edit and fd["id"]:
                _db_update_build(fd["id"], b)
            else:
                _db_save_build(b)
            state["builds_tab"] = "my"
            navigate("builds")

        def do_cancel(e):
            state["builds_tab"] = "my"
            navigate("builds")

        hero_preview = _hero_img(fd["hero_img"], size=80) if fd.get("hero_img") else ft.Container()
        w1_preview   = _hero_img(fd["weapon1_img"], size=60) if fd.get("weapon1_img") else ft.Container()

        title = t("edit") + " Build" if is_edit else t("new_build")
        return ft.Column([
            ft.Row([_hdr(title, size=16)], alignment=ft.MainAxisAlignment.CENTER),
            _divider(),
            name_field,
            class_dd,
            _hdr(t("build_hero"), size=13, color=_c("cyan")),
            hero_field,
            ft.Row([
                hero_img_field,
                ft.IconButton(ft.Icons.IMAGE_SEARCH, icon_color=_c("cyan"),
                              tooltip=t("search_hero"),
                              on_click=go_search_hero("hero_img")),
            ], spacing=6),
            hero_preview,
            _divider(),
            _hdr(t("weapons"), size=13, color=_c("cyan")),
            weapon1_field,
            ft.Row([
                weapon1_img_field,
                ft.IconButton(ft.Icons.IMAGE_SEARCH, icon_color=_c("sub"),
                              tooltip=t("search_hero"),
                              on_click=go_search_hero("weapon1_img")),
            ], spacing=6),
            w1_preview,
            weapon2_field,
            _divider(),
            skills_field,
            desc_field,
            purpose_field,
            _hdr(t("build_tags"), size=13, color=_c("cyan")),
            ft.Row(ref=tag_row_ref, controls=_tag_chips(), wrap=True, spacing=4),
            _divider(),
            ft.Row([
                _btn(t("save"),   do_save,   color=_c("green")),
                _btn(t("cancel"), do_cancel, color=_c("sub")),
            ], spacing=10),
        ], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

    # ── HERO SEARCH screen ────────────────────────────────────────────────────
    def _screen_hero_search():
        query_field = ft.TextField(
            label=t("hero_placeholder"),
            value=state["hero_search_query"],
            border_color=_c("border"), color=_c("text"),
            label_style=ft.TextStyle(color=_c("sub")),
            expand=True,
            autofocus=True,
        )

        def do_search(e):
            q = (query_field.value or "").strip()
            if not q:
                return
            state["hero_search_query"] = q
            async def _s(qry=q): await _task_search_heroes(qry)
            page.run_task(_s)

        def go_back(e):
            navigate(state["hero_search_origin"])

        results = []
        if state["hero_search_loading"]:
            results.append(ft.ProgressRing(width=36, height=36, stroke_width=3,
                                           color=_c("orange")))
        elif state["hero_search_results"]:
            for h in state["hero_search_results"]:
                name    = h["name"]
                img_url = h["image"]

                def on_select(n=name, u=img_url):
                    def _h(e):
                        fd = state["form_data"]
                        field = state["hero_search_field"]
                        if field == "hero_img":
                            fd["hero_img"] = u
                            fd["hero"]     = n
                        elif field == "weapon1_img":
                            fd["weapon1_img"] = u
                            if not fd["weapon1"]:
                                fd["weapon1"] = n
                        navigate(state["hero_search_origin"])
                    return _h

                results.append(ft.Container(
                    content=ft.Row([
                        _hero_img(img_url, size=56),
                        _txt(name, size=13, color=_c("text")),
                        ft.FilledButton(
                            content=ft.Text(t("select"), color="#ffffff"),
                            on_click=on_select(),
                            bgcolor=_c("orange"),
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8)),
                        ),
                    ], spacing=10,
                       vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=_c("card"),
                    border=_border_all(1, _c("border")),
                    border_radius=10,
                    padding=10, margin=4,
                ))
        elif state["hero_search_query"] and not state["hero_search_loading"]:
            results.append(_txt(t("no_hero_results"), color=_c("sub")))

        return ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, icon_color=_c("orange"),
                              on_click=go_back),
                _hdr(t("hero_search_title"), size=15),
            ], spacing=4),
            _divider(),
            ft.Row([
                query_field,
                ft.IconButton(ft.Icons.SEARCH, icon_color=_c("cyan"),
                              on_click=do_search),
            ], spacing=6),
            _sub("Powered by fortnite-api.com", size=10),
            *results,
        ], spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    # ── GUIDE screen ──────────────────────────────────────────────────────────
    def _screen_guide():
        sections = []
        for title_s, body_s in GUIDE[LANG[0]]:
            sections.append(ft.ExpansionTile(
                title=ft.Text(title_s, size=14, weight=ft.FontWeight.BOLD,
                              color=_c("cyan")),
                controls=[
                    ft.Container(
                        content=ft.Text(body_s, size=12, color=_c("text")),
                        padding=_pad_only(left=8, right=8, bottom=10),
                    )
                ],
                bgcolor=_c("card"),
                collapsed_bgcolor=_c("card"),
                icon_color=_c("orange"),
                collapsed_icon_color=_c("orange"),
                text_color=_c("cyan"),
                controls_padding=0,
            ))
        sections.append(_footer())
        return ft.Column(
            sections,
            spacing=6, scroll=ft.ScrollMode.AUTO, expand=True,
        )

    # ── SETTINGS screen ───────────────────────────────────────────────────────
    def _screen_settings():
        rows = []

        def set_theme(val):
            def _h(e):
                THEME[0] = val
                prefs["theme"] = val
                _save_prefs(prefs)
                render()
            return _h

        rows.append(_card(
            _sub(t("theme")),
            ft.Row([
                _toggle_btn(t("dark"),  THEME[0] == "dark",  set_theme("dark")),
                _toggle_btn(t("light"), THEME[0] == "light", set_theme("light")),
            ], spacing=8),
        ))

        def set_lang(val):
            def _h(e):
                LANG[0] = val
                prefs["lang"] = val
                _save_prefs(prefs)
                render()
            return _h

        rows.append(_card(
            _sub(t("language")),
            ft.Row([
                _toggle_btn(t("spanish"), LANG[0] == "es", set_lang("es")),
                _toggle_btn(t("english"), LANG[0] == "en", set_lang("en")),
            ], spacing=8),
        ))

        def on_region_change(e):
            state["region"] = e.control.value
            prefs["region"] = state["region"]
            _save_prefs(prefs)

        rows.append(_card(
            _sub(t("region_lbl")),
            ft.Dropdown(
                value=state["region"],
                options=[ft.dropdown.Option(r) for r in _REGIONS],
                on_select=on_region_change,
                border_color=_c("border"), color=_c("text"),
                label_style=ft.TextStyle(color=_c("sub")),
            ),
        ))

        notif_tf = ft.TextField(
            label=t("notif_hour"), value=str(state["notif_hour"]),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=_c("border"), color=_c("text"),
            label_style=ft.TextStyle(color=_c("sub")),
        )

        def save_settings(e):
            try:
                h = max(0, min(23, int(notif_tf.value or 8)))
            except ValueError:
                h = 8
            state["notif_hour"] = h
            prefs["notif_hour"] = h
            prefs["region"]     = state["region"]
            _save_prefs(prefs)
            try:
                page.show_dialog(ft.SnackBar(
                    content=ft.Text(t("save_settings")),
                    bgcolor=_c("green"),
                ))
            except Exception:
                pass

        rows.append(_card(notif_tf, _btn(t("save_settings"), save_settings)))

        update_status = ft.Text("", size=13, color=_c("sub"))

        async def manual_check_update(e):
            update_status.value = t("checking")
            page.update()
            info = await asyncio.to_thread(_sync_check_update)
            if info:
                state["update_info"]      = info
                state["update_dismissed"] = False
                update_status.value = f"{t('update_available')}: v{info['version']}"
                update_status.color = _c("yellow")
            else:
                update_status.value = t("up_to_date")
                update_status.color = _c("green")
            page.update()

        rows.append(_card(
            ft.Row([
                _btn(t("check_update"), manual_check_update,
                     icon=ft.Icons.SYSTEM_UPDATE),
                update_status,
            ], spacing=10, wrap=True),
        ))

        genesis_ok = _verify_genesis()
        rows.append(_card(
            _hdr(t("about"), size=14),
            _sub(f"{APP_NAME}  v{APP_VERSION}"),
            _divider(),
            ft.Row([
                ft.Icon(
                    ft.Icons.VERIFIED if genesis_ok else ft.Icons.WARNING_AMBER,
                    color=_c("green") if genesis_ok else _c("red"), size=18),
                ft.Column([
                    _txt(t("genesis_valid") if genesis_ok else t("genesis_invalid"),
                         size=12,
                         color=_c("green") if genesis_ok else _c("red")),
                    _sub(f"SHA-256: {_GENESIS_SEAL[:24]}...", size=10),
                    _sub(f"Origin: {_GENESIS_COMMIT}", size=10),
                    _sub(f"Date: {_GENESIS_DATE}", size=10),
                    _sub(f"Author: {_GENESIS_AUTHOR}", size=10),
                ], spacing=2),
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.START),
        ))
        rows.append(_footer())
        return ft.Column(rows, spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    # ── Render ─────────────────────────────────────────────────────────────────
    def render():
        try:
            APP_YEAR_NOW = str(date.today().year)
            global COPYRIGHT
            COPYRIGHT = (f"Creado por: {APP_AUTHOR}   ·   "
                         f"{APP_RIGHTS}   ©{APP_YEAR_NOW}")

            page.bgcolor = _c("bg")

            screen = state["screen"]
            is_sub = screen in ("build_create", "build_edit", "hero_search")

            if screen == "home":
                content = _screen_home()
                title   = f"{APP_NAME} v{APP_VERSION}"
                appbar  = _appbar(title)
            elif screen == "news":
                content = _screen_news()
                title   = t("news_title")
                appbar  = _appbar(title)
            elif screen == "builds":
                content = _screen_builds()
                title   = t("builds")
                appbar  = _appbar(title)
            elif screen in ("build_create", "build_edit"):
                content = _screen_build_form()
                title   = APP_NAME
                appbar  = _appbar(title, back_screen="builds")
            elif screen == "hero_search":
                content = _screen_hero_search()
                title   = t("hero_search_title")
                appbar  = _appbar(title,
                                  back_screen=state["hero_search_origin"])
            elif screen == "guide":
                content = _screen_guide()
                title   = t("guide_title")
                appbar  = _appbar(title)
            elif screen == "settings":
                content = _screen_settings()
                title   = t("settings_title")
                appbar  = _appbar(title)
            else:
                content = _screen_home()
                title   = APP_NAME
                appbar  = _appbar(title)

            page.appbar         = appbar
            page.navigation_bar = None if is_sub else _nav_bar()
            page.controls.clear()
            page.add(
                ft.Container(
                    content=content,
                    bgcolor=_c("bg"),
                    padding=_pad_sym(horizontal=12, vertical=8),
                    expand=True,
                )
            )
            page.update()
        except Exception as _render_err:
            _tb = traceback.format_exc()
            try:
                page.bgcolor = "#07071a"
                page.appbar = None
                page.navigation_bar = None
                page.controls.clear()
                page.add(ft.Container(
                    content=ft.Column([
                        ft.Text("⚠ RENDER ERROR", size=15, color="#ff3355",
                                weight=ft.FontWeight.BOLD),
                        ft.Text(f"Screen: {state.get('screen','?')}",
                                size=11, color="#ffd700"),
                        ft.Text(str(_render_err), size=10, color="#ff9944",
                                selectable=True),
                        ft.Text(_tb, size=9, color="#aaaaaa", selectable=True),
                    ], spacing=6, scroll=ft.ScrollMode.AUTO),
                    padding=16, expand=True, bgcolor="#07071a",
                ))
                page.update()
            except Exception:
                pass

    # ── Startup ────────────────────────────────────────────────────────────────
    render()
    page.run_task(_task_load_alerts)
    page.run_task(_task_load_news)
    page.run_task(_task_check_update)
    page.run_task(_task_load_meta_imgs)
    page.run_task(_task_load_community_builds)
    page.run_task(_auto_refresh_loop)
    page.run_task(_task_clock_ticker)


ft.run(main)
