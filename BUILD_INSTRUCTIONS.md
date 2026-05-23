# STW Hub — Guía de Compilación / Build Guide

> **STW Hub v2.5.2** · Creado por: Pedro Espinal · Todos los derechos reservados © 2026

---

## Resumen de la aplicación / App Summary

| Campo / Field     | Valor / Value                     |
|-------------------|-----------------------------------|
| Framework         | Flet 0.85.1 (Python → Android)    |
| Archivo principal | `main.py`                         |
| APK mínimo        | Android 7.0 (API 24)              |
| APK objetivo      | Android 13+ (API 35)              |
| Package ID        | `com.pedroespinal.stwhub`         |
| Versión           | 2.5.2 (build 23)                  |

---

## Características / Features

- ⚡ Alertas diarias de misiones STW desde la API oficial de Epic Games
- 💰 Filtro exclusivo para misiones con V-Bucks
- 🗺️ Vista Supercargadores — todas las misiones activas ordenadas por PL
- 🔧 Builds meta (Constructor, Ninja, Explorador, Soldado) con descripción detallada
- 📰 Noticias oficiales STW vía fortnite-api.com
- 📖 Guía de usuario completa integrada en la app
- 🌍 Selector de región (NAE, NAW, EU, BR, OC, AS)
- 🌐 Bilingüe: Español / English (switch instantáneo en cualquier pantalla)
- 🎨 Dark mode neon / Light mode
- 🛡️ Firma digital SHA-256 incrustada en el código (prueba de autoría)
- 📱 Footer naranja neon: "Creado por: Pedro Espinal · Todos los derechos reservados ©{año}"
- 🔄 Cache local para uso offline después de la primera carga
- 🔐 Panel Admin (super-usuario S053xY) con overrides de misiones y héroes vía GitHub

---

## Compilar en Windows (PowerShell)

```powershell
chcp 65001 | Out-Null
cd C:\STWHub
flet build apk --artifact "STWHub-2-5-0"
```

El APK se genera en `build\apk\`.

---

## Método alternativo — Google Colab

**Sin instalar nada en tu PC — compila directamente en la nube.**

1. Abre [Google Colab](https://colab.research.google.com) en tu navegador.
2. Crea un nuevo notebook y ejecuta las celdas en orden:

```python
# Celda 1 — Instalar Flet
!pip install flet
!pip install flet[build]
```

```python
# Celda 2 — Subir archivos del proyecto
from google.colab import files
import zipfile, os

uploaded = files.upload()   # sube el ZIP con main.py, pyproject.toml, assets/
with zipfile.ZipFile(list(uploaded.keys())[0]) as z:
    z.extractall("stwhub")
os.chdir("stwhub")
```

```python
# Celda 3 — Compilar APK
!flet build apk --artifact "STWHub-2-5-0"
```

```python
# Celda 4 — Descargar el APK
from google.colab import files
import glob
for apk in glob.glob("build/**/*.apk", recursive=True):
    files.download(apk)
    print(f"Descargando: {apk}")
```

---

## Estructura de archivos / File structure

```
STWHub/
├── main.py                  # App principal (Flet)
├── pyproject.toml           # Configuracion Flet build
├── requirements.txt         # Dependencias Python
├── hero_images.json         # Overrides de imagenes de heroes (admin)
├── mission_names.json       # Overrides de nombres de misiones (admin)
├── BUILD_INSTRUCTIONS.md    # Este archivo
├── debug_missions.py        # Script de debug (solo desarrollo)
└── assets/
    ├── icon.png             # Icono 512x512
    └── presplash.png        # Splash 1024x500
```

---

## Sistema Admin (solo Pedro Espinal)

El panel admin se activa en **Configuracion > Admin**:

1. En Configuracion, en el campo **Tag del jugador**, escribe `S053xY` y guarda.
2. Aparecera el bloque Admin bloqueado (icono candado).
3. Ingresa el **codigo de activacion** (guardalo en lugar seguro).
4. Al activarse, el panel admin completo aparece.
5. Para hacer push a GitHub de los overrides, ingresa tu **PAT** de GitHub en el campo correspondiente.

Los archivos `hero_images.json` y `mission_names.json` en el repo se actualizan automaticamente y todos los usuarios reciben los cambios en su proxima sesion.

---

## Nombres de misiones (generadores Epic API)

| Abreviacion | Nombre en juego            |
|-------------|---------------------------|
| RTD / RtD   | Retrieve the Data         |
| RtL         | Ride the Lightning        |
| RtS         | Repair the Shelter        |
| DtB         | Deliver the Bomb          |
| DtE         | Eliminate & Collect       |
| EtShelter   | Evacuate the Shelter      |
| EtSurvivors | Rescue Survivors          |
| LtR         | Resupply                  |
| LtB         | Launch the Balloon        |
| PtS         | Protect Home Base         |
| 1-4 Gate(s) | Storm Gates               |
| Cat1FtS     | Fight the Storm           |
| HTM         | Hunt                      |

---

## Firma Digital / Digital Signature

```
Genesis commit : stwhub-genesis-20260521
Fecha creacion : 2026-05-21T00:00:00
Autor          : Pedro Espinal
App            : STW Hub
Sello SHA-256  : bdeedb31e7c0e361f24a71fa9f7a14eb584d1d867bbd0f36e5b755b122166aff
```

Verificable en la pestana **Configuracion > Acerca de** dentro de la app.

---

## Historial de versiones

| Version | Build | Cambios principales |
|---------|-------|---------------------|
| 2.5.2   | 23    | Fix dialog editar imagen heroe (admin builds), filtro Dudebro en SC, tarjeta SC rediseñada (3 tipos), HTM→Hunt the Monster, traducciones ES misiones (Storm Gates→Puertas de la Tormenta, etc.) |
| 2.5.1   | 22    | PL badge explicito (PL NNN), elemento bajo zona, Fight the Storm Cat 1/2/3/4, nuevos emojis por tipo de mision |
| 2.5.0   | 21    | Admin con codigo hash, nombres de misiones completos (126 generadores mapeados), camelCase split en generators, cosmeticos STW en Settings |
| 2.4.0   | 20    | Sistema admin super-usuario, overrides GitHub, primera pantalla de configuracion, vista Supercargadores |
| 1.0.0   | 1     | Version inicial |

---

*STW Hub v2.5.2 · Creado por Pedro Espinal · Todos los derechos reservados © 2026*
