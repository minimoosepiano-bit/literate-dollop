#!/usr/bin/env python3
"""Offline sanity checks for the mod (no game needed).

- braces balance in every script / gui / gfx file
- every ai_ctrl_* effect or trigger that is called is also defined
- every localisation key used by the GUI, decisions and modifiers exists
- every sprite used by the GUI is defined, and every texture file exists
"""
import re
import sys
from pathlib import Path

MOD = Path(__file__).resolve().parent.parent / "ai_control_panel"
errors = []


def strip_comments(text):
    return "\n".join(line.split("#", 1)[0] for line in text.splitlines())


script_files = [p for p in MOD.rglob("*") if p.suffix in (".txt", ".gui", ".gfx")]
for p in script_files:
    text = strip_comments(p.read_text(encoding="utf-8"))
    depth = 0
    for ch in text:
        depth += ch == "{"
        depth -= ch == "}"
        if depth < 0:
            errors.append(f"{p.relative_to(MOD)}: unmatched '}}'")
            break
    if depth > 0:
        errors.append(f"{p.relative_to(MOD)}: {depth} unclosed '{{'")
    if text.count('"') % 2:
        errors.append(f"{p.relative_to(MOD)}: odd number of quotes")

# --- scripted effects / triggers -------------------------------------------
defined = set()
for sub in ("common/scripted_effects", "common/scripted_triggers"):
    for p in (MOD / sub).glob("*.txt"):
        defined |= set(re.findall(r"^(ai_ctrl_\w+)\s*=", strip_comments(p.read_text()), re.M))

called = set()
for p in (MOD / "common").rglob("*.txt"):
    called |= set(re.findall(r"\b(ai_ctrl_\w+)\s*=\s*yes\b", strip_comments(p.read_text())))
for name in sorted(called - defined):
    errors.append(f"effect/trigger called but never defined: {name}")

# --- localisation ---------------------------------------------------------
loc_keys = set()
for p in (MOD / "localisation").rglob("*.yml"):
    raw = p.read_bytes()
    if not raw.startswith(b"\xef\xbb\xbf"):
        errors.append(f"{p.relative_to(MOD)}: missing UTF-8 BOM")
    loc_keys |= set(re.findall(r"^\s+([\w.]+):\d*\s", raw.decode("utf-8-sig"), re.M))
for p in (MOD / "common/scripted_localisation").glob("*.txt"):
    loc_keys |= set(re.findall(r"name\s*=\s*(\w+)", p.read_text()))

gui = strip_comments((MOD / "interface/ai_ctrl.gui").read_text())
used_loc = set(re.findall(r'(?:text|buttonText|pdx_tooltip)\s*=\s*"(\w+)"', gui))
for p in (MOD / "common/scripted_localisation").glob("*.txt"):
    used_loc |= set(re.findall(r"localization_key\s*=\s*(\w+)", p.read_text()))
for p in (MOD / "localisation").rglob("*.yml"):
    used_loc |= set(re.findall(r"\[(AI_CTRL_\w+)\]", p.read_text(encoding="utf-8-sig")))
used_loc |= {"ai_ctrl_category", "ai_ctrl_open_panel", "ai_ctrl_research_lock"}
for key in sorted(used_loc - loc_keys):
    errors.append(f"missing localisation key: {key}")

# --- GUI element names vs scripted GUI hooks -----------------------------
elements = set(re.findall(r'name\s*=\s*"(\w+)"', gui))
sgui = strip_comments((MOD / "common/scripted_guis/ai_ctrl_scripted_guis.txt").read_text())
for hook in re.findall(r"^\s*(\w+?)_(click|visible|click_enabled)\s*=", sgui, re.M):
    if hook[0] not in elements:
        errors.append(f"scripted GUI hook for unknown element: {hook[0]}_{hook[1]}")
for win in re.findall(r'window_name\s*=\s*"(\w+)"', sgui):
    if win not in elements:
        errors.append(f"scripted GUI window not in .gui: {win}")

# --- sprites ----------------------------------------------------------------
gfx = (MOD / "interface/ai_ctrl.gfx").read_text()
sprites = set(re.findall(r'name\s*=\s*"(GFX_\w+)"', gfx))
used_sprites = set(re.findall(r'spriteType\s*=\s*"(GFX_\w+)"', gui))
used_sprites |= set(re.findall(r"icon\s*=\s*(GFX_\w+)",
                               (MOD / "common/dynamic_modifiers/ai_ctrl_dynamic_modifiers.txt").read_text()))
for s in sorted(used_sprites - sprites):
    errors.append(f"sprite used but not defined: {s}")
for tex in re.findall(r'texturefile\s*=\s*"([^"]+)"', gfx):
    if not (MOD / tex).exists():
        errors.append(f"texture missing: {tex}")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"OK - {len(script_files)} script files, {len(defined)} effects/triggers, "
      f"{len(loc_keys)} loc keys, {len(sprites)} sprites")
