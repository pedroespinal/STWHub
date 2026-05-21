#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STW Hub — Husk icon generator (1024x1024 PNG)
Creado por: Pedro Espinal
"""
import os
import math
from PIL import Image, ImageDraw, ImageFilter

SIZE = 1024
CX = CY = SIZE // 2

os.makedirs("assets", exist_ok=True)
img = Image.new("RGBA", (SIZE, SIZE), (7, 7, 26, 255))
draw = ImageDraw.Draw(img)


def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


# ── Background radial glow (deep purple) ─────────────────────────────────────
for r in range(490, 0, -4):
    a = int(45 * math.sin(math.pi * r / 490))
    c = (18 + int(14 * r / 490), 5, 35 + int(20 * r / 490), a)
    draw.ellipse([CX - r, CY - r, CX + r, CY + r], fill=c)

# ── Outer neon ring (orange) ──────────────────────────────────────────────────
for gw in range(28, 0, -2):
    a = int(120 * (gw / 28) ** 1.5)
    rr = 478 + gw
    draw.ellipse([CX - rr, CY - rr, CX + rr, CY + rr], outline=(255, 100, 0, a), width=4)
draw.ellipse([CX - 478, CY - 478, CX + 478, CY + 478], outline=(255, 120, 10), width=6)

# ── Husk head (dark amber-brown oval) ────────────────────────────────────────
HR = 310
HY = CY - 10
draw.ellipse([CX - HR, HY - int(HR * 1.08), CX + HR, HY + int(HR * 1.08)],
             fill=(52, 34, 18))

# Skin texture horizontal lines
for i in range(-7, 8):
    y = HY + i * 38
    alpha = 60 + abs(i) * 5
    draw.line([CX - HR + 30, y, CX + HR - 30, y],
              fill=(35, 20, 8, alpha), width=2)

# ── Cracks ────────────────────────────────────────────────────────────────────
crack = (30, 16, 6)
draw.line([(CX + 60, HY - 240), (CX + 140, HY - 100), (CX + 90, HY + 20)],
          fill=crack, width=4)
draw.line([(CX - 100, HY - 200), (CX - 50, HY - 60)], fill=crack, width=3)
draw.line([(CX - 140, HY + 80), (CX - 80, HY + 180)], fill=crack, width=3)

# ── Eyebrows (sunken, menacing) ───────────────────────────────────────────────
for ex, angle in [(CX - 118, -18), (CX + 118, 18)]:
    ey = HY - 115
    rad = math.radians(angle)
    draw.polygon([
        (ex - 70 - int(10 * math.cos(rad)), ey - 22 + int(10 * math.sin(rad))),
        (ex + 70 + int(10 * math.cos(rad)), ey - 22 - int(10 * math.sin(rad))),
        (ex + 70, ey + 12),
        (ex - 70, ey + 12),
    ], fill=(28, 14, 6))

# ── Eye sockets ───────────────────────────────────────────────────────────────
for ex in [CX - 118, CX + 118]:
    ey = HY - 65
    er = 72
    # Deep socket
    draw.ellipse([ex - er, ey - er, ex + er, ey + er], fill=(12, 6, 3))
    # Glow layers (orange → yellow center)
    for gw, gc in [(55, (200, 80, 0, 80)), (42, (230, 110, 0, 120)),
                   (30, (255, 140, 0, 160)), (18, (255, 180, 20, 200)),
                   (9,  (255, 220, 80, 230))]:
        draw.ellipse([ex - gw, ey - gw, ex + gw, ey + gw], fill=gc)
    # Dark slit pupil
    draw.ellipse([ex - 12, ey - 20, ex + 12, ey + 20], fill=(8, 3, 2))

# ── Nasal cavity ──────────────────────────────────────────────────────────────
for nx in [CX - 22, CX + 22]:
    draw.ellipse([nx - 14, HY + 28 - 18, nx + 14, HY + 28 + 18], fill=(20, 10, 5))

# ── Mouth ─────────────────────────────────────────────────────────────────────
MX, MY = CX, HY + 150
MW = 210
# Gum base
draw.rounded_rectangle([MX - MW, MY - 8, MX + MW, MY + 68], radius=8,
                        fill=(80, 20, 8))
# Teeth
TW, TH = 36, 52
NT = 10
sx = MX - (NT // 2) * TW + TW // 2
for i in range(NT):
    tx = sx + i * TW
    # Alternating height for jagged look
    th = TH if i % 2 == 0 else TH - 14
    draw.polygon([
        (tx - TW // 2 + 3, MY),
        (tx + TW // 2 - 3, MY),
        (tx + TW // 2 - 8, MY + th),
        (tx - TW // 2 + 8, MY + th),
    ], fill=(210, 200, 185))
    # Tooth shading
    draw.line([(tx - TW // 2 + 8, MY), (tx - TW // 2 + 8, MY + th - 6)],
              fill=(180, 168, 152), width=2)

# Dark gap between upper / lower jaw
draw.rectangle([MX - MW + 4, MY + 70, MX + MW - 4, MY + 90], fill=(10, 4, 2))

# ── "STW" neon text ───────────────────────────────────────────────────────────
try:
    from PIL import ImageFont
    fnt = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 110)
except Exception:
    try:
        from PIL import ImageFont
        fnt = ImageFont.truetype("arial.ttf", 110)
    except Exception:
        fnt = None

if fnt:
    txt = "STW"
    # Glow halo
    glow_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    for offset in range(10, 0, -2):
        a = int(90 * (offset / 10))
        gd.text((CX, SIZE - 108), txt, font=fnt, fill=(255, 100, 0, a), anchor="mm")
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=6))
    img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img)
    draw.text((CX, SIZE - 108), txt, font=fnt, fill=(255, 160, 30), anchor="mm")
    draw.text((CX, SIZE - 108), txt, font=fnt, fill=(255, 220, 120), anchor="mm")

# ── Final glow pass (soft) ────────────────────────────────────────────────────
final = img.filter(ImageFilter.GaussianBlur(radius=1))
img = Image.blend(img, final, 0.18)

img.save("assets/icon.png")
print("assets/icon.png saved — 1024x1024 Husk icon")
