# STW Hub

**Fortnite: Save The World** — Companion app para Android  
Alertas diarias · Builds · Noticias · Guía · Tracker

[![Version](https://img.shields.io/badge/version-2.9.3-orange)](https://github.com/pedroespinal/STWHub/releases/latest)
[![Android](https://img.shields.io/badge/Android-7.0%2B-green)](https://github.com/pedroespinal/STWHub/releases/latest)
[![License](https://img.shields.io/badge/license-All%20rights%20reserved-red)](https://github.com/pedroespinal/STWHub)

---

## 📥 Descargar / Download

> **[⬇ Descargar STWHub-2.9.3.apk](https://github.com/pedroespinal/STWHub/releases/latest)**

Activa **"Instalar apps de fuentes desconocidas"** en Android antes de instalar.

---

## 📱 Pantallas / Screens

### 🏠 Home — Alertas Diarias
- Alertas en tiempo real desde la API oficial de Epic Games
- Filtro por mundo (Bosque Pedregoso / Villa Tablón / Cañada Canny / Cumbres de Twine)
- Filtro por tipo de misión (Sobrevivir / Recuperar / Rescatar / Defender / Campamento)
- Filtro por PL mínimo (Todo / 40+ / 70+ / 100+ / 124+ / 140+)
- Ordenar alertas (Por defecto / PL↑ / PL↓ / V-Bucks primero)
- Contador de V-Bucks disponibles hoy (por mundo y total)
- Countdown al reset UTC
- Cache offline — funciona sin red

**Sub-tabs:**
| Tab | Descripción |
|-----|-------------|
| 📋 Activas | Alertas del día con V-Bucks, PL, tipo de misión |
| ⭐ Favoritos | Alertas guardadas con nota personalizada |
| 📅 Historial | Últimos 7 días de alertas + historial de V-Bucks |
| ✅ Checklist | 7 tareas diarias STW con checkbox, reset automático UTC |

---

### ⚡ Supercargadores
- Tipo de SC correcto mostrado al instante (sin esperar red)
- Cargado desde `stw_weekly.json` bundled + actualización desde GitHub

---

### 🔧 Builds
5 pestañas:

| Pestaña | Descripción |
|---------|-------------|
| Meta Builds | Builds meta por clase (Constructor / Ninja / Explorador / Soldado) |
| Mis Builds | CRUD personal — crear, editar, ordenar (fecha/nombre/clase), compartir como imagen |
| Comunidad | Builds subidas por la comunidad, cargadas desde GitHub |
| 📦 Materiales | Tracker de recursos con metas, barra de progreso, presets y reset |
| 🪤 Trampas | Loadouts de trampas personales por mundo |

**Mis Builds incluye:**
- Crear / editar / eliminar builds
- Tags, habilidades, héroes, armas
- 📷 Generar imagen compartible (PNG 400×320, tema oscuro)
- ⬆ Subir a Comunidad directamente desde la app

**Tracker de Materiales incluye:**
- 8 presets rápidos (Madera, Ladrillo, Metal, Tuercas, Malachite, Fibrous Herb, Twine Fiber, Coal)
- Agregar material custom (emoji + nombre + cantidad objetivo)
- Barra de progreso `█████░░░░░`  +  botones +50 / -50
- Progreso total: "X/N listos ✓"
- Reset ↺ con confirmación

---

### 📰 Noticias
- Noticias oficiales STW desde fortnite-api.com
- Botón **📋 Ver Patch Notes oficiales** — abre la página de parches de Epic Games directamente

---

### 📖 Guía
4 pestañas:

| Pestaña | Descripción |
|---------|-------------|
| Mundos | 8 secciones bilingüe por zona |
| Armas | 12 armas top, filtro por tag, **comparar 2 armas** (DPS / Mag / RoF) |
| Calcular Poder | Fórmula: Héroe 25% + Arma 25% + Supervivientes 40% + Investigación 10% |
| Héroes | 6 tipos de misión — build completa: 1 principal + 5 apoyos + team perk + gadgets |

---

### ⚙️ Configuración
- Tema oscuro / claro
- Idioma Español / English (switch instantáneo)
- Región (NAE / NAW / EU / BR / OC / AS)
- Verificador de actualizaciones (GitHub Releases API)
- Firma digital SHA-256 (verificación de autoría)

---

## 🛠 Stack técnico

| Componente | Versión |
|-----------|---------|
| Python | 3.11 |
| Flet | 0.85.1 |
| SQLite | local (stwhub.db) |
| Pillow | image generation |
| requests | API calls |
| Target Android | API 35 (Android 13+) |
| Min Android | API 24 (Android 7.0) |

---

## 🗄 Base de datos (SQLite)

```sql
my_builds         -- builds personales (CRUD)
alert_favorites   -- alertas favoritas + nota personalizada
alert_history     -- historial de alertas por día/mundo
material_list     -- tracker de materiales con metas
trap_loadouts     -- loadouts de trampas por mundo
daily_tasks       -- checklist diario con estado y último reset
```

---

## 🔐 Firma Digital

```
Genesis:  stwhub-genesis-20260521
Autor:    Pedro Espinal
SHA-256:  bdeedb31e7c0e361f24a71fa9f7a14eb584d1d867bbd0f36e5b755b122166aff
```

Verificable en **Configuración → Acerca de** dentro de la app.

---

## 📦 Releases

| Versión | Build | Highlights |
|---------|-------|------------|
| **2.9.3** | 48 | Fix misión Dudebro, botón Patch Notes oficiales en Noticias |
| 2.9.2 | 47 | Fix tags, Trap Loadouts, Checklist, comparar armas, notas favoritos |
| 2.9.1 | 46 | Tracker materiales, share build imagen, builds héroes completas |
| 2.9.0 | 45 | Guía héroes por misión, historial V-Bucks 7 días |
| 2.8.4 | 44 | Contador V-Bucks, filtro PL, ordenar alertas |
| 2.8.3 | 43 | UI compacta, world dropdown, gradiente dark mode |
| 2.8.2 | 42 | Ícono V-Bucks original |
| 2.8.1 | 41 | Fondo Twine Peaks (arte Pillow) |
| 2.8.0 | 40 | Community Builds — subida directa vía GitHub Issues API |
| 2.7.x | 35–39 | Favoritos, historial, weapons DB, PL calc, bilingüe completo |

---

## ⚠️ Aviso Legal

Esta aplicación es un proyecto independiente y gratuito, creado por fans para ayudar a los jugadores de Fortnite: Save The World con sus alertas diarias, builds y progreso. No tiene ningún fin monetario, no está afiliada ni respaldada por Epic Games, y así permanecerá. Todos los datos del juego son propiedad de Epic Games.

---

*Creado por **Pedro Espinal** · Todos los derechos reservados © 2026*
