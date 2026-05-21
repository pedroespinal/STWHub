# STW Hub — Guía de Compilación / Build Guide

> **STW Hub v1.0.0** · Creado por: Pedro Espinal · Todos los derechos reservados © 2026

---

## Resumen de la aplicación / App Summary

| Campo / Field     | Valor / Value                     |
|-------------------|-----------------------------------|
| Framework         | Flet 0.85+ (Python → Android)     |
| Archivo principal | `main.py`                         |
| APK mínimo        | Android 7.0 (API 24)              |
| APK objetivo      | Android 13+ (API 35)              |
| Package ID        | `com.pedroespinal.stwhub`         |
| Versión           | 1.0.0                             |

---

## Características / Features

- ⚡ Alertas diarias de misiones STW desde la API oficial de Epic Games
- 💰 Filtro exclusivo para misiones con V-Bucks
- 🔧 8 builds meta (Constructor, Ninja, Explorador, Soldado) con descripción detallada
- 📰 Noticias oficiales STW vía fortnite-api.com
- 📖 Guía de usuario completa integrada en la app
- 🌍 Selector de región (NAE, NAW, EU, BR, OC, AS)
- 🌐 Bilingüe: Español / English (switch instantáneo en cualquier pantalla)
- 🎨 Dark mode neon / Light mode
- 🛡️ Firma digital SHA-256 incrustada en el código (prueba de autoría)
- 📱 Footer naranja neon: "Creado por: Pedro Espinal · Todos los derechos reservados ©{año}"
- 🔄 Cache local para uso offline después de la primera carga

---

## Método 1 — Google Colab (recomendado para Windows)

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

# Sube el ZIP con: main.py, pyproject.toml, requirements.txt, assets/
uploaded = files.upload()   # selecciona stwhub.zip
with zipfile.ZipFile(list(uploaded.keys())[0]) as z:
    z.extractall("stwhub")
os.chdir("stwhub")
```

```python
# Celda 3 — Compilar APK
!flet build apk --verbose
```

```python
# Celda 4 — Descargar el APK generado
from google.colab import files
import glob
apks = glob.glob("build/**/*.apk", recursive=True)
for apk in apks:
    files.download(apk)
    print(f"Descargando: {apk}")
```

---

## Método 2 — Linux nativo (Ubuntu / WSL)

```bash
pip install flet requests
cd /ruta/del/proyecto
flet build apk
```

El APK se genera en `build/apk/app-release.apk`.

---

## Firmar el APK (para distribución)

```bash
keytool -genkey -v -keystore stwhub-release.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias stwhub \
  -dname "CN=Pedro Espinal, OU=DEV, O=PedroEspinal, L=NA, S=NA, C=DO"

apksigner sign \
  --ks stwhub-release.jks \
  --ks-key-alias stwhub \
  --out STWHub-v1.0.0-signed.apk \
  build/apk/app-release.apk
```

---

## Estructura de archivos / File structure

```
STWHub/
├── main.py                  # App principal (Flet)
├── pyproject.toml           # Configuración Flet build
├── buildozer.spec           # Configuración Kivy/Buildozer (alternativo)
├── requirements.txt         # Dependencias Python
├── make_icon.py             # Generador de icono y presplash
├── BUILD_INSTRUCTIONS.md    # Este archivo
└── assets/
    ├── icon.png             # Icono 512×512 (Husk STW neon)
    └── presplash.png        # Splash 1024×500
```

---

## Firma Digital / Digital Signature

```
Genesis commit : stwhub-genesis-20260521
Fecha creación : 2026-05-21T00:00:00
Autor          : Pedro Espinal
App            : STW Hub
Sello SHA-256  : bdeedb31e7c0e361f24a71fa9f7a14eb584d1d867bbd0f36e5b755b122166aff
```

Verificable en la pestaña **Configuración → Acerca de** dentro de la app.

---

## Nombre del APK / APK naming

```
STWHub-v1.0.0.apk
```

---

*STW Hub v1.0.0 · Creado por Pedro Espinal · Todos los derechos reservados © 2026*
