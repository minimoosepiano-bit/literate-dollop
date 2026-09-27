#!/usr/bin/env python3
"""Generates the mod's textures (uncompressed 32-bit DDS) and thumbnail.png.

Requires Pillow:  pip install pillow
Run from anywhere:  python3 tools/gen_textures.py
"""
import struct
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent / "ai_control_panel"
GFX = ROOT / "gfx/interface/ai_control_panel"

# must match interface/ai_ctrl.gui
PANEL_W, PANEL_H = 620, 552
ROW_Y0, ROW_H, ROW_STEP, ROWS = 104, 88, 96, 4

GOLD = (196, 164, 92, 255)
GOLD_DIM = (120, 100, 58, 255)


def save_dds(img: Image.Image, path: Path):
    """Write an uncompressed A8R8G8B8 DDS, which HoI4 reads natively."""
    img = img.convert("RGBA")
    w, h = img.size
    flags = 0x1 | 0x2 | 0x4 | 0x8 | 0x1000  # CAPS|HEIGHT|WIDTH|PITCH|PIXELFORMAT
    header = struct.pack(
        "<4s7I44x",
        b"DDS ", 124, flags, h, w, w * 4, 0, 1,
    )
    pixfmt = struct.pack(
        "<8I", 32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000
    )
    caps = struct.pack("<5I", 0x1000, 0, 0, 0, 0)
    r, g, b, a = img.split()
    data = Image.merge("RGBA", (b, g, r, a)).tobytes()  # BGRA byte order
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(header + pixfmt + caps + data)


def vgradient(w, h, top, bottom):
    img = Image.new("RGBA", (w, h))
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(4))
        for x in range(w):
            px[x, y] = c
    return img


def font(size):
    for name in ("DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "Arial Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def panel_bg():
    img = vgradient(PANEL_W, PANEL_H, (30, 36, 46, 245), (16, 19, 25, 245))
    d = ImageDraw.Draw(img)
    # header strip
    d.rectangle([2, 2, PANEL_W - 3, 52], fill=(44, 52, 66, 255))
    d.line([2, 53, PANEL_W - 3, 53], fill=GOLD_DIM, width=1)
    # rows
    for i in range(ROWS):
        y0 = ROW_Y0 + i * ROW_STEP
        d.rounded_rectangle([24, y0, PANEL_W - 24, y0 + ROW_H], radius=6,
                            fill=(38, 45, 57, 235), outline=(70, 80, 96, 255))
    # footer divider
    fy = ROW_Y0 + ROWS * ROW_STEP
    d.line([24, fy, PANEL_W - 24, fy], fill=(70, 80, 96, 255), width=1)
    # outer frame
    d.rectangle([0, 0, PANEL_W - 1, PANEL_H - 1], outline=GOLD, width=2)
    d.rectangle([3, 3, PANEL_W - 4, PANEL_H - 4], outline=GOLD_DIM, width=1)
    return img


def button(w, h, top, bottom, outline):
    img = vgradient(w, h, top, bottom)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=5, fill=255)
    img.putalpha(mask)
    ImageDraw.Draw(img).rounded_rectangle([0, 0, w - 1, h - 1], radius=5, outline=outline, width=1)
    return img


def close_button():
    img = button(28, 28, (150, 50, 45, 255), (100, 30, 28, 255), (210, 120, 110, 255))
    d = ImageDraw.Draw(img)
    d.line([8, 8, 19, 19], fill=(240, 230, 220, 255), width=3)
    d.line([19, 8, 8, 19], fill=(240, 230, 220, 255), width=3)
    return img


def light():
    img = Image.new("RGBA", (12, 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, 11, 11], fill=(40, 90, 40, 255))
    d.ellipse([2, 2, 9, 9], fill=(110, 230, 110, 255))
    return img


def chip(size):
    """A small 'AI' circuit-chip emblem used for the modifier icon & thumbnail."""
    s = size
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m = s // 5
    pin = max(2, s // 32)
    for k in range(4):
        p = m + (k + 0.5) * (s - 2 * m) / 4
        d.line([p, m // 3, p, m], fill=GOLD, width=pin)
        d.line([p, s - m, p, s - m // 3], fill=GOLD, width=pin)
        d.line([m // 3, p, m, p], fill=GOLD, width=pin)
        d.line([s - m, p, s - m // 3, p], fill=GOLD, width=pin)
    d.rounded_rectangle([m, m, s - m, s - m], radius=s // 12,
                        fill=(36, 44, 58, 255), outline=GOLD, width=max(2, s // 32))
    f = font(int(s * 0.3))
    d.text((s / 2, s / 2), "AI", fill=(235, 225, 200, 255), font=f, anchor="mm")
    return img


def modifier_icon():
    # sized like vanilla national spirit icons
    img = Image.new("RGBA", (64, 68), (0, 0, 0, 0))
    img.alpha_composite(chip(60), (2, 4))
    return img


def thumbnail():
    img = vgradient(256, 256, (34, 42, 56, 255), (14, 17, 22, 255))
    img.alpha_composite(chip(150), (53, 26))
    d = ImageDraw.Draw(img)
    d.text((128, 200), "AI CONTROL", fill=GOLD, font=font(28), anchor="mm")
    d.text((128, 230), "PANEL", fill=(220, 214, 200, 255), font=font(20), anchor="mm")
    d.rectangle([0, 0, 255, 255], outline=GOLD, width=3)
    return img


def main():
    save_dds(panel_bg(), GFX / "ai_ctrl_panel_bg.dds")
    save_dds(button(120, 32, (70, 150, 70, 255), (35, 95, 40, 255), (150, 220, 150, 255)),
             GFX / "ai_ctrl_toggle_on.dds")
    save_dds(button(120, 32, (80, 84, 92, 255), (50, 53, 60, 255), (140, 145, 155, 255)),
             GFX / "ai_ctrl_toggle_off.dds")
    save_dds(button(160, 32, (70, 88, 118, 255), (42, 54, 76, 255), (140, 160, 195, 255)),
             GFX / "ai_ctrl_button.dds")
    save_dds(button(120, 28, (70, 88, 118, 255), (42, 54, 76, 255), (140, 160, 195, 255)),
             GFX / "ai_ctrl_button_small.dds")
    save_dds(button(150, 36, (58, 70, 92, 255), (30, 37, 50, 255), GOLD), GFX / "ai_ctrl_launcher.dds")
    save_dds(close_button(), GFX / "ai_ctrl_close.dds")
    save_dds(light(), GFX / "ai_ctrl_light.dds")
    save_dds(modifier_icon(), GFX / "ai_ctrl_research_lock.dds")
    thumbnail().save(ROOT / "thumbnail.png")
    print("textures written to", GFX)


if __name__ == "__main__":
    main()
