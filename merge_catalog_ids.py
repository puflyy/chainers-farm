import json
import os
import glob
import re

bot_path = "/data/data/com.termux/files/home/chainers-farm/bot.py"
hex_regex = re.compile(r"^[a-f0-9]{24}$")

found_ids = {}

# 1. Mevcut tüm JSON dosyalarını tara
for jf in glob.glob("/data/data/com.termux/files/home/chainers-farm/*.json"):
    try:
        with open(jf, "r", encoding="utf-8") as f:
            data = json.load(f)

            def extract(obj, parent_key=""):
                if isinstance(obj, dict):
                    s_id = obj.get("seed_id") or obj.get("seedID") or obj.get("id") or obj.get("itemId")
                    code = obj.get("code") or obj.get("code_key") or obj.get("itemCode") or parent_key

                    if s_id and isinstance(s_id, str) and hex_regex.match(s_id):
                        if code and isinstance(code, str) and ("seed" in code.lower() or "food" in code.lower()):
                            found_ids[code.lower().strip()] = s_id

                    for k, v in obj.items():
                        extract(v, k)
                elif isinstance(obj, list):
                    for item in obj:
                        extract(item, parent_key)

            extract(data)
    except Exception:
        pass

# 2. bot.py içindeki mevcut SEED_CATALOG_IDS sözlüğünü oku ve birleştir
if os.path.exists(bot_path):
    with open(bot_path, "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r"const SEED_CATALOG_IDS = (\{.*?\});", content, re.DOTALL)
    existing_catalog = {}
    if match:
        try:
            existing_catalog = json.loads(match.group(1))
        except Exception:
            pass

    # Mevcutlar ile yeni bulunanları birleştir
    merged_catalog = {**existing_catalog, **found_ids}

    # bot.py içine yeni genişletilmiş sözlüğü yaz
    new_catalog_str = "const SEED_CATALOG_IDS = " + json.dumps(merged_catalog, ensure_ascii=False) + ";"
    content = re.sub(r"const SEED_CATALOG_IDS = \{.*?\};", new_catalog_str, content, flags=re.DOTALL)

    with open(bot_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Başarılı! Katalog {len(existing_catalog)} adetten {len(merged_catalog)} adede genişletildi.")
    print("Güncel katalog bot.py'ye kaydedildi.")
else:
    print("⚠️ bot.py bulunamadı.")
