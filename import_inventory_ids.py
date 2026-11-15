import json
import os
import re
import unicodedata

base_dir = "/data/data/com.termux/files/home/chainers-farm"
bot_path = os.path.join(base_dir, "bot.py")
lib_path = os.path.join(base_dir, "crops_library.json")

inventory_ids = {
    "epic_ghost_food": "6abce61e4256b50d4349e800",
    "rare_ginger_seeds": "67dc227a59b878f195998e6c",
    "uncommon_light_tree_seeds": "6ab282d700c19f4431021f97",
    "common_radish_seeds": "67dc227a59b878f195998e7e",
    "common_pufferfish_food": "6ad9f925a598ffe738bc42c2",
    "common_proto_flower_seeds": "6a1832bb8745e0fa5293bb94",
    "common_crystal_eagle_food": "6af5a22f40e5d277ce8494b0",
    "common_melon_seeds": "683dbe2ba9ec974575a4bf2a",
    "common_spooky_cauldron_seeds": "6abce62cc7313e5d05935bc3",
    "common_star_anise_seeds": "6970f73d4297528ed0eb352d",
    "rare_onion_seeds": "67dc227a59b878f195998dd6",
    "rare_peas_seeds": "673e0c942c7bfd708b35246b",
    "common_garlic_seeds": "67dc227a59b878f195998e42",
    "common_sweet_potato_seeds": "67dc227a59b878f195998e24",
    "common_radiant_calla_lily_seeds": "6aec62fde661def7703b43c3",
    "common_pineapple_seeds": "68824771915623f3dcc1fafd",
    "common_hyacinths_seeds": "6582e209591717d062d19e3d",
    "common_cabbage_seeds": "67dc227a59b878f195998d8e",
    "common_patisson_seeds": "69285140f803f06b82ab22e0",
    "uncommon_strawberry_seeds": "673e0c942c7bfd708b352447",
    "common_watermelon_seeds": "673e0c942c7bfd708b35247d",
    "rare_melon_seeds": "683dbe2ba9ec974575a4bf36",
    "common_marigold_seeds": "6582e209591717d062d19e25",
    "rare_broccoli_seeds": "67dc227a59b878f195998d7c",
    "common_broccoli_seeds": "67dc227a59b878f195998d70",
    "rare_chili_pepper_seeds": "67dc227a59b878f195998e12",
    "uncommon_leek_seeds": "67dc227a59b878f195998efc",
    "common_tomato_seeds": "6582e209591717d062d19e1f",
    "common_strawberry_seeds": "673e0c942c7bfd708b352441",
    "common_jack_pumpkin_seeds": "6900ddfce2a48c502f309993",
    "uncommon_jack_pumpkin_seeds": "6900ddfce2a48c502f309999",
    "rare_sweet_potato_seeds": "67dc227a59b878f195998e30",
    "common_glowing_grass_seeds": "6ae8863e99b448e3b8a1e1da",
    "rare_watermelon_seeds": "673e0c942c7bfd708b352489",
    "common_aurora_dragon_food": "6aec62ead6f343f8bda2e32b",
    "common_bell_pepper_seeds": "67dc227a59b878f195998de8",
    "uncommon_garlic_seeds": "67dc227a59b878f195998e48",
    "common_bee_food": "6a73475964ee63b1f4561ca1",
    "common_peacock_food": "69fb464a6011b66560c7b437",
    "uncommon_corn_seeds": "673e0c942c7bfd708b35240b",
    "common_bird_food": "665f2698534176fcd32f9a7d",
    "uncommon_white_lily_seeds": "6801032feafb0e6b32164706",
    "common_dragon_fruit_seeds": "69945ab309abeb19e22a83f9",
    "epic_melon_seeds": "683dbe2ba9ec974575a4bf3c",
    "legendary_ghost_food": "6abce61e4256b50d4349e806",
    "uncommon_hyacinths_seeds": "65d38d0cda839cd1e0f7ecc1",
    "common_dark_watcher_food": "6acf932cce916ef21d35f1f4",
    "common_peas_seeds": "673e0c942c7bfd708b35245f",
    "common_corn_seeds": "673e0c942c7bfd708b352405",
    "legendary_proto_flower_seeds": "6a1832bb8745e0fa5293bbac",
    "uncommon_mangold_seeds": "67dc227a59b878f195998ede",
    "uncommon_marigold_seeds": "65d38d0cda839cd1e0f7ec61",
    "uncommon_patisson_seeds": "69285140f803f06b82ab22e6",
    "uncommon_spinach_seeds": "67dc227a59b878f195998ec0",
    "uncommon_cauliflower_seeds": "67dc227a59b878f195998db2",
    "rare_white_lily_seeds": "6801032feafb0e6b3216470c",
    "legendary_jack_piggy_food": "69b9558333072e7b647f38d0",
    "epic_spooky_cauldron_seeds": "6abce62cc7313e5d05935bd5",
    "uncommon_proto_flower_seeds": "6a1832bb8745e0fa5293bb9a",
    "rare_fiery_barberry_seeds": "6a997a87146b5c4a5f9c281d",
    "uncommon_spooky_cauldron_seeds": "6abce62cc7313e5d05935bc9",
    "common_trout_seeds": "6a7c6ec3e0ba09e95a5531b6",
    "common_sugarcane_seeds": "6a6b1e1913ccd7c96918bf6b",
    "common_light_tree_seeds": "6ab282d700c19f4431021f91",
    "uncommon_pineapple_seeds": "68824771915623f3dcc1fb03",
    "uncommon_bell_pepper_seeds": "67dc227a59b878f195998dee",
    "rare_spooky_cauldron_seeds": "6abce62cc7313e5d05935bcf",
    "common_onion_seeds": "67dc227a59b878f195998dca",
    "epic_proto_flower_seeds": "6a1832bb8745e0fa5293bba6",
    "uncommon_star_anise_seeds": "6970f73d4297528ed0eb3533",
    "epic_cauliflower_seeds": "67dc227a59b878f195998dbe",
    "common_dark_fern_seeds": "6acf93679e89090bba1be81e",
    "rare_hyacinths_seeds": "65d38d0cda839cd1e0f7ecc7",
    "uncommon_dragon_fruit_seeds": "69945ab309abeb19e22a83ff",
    "common_dark_tree_seeds": "6abfafd83202113b4293f231",
    "rare_marigold_seeds": "65d38d0cda839cd1e0f7ec67",
    "rare_tomato_seeds": "65d38d0cda839cd1e0f7ec4f",
    "common_spectral_trout_seeds": "6a87292a1c0d284dcab6e185",
    "rare_proto_flower_seeds": "6a1832bb8745e0fa5293bba0",
    "rare_bamboo_seeds": "65d38d0cda839cd1e0f7ec7f",
    "common_eggplant_seeds": "673e0c942c7bfd708b352423",
    "common_firebird_food": "6a9014f3b52f06fb05edff76",
    "common_ginger_seeds": "67dc227a59b878f195998e60",
    "common_fiery_barberry_seeds": "6a997a87146b5c4a5f9c2811",
    "common_black_lotus_seeds": "673e0c942c7bfd708b35249b",
    "common_bamboo_seeds": "6582e209591717d062d19e2b",
    "common_otter_food": "6a6b1b0ab16630f880986663",
    "common_snowdrop_seeds": "67dc227a59b878f195998e9c",
    "uncommon_tomato_seeds": "65d38d0cda839cd1e0f7ec49",
    "uncommon_bamboo_seeds": "65d38d0cda839cd1e0f7ec79",
    "common_physalis_seeds": "6a3e7e10c9263d5e1dac306e"
}

def norm(s):
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode("utf-8").lower().strip()

with open(bot_path, "r", encoding="utf-8") as f:
    b_text = f.read()

m = re.search(r"const SEED_CATALOG_IDS = (\{.*?\});", b_text, re.DOTALL)
existing_cat = json.loads(m.group(1)) if m else {}
merged_cat = {**existing_cat, **inventory_ids}

new_cat_str = "const SEED_CATALOG_IDS = " + json.dumps(merged_cat, ensure_ascii=False) + ";"
b_text = re.sub(r"const SEED_CATALOG_IDS = \{.*?\};", new_cat_str, b_text, flags=re.DOTALL)

with open(bot_path, "w", encoding="utf-8") as f:
    f.write(b_text)

if os.path.exists(lib_path):
    with open(lib_path, "r", encoding="utf-8") as f:
        lib = json.load(f)

    for cname, cdata in lib.items():
        for t_str, t_info in cdata.get("tiers", {}).items():
            raw_code = t_info.get("code", "")
            clean_code = norm(raw_code)
            found_id = merged_cat.get(raw_code) or merged_cat.get(clean_code)
            if found_id:
                t_info["id"] = found_id
                t_info["seed_id"] = found_id

    with open(lib_path, "w", encoding="utf-8") as f:
        json.dump(lib, f, indent=4, ensure_ascii=False)

print(f"✅ Başarılı! Toplam {len(merged_cat)} adet tohum ve yem ID'si kalıcı havuza kaydedildi.")
