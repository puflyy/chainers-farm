import os

bot_path = "/data/data/com.termux/files/home/chainers-farm/bot.py"

with open(bot_path, "r", encoding="utf-8") as f:
    code = f.read()

sync_code = '''
def sync_crops_from_minaryganar():
    """Minaryganar public API'sinden tüm güncel tohumları çekip crops_library.json ile birleştirir."""
    url = "https://api.minaryganar.com/api/public/chainers/seeds?all=true"
    try:
        res = requests.get(url, timeout=15)
        if res.status_code != 200:
            log(f"⚠️ Minaryganar API yanıt vermedi (Kod: {res.status_code})")
            return {"success": False, "added": 0, "updated": 0}

        payload = res.json()
        items = payload.get("items", []) if isinstance(payload, dict) else payload
        if not items:
            return {"success": False, "added": 0, "updated": 0}

        lib = load_library()
        import unicodedata
        def norm(s):
            return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode("utf-8").lower().strip()

        existing_norm_map = {norm(k): k for k in lib.keys()}
        tier_map = {"common": "1", "uncommon": "2", "rare": "3", "epic": "4", "legendary": "5"}
        pref_map = {"1": "common_", "2": "uncommon_", "3": "rare_", "4": "epic_", "5": "legendary_"}

        added = 0
        updated = 0

        for item in items:
            raw_name = (item.get("name") or "").strip()
            base_code = (item.get("base_code") or "").strip().lower()
            if not raw_name:
                continue

            # İsim standardizasyonu (İlk harf büyük, kalanı küçük)
            std_name = raw_name[0].upper() + raw_name[1:].lower()
            n_key = norm(std_name)

            target_key = existing_norm_map.get(n_key, std_name)
            is_new = target_key not in lib

            img_path = item.get("icon_image_path") or item.get("preview_image_path") or ""
            if img_path and not img_path.startswith("http"):
                img_path = "https://api.minaryganar.com/assets" + ("" if img_path.startswith("/") else "/") + img_path

            rarities = item.get("rarities", [])
            order = ["common", "uncommon", "rare", "epic", "legendary"]
            rarities_sorted = sorted(rarities, key=lambda x: order.index(x.get("rarity", "").lower()) if x.get("rarity", "").lower() in order else 99)

            tiers_dict = lib.get(target_key, {}).get("tiers", {})
            last_valid_sec = 0

            for r in rarities_sorted:
                r_name = (r.get("rarity") or "").lower().strip()
                t_num = tier_map.get(r_name)
                if not t_num:
                    continue

                bp = float(r.get("biopoints") or 0)
                sec = int(r.get("growth_time_seconds") or 0)
                if sec > 1:
                    last_valid_sec = sec
                elif last_valid_sec > 1:
                    sec = last_valid_sec

                if bp <= 0 or sec <= 1:
                    continue

                total_min = (sec + 59) // 60
                h = total_min // 60
                m = total_min % 60
                bp_min_str = f"{bp / (sec / 60.0):.2f}"

                slug = base_code if base_code else norm(std_name).replace(" ", "_")
                default_code = f"{pref_map[t_num]}{slug}_seeds"

                old_tier = tiers_dict.get(t_num, {})
                old_tier["hours"] = h
                old_tier["minutes"] = m
                old_tier["bp_min"] = bp_min_str
                if not old_tier.get("code"):
                    old_tier["code"] = default_code
                tiers_dict[t_num] = old_tier

            if tiers_dict:
                if is_new:
                    lib[target_key] = {"image": img_path, "tiers": tiers_dict}
                    existing_norm_map[n_key] = target_key
                    added += 1
                else:
                    if img_path:
                        lib[target_key]["image"] = img_path
                    lib[target_key]["tiers"] = tiers_dict
                    updated += 1

        with open(LIBRARY_FILE, "w", encoding="utf-8") as f:
            json.dump(lib, f, indent=4, ensure_ascii=False)

        global CROPS_LIBRARY
        CROPS_LIBRARY = lib
        log(f"🔄 Minaryganar Kütüphane Senkronizasyonu: {added} yeni ekin eklendi, {updated} ekin güncellendi (Toplam: {len(lib)}).")
        return {"success": True, "added": added, "updated": updated, "total": len(lib)}
    except Exception as e:
        log(f"⚠️ Minaryganar senkronizasyon hatası: {e}")
        return {"success": False, "error": str(e)}
'''

if "def sync_crops_from_minaryganar():" not in code:
    code = code.replace("CROPS_LIBRARY = load_library()", "CROPS_LIBRARY = load_library()\n" + sync_code, 1)

# 2. Panel HTML'ine 'Siteden Güncelle' butonu ekle
old_btn_html = '<button type="button" class="btn-add" onclick="openSeedModal()">➕ Tohum Ekle</button>'
new_btn_html = '''<div style="display:flex; gap:8px;">
                    <button type="button" class="btn-add" id="btnSyncLib" style="background:#3b82f6;" onclick="syncLibraryFromSite()">🔄 Siteden Güncelle</button>
                    <button type="button" class="btn-add" onclick="openSeedModal()">➕ Tohum Ekle</button>
                </div>'''
if old_btn_html in code and "syncLibraryFromSite" not in code:
    code = code.replace(old_btn_html, new_btn_html, 1)

# 3. JS fonksiyonu ekle
sync_js = '''
        function syncLibraryFromSite() {
            const btn = document.getElementById('btnSyncLib');
            btn.textContent = '⏳ Çekiliyor...';
            btn.disabled = true;
            fetch('/sync_library', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        alert(`✅ Kütüphane Güncellendi!\\n• Yeni Eklenen: ${data.added} ekin\\n• Güncellenen: ${data.updated} ekin\\n• Toplam Kütüphane: ${data.total} ekin`);
                        location.reload();
                    } else {
                        alert('⚠️ Güncelleme sırasında hata oluştu.');
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
if "function syncLibraryFromSite()" not in code:
    code = code.replace("function openSeedModal() {", sync_js + "\n        function openSeedModal() {", 1)

# 4. POST route ekle (/sync_library)
sync_route = '''
        elif self.path == "/sync_library":
            res_data = sync_crops_from_minaryganar()
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(res_data, ensure_ascii=False).encode("utf-8"))
'''
if 'self.path == "/sync_library"' not in code:
    code = code.replace('elif self.path == "/delete_seed":', sync_route + '\n        elif self.path == "/delete_seed":', 1)

# 5. Bot açılışında otomatik senkronizasyon çağrısı ekle
if "def run_farm():" in code and "sync_crops_from_minaryganar()" not in code.split("def run_farm():")[1]:
    code = code.replace("load_seeds()", "load_seeds()\n    threading.Thread(target=sync_crops_from_minaryganar, daemon=True).start()", 1)

with open(bot_path, "w", encoding="utf-8") as f:
    f.write(code)

print("✅ Otomatik Minaryganar senkronizasyon sistemi başarıyla kuruldu!")
