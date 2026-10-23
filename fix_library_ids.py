import json
import os

lib_path = "/data/data/com.termux/files/home/chainers-farm/crops_library.json"
bot_path = "/data/data/com.termux/files/home/chainers-farm/bot.py"

seed_id_map = {
    "epic_ghost_food": "6abce61e4256b50d4349e800",
    "common_onion_seeds": "67dc227a59b878f195998dca",
    "rare_onion_seeds": "67dc227a59b878f195998dd6",
    "legendary_ghost_food": "6abce61e4256b50d4349e806",
    "common_hyacinths_seeds": "6582e209591717d062d19e3d",
    "uncommon_hyacinths_seeds": "65d38d0cda839cd1e0f7ecc1",
    "rare_hyacinths_seeds": "65d38d0cda839cd1e0f7ecc7",
    "uncommon_spinach_seeds": "67dc227a59b878f195998ec0",
    "common_melon_seeds": "683dbe2ba9ec974575a4bf2a",
    "epic_melon_seeds": "683dbe2ba9ec974575a4bf3c",
    "common_cabbage_seeds": "67dc227a59b878f195998d8e",
    "common_proto_flower_seeds": "6a1832bb8745e0fa5293bb94",
    "uncommon_proto_flower_seeds": "6a1832bb8745e0fa5293bb9a",
    "rare_proto_flower_seeds": "6a1832bb8745e0fa5293bba0",
    "epic_proto_flower_seeds": "6a1832bb8745e0fa5293bba6",
    "common_light_tree_seeds": "6ab282d700c19f4431021f91",
    "common_ghost_food": "6abce61e4256b50d4349e7ee",
    "uncommon_ghost_food": "6abce61e4256b50d4349e7f4",
    "rare_ghost_food": "6abce61e4256b50d4349e7fa",
    "uncommon_star_anise_seeds": "6970f73d4297528ed0eb3533",
    "common_cauliflower_seeds": "67dc227a59b878f195998dac",
    "epic_cauliflower_seeds": "67dc227a59b878f195998dbe",
    "common_dark_fern_seeds": "6acf93679e89090bba1be81e",
    "common_spooky_cauldron_seeds": "6abce62cc7313e5d05935bc3",
    "uncommon_spooky_cauldron_seeds": "6abce62cc7313e5d05935bc9",
    "rare_spooky_cauldron_seeds": "6abce62cc7313e5d05935bcf",
    "uncommon_dragon_fruit_seeds": "69945ab309abeb19e22a83ff",
    "uncommon_sunflower_seeds": "673e0c942c7bfd708b3524bf",
    "rare_sunflower_seeds": "673e0c942c7bfd708b3524c5",
    "common_bell_pepper_seeds": "67dc227a59b878f195998de8",
    "rare_bell_pepper_seeds": "67dc227a59b878f195998df4",
    "common_white_lily_seeds": "6801032feafb0e6b32164700",
    "rare_white_lily_seeds": "6801032feafb0e6b3216470c",
    "rare_watermelon_seeds": "673e0c942c7bfd708b352489",
    "common_mangold_seeds": "67dc227a59b878f195998ed8",
    "rare_mangold_seeds": "67dc227a59b878f195998ee4",
    "common_dark_tree_seeds": "6abfafd83202113b4293f231",
    "uncommon_strawberry_seeds": "673e0c942c7bfd708b352447",
    "common_marigold_seeds": "6582e209591717d062d19e25",
    "uncommon_marigold_seeds": "65d38d0cda839cd1e0f7ec61",
    "rare_marigold_seeds": "65d38d0cda839cd1e0f7ec67",
    "common_tomato_seeds": "6582e209591717d062d19e1f",
    "uncommon_tomato_seeds": "65d38d0cda839cd1e0f7ec49",
    "rare_tomato_seeds": "65d38d0cda839cd1e0f7ec4f",
    "rare_broccoli_seeds": "67dc227a59b878f195998d7c",
    "common_bird_food": "665f2698534176fcd32f9a7d",
    "common_corn_seeds": "673e0c942c7bfd708b352405",
    "uncommon_corn_seeds": "673e0c942c7bfd708b35240b",
    "common_peas_seeds": "673e0c942c7bfd708b35245f",
    "rare_peas_seeds": "673e0c942c7bfd708b35246b",
    "common_spectral_trout_seeds": "6a87292a1c0d284dcab6e185",
    "common_bamboo_seeds": "6582e209591717d062d19e2b",
    "uncommon_bamboo_seeds": "65d38d0cda839cd1e0f7ec79",
    "rare_bamboo_seeds": "65d38d0cda839cd1e0f7ec7f",
    "legendary_jack_piggy_food": "69b9558333072e7b647f38d0",
    "uncommon_pineapple_seeds": "68824771915623f3dcc1fb03",
    "common_eggplant_seeds": "673e0c942c7bfd708b352423",
    "rare_garlic_seeds": "67dc227a59b878f195998e4e",
    "common_firebird_food": "6a9014f3b52f06fb05edff76",
    "uncommon_chili_pepper_seeds": "67dc227a59b878f195998e0c",
    "common_leek_seeds": "67dc227a59b878f195998ef6",
    "uncommon_jack_pumpkin_seeds": "6900ddfce2a48c502f309999",
    "common_patisson_seeds": "69285140f803f06b82ab22e0",
    "uncommon_patisson_seeds": "69285140f803f06b82ab22e6",
    "common_radish_seeds": "67dc227a59b878f195998e7e",
    "common_ginger_seeds": "67dc227a59b878f195998e60",
    "common_fiery_barberry_seeds": "6a997a87146b5c4a5f9c2811",
    "common_black_lotus_seeds": "673e0c942c7bfd708b35249b",
    "uncommon_sweet_potato_seeds": "67dc227a59b878f195998e2a",
    "common_bee_food": "6a73475964ee63b1f4561ca1",
    "common_otter_food": "6a6b1b0ab16630f880986663",
    "common_snowdrop_seeds": "67dc227a59b878f195998e9c",
    "common_physalis_seeds": "6a3e7e10c9263d5e1dac306e",
    "common_sugarcane_seeds": "6a6b1e1913ccd7c96918bf6b"
}

tier_prefix = {"1": "common_", "2": "uncommon_", "3": "rare_", "4": "epic_", "5": "legendary_"}

# 1. crops_library.json dosyasını güncelle
if os.path.exists(lib_path):
    with open(lib_path, "r", encoding="utf-8") as f:
        crops = json.load(f)

    for cname, cdata in crops.items():
        tiers = cdata.get("tiers", {})
        cslug = cname.lower().replace(" ", "_")
        for t_str, t_info in tiers.items():
            code = t_info.get("code")
            if not code:
                pref = tier_prefix.get(str(t_str), "common_")
                cand1 = f"{pref}{cslug}_seeds"
                cand2 = f"{pref}{cslug}"
                if cand1 in seed_id_map:
                    code = cand1
                elif cand2 in seed_id_map:
                    code = cand2
                else:
                    code = cand1
                t_info["code"] = code

            if code in seed_id_map:
                t_info["id"] = seed_id_map[code]
                t_info["seed_id"] = seed_id_map[code]

    with open(lib_path, "w", encoding="utf-8") as f:
        json.dump(crops, f, indent=4, ensure_ascii=False)
    print("✅ crops_library.json başarıyla tüm ID ve kodlarla donatıldı!")

# 2. bot.py içindeki onLibrarySelectChange fonksiyonunun tInfo.id/seed_id okumasını sağla
if os.path.exists(bot_path):
    with open(bot_path, "r", encoding="utf-8") as f:
        bot_code = f.read()

    old_target = 'document.getElementById("inputSeedCode").value = sCode;'
    if old_target not in bot_code:
        old_target = "document.getElementById('inputSeedCode').value = sCode;"

    replacement = """document.getElementById("inputSeedCode").value = sCode;
                let foundId = tInfo.id || tInfo.seed_id || (typeof SEED_CATALOG_IDS !== "undefined" && SEED_CATALOG_IDS[sCode] ? SEED_CATALOG_IDS[sCode] : "");
                if (foundId) {
                    document.getElementById("inputSeedId").value = foundId;
                }"""

    if old_target in bot_code and "let foundId = tInfo.id" not in bot_code:
        bot_code = bot_code.replace(old_target, replacement, 1)
        with open(bot_path, "w", encoding="utf-8") as f:
            f.write(bot_code)
        print("✅ bot.py içindeki ID doldurma mantığı tInfo bağlantısıyla güçlendirildi!")

print("Tamamlandı.")
