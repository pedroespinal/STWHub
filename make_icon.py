#!/usr/bin/env python3
"""
Genera el icono STW Hub (512x512) con cara de Husk reconocible.
Requiere: pip install Pillow
"""
from PIL import Image, ImageDraw, ImageFilter
import os, math

W = H = 512
img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d   = ImageDraw.Draw(img)
cx, cy = W // 2, H // 2

# ── Fondo: degradado oscuro navy→purple-storm ─────────────────────────────────
for y in range(H):
    t = y / H
    r = int(7   + t * 35)
    g = int(7   + t * 5)
    b = int(26  + t * 55)
    for x in range(W):
        img.putpixel((x, y), (r, g, b, 255))

d = ImageDraw.Draw(img)

# ── Aura naranja exterior (storm glow) ────────────────────────────────────────
for i in range(10, 0, -1):
    alpha = int(30 + i * 4)
    r_aura = 240 + i * 3
    d.ellipse(
        [cx - r_aura, cy - r_aura, cx + r_aura, cy + r_aura],
        outline=(255, 109, 0, alpha), width=3,
    )

# ── Nube de tormenta (fondo, parte superior) ──────────────────────────────────
storm_col = (80, 20, 120, 200)
d.ellipse([cx - 160, 30, cx + 160, 180], fill=(55, 15, 90, 180))
d.ellipse([cx - 100, 10, cx + 80,  130], fill=(70, 18, 110, 180))
d.ellipse([cx + 30,  20, cx + 200, 150], fill=(60, 16, 100, 180))
d.ellipse([cx - 230, 50, cx + 10,  160], fill=(50, 12, 80,  150))

# Borde brillante de la nube
d.arc([cx - 155, 35, cx + 155, 175], start=180, end=0, fill=(160, 60, 220), width=3)

# ── Rayos desde la nube ───────────────────────────────────────────────────────
def draw_bolt(d, x1, y1, x2, y2, w, col):
    d.line([x1, y1, x2, y2], fill=col, width=w)
    # glow
    d.line([x1, y1, x2, y2], fill=(col[0], col[1], col[2], 80), width=w + 4)

draw_bolt(d, cx - 60, 140, cx - 40, 200, 3, (255, 213, 0, 255))
draw_bolt(d, cx + 50, 130, cx + 35, 195, 3, (255, 213, 0, 255))
draw_bolt(d, cx,      120, cx + 5,  200, 4, (255, 213, 0, 255))

# ── CARA DEL HUSK (zombie STW) ────────────────────────────────────────────────
# Piel: gris verdosa desaturada (característica de los husks)
HUSK_SKIN  = (140, 130, 110, 255)
HUSK_DARK  = (90,  82,  68,  255)
HUSK_EYE   = (255, 60,  0,   255)   # ojos naranja-rojo brillante
HUSK_GLOW  = (255, 130, 0,   200)
HUSK_MOUTH = (40,  25,  15,  255)
HUSK_TOOTH = (220, 210, 180, 255)

# Cabeza (óvalo principal) — ocupa la mitad inferior del icono
head_x0, head_y0 = cx - 145, 175
head_x1, head_y1 = cx + 145, 430
d.ellipse([head_x0, head_y0, head_x1, head_y1], fill=HUSK_SKIN)

# Sombras en la cabeza para dar volumen
d.ellipse([head_x0 + 15, head_y0 + 10,
           head_x1 - 15, head_y1 - 10],
          outline=HUSK_DARK, width=2)

# ── Frente arrugada (líneas características del husk) ────────────────────────
for i, (fx0, fy0, fx1, fy1) in enumerate([
    (cx - 50, 195, cx - 20, 205),
    (cx - 30, 210, cx + 10, 218),
    (cx + 10, 195, cx + 45, 205),
    (cx + 25, 210, cx + 55, 218),
]):
    d.line([(fx0, fy0), (fx1, fy1)], fill=HUSK_DARK, width=2)

# ── Cavidades oculares (hundidas, oscuras) ───────────────────────────────────
# Ojo izquierdo
eye_lx, eye_ly = cx - 72, 248
d.ellipse([eye_lx - 38, eye_ly - 28,
           eye_lx + 38, eye_ly + 28],
          fill=(35, 20, 10, 255))
# Iris naranja brillante
d.ellipse([eye_lx - 20, eye_ly - 16,
           eye_lx + 20, eye_ly + 16],
          fill=HUSK_EYE)
# Glow del ojo
for g in range(4, 0, -1):
    ga = int(200 - g * 40)
    d.ellipse([eye_lx - 20 - g*3, eye_ly - 16 - g*3,
               eye_lx + 20 + g*3, eye_ly + 16 + g*3],
              outline=(255, 100, 0, ga), width=1)
# Pupila negra
d.ellipse([eye_lx - 7, eye_ly - 7,
           eye_lx + 7, eye_ly + 7],
          fill=(0, 0, 0, 255))

# Ojo derecho
eye_rx, eye_ry = cx + 72, 248
d.ellipse([eye_rx - 38, eye_ry - 28,
           eye_rx + 38, eye_ry + 28],
          fill=(35, 20, 10, 255))
d.ellipse([eye_rx - 20, eye_ry - 16,
           eye_rx + 20, eye_ry + 16],
          fill=HUSK_EYE)
for g in range(4, 0, -1):
    ga = int(200 - g * 40)
    d.ellipse([eye_rx - 20 - g*3, eye_ry - 16 - g*3,
               eye_rx + 20 + g*3, eye_ry + 16 + g*3],
              outline=(255, 100, 0, ga), width=1)
d.ellipse([eye_rx - 7, eye_ry - 7,
           eye_rx + 7, eye_ry + 7],
          fill=(0, 0, 0, 255))

# ── Nariz aplanada ───────────────────────────────────────────────────────────
d.ellipse([cx - 14, 286, cx + 14, 310], fill=HUSK_DARK)
d.ellipse([cx - 8,  290, cx + 8,  306], fill=(60, 40, 25, 255))

# ── Boca rasgada (característica del husk) ───────────────────────────────────
# Boca principal — abertura oscura rasgada
mouth_pts = [
    (cx - 75, 335),
    (cx - 55, 348),
    (cx - 35, 355),
    (cx - 10, 360),
    (cx,      361),
    (cx + 10, 360),
    (cx + 35, 355),
    (cx + 55, 348),
    (cx + 75, 335),
    (cx + 60, 345),
    (cx + 30, 368),
    (cx,      372),
    (cx - 30, 368),
    (cx - 60, 345),
]
d.polygon(mouth_pts, fill=HUSK_MOUTH)

# Dientes irregulares (arriba)
teeth_top = [
    (cx - 62, 338, cx - 48, 352),
    (cx - 40, 340, cx - 24, 358),
    (cx - 16, 342, cx + 2,  360),
    (cx + 8,  342, cx + 26, 360),
    (cx + 32, 340, cx + 48, 356),
    (cx + 50, 338, cx + 64, 350),
]
for tx0, ty0, tx1, ty1 in teeth_top:
    d.rectangle([tx0, ty0, tx1, ty1], fill=HUSK_TOOTH)
    d.rectangle([tx0 + 1, ty0 + 1, tx1 - 1, ty1 - 1], fill=(200, 190, 165, 255))

# Grieta/corte en la mejilla izquierda
d.line([(cx - 110, 295), (cx - 80, 320), (cx - 90, 345)],
       fill=HUSK_DARK, width=3)

# ── "STW" grande centrado (encima de la boca, debajo de los ojos) ─────────────
try:
    from PIL import ImageFont
    # Intenta fuentes disponibles en Windows
    for fname in ["ariblk.ttf", "arialbd.ttf", "impact.ttf", "arial.ttf"]:
        try:
            font_big = ImageFont.truetype(fname, 80)
            break
        except Exception:
            font_big = ImageFont.load_default()
except Exception:
    font_big = ImageFont.load_default()

stw_text = "STW"
bbox = d.textbbox((0, 0), stw_text, font=font_big)
tw = bbox[2] - bbox[0]
th = bbox[3] - bbox[1]
tx = cx - tw // 2
ty = 390      # debajo de la boca

# Sombra del texto
d.text((tx + 3, ty + 3), stw_text, font=font_big, fill=(20, 10, 0, 200))
# Texto naranja neon principal
d.text((tx, ty), stw_text, font=font_big, fill=(255, 109, 0, 255))
# Brillo del texto (línea interior más clara)
d.text((tx, ty), stw_text, font=font_big, fill=(255, 213, 0, 90))

# ── Borde del icono (marco neon naranja) ─────────────────────────────────────
margin = 8
d.rounded_rectangle(
    [margin, margin, W - margin, H - margin],
    radius=60,
    outline=(255, 109, 0, 230),
    width=5,
)
# Segundo borde tenue
d.rounded_rectangle(
    [margin + 6, margin + 6, W - margin - 6, H - margin - 6],
    radius=56,
    outline=(255, 213, 0, 80),
    width=2,
)

# ── Guardar icono principal ───────────────────────────────────────────────────
os.makedirs("assets", exist_ok=True)
# Aplicar esquinas redondeadas con máscara (para transparencia real)
mask = Image.new("L", (W, H), 0)
dm = ImageDraw.Draw(mask)
dm.rounded_rectangle([0, 0, W, H], radius=64, fill=255)
img.putalpha(mask)

img.save("assets/icon.png")
print("OK  assets/icon.png — Husk STW 512x512")

# ── Presplash (1024x500) ──────────────────────────────────────────────────────
splash = Image.new("RGBA", (1024, 500), (7, 7, 26, 255))
ds = ImageDraw.Draw(splash)

# Línea de tormenta horizontal
for x in range(1024):
    t = x / 1024
    r = int(255 * (0.5 + 0.5 * abs(math.sin(t * math.pi))))
    ds.point((x, 248), fill=(r, int(r * 0.43), 0, 200))
    ds.point((x, 249), fill=(r, int(r * 0.43), 0, 150))
    ds.point((x, 250), fill=(r, int(r * 0.43), 0, 100))

# Título
try:
    from PIL import ImageFont as IF
    for fn in ["ariblk.ttf", "arialbd.ttf", "arial.ttf"]:
        try:
            ftitle = IF.truetype(fn, 88); break
        except: ftitle = IF.load_default()
    for fn in ["arialbd.ttf", "arial.ttf"]:
        try:
            fsub = IF.truetype(fn, 30); break
        except: fsub = IF.load_default()
    for fn in ["arialbd.ttf", "arial.ttf"]:
        try:
            fsub2 = IF.truetype(fn, 20); break
        except: fsub2 = IF.load_default()
except Exception:
    ftitle = fsub = fsub2 = ImageFont.load_default()

title = "STW Hub"
tb = ds.textbbox((0, 0), title, font=ftitle)
ds.text((512 - (tb[2]-tb[0])//2 + 2, 102), title, fill=(80, 40, 0, 200), font=ftitle)
ds.text((512 - (tb[2]-tb[0])//2,     100), title, fill=(255, 109, 0, 255), font=ftitle)
ds.text((512 - (tb[2]-tb[0])//2,     100), title, fill=(255, 213, 0, 60),  font=ftitle)

sub1 = "Fortnite: Save The World"
sb1  = ds.textbbox((0, 0), sub1, font=fsub)
ds.text((512 - (sb1[2]-sb1[0])//2, 260), sub1, fill=(255, 170, 68, 255), font=fsub)

sub2 = "Alertas  ·  Builds  ·  Noticias  /  Alerts  ·  Builds  ·  News"
sb2  = ds.textbbox((0, 0), sub2, font=fsub2)
ds.text((512 - (sb2[2]-sb2[0])//2, 300), sub2, fill=(136, 138, 170, 200), font=fsub2)

splash.save("assets/presplash.png")
print("OK  assets/presplash.png — 1024x500")
