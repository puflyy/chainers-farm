import os

bot_path = "/data/data/com.termux/files/home/chainers-farm/bot.py"
with open(bot_path, "r", encoding="utf-8") as f:
    code = f.read()

food_sync_fn = '''
def sync_foods_from_minaryganar():
    """Minaryganar farm-catalog / seeds API'sinden hayvan yemlerini çekip yem_referans.json ile birleştirir."""
    urls = [
        "https://api.minaryganar.com/api/public/chainers/farm-catalog",
        "https://api.minaryganar.com/api/public/chainers/seeds?all=true"
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Origin": "https://minaryganar.com",
        "Referer": "https://minaryganar.com/"
    }
    try:
        items = []
        for u in urls:
            res = requests.get(u, headers=headers, timeout=15)
            if res.status_code == 200:
                payload = res.json()
                if isinstance(payload, dict):
                    for k in ("animal_foods", "foods", "items", "animals"):
                        if isinstance(payload.get(k), list):
                            items.extend(payload[k])
                elif isinstance(payload, list):
                    items.extend(payload)

        if not items:
            return {"success": False, "added": 0, "updated": 0}

        ref_list = []
        if os.path.exists(YEM_REF_FILE):
            with open(YEM_REF_FILE, "r", encoding="utf-8") as f:
                ref_list = json.load(f)

        by_code_key = {entry.get("kod_anahtari"): entry for entry in ref_list if entry.get("kod_anahtari")}
        existing_item_codes = set()
        for entry in ref_list:
            for y in entry.get("yemler", []):
                if y.get("item_code"):
                    existing_item_codes.add(y["item_code"].lower())

        rarity_labels = {"common": "Common", "uncommon": "Uncommon", "rare": "Rare", "epic": "Epic", "legendary": "Legendary"}
        order = ["common", "uncommon", "rare", "epic", "legendary"]
        added, updated = 0, 0

        for item in items:
            base_code = (item.get("base_code") or item.get("code") or "").strip().lower()
            seed_type = (item.get("seed_type") or item.get("category") or "").lower()
            is_food = ("food" in base_code) or ("animal" in seed_type) or bool(item.get("compatible_animal_names"))
            if not is_food or not base_code:
                continue

            slug = base_code.replace("_food", "")
            animals = item.get("compatible_animal_names") or []
            animal_display = animals[0] if animals else (item.get("animal_name") or slug.replace("_", " ").title())
            root_title = (item.get("name") or slug.replace("_", " ").title()).replace(" Food", "").strip()

            rarities = item.get("rarities", [])
            rarities_sorted = sorted(rarities, key=lambda x: order.index(x.get("rarity", "").lower()) if x.get("rarity", "").lower() in order else 99)

            yemler_new = []
            last_sec = 0
            for r in rarities_sorted:
                r_low = (r.get("rarity") or "").lower().strip()
                if r_low not in rarity_labels:
                    continue
                bp = float(r.get("biopoints") or 0)
                sec = int(r.get("growth_time_seconds") or 0)
                if sec > 1:
                    last_sec = sec
                elif last_sec > 1:
                    sec = last_sec
                if bp <= 0 or sec <= 1:
                    continue

                tot_m = (sec + 59) // 60
                h, m = tot_m // 60, tot_m % 60
                sure_str = f"{h}h {m}m" if h > 0 and m > 0 else (f"{h}h" if h > 0 else f"{m}m")
                bp_dk = f"{bp / (sec / 60.0):.2f}".rstrip("0").rstrip(".")

                img = r.get("preview_image_path") or item.get("icon_image_path") or item.get("preview_image_path") or ""
                if img and not img.startswith("http"):
                    img = "https://api.minaryganar.com/assets" + ("" if img.startswith("/") else "/") + img

                i_code = f"{r_low}_{slug}_food"
                yemler_new.append({
                    "nadirlik": rarity_labels[r_low],
                    "yem_tam_adi": f"{rarity_labels[r_low]} {root_title} Food",
                    "item_code": i_code,
                    "gorsel": img,
                    "sure": sure_str,
                    "bp_dk": bp_dk
                })

            if not yemler_new:
                continue

            if slug in by_code_key:
                old_map = {y["nadirlik"].lower(): y for y in by_code_key[slug].get("yemler", [])}
                for yn in yemler_new:
                    old_map[yn["nadirlik"].lower()] = yn
                by_code_key[slug]["yemler"] = [old_map[k] for k in order if k in old_map]
                updated += 1
            elif not any(yn["item_code"] in existing_item_codes for yn in yemler_new):
                new_entry = {
                    "hayvan_oyun_adi": animal_display,
                    "kod_anahtari": slug,
                    "yem_koku": root_title,
                    "yemler": yemler_new
                }
                ref_list.append(new_entry)
                by_code_key[slug] = new_entry
                added += 1

        with open(YEM_REF_FILE, "w", encoding="utf-8") as f:
            json.dump(ref_list, f, indent=2, ensure_ascii=False)

        global YEM_REF_LIB
        YEM_REF_LIB = ref_list
        log(f"🥩 Minaryganar Yem Senkronizasyonu: {added} yeni yem grubu eklendi, {updated} güncellendi.")
        return {"success": True, "added": added, "updated": updated, "total": len(ref_list)}
    except Exception as e:
        log(f"⚠️ Yem senkronizasyon hatası: {e}")
        return {"success": False, "error": str(e)}
'''

if "def sync_foods_from_minaryganar():" not in code:
    code = code.replace("def load_animals():", food_sync_fn + "\ndef load_animals():", 1)

# Yem Kataloğu başlığına 'Siteden Güncelle' butonu ekle
old_food_btn = '<button type="button" class="btn-add" onclick="openFoodModal()">➕ Yem Ekle</button>'
new_food_btn = '''<div style="display:flex; gap:8px;">
                    <button type="button" class="btn-add" id="btnSyncFood" style="background:#3b82f6;" onclick="syncFoodsFromSite()">🔄 Siteden Güncelle</button>
                    <button type="button" class="btn-add" onclick="openFoodModal()">➕ Yem Ekle</button>
                </div>'''
if old_food_btn in code and "syncFoodsFromSite" not in code:
    code = code.replace(old_food_btn, new_food_btn, 1)

food_js = '''
        function syncFoodsFromSite() {
            const btn = document.getElementById('btnSyncFood');
            btn.textContent = '⏳ Çekiliyor...';
            btn.disabled = true;
            fetch('/sync_foods', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        alert(`✅ Yem Kataloğu Güncellendi!\\n• Yeni Eklenen: ${data.added} yem grubu\\n• Güncellenen: ${data.updated} yem grubu\\n• Toplam: ${data.total}`);
                        location.reload();
                    } else {
                        alert('⚠️ Yem güncelleme hatası: ' + (data.error || 'Veri alınamadı'));
                        btn.textContent = '🔄 Siteden Güncelle';
                        btn.disabled = false;
                    }
                })
                .catch(() => {
                    btn.textContent = '🔄 Siteden Güncelle';
                    btn.disabled = false;
                });
        }
'''
if "function syncFoodsFromSite()" not in code:
    code = code.replace("function openFoodModal() {", food_js + "\n        function openFoodModal() {", 1)

food_route = '''
        elif self.path == "/sync_foods":
            res_data = sync_foods_from_minaryganar()
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(res_data, ensure_ascii=False).encode("utf-8"))
'''
if 'self.path == "/sync_foods"' not in code:
    code = code.replace('elif self.path == "/delete_food":', food_route + '\n        elif self.path == "/delete_food":', 1)

if "sync_foods_from_minaryganar()" not in code.split("def run_farm():")[1]:
    code = code.replace("load_animals()", "load_animals()\n    threading.Thread(target=sync_foods_from_minaryganar, daemon=True).start()", 1)

with open(bot_path, "w", encoding="utf-8") as f:
    f.write(code)

print("✅ Yem Kataloğu otomatik senkronizasyon sistemi başarıyla eklendi!")
