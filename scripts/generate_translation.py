#!/usr/bin/env python

import asyncio
import json
import re
from pathlib import Path

from pyhon import HonAPI

# These languages are official supported by hOn
LANGUAGES = [
    "cs",  # Czech
    "de",  # German
    "el",  # Greek
    "en",  # English
    "es",  # Spanish
    "fr",  # French
    "he",  # Hebrew
    "hr",  # Croatian
    "it",  # Italian
    "nl",  # Dutch
    "pl",  # Polish
    "pt",  # Portuguese
    "ro",  # Romanian
    "ru",  # Russian
    "sk",  # Slovak
    "sl",  # Slovenian
    "sr",  # Serbian
    "tr",  # Turkish
    "zh",  # Chinese
]

WASHING_PR_PHASE = {
    0: "WASHING_CMD&CTRL.PHASE_READY.TITLE",
    1: "WASHING_CMD&CTRL.PHASE_WASHING.TITLE",
    2: "WASHING_CMD&CTRL.PHASE_WASHING.TITLE",
    3: "WASHING_CMD&CTRL.PHASE_SPIN.TITLE",
    4: "WASHING_CMD&CTRL.PHASE_RINSE.TITLE",
    5: "WASHING_CMD&CTRL.PHASE_RINSE.TITLE",
    6: "WASHING_CMD&CTRL.PHASE_RINSE.TITLE",
    7: "WASHING_CMD&CTRL.PHASE_DRYING.TITLE",
    9: "WASHING_CMD&CTRL.PHASE_STEAM.TITLE",
    10: "WASHING_CMD&CTRL.PHASE_READY.TITLE",
    11: "WASHING_CMD&CTRL.PHASE_SPIN.TITLE",
    12: "WASHING_CMD&CTRL.PHASE_WEIGHTING.TITLE",
    13: "WASHING_CMD&CTRL.PHASE_WEIGHTING.TITLE",
    14: "WASHING_CMD&CTRL.PHASE_WASHING.TITLE",
    15: "WASHING_CMD&CTRL.PHASE_WASHING.TITLE",
    16: "WASHING_CMD&CTRL.PHASE_WASHING.TITLE",
    17: "WASHING_CMD&CTRL.PHASE_RINSE.TITLE",
    18: "WASHING_CMD&CTRL.PHASE_RINSE.TITLE",
    19: "WASHING_CMD&CTRL.PHASE_SCHEDULED.TITLE",
    20: "WASHING_CMD&CTRL.PHASE_TUMBLING.TITLE",
    24: "WASHING_CMD&CTRL.PHASE_REFRESH.TITLE",
    25: "WASHING_CMD&CTRL.PHASE_WASHING.TITLE",
    26: "WASHING_CMD&CTRL.PHASE_HEATING.TITLE",
    27: "WASHING_CMD&CTRL.PHASE_WASHING.TITLE",
}
MACH_MODE = {
    0: "WASHING_CMD&CTRL.PHASE_READY.TITLE",
    1: "WASHING_CMD&CTRL.PHASE_READY.TITLE",
    3: "WASHING_CMD&CTRL.PHASE_PAUSE.TITLE",
    4: "WASHING_CMD&CTRL.PHASE_SCHEDULED.TITLE",
    5: "WASHING_CMD&CTRL.PHASE_SCHEDULED.TITLE",
    6: "WASHING_CMD&CTRL.PHASE_ERROR.TITLE",
    7: "WASHING_CMD&CTRL.PHASE_READY.TITLE",
}
TUMBLE_DRYER_PR_PHASE = {
    0: "WASHING_CMD&CTRL.PHASE_READY.TITLE",
    1: "TD_CMD&CTRL.STATUS_PHASE.PHASE_HEAT_STROKE",
    2: "WASHING_CMD&CTRL.PHASE_DRYING.TITLE",
    3: "TD_CMD&CTRL.STATUS_PHASE.PHASE_COOLDOWN",
    13: "TD_CMD&CTRL.STATUS_PHASE.PHASE_COOLDOWN",
    14: "TD_CMD&CTRL.STATUS_PHASE.PHASE_HEAT_STROKE",
    15: "TD_CMD&CTRL.STATUS_PHASE.PHASE_HEAT_STROKE",
    16: "TD_CMD&CTRL.STATUS_PHASE.PHASE_COOLDOWN",
    18: "WASHING_CMD&CTRL.PHASE_TUMBLING.DASHBOARD_TITLE",
    19: "WASHING_CMD&CTRL.PHASE_DRYING.TITLE",
    20: "WASHING_CMD&CTRL.PHASE_DRYING.TITLE",
}
DISHWASHER_PR_PHASE = {
    0: "WASHING_CMD&CTRL.PHASE_READY.TITLE",
    1: "WASHING_CMD&CTRL.PHASE_PREWASH.TITLE",
    2: "WASHING_CMD&CTRL.PHASE_WASHING.TITLE",
    3: "WASHING_CMD&CTRL.PHASE_RINSE.TITLE",
    4: "WASHING_CMD&CTRL.PHASE_DRYING.TITLE",
    5: "WASHING_CMD&CTRL.PHASE_READY.TITLE",
    6: "WASHING_CMD&CTRL.PHASE_HOT_RINSE.TITLE",
}

TUMBLE_DRYER_DRY_LEVEL = {
    0: "WASHING_CMD&CTRL.PROGRAM_CYCLE_DETAIL_MAIN_OPTIONS.NO_DRY",
    1: "WASHING_CMD&CTRL.PROGRAM_CYCLE_DETAIL_OPTIONS_VALUES_DESCRIPTION.IRON_DRY",
    2: "WASHING_CMD&CTRL.GUIDED_WASHING_SYMBOLS_DRYING.NO_DRY_IRON_TITLE",
    3: "WASHING_CMD&CTRL.GUIDED_WASHING_SYMBOLS_DRYING.CUPBOARD_DRY_TITLE",
    4: "WASHING_CMD&CTRL.GUIDED_WASHING_SYMBOLS_DRYING.EXTRA_DRY_TITLE",
    12: "WASHING_CMD&CTRL.PROGRAM_CYCLE_DETAIL_OPTIONS_VALUES_DESCRIPTION.IRON_DRY",
    13: "WASHING_CMD&CTRL.GUIDED_WASHING_SYMBOLS_DRYING.CUPBOARD_DRY_TITLE",
    14: "WASHING_CMD&CTRL.GUIDED_WASHING_SYMBOLS_DRYING.READY_TO_WEAR_TITLE",
    15: "WASHING_CMD&CTRL.GUIDED_WASHING_SYMBOLS_DRYING.EXTRA_DRY_TITLE",
}

SENSOR = {
    "washing_modes": MACH_MODE,
    "program_phases_wm": WASHING_PR_PHASE,
    "program_phases_td": TUMBLE_DRYER_PR_PHASE,
    "program_phases_dw": DISHWASHER_PR_PHASE,
    "dry_levels": TUMBLE_DRYER_DRY_LEVEL,
}

SELECT = {"dry_levels": TUMBLE_DRYER_DRY_LEVEL}

PROGRAMS = {
    "programs_dw": "PROGRAMS.DW",
    "programs_ih": "PROGRAMS.IH",
    "programs_ov": "PROGRAMS.OV",
    "programs_td": "PROGRAMS.TD",
    "programs_wm": "PROGRAMS.WM_WD",
}

NAMES = {
    "switch": {
        "anti_crease": "HDRY_CMD&CTRL.PROGRAM_CYCLE_DETAIL.ANTICREASE_TITLE",
        "add_dish": "DW_CMD&CTRL.c.ADD_DISH",
        "eco_express": "DW_CMD&CTRL.PROGRAM_CYCLE_DETAIL_OTHER_OPTIONS.ECO",
        "extra_dry": "DW_CMD&CTRL.PROGRAM_CYCLE_DETAIL_OTHER_OPTIONS.EXTRA_DRY",
        "half_load": "DW_CMD&CTRL.PROGRAM_CYCLE_DETAIL_OTHER_OPTIONS.HALF_LOAD",
        "open_door": "DW_CMD&CTRL.PROGRAM_CYCLE_DETAIL_OTHER_OPTIONS.OPEN_DOOR",
        "three_in_one": "DW_CMD&CTRL.PROGRAM_CYCLE_DETAIL_OTHER_OPTIONS.THREE_IN_ONE",
        "preheat": "OV.PROGRAM_DETAIL.PREHEAT",
        "dish_washer": "GLOBALS.APPLIANCES_NAME.DW",
        "tumble_dryer": "GLOBALS.APPLIANCES_NAME.TD",
        "washing_machine": "GLOBALS.APPLIANCES_NAME.WM",
        "washer_dryer": "GLOBALS.APPLIANCES_NAME.WD",
        "oven": "GLOBALS.APPLIANCES_NAME.OV",
        "prewash": "WASHING_CMD&CTRL.PROGRAM_CYCLE_DETAIL_OTHER_OPTIONS.PREWASH",
        "pause": "GENERAL.PAUSE_PROGRAM",
        "keep_fresh": "GLOBALS.APPLIANCE_STATUS.TUMBLING",
        "delay_time": "HINTS.TIPS_TIME_ENERGY_SAVING.TIPS_USE_AT_NIGHT_TITLE",
    },
    "binary_sensor": {
        "door_lock": "WASHING_CMD&CTRL.CHECK_UP_RESULTS.DOOR_LOCK",
        "extra_rinse_1": "WASHING_CMD&CTRL.PROGRAM_CYCLE_DETAIL_OTHER_OPTIONS.EXTRARINSE1",
        "extra_rinse_2": "WASHING_CMD&CTRL.PROGRAM_CYCLE_DETAIL_OTHER_OPTIONS.EXTRARINSE2",
        "extra_rinse_3": "WASHING_CMD&CTRL.PROGRAM_CYCLE_DETAIL_OTHER_OPTIONS.EXTRARINSE3",
        "good_night": "WASHING_CMD&CTRL.PROGRAM_CYCLE_DETAIL_OTHER_OPTIONS.GOODNIGHT",
        "anti_crease": "HDRY_CMD&CTRL.PROGRAM_CYCLE_DETAIL.ANTICREASE_TITLE",
        "aqua_plus": "WASHING_CMD&CTRL.PROGRAM_CYCLE_DETAIL_OTHER_OPTIONS.ACQUAPLUS",
        "spin_speed": "WASHING_CMD&CTRL.PROGRAM_CYCLE_DETAIL_MAIN_OPTIONS.SPINSPEED",
        "still_hot": "IH.COILS_STATUS.STILL_HOT",
        "pan_status": "IH.COILS_STATUS.PAN",
        "remote_control": "OV.SUPPORT.REMOTE_CONTROL",
        "rinse_aid": "DW_CMD&CTRL.MAINTENANCE.CONSUMABLE_LEVELS_ICON_RINSE_AID",
        "salt_level": "DW_CMD&CTRL.MAINTENANCE.CONSUMABLE_LEVELS_ICON_SALT",
        "door_open": "GLOBALS.APPLIANCE_STATUS.DOOR_OPEN",
        "connection": "ENROLLMENT_COMMON.HEADER_NAME.STEP_APPLIANCE_CONNECTION",
        "child_lock": "AP.FOOTER_MENU_MORE.SECURITY_LOCK_TITLE",
        "on": "GLOBALS.GENERAL.ON",
        "prewash": "WASHING_CMD&CTRL.PROGRAM_CYCLE_DETAIL_OTHER_OPTIONS.PREWASH",
    },
    "button": {
        "induction_hob": "GLOBALS.APPLIANCES_NAME.IH",
    },
    "select": {
        "dry_levels": "WASHING_CMD&CTRL.DRAWER_CYCLE_DRYING.TAB_LEVEL",
        "dry_time": "WASHING_CMD&CTRL.DRAWER_CYCLE_DRYING.TAB_TIME",
        "spin_speed": "WASHING_CMD&CTRL.PROGRAM_CYCLE_DETAIL_MAIN_OPTIONS.SPINSPEED",
        "temperature": "IH.COMMON.TEMPERATURE",
        "programs_dw": "WC.SET_PROGRAM.PROGRAM",
        "programs_ih": "WC.SET_PROGRAM.PROGRAM",
        "programs_ov": "WC.SET_PROGRAM.PROGRAM",
        "programs_td": "WC.SET_PROGRAM.PROGRAM",
        "programs_wm": "WC.SET_PROGRAM.PROGRAM",
    },
    "sensor": {
        "dry_levels": "WASHING_CMD&CTRL.DRAWER_CYCLE_DRYING.TAB_LEVEL",
        "dry_time": "WASHING_CMD&CTRL.DRAWER_CYCLE_DRYING.TAB_TIME",
        "power": "OV.RECIPE_DETAIL.POWER_LEVEL",
        "remaining_time": "ENROLLMENT_COMMON.GENERAL.REMAINING_TIME",
        "temperature": "IH.COMMON.TEMPERATURE",
        "water_efficiency": "WASHING_CMD&CTRL.PROGRAM_CYCLE_DETAIL_RESULT.WATER_EFFICIENCY",
        "water_saving": "STATISTICS.SMART_AI_CYCLE.WATER_SAVING",
        "duration": "WASHING_CMD&CTRL.DRAWER_PROGRAM_FILTERS.DURATION",
        "target_temperature": "IH.COOKING_DETAIL.TEMPERATURE_TARGETING",
        "spin_speed": "WASHING_CMD&CTRL.PROGRAM_CYCLE_DETAIL_MAIN_OPTIONS.SPINSPEED",
        "steam_leve": "WASHING_CMD&CTRL.PROGRAM_CYCLE_DETAIL_MAIN_OPTIONS.STEAM_LEVEL",
        "dirt_level": "WASHING_CMD&CTRL.PROGRAM_CYCLE_DETAIL_MAIN_OPTIONS.DIRTY_LEVEL",
        "program_phases_wm": "WASHING_CMD&CTRL.STATISTICS_GRAPHIC_INSTANT_CONSUMPTION.PHASE",
        "program_phases_td": "WASHING_CMD&CTRL.STATISTICS_GRAPHIC_INSTANT_CONSUMPTION.PHASE",
        "program_phases_dw": "WASHING_CMD&CTRL.STATISTICS_GRAPHIC_INSTANT_CONSUMPTION.PHASE",
        "delay_time": "HINTS.TIPS_TIME_ENERGY_SAVING.TIPS_USE_AT_NIGHT_TITLE",
        "suggested_load": "WASHING_CMD&CTRL.DRAWER_PROGRAM_FILTERS.LOAD_CAPACITY",
        "energy_label": "WASHING_CMD&CTRL.DRAWER_PROGRAM_FILTERS.ENERGY_EFFICIENCY",
        "det_dust": "HUBS.WIDGET.STAINS_WIDGET.STAINS.SUGGESTED_DET_DUST",
        "det_liquid": "HUBS.WIDGET.STAINS_WIDGET.STAINS.SUGGESTED_DET_LIQUID",
        "errors": "ROBOT_CMD&CTRL.PHASE_ERROR.TITLE",
        "programs": "OV.TABS.CURRENT_PROGRAM",
        "cycles_total": [
            "WASHING_CMD&CTRL.GENERAL.CYCLES",
            "WC.VIRTUAL_WINE_STATS_COUNTRY.TOTAL",
        ],
        "energy_total": [
            "MISE.ENERGY_CONSUMPTION.TITLE",
            "WC.VIRTUAL_WINE_STATS_COUNTRY.TOTAL",
        ],
        "water_total": [
            "WASHING_CMD&CTRL.PROGRAM_CYCLE_DETAIL_RESULT.WATER_EFFICIENCY",
            "WC.VIRTUAL_WINE_STATS_COUNTRY.TOTAL",
        ],
        "energy_current": [
            "MISE.ENERGY_CONSUMPTION.TITLE",
            "CUBE90_GLOBAL.GENERAL.CURRENT",
        ],
        "water_current": [
            "WASHING_CMD&CTRL.PROGRAM_CYCLE_DETAIL_RESULT.WATER_EFFICIENCY",
            "CUBE90_GLOBAL.GENERAL.CURRENT",
        ],
    },
    "number": {
        "power_management": "HINTS.COOKING_WITH_INDUCTION.POWER_MANAGEMENT",
        "temperature": "IH.COMMON.TEMPERATURE",
        "delay_time": "HINTS.TIPS_TIME_ENERGY_SAVING.TIPS_USE_AT_NIGHT_TITLE",
        "water_hard": "WASHING_CMD&CTRL.DASHBOARD_MENU_MORE_SETTINGS_WATER.TITLE",
        "program_duration": "OV.PROGRAM_DETAIL.PROGRAM_DURATION",
        "target_temperature": "IH.COOKING_DETAIL.TEMPERATURE_TARGETING",
        "rinse_iterations": "WASHING_CMD&CTRL.PROGRAM_CYCLE_DETAIL.DRAWER_HEADER_RINSE",
        "wash_time": "WASHING_CMD&CTRL.PROGRAM_CYCLE_DETAIL.WASHING_TIME",
        "dry_time": "WASHING_CMD&CTRL.DRAWER_CYCLE_DRYING.TAB_TIME",
    },
}


async def check_translation_files(translations):
    for language in LANGUAGES:
        path = translations / f"{language}.json"
        if not path.is_file():
            async with HonAPI(anonymous=True) as hon:
                keys = await hon.translation_keys(language)
                save_json(path, keys)


def load_hon_translations():
    translations = Path(__file__).parent / "translations"
    translations.mkdir(exist_ok=True)
    asyncio.run(check_translation_files(translations))
    return {f.stem: f for f in translations.glob("*.json")}


def load_hass_translations():
    translations = (
        Path(__file__).parent.parent / "custom_components" / "hon" / "translations"
    )
    return {f.stem: f for f in translations.glob("*.json")}


def load_json(path):
    if path:
        with open(path, "r") as file:
            return json.loads(file.read())
    return {}


def save_json(path, keys):
    with open(path, "w") as json_file:
        json_file.write(json.dumps(keys, indent=4))


def load_key(full_key, json_data, fallback=None):
    if isinstance(full_key, list):
        return " ".join(
            [load_key(item, json_data, fallback).strip() for item in full_key]
        )
    result = json_data.copy()
    for key in full_key.split("."):
        result = result.get(key, {})
    if not result and fallback:
        return load_key(full_key, fallback)
    return result or ""


def load_keys(full_key, json_data):
    blacklist = ["description", "_recipe_", "_guided_"]
    first, last = full_key.split(".")
    data = json_data.get(first, {}).get(last, {})
    return {
        key.lower(): value
        for key, value in data.items()
        if not any(b in key.lower() for b in blacklist)
        and re.findall("^[a-z0-9-_]+$", key.lower())
    }


def add_data(old, original, fallback, data, name, entity="sensor"):
    sensor = old.setdefault("entity", {}).setdefault(entity, {})
    for number, phase in data.items():
        state = sensor.setdefault(name, {}).setdefault("state", {})
        if key := load_key(phase, original, fallback):
            state[str(number)] = key


def main():
    hass = load_hass_translations()
    hon = load_hon_translations()
    base_path = Path(__file__).parent.parent / "custom_components/hon/translations"
    fallback = load_json(hon.get("en", ""))
    for language in LANGUAGES:
        original = load_json(hon.get(language, ""))
        old = load_json(hass.get(language, ""))
        for name, data in SENSOR.items():
            add_data(old, original, fallback, data, name)
        for name, data in SELECT.items():
            add_data(old, original, fallback, data, name, "select")
        for name, program in PROGRAMS.items():
            select = old.setdefault("entity", {}).setdefault("select", {})
            select.setdefault(name, {})["state"] = load_keys(program, original)
        for entity, data in NAMES.items():
            for name, key in data.items():
                select = old.setdefault("entity", {}).setdefault(entity, {})
                select.setdefault(name, {})["name"] = load_key(key, original, fallback)
        save_json(base_path / f"{language}.json", old)


if __name__ == "__main__":
    main()
