#!/usr/bin/env python3
"""Generates ai_ctrl_research_lists.txt (the AI's technology priority lists).

Edit the lists below and re-run:  python3 tools/gen_research.py
Each entry is (technology_id, earliest_year). The AI never researches a tech
before that year (so it doesn't pay ahead-of-time penalties it can't see),
and inside a category it always takes the first entry it can research.
Techs that don't exist in your game (e.g. DLC-only) are simply skipped.
"""
from pathlib import Path

CATEGORIES = {
    "industry": [
        ("basic_machine_tools", None),
        ("concentrated_industry", None),
        ("dispersed_industry", None),
        ("construction1", None),
        ("excavation1", None),
        ("fuel_silos", None),
        ("synth_oil_experiments", None),
        ("concentrated_industry2", 1937),
        ("dispersed_industry2", 1937),
        ("construction2", 1938),
        ("excavation2", 1938),
        ("fuel_refining", 1938),
        ("oil_processing", 1938),
        ("improved_machine_tools", 1939),
        ("concentrated_industry3", 1939),
        ("dispersed_industry3", 1939),
        ("construction3", 1940),
        ("excavation3", 1940),
        ("improved_oil_processing", 1940),
        ("concentrated_industry4", 1941),
        ("dispersed_industry4", 1941),
        ("advanced_machine_tools", 1941),
        ("construction4", 1942),
        ("excavation4", 1942),
        ("advanced_oil_processing", 1942),
        ("concentrated_industry5", 1943),
        ("dispersed_industry5", 1943),
        ("construction5", 1944),
        ("excavation5", 1944),
    ],
    "land": [
        ("infantry_weapons", None),
        ("support_weapons", None),
        ("tech_support", None),
        ("tech_engineers", None),
        ("tech_recon", None),
        ("motorised_infantry", None),
        ("tech_logistics_company", None),
        ("tech_maintenance_company", None),
        ("tech_military_police", None),
        ("tech_signal_company", None),
        ("tech_field_hospital", 1938),
        ("infantry_weapons1", 1939),
        ("tech_engineers2", 1939),
        ("tech_recon2", 1939),
        ("tech_logistics_company2", 1939),
        ("tech_signal_company2", 1939),
        ("night_vision", 1939),
        ("support_weapons2", 1940),
        ("infantry_at", 1940),
        ("improved_infantry_weapons", 1940),
        ("mechanised_infantry", 1940),
        ("tech_field_hospital2", 1940),
        ("tech_maintenance_company2", 1940),
        ("tech_military_police2", 1940),
        ("infantry_weapons2", 1942),
        ("support_weapons3", 1942),
        ("night_vision2", 1942),
        ("tech_engineers3", 1942),
        ("tech_recon3", 1942),
        ("tech_logistics_company3", 1942),
        ("tech_signal_company3", 1942),
        ("mechanised_infantry2", 1942),
        ("infantry_at2", 1943),
        ("improved_infantry_weapons_2", 1943),
        ("support_weapons4", 1944),
    ],
    "electronics": [
        ("electronic_mechanical_engineering", None),
        ("radio", None),
        ("mechanical_computing", None),
        ("radio_detection", 1937),
        ("computing_machine", 1938),
        ("decimetric_radar", 1939),
        ("improved_computing_machine", 1940),
        ("improved_decimetric_radar", 1941),
        ("advanced_computing_machine", 1942),
    ],
    "artillery": [
        ("gw_artillery", None),
        ("interwar_artillery", None),
        ("interwar_antitank", None),
        ("interwar_antiair", None),
        ("artillery1", 1938),
        ("artillery2", 1939),
        ("antitank2", 1939),
        ("antiair2", 1939),
        ("artillery3", 1940),
        ("rocket_artillery", 1940),
        ("artillery4", 1941),
        ("antitank3", 1941),
        ("antiair3", 1941),
        ("rocket_artillery2", 1941),
        ("artillery5", 1942),
        ("antitank4", 1942),
        ("antiair4", 1942),
        ("rocket_artillery3", 1943),
        ("antitank5", 1943),
        ("antiair5", 1943),
    ],
    "armor_air": [
        ("early_fighter", None),
        ("gwtank_chassis", None),
        ("basic_light_tank_chassis", None),
        ("cas1", 1936),
        ("basic_medium_tank_chassis", 1938),
        ("improved_light_tank_chassis", 1939),
        ("fighter1", 1940),
        ("cas2", 1940),
        ("improved_medium_tank_chassis", 1941),
        ("advanced_light_tank_chassis", 1941),
        ("fighter2", 1942),
        ("advanced_medium_tank_chassis", 1943),
        ("cas3", 1944),
        ("fighter3", 1944),
    ],
}

HEADER = """###############################################################################
# AI Control Panel - research priority lists
#
# GENERATED FILE - edit tools/gen_research.py and re-run it instead.
#
# Each ai_ctrl_research_try_<category> effect grants the first technology in
# its list that the country can research (and whose year has come), then
# sets the temp variable ai_ctrl_picked = 1.  It does nothing if
# ai_ctrl_picked is already 1.
###############################################################################
"""


def block(tech, year, first):
    kw = "if" if first else "else_if"
    date = f"\n\t\t\t\tdate > {year}.1.1" if year else ""
    return (
        f"\t\t{kw} = {{\n"
        f"\t\t\tlimit = {{{date}\n"
        f"\t\t\t\tcan_research = {tech}\n"
        f"\t\t\t}}\n"
        f"\t\t\tset_technology = {{ {tech} = 1 popup = yes }}\n"
        f"\t\t\tset_temp_variable = {{ ai_ctrl_picked = 1 }}\n"
        f"\t\t}}\n"
    )


def main():
    out = [HEADER]
    for cat, techs in CATEGORIES.items():
        out.append(f"\nai_ctrl_research_try_{cat} = {{\n")
        out.append("\tif = {\n\t\tlimit = { check_variable = { ai_ctrl_picked = 0 } }\n")
        for i, (tech, year) in enumerate(techs):
            out.append(block(tech, year, i == 0))
        out.append("\t}\n}\n")
    dest = Path(__file__).resolve().parent.parent / "ai_control_panel/common/scripted_effects/ai_ctrl_research_lists.txt"
    dest.write_text("".join(out), encoding="utf-8")
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
