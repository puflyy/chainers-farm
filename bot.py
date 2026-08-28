import os
import re
import json
import time
import random
import threading
import requests
from urllib.parse import parse_qs
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler

# === GÜVENLİK VE OTURUM BAŞLIKLARI ===
HEADERS = {
    "accept": "application/json",
    "accept-language": "tr-TR,tr;q=0.7",
    "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXNzaW9uSUQiOiI2YTkxNWY1OGRkNjNmOTYyMzUzN2RmOWUiLCJ1c2Vyc0lEIjoiNjg2MmU1MDkzNzBhMjEwMjI1ODg0ZjQ2IiwiaWF0IjoxNzg3OTEyMDI0LCJleHAiOjE3ODkxMTIwMjR9.OJcTJk_V8f8chJElAgLzOGLsPh9uY3Yb4JkdV567Qnw",
    "content-type": "application/json",
    "origin": "https://static.chainers.io",
    "priority": "u=1, i",
    "referer": "https://static.chainers.io/",
    "sec-ch-ua": '"Chromium";v="152", "Not?A_Brand";v="24", "Brave";v="152"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "sec-gpc": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
    "x-csrf": '{"expiration":"2026-08-29T10:14:02.44751215Z","token":"cbbe1ccc-f4ab-4176-a56e-9ef05d41"}',
    "x-request-token-id": "a3230f63dbc5530f-FRA"
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

URL_GARDENS = "https://chainers.io/api/farm/user/gardens"
URL_INVENTORY = "https://chainers.io/api/farm/user/inventory"
URL_INVENTORY_SHORT = "https://chainers.io/api/farm/user/inventory/short"
URL_HARVEST = "https://chainers.io/api/farm/control/collect-harvest"
URL_PLANT = "https://chainers.io/api/farm/control/plant-seed"
GARDEN_ID = "6862e5b80db08304717fd919"
CONFIG_FILE = "farm_targets.json"

# === DOĞRULANMIŞ TOHUM VERİ TABANI ===
SEEDS_DB = {
    # Seviye 3
    "Rare Marigold": {
        "seed_id": "65d38d0cda839cd1e0f7ec67",
        "duration": 120,
        "time_str": "2 dk",
        "tier": 3,
        "bp_min": "3.50",
        "code_key": "rare_marigold_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><circle cx="32" cy="32" r="16" fill="#3b82f6"/><circle cx="32" cy="32" r="8" fill="#ffa502"/></svg>'
    },
    "Rare Peas": {
        "seed_id": "673e0c942c7bfd708b35246b",
        "duration": 240,
        "time_str": "4 dk",
        "tier": 3,
        "bp_min": "0.75",
        "code_key": "rare_peas_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><path d="M16 22c12-8 32-2 36 20-8 12-28 14-36-20z" fill="#1e90ff"/><circle cx="26" cy="30" r="4" fill="#00d2d3"/><circle cx="34" cy="32" r="4" fill="#00d2d3"/><circle cx="42" cy="32" r="4" fill="#00d2d3"/></svg>'
    },

    # Seviye 2
    "Broccoli": {
        "seed_id": "67dc227a59b878f195998d76",
        "duration": 19680,
        "time_str": "5 sa 28 dk",
        "tier": 2,
        "bp_min": "0.85",
        "code_key": "uncommon_broccoli_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><path d="M28 38h8v16h-8z" fill="#badc58"/><circle cx="32" cy="22" r="12" fill="#6ab04c"/><circle cx="22" cy="28" r="10" fill="#6ab04c"/><circle cx="42" cy="28" r="10" fill="#6ab04c"/></svg>'
    },
    "Uncommon Corn": {
        "seed_id": "673e0c942c7bfd708b35240b",
        "duration": 360,
        "time_str": "6 dk",
        "tier": 2,
        "bp_min": "0.50",
        "code_key": "uncommon_corn_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><path d="M26 14c-4 12 2 28 8 36 6-8 12-24 8-36-8-2-8-2-16 0z" fill="#2ecc71"/><path d="M22 28c4 10 6 18 10 22-8-2-12-10-10-22z" fill="#badc58"/><path d="M42 28c-4 10-6 18-10 22 8-2 12-10 10-22z" fill="#badc58"/></svg>'
    },
    "Uncommon Peas": {
        "seed_id": "673e0c942c7bfd708b352465",
        "duration": 240,
        "time_str": "4 dk",
        "tier": 2,
        "bp_min": "0.50",
        "code_key": "uncommon_peas_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><path d="M16 22c12-8 32-2 36 20-8 12-28 14-36-20z" fill="#27ae60"/><circle cx="26" cy="30" r="4" fill="#2ecc71"/><circle cx="34" cy="32" r="4" fill="#2ecc71"/><circle cx="42" cy="32" r="4" fill="#2ecc71"/></svg>'
    },

    # Seviye 1
    "Sugarcane": {
        "seed_id": "6a6b1e1913ccd7c96918bf6b",
        "duration": 28500,
        "time_str": "7 sa 55 dk",
        "tier": 1,
        "bp_min": "27.00",
        "code_key": "common_sugarcane_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><rect x="22" y="10" width="6" height="44" rx="2" fill="#2ed573"/><rect x="34" y="16" width="6" height="38" rx="2" fill="#2ed573"/></svg>'
    },
    "Dragon Fruit": {
        "seed_id": "69945ab309abeb19e22a83f9",
        "duration": 90000,
        "time_str": "1g 1sa",
        "tier": 1,
        "bp_min": "0.90",
        "code_key": "common_dragon_fruit_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><path d="M32 12c-14 0-20 16-16 32 3 12 16 16 16 16s13-4 16-16c4-16-2-32-16-32z" fill="#ff4757"/><path d="M32 12c-4 6-12 8-12 8s4 8 2 14c4-2 8-8 10-14 0 0 4 6 8 8-2-6 0-12-2-14-2-2-6-4-6-12z" fill="#2ed573"/></svg>'
    },
    "White Lily": {
        "seed_id": "6801032feafb0e6b32164700",
        "duration": 18000,
        "time_str": "5 saat",
        "tier": 1,
        "bp_min": "0.63",
        "code_key": "common_white_lily_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><path d="M32 16c-6 10-12 14-12 24 0 10 12 14 12 14s12-4 12-14c0-10-6-14-12-24z" fill="#f1f2f6"/><circle cx="32" cy="38" r="3" fill="#ffa502"/></svg>'
    },
    "Pineapple": {
        "seed_id": "68824771915623f3dcc1fafd",
        "duration": 25200,
        "time_str": "7 saat",
        "tier": 1,
        "bp_min": "0.60",
        "code_key": "common_pineapple_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><ellipse cx="32" cy="38" rx="14" ry="18" fill="#f0932b"/><path d="M32 4c-4 6-2 14-2 14s-8-4-12 2c6 2 10 8 10 8s-6 0-8 6c6 0 10-2 12-4" fill="#2ed573"/><path d="M22 28l20 20m-20 0l20-20m-22 10h24" stroke="#d35400" stroke-width="2"/></svg>'
    },
    "Sunflower": {
        "seed_id": "673e0c942c7bfd708b3524b9",
        "duration": 3600,
        "time_str": "1 saat",
        "tier": 1,
        "bp_min": "0.53",
        "code_key": "common_sunflower_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><circle cx="32" cy="32" r="14" fill="#ffa502"/><circle cx="32" cy="32" r="8" fill="#573820"/></svg>'
    },
    "Strawberry": {
        "seed_id": "673e0c942c7bfd708b352441",
        "duration": 120,
        "time_str": "2 dk",
        "tier": 1,
        "bp_min": "0.50",
        "code_key": "common_strawberry_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><path d="M32 14c-12 0-22 10-18 28 3 14 18 20 18 20s15-6 18-20c4-18-6-28-18-28z" fill="#ff4757"/><path d="M32 6c-3 4-8 6-12 6 0 4 3 8 7 8 5-2 5-8 5-14zm0 0c3 4 8 6 12 6 0 4-3 8-7 8-5-2-5-8-5-14z" fill="#2ed573"/><circle cx="26" cy="26" r="1.5" fill="#ffa502"/><circle cx="38" cy="26" r="1.5" fill="#ffa502"/><circle cx="32" cy="34" r="1.5" fill="#ffa502"/><circle cx="32" cy="48" r="1.5" fill="#ffa502"/></svg>'
    },
    "Eggplant": {
        "seed_id": "673e0c942c7bfd708b352423",
        "duration": 1020,
        "time_str": "17 dk",
        "tier": 1,
        "bp_min": "0.47",
        "code_key": "common_eggplant_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><path d="M36 18c-8 0-16 10-14 26 2 12 10 16 16 16s14-6 12-18c-2-12-6-24-14-24z" fill="#683cb0"/><path d="M38 12c-2 2-6 3-10 2 1 4 4 6 8 6 4 0 5-4 4-8z" fill="#2ed573"/></svg>'
    },
    "Onion": {
        "seed_id": "67dc227a59b878f195998dca",
        "duration": 900,
        "time_str": "15 dk",
        "tier": 1,
        "bp_min": "0.47",
        "code_key": "common_onion_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><path d="M32 10c0 0-16 12-16 28 0 12 7 20 16 20s16-8 16-20c0-16-16-28-16-28z" fill="#e056fd"/><path d="M32 6v10m-4-6l4 6 4-6" stroke="#2ed573" stroke-width="3" stroke-linecap="round"/><path d="M26 26c-4 6-4 16 0 24m12-24c4 6 4 16 0 24" stroke="#be2edd" stroke-width="2" fill="none"/></svg>'
    },
    "Bell Pepper": {
        "seed_id": "67dc227a59b878f195998de8",
        "duration": 3780,
        "time_str": "1 sa 3 dk",
        "tier": 1,
        "bp_min": "0.46",
        "code_key": "common_bell_pepper_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><path d="M24 20c-6 0-10 8-8 24 2 12 8 16 16 16s14-4 16-16c2-16-2-24-8-24-4 0-6 4-8 4s-4-4-8-4z" fill="#e74c3c"/><path d="M32 10v10" stroke="#2ed573" stroke-width="4" stroke-linecap="round"/></svg>'
    },
    "Watermelon": {
        "seed_id": "673e0c942c7bfd708b35247d",
        "duration": 6720,
        "time_str": "1 sa 52 dk",
        "tier": 1,
        "bp_min": "0.46",
        "code_key": "common_watermelon_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><path d="M12 24c0 16 9 28 20 28s20-12 20-28H12z" fill="#2ed573"/><path d="M15 26c0 13 8 23 17 23s17-10 17-23H15z" fill="#ff4757"/><circle cx="24" cy="34" r="1.5" fill="#2f3542"/><circle cx="32" cy="38" r="1.5" fill="#2f3542"/><circle cx="40" cy="34" r="1.5" fill="#2f3542"/></svg>'
    },
    "Chili Pepper": {
        "seed_id": "67dc227a59b878f195998e06",
        "duration": 10860,
        "time_str": "3 sa 1 dk",
        "tier": 1,
        "bp_min": "0.45",
        "code_key": "common_chili_pepper_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><path d="M38 14c-12 0-22 10-18 26 3 14 12 18 16 18 2 0 4-4 2-10-2-8 4-18 8-22 2-3 0-8-8-12z" fill="#eb4d4b"/><path d="M38 14c3-3 8-5 12-4-2 4-6 6-10 6" fill="#6ab04c"/></svg>'
    },
    "Ginger": {
        "seed_id": "67dc227a59b878f195998e60",
        "duration": 28140,
        "time_str": "7 sa 49 dk",
        "tier": 1,
        "bp_min": "0.42",
        "code_key": "common_ginger_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><rect x="22" y="24" width="20" height="26" rx="10" fill="#eccc68"/><circle cx="20" cy="28" r="8" fill="#eccc68"/><circle cx="44" cy="34" r="8" fill="#eccc68"/><circle cx="32" cy="18" r="7" fill="#eccc68"/></svg>'
    },
    "Corn": {
        "seed_id": "673e0c942c7bfd708b352405",
        "duration": 360,
        "time_str": "6 dk",
        "tier": 1,
        "bp_min": "0.33",
        "code_key": "common_corn_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><path d="M26 14c-4 12 2 28 8 36 6-8 12-24 8-36-8-2-8-2-16 0z" fill="#f1c40f"/><path d="M22 28c4 10 6 18 10 22-8-2-12-10-10-22z" fill="#2ed573"/><path d="M42 28c-4 10-6 18-10 22 8-2 12-10 10-22z" fill="#2ed573"/></svg>'
    },
    "Peas": {
        "seed_id": "673e0c942c7bfd708b35245f",
        "duration": 240,
        "time_str": "4 dk",
        "tier": 1,
        "bp_min": "0.25",
        "code_key": "common_peas_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><path d="M16 22c12-8 32-2 36 20-8 12-28 14-36-20z" fill="#6ab04c"/><circle cx="26" cy="30" r="4" fill="#badc58"/><circle cx="34" cy="32" r="4" fill="#badc58"/><circle cx="42" cy="32" r="4" fill="#badc58"/></svg>'
    },
    "Star Anise": {
        "seed_id": "6970f73d4297528ed0eb352d",
        "duration": 720,
        "time_str": "12 dk",
        "tier": 1,
        "bp_min": "0.17",
        "code_key": "common_star_anise_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><polygon points="32,8 38,24 54,24 40,34 46,50 32,40 18,50 24,34 10,24 26,24" fill="#a0522d"/></svg>'
    }
}

SEED_ID_TO_NAME = {v["seed_id"]: k for k, v in SEEDS_DB.items()}

VALID_BED_IDS = {
    "6862f39a269206e9f5c678f8", # Lv2 Broccoli
    "6a8c41395b50ac4ade330786", # Lv2 Dragon Fruit
    "686784908aeeff0efa28d316", # Lv1 Ginger
    "6a8a457c2cf15a50df8aaaad", # Lv1 Pineapple
    "6a8ecc892cf15a50df3261ff", # Lv1 Watermelon
    "6a8ecc892cf15a50df3261fb", # Lv1 Chili Pepper
    "6a8ecc892cf15a50df32620b", # Lv1 Onion
    "6a8ecc892cf15a50df326207", # Lv1 Strawberry
    "6a8ecc892cf15a50df326203"  # Lv1 Sunflower
}

LV2_BED_IDS = {
    "6862f39a269206e9f5c678f8",
    "6a8c41395b50ac4ade330786"
}

BED_TARGETS = {}
TOTAL_ACTIONS = 0
NEXT_BREAK_ACTION = random.randint(12, 18)

def sync_dynamic_seeds():
    """Canlı envanterden yeni tohum gelirse dinamik olarak ID'leri günceller."""
    stock_dict = {}
    for url in (URL_INVENTORY_SHORT, URL_INVENTORY):
        try:
            res = SESSION.get(url, timeout=3)
            if res.status_code == 200:
                raw = res.json().get("data", {})
                items = raw.get("items", []) if isinstance(raw, dict) else (raw if isinstance(raw, list) else [])
                for item in items:
                    if item.get("itemType") == "farmSeeds":
                        i_id = item.get("itemID") or item.get("id")
                        i_code = item.get("itemCode", "").lower()
                        count = item.get("count", 0)
                        if i_id:
                            stock_dict[i_id] = count
                            for c_name, c_meta in SEEDS_DB.items():
                                if c_meta.get("code_key") == i_code:
                                    c_meta["seed_id"] = i_id
                                    SEED_ID_TO_NAME[i_id] = c_name
        except Exception:
            pass
    return stock_dict

def load_targets():
    global BED_TARGETS
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                BED_TARGETS = json.load(f)
        except Exception:
            BED_TARGETS = {}

def save_targets():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(BED_TARGETS, f, indent=4, ensure_ascii=False)

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def human_delay(min_s=30.0, max_s=90.0):
    wait_time = random.uniform(min_s, max_s)
    log(f"🌱 Tohum hazırlığı: {wait_time:.1f} saniye bekleniyor...")
    time.sleep(wait_time)

# === PANEL WEB SUNUCUSU ===
HTML_PAGE = """<!DOCTYPE html>
<html lang="tr">
<head>
    <title>Chainers Akıllı Tarla & Envanter Paneli</title>
    <meta charset="utf-8">
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background:#0f111a; color:#f1f2f6; margin:0; padding:25px; }
        .container { max-width: 1240px; margin: 0 auto; display: grid; grid-template-columns: 1.55fr 1fr; gap: 25px; }
        .panel-card { background:#1a1c29; border-radius:12px; padding:25px; box-shadow:0 8px 24px rgba(0,0,0,0.4); border: 1px solid #282b3d; }
        h2 { margin-top:0; font-size:22px; color:#fff; display:flex; align-items:center; gap:10px; }
        .subtext { color:#8f94a6; font-size:14px; margin-bottom:20px; line-height: 1.5; }
        table { width:100%; border-collapse:collapse; }
        th, td { padding:14px 10px; border-bottom:1px solid #282b3d; text-align:left; vertical-align:middle; }
        th { color:#8f94a6; font-size:13px; text-transform:uppercase; letter-spacing:0.5px; user-select:none; }
        th.sortable { cursor:pointer; transition:0.2s; }
        th.sortable:hover { color:#10b981; }
        .badge { padding:4px 8px; border-radius:5px; font-weight:bold; font-size:12px; }
        .badge-lv1 { background:#4b5563; color:#fff; }
        .badge-lv2 { background:#f59e0b; color:#fff; }
        .badge-lv3 { background:#3b82f6; color:#fff; }
        .countdown-cell { font-weight:bold; color:#00d2d3; font-variant-numeric: tabular-nums; }
        .ready { color:#10b981 !important; }
        select { width:100%; padding:8px 10px; border-radius:6px; background:#0f111a; color:#fff; border:1px solid #374151; font-weight:bold; outline:none; }
        select:focus { border-color:#10b981; }
        .btn-save { background:#10b981; color:#fff; border:none; padding:14px; border-radius:8px; font-weight:bold; font-size:15px; cursor:pointer; width:100%; margin-top:20px; transition:0.2s; }
        .btn-save:hover { background:#059669; }
        .catalog-grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap:12px; max-height: 560px; overflow-y: auto; padding-right: 5px; }
        .crop-card { background:#0f111a; border: 1px solid #282b3d; border-radius:10px; padding:12px; display:flex; flex-direction:column; align-items:center; text-align:center; transition:0.2s; position:relative; }
        .crop-card:hover { border-color:#57606f; background:#141724; transform:scale(1.02); }
        .crop-icon-wrapper { width:52px; height:52px; display:flex; align-items:center; justify-content:center; background:rgba(255,255,255,0.04); border-radius:50%; margin-bottom:8px; }
        .crop-title { font-size:13px; font-weight:bold; margin-bottom:3px; }
        .crop-time { font-size:11px; color:#9ca3af; margin-bottom:4px; }
        .bp-badge { font-size:11px; font-weight:bold; color:#f59e0b; background:rgba(245,158,11,0.1); padding:2px 6px; border-radius:4px; margin-bottom:4px; }
        .stock-badge { font-size:11px; font-weight:bold; color:#10b981; background:rgba(16,185,129,0.1); padding:2px 6px; border-radius:4px; }
        .token-box { margin-top: 25px; grid-column: span 2; background:#1a1c29; border-radius:12px; padding:20px; border: 1px solid #282b3d; }
        .token-input { width:100%; height:65px; background:#0f111a; border:1px solid #374151; color:#a4a6b3; padding:10px; border-radius:8px; font-family:monospace; font-size:12px; resize:none; outline:none; }
        .token-input:focus { border-color:#3b82f6; }
        .btn-token { background:#3b82f6; color:#fff; border:none; padding:12px 20px; border-radius:8px; font-weight:bold; font-size:14px; cursor:pointer; margin-top:10px; }
        .btn-token:hover { background:#2563eb; }
    </style>
</head>
<body>
    <div class="container">
        <!-- Sol: Aktif Yataklar -->
        <div class="panel-card">
            <h2>🌾 Tarla Yönetimi</h2>
            <div class="subtext">Başlıklara tıklayarak <b>Seviye</b>, <b>Kalan Süre</b> ve <b>BP/dk Verimi</b>ne göre sıralayabilirsiniz.</div>
            <form id="targetsForm">
                <table id="farmTable">
                    <thead>
                        <tr>
                            <th class="sortable" onclick="sortTable('level')">SEVİYE <span id="sort-icon-level">▲</span></th>
                            <th>TOHUM ADI</th>
                            <th class="sortable" onclick="sortTable('time')">KALAN SÜRE <span id="sort-icon-time">↕</span></th>
                            <th class="sortable" onclick="sortTable('bp')">HEDEF (VERİM: BP/DK) <span id="sort-icon-bp">↕</span></th>
                        </tr>
                    </thead>
                    <tbody id="farmBody">
                        __ROWS_HTML__
                    </tbody>
                </table>
                <button type="submit" id="btnSave" class="btn-save">💾 Hedefleri Kaydet</button>
            </form>
        </div>

        <!-- Sağ: Envanter & Ekin Kataloğu -->
        <div class="panel-card">
            <h2>📦 Envanter & Tohum Kataloğu</h2>
            <div class="subtext">Deponuzdaki tohumlar ve <b>dakika başı BP verimleri</b>.</div>
            <div class="catalog-grid">
                __CATALOG_HTML__
            </div>
        </div>

        <!-- Alt: Canlı Token Güncelleyici -->
        <div class="token-box">
            <h3 style="margin-top:0;font-size:16px;">🔑 Canlı Oturum / cURL Yenileme (Botu Kapatmadan)</h3>
            <div class="subtext" style="margin-bottom:10px;">
                Token süresi bittiğinde: <b>F12</b> → <b>Network</b> → Sayfayı yenileyin (F5) → Filtreye <b>gardens</b> yazın → 
                Gelen <code style="color:#00d2d3;">gardens</code> isteğine <b>Sağ Tık → Copy → Copy as cURL (bash)</b> deyin → Yapıştırıp butona basın.
            </div>
            <form id="tokenForm">
                <textarea id="curlData" name="curl_data" class="token-input" placeholder="curl --url 'https://chainers.io/api/farm/user/gardens' -H 'authorization: Bearer ...'"></textarea>
                <button type="submit" id="btnToken" class="btn-token">🔄 Oturumu & Tokenı Güncelle</button>
            </form>
        </div>
    </div>

    <script>
        let sortDirections = { level: 1, time: 1, bp: 1 };

        function updateTicks() {
            const selects = Array.from(document.querySelectorAll('#farmBody select'));
            const selectedValues = new Set(selects.map(s => s.value));

            selects.forEach(sel => {
                Array.from(sel.options).forEach(opt => {
                    let baseText = opt.getAttribute('data-raw-text');
                    if (!baseText) {
                        baseText = opt.textContent.replace(' ✓', '').trim();
                        opt.setAttribute('data-raw-text', baseText);
                    }
                    if (selectedValues.has(opt.value)) {
                        opt.textContent = baseText + ' ✓';
                    } else {
                        opt.textContent = baseText;
                    }
                });
            });
        }

        function sortTable(type) {
            const tbody = document.getElementById('farmBody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const dir = sortDirections[type];

            ['level', 'time', 'bp'].forEach(k => {
                document.getElementById('sort-icon-' + k).textContent = '↕';
            });
            document.getElementById('sort-icon-' + type).textContent = dir === 1 ? '▼' : '▲';

            rows.sort((a, b) => {
                let valA, valB;
                if (type === 'level') {
                    valA = parseInt(a.getAttribute('data-level'), 10);
                    valB = parseInt(b.getAttribute('data-level'), 10);
                } else if (type === 'time') {
                    valA = parseInt(a.querySelector('.countdown-cell').getAttribute('data-remaining') || 0, 10);
                    valB = parseInt(b.querySelector('.countdown-cell').getAttribute('data-remaining') || 0, 10);
                } else if (type === 'bp') {
                    const selA = a.querySelector('select');
                    const selB = b.querySelector('select');
                    const optA = selA.options[selA.selectedIndex];
                    const optB = selB.options[selB.selectedIndex];
                    valA = parseFloat(optA.getAttribute('data-bp') || 0);
                    valB = parseFloat(optB.getAttribute('data-bp') || 0);
                }
                return dir === 1 ? valB - valA : valA - valB;
            });

            sortDirections[type] = dir === 1 ? -1 : 1;
            rows.forEach(r => tbody.appendChild(r));
            updateTicks();
        }

        function formatDuration(rem) {
            if (rem <= 0) return 'Hazır';
            const d = Math.floor(rem / 86400);
            const h = Math.floor((rem % 86400) / 3600);
            const m = Math.floor((rem % 3600) / 60);
            const s = rem % 60;
            const sStr = (s < 10 ? '0' : '') + s;

            if (d > 0) {
                return d + ' gün ' + h + ' sa ' + m + ' dk ' + sStr + ' sn';
            } else if (h > 0) {
                return h + ' sa ' + m + ' dk ' + sStr + ' sn';
            } else {
                return m + ' dk ' + sStr + ' sn';
            }
        }

        function updateTimers() {
            const cells = document.querySelectorAll('.countdown-cell');
            cells.forEach(cell => {
                let rem = parseInt(cell.getAttribute('data-remaining'), 10);
                if (isNaN(rem) || rem <= 0) {
                    cell.textContent = 'Hazır';
                    cell.classList.add('ready');
                } else {
                    cell.textContent = formatDuration(rem);
                    cell.setAttribute('data-remaining', rem - 1);
                }
            });
        }
        setInterval(updateTimers, 1000);
        updateTimers();

        document.getElementById('targetsForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const btn = document.getElementById('btnSave');
            btn.textContent = '⏳ Kaydediliyor...';
            const formData = new URLSearchParams(new FormData(this)).toString();
            fetch('/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            }).then(() => {
                btn.textContent = '✓ Başarıyla Kaydedildi!';
                updateTicks();
                setTimeout(() => { btn.textContent = '💾 Hedefleri Kaydet'; }, 2000);
            }).catch(() => {
                btn.textContent = '❌ Hata Oluştu';
            });
        });

        document.getElementById('tokenForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const btn = document.getElementById('btnToken');
            btn.textContent = '⏳ Güncelleniyor...';
            const formData = new URLSearchParams(new FormData(this)).toString();
            fetch('/update_token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            }).then(() => {
                btn.textContent = '✓ Token Başarıyla Güncellendi!';
                document.getElementById('curlData').value = '';
                setTimeout(() => { btn.textContent = '🔄 Oturumu & Tokenı Güncelle'; }, 2000);
            }).catch(() => {
                btn.textContent = '❌ Hata Oluştu';
            });
        });

        document.querySelectorAll('#farmBody select').forEach(sel => {
            sel.addEventListener('change', updateTicks);
        });
        updateTicks();
    </script>
</body>
</html>"""

class PanelHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path in ("/", ""):
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            
            raw_beds = fetch_live_garden() or []
            beds = [b for b in raw_beds if b.get("userBedsID") in VALID_BED_IDS]
            beds.sort(key=lambda x: 0 if x.get("userBedsID") in LV2_BED_IDS else 1)
            
            stock_map = sync_dynamic_seeds()
            now_ts = datetime.now(timezone.utc).timestamp()
            
            sorted_all_available = sorted(
                SEEDS_DB.items(),
                key=lambda item: (-item[1]["tier"], -float(item[1]["bp_min"]))
            )

            rows_html = ""
            for idx, bed in enumerate(beds):
                b_id = bed.get("userBedsID")
                is_lv2 = b_id in LV2_BED_IDS
                level_num = 2 if is_lv2 else 1
                tier_badge = "<span class='badge badge-lv2'>Lv 2</span>" if is_lv2 else "<span class='badge badge-lv1'>Lv 1</span>"
                
                p_seed = bed.get("plantedSeed", {})
                cur_name = SEED_ID_TO_NAME.get(p_seed.get("seedID"), "Boş")
                date_str = p_seed.get("dateGrowth")
                rem_seconds = 0
                if date_str:
                    fts = datetime.fromisoformat(date_str.replace("Z", "+00:00")).timestamp()
                    rem_seconds = max(0, int(fts - now_ts))
                
                default_target = cur_name if cur_name in SEEDS_DB else "Strawberry"
                target = BED_TARGETS.get(b_id, default_target)
                
                options = ""
                for s_name, s_meta in sorted_all_available:
                    sel = "selected" if s_name == target else ""
                    options += f"<option value='{s_name}' data-bp='{s_meta['bp_min']}' {sel}>[Lv{s_meta['tier']}] {s_name} ({s_meta['time_str']} - {s_meta['bp_min']} BP/dk)</option>"
                
                rows_html += f"""<tr data-level='{level_num}'>
                    <td>{tier_badge}</td>
                    <td><b>{cur_name}</b></td>
                    <td class='countdown-cell' id='timer-{idx}' data-remaining='{rem_seconds}'>Hesaplanıyor...</td>
                    <td>
                        <select name="{b_id}">
                            {options}
                        </select>
                    </td>
                </tr>"""
            
            catalog_html = ""
            for name, meta in sorted_all_available:
                if meta["tier"] == 3:
                    t_badge = "<span class='badge badge-lv3'>Lv 3</span>"
                elif meta["tier"] == 2:
                    t_badge = "<span class='badge badge-lv2'>Lv 2</span>"
                else:
                    t_badge = "<span class='badge badge-lv1'>Lv 1</span>"

                stock_count = stock_map.get(meta.get("seed_id"), 0)
                catalog_html += f"""<div class="crop-card">
                    <div class="crop-icon-wrapper">
                        {meta['icon']}
                    </div>
                    <div class="crop-title">{name} {t_badge}</div>
                    <div class="crop-time">⏱ {meta['time_str']}</div>
                    <div class="bp-badge">⭐ {meta['bp_min']} BP/dk</div>
                    <div class="stock-badge">Stok: {stock_count}</div>
                </div>"""
            
            full_html = HTML_PAGE.replace("__ROWS_HTML__", rows_html).replace("__CATALOG_HTML__", catalog_html)
            self.wfile.write(full_html.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = parse_qs(post_data)

        if self.path == "/save":
            for b_id, val in params.items():
                if b_id in VALID_BED_IDS:
                    BED_TARGETS[b_id] = val[0]
            save_targets()
            log("💾 Panelden yeni ekin hedefleri kaydedildi!")

        elif self.path == "/update_token":
            raw_curl = params.get("curl_data", [""])[0]
            if raw_curl:
                auth_match = re.search(r"authorization:\s*(Bearer\s+[^\s'\"]+)", raw_curl, re.IGNORECASE)
                csrf_match = re.search(r"x-csrf:\s*(\{[^\r\n']+\})", raw_curl, re.IGNORECASE)
                token_match = re.search(r"x-request-token-id:\s*([^\s'\"]+)", raw_curl, re.IGNORECASE)
                
                if auth_match:
                    HEADERS["authorization"] = auth_match.group(1).strip()
                if csrf_match:
                    HEADERS["x-csrf"] = csrf_match.group(1).strip()
                if token_match:
                    HEADERS["x-request-token-id"] = token_match.group(1).strip()

                SESSION.headers.update(HEADERS)
                log("🔑 Canlı Panel Üzerinden Oturum Başlıkları / Token Başarıyla Güncellendi!")

        self.send_response(200)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.send_header("Content-Length", "15")
        self.end_headers()
        self.wfile.write(b'{"success":true}')

def start_server():
    server = HTTPServer(("127.0.0.1", 5000), PanelHandler)
    server.serve_forever()

# === BOT MOTORU ===
def fetch_live_garden():
    try:
        res = SESSION.get(URL_GARDENS)
        if res.status_code == 200:
            return res.json().get("data", [])[0].get("placedBeds", [])
        elif res.status_code == 429:
            log("⚠️ Rate limit algılandı! 30 saniye bekleniyor...")
            time.sleep(30)
        elif res.status_code in (401, 403):
            log("❌ Oturum/Token Süresi Doldu! Lütfen panelden yeni cURL yapıştırın.")
    except Exception:
        pass
    return None

def harvest_crop(farming_id):
    if not farming_id:
        return False
    try:
        res = SESSION.post(URL_HARVEST, json={"userFarmingID": farming_id})
        return res.status_code == 200
    except Exception:
        return False

def plant_seed(bed_id, seed_id, seed_name=""):
    payload = {
        "userGardensID": GARDEN_ID,
        "userBedsID": bed_id,
        "seedID": seed_id
    }
    try:
        res = SESSION.post(URL_PLANT, json=payload)
        if res.status_code == 200:
            return True
        else:
            log(f"❌ Ekim Hatası [{seed_name}] (Kod {res.status_code}): {res.text}")
            return False
    except Exception as e:
        log(f"❌ İstek Hatası: {e}")
        return False

def live_countdown(target_name, seconds):
    while seconds > 0:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        if h > 0:
            time_str = f"{h:02d}:{m:02d}:{s:02d}"
        else:
            time_str = f"{m:02d}:{s:02d}"
        print(f"\r⏳ [{target_name}] Hasadına Kalan Canlı Süre: {time_str} ", end="", flush=True)
        time.sleep(1)
        seconds -= 1
    print("\n")

def run_farm():
    global TOTAL_ACTIONS, NEXT_BREAK_ACTION
    load_targets()
    sync_dynamic_seeds()
    threading.Thread(target=start_server, daemon=True).start()
    log("🌐 Canlı Envanter & Tarla Paneli: http://localhost:5000")
    log("🛡️ Anti-Bot Güvenlik Katmanı ve Canlı Token Güncelleyici Devrede!")

    while True:
        if TOTAL_ACTIONS >= NEXT_BREAK_ACTION:
            break_time = random.randint(120, 300)
            log(f"☕ Anti-Bot: Doğal oyuncu molası veriliyor ({break_time // 60} dakika)...")
            time.sleep(break_time)
            TOTAL_ACTIONS = 0
            NEXT_BREAK_ACTION = random.randint(12, 18)

        raw_beds = fetch_live_garden()
        if raw_beds is None:
            time.sleep(random.uniform(5.0, 8.0))
            continue

        beds = [b for b in raw_beds if b.get("userBedsID") in VALID_BED_IDS]
        now_ts = datetime.now(timezone.utc).timestamp()
        crop_locations = {}
        ready_beds = []
        active_crops = []

        for bed in beds:
            p_seed = bed.get("plantedSeed", {})
            s_name = SEED_ID_TO_NAME.get(p_seed.get("seedID"))
            date_str = p_seed.get("dateGrowth")
            diff = 0
            if date_str:
                fts = datetime.fromisoformat(date_str.replace("Z", "+00:00")).timestamp()
                diff = max(0, int(fts - now_ts))
            
            if s_name:
                crop_locations[s_name] = diff

        for bed in beds:
            b_id = bed.get("userBedsID")
            p_seed = bed.get("plantedSeed", {})
            cur_seed_id = p_seed.get("seedID")
            cur_name = SEED_ID_TO_NAME.get(cur_seed_id, "Boş")
            
            default_target = cur_name if cur_name in SEEDS_DB else "Strawberry"
            target_name = BED_TARGETS.get(b_id, default_target)
            
            farming_id = p_seed.get("userFarmingID")
            date_str = p_seed.get("dateGrowth")
            
            diff = 0
            if date_str:
                fts = datetime.fromisoformat(date_str.replace("Z", "+00:00")).timestamp()
                diff = fts - now_ts

            if not p_seed or diff <= 0:
                ready_beds.append({
                    "bed_id": b_id,
                    "farming_id": farming_id,
                    "cur_name": cur_name,
                    "target_name": target_name
                })
            else:
                active_crops.append({"name": cur_name, "diff": diff})

        print("\n" + "="*50)
        for c in active_crops:
            h = int(c["diff"] // 3600)
            m = int((c["diff"] % 3600) // 60)
            s = int(c["diff"] % 60)
            if h > 0:
                log(f"🌱 {c['name']:<16} -> Kalan: {h} sa {m} dk {s} sn")
            else:
                log(f"🌱 {c['name']:<16} -> Kalan: {m} dk {s} sn")
        print("="*50)

        if ready_beds:
            jitter = random.uniform(60.0, 210.0)
            log(f"🕒 Ekin hazır! Doğal insan tepkisi için {int(jitter // 60)} dk {int(jitter % 60)} sn bekleniyor...")
            time.sleep(jitter)

            for rb in ready_beds:
                if rb["farming_id"]:
                    log(f"⚡ {rb['cur_name']} hasat ediliyor...")
                    harvest_crop(rb["farming_id"])
                    TOTAL_ACTIONS += 1
                    human_delay(30.0, 90.0)

                target = rb["target_name"]
                if target not in SEEDS_DB:
                    target = "Strawberry"

                plant_choice = target
                
                if target in crop_locations and crop_locations[target] > 0:
                    rem_time = crop_locations[target]
                    straw_dur = SEEDS_DB["Strawberry"]["duration"] if "Strawberry" in SEEDS_DB else 120
                    
                    if rem_time >= straw_dur:
                        log(f"⏳ {target} başka yatakta büyüyor ({rem_time} sn kaldı). Ara dolgu olarak Strawberry ekiliyor.")
                        plant_choice = "Strawberry"
                    else:
                        log(f"🛑 {target} hasadına {rem_time} sn kaldı! Strawberry süresi aşacağı için yatak bekletiliyor.")
                        plant_choice = None

                if plant_choice and plant_choice in SEEDS_DB:
                    s_id = SEEDS_DB[plant_choice]["seed_id"]
                    log(f"🌱 {plant_choice} ekiliyor...")
                    success = plant_seed(rb["bed_id"], s_id, plant_choice)
                    if success:
                        TOTAL_ACTIONS += 1
                    human_delay(30.0, 90.0)

            time.sleep(2)
            continue

        if active_crops:
            target_crop = min(active_crops, key=lambda x: x["diff"])
            sleep_time = max(int(target_crop["diff"]) + random.randint(10, 30), 5)
            live_countdown(target_crop["name"], sleep_time)
        else:
            time.sleep(random.uniform(10.0, 20.0))

if __name__ == "__main__":
    run_farm()