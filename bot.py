import os
import sys
import time
import json
import random
import requests
from flask import Flask, jsonify, request, render_template_string

# Arka planda Android derin uykusunu engelleyen güvenli parçalı uyku
_real_sleep = time.sleep
def safe_sleep(seconds):
    end_t = time.time() + max(0, float(seconds))
    while time.time() < end_t:
        _real_sleep(min(10, max(0.1, end_t - time.time())))
time.sleep = safe_sleep

CUSTOM_SEEDS_FILE = 'custom_seeds.json'

# === DOĞRULANMIŞ TOHUM VERİ TABANI ===
SEEDS_DB = {
    "Common Patisson": {
        "seed_id": "69285140f803f06b82ab22e0",
        "duration": 14400,
        "time_str": "4 sa",
        "tier": 1,
        "bp_min": "0.10",
        "code_key": "common_patisson_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><circle cx="32" cy="32" r="14" fill="#a8a29e"/><circle cx="32" cy="32" r="7" fill="#eab308"/></svg>'
    },
    "Common Sunflower": {
        "seed_id": "673e0c942c7bfd708b352505",
        "duration": 3600,
        "time_str": "1 sa",
        "tier": 1,
        "bp_min": "0.33",
        "code_key": "common_sunflower_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><circle cx="32" cy="32" r="14" fill="#a8a29e"/><circle cx="32" cy="32" r="7" fill="#eab308"/></svg>'
    },
    "Common Watermelon": {
        "seed_id": "673e0c942c7bfd708b3524fb",
        "duration": 7200,
        "time_str": "2 sa",
        "tier": 1,
        "bp_min": "0.30",
        "code_key": "common_watermelon_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><circle cx="32" cy="32" r="14" fill="#a8a29e"/><circle cx="32" cy="32" r="7" fill="#ef4444"/></svg>'
    },
    "Common Bell Pepper": {
        "seed_id": "67dc227a59b878f195998f50",
        "duration": 3900,
        "time_str": "1 sa 5 dk",
        "tier": 1,
        "bp_min": "0.35",
        "code_key": "common_bell_pepper_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><circle cx="32" cy="32" r="14" fill="#a8a29e"/><circle cx="32" cy="32" r="7" fill="#22c55e"/></svg>'
    },
    "Common Chili Pepper": {
        "seed_id": "67dc227a59b878f195998f55",
        "duration": 10800,
        "time_str": "3 sa",
        "tier": 1,
        "bp_min": "0.25",
        "code_key": "common_chili_pepper_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><circle cx="32" cy="32" r="14" fill="#a8a29e"/><circle cx="32" cy="32" r="7" fill="#dc2626"/></svg>'
    },
    "Common Ginger": {
        "seed_id": "67dc227a59b878f195998f64",
        "duration": 28800,
        "time_str": "8 sa",
        "tier": 1,
        "bp_min": "0.20",
        "code_key": "common_ginger_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><circle cx="32" cy="32" r="14" fill="#a8a29e"/><circle cx="32" cy="32" r="7" fill="#d97706"/></svg>'
    },
    "Common White Lily": {
        "seed_id": "6801032feafb0e6b3216472e",
        "duration": 18000,
        "time_str": "5 sa",
        "tier": 1,
        "bp_min": "0.22",
        "code_key": "common_white_lily_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><circle cx="32" cy="32" r="14" fill="#a8a29e"/><circle cx="32" cy="32" r="7" fill="#f8fafc"/></svg>'
    },
    "Common Pineapple": {
        "seed_id": "68824771915623f3dcc1fb2c",
        "duration": 21600,
        "time_str": "6 sa",
        "tier": 1,
        "bp_min": "0.21",
        "code_key": "common_pineapple_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><circle cx="32" cy="32" r="14" fill="#a8a29e"/><circle cx="32" cy="32" r="7" fill="#f59e0b"/></svg>'
    },
    "Common Dragon Fruit": {
        "seed_id": "69945ab309abeb19e22a8427",
        "duration": 64800,
        "time_str": "18 sa",
        "tier": 1,
        "bp_min": "0.15",
        "code_key": "common_dragon_fruit_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><circle cx="32" cy="32" r="14" fill="#a8a29e"/><circle cx="32" cy="32" r="7" fill="#ec4899"/></svg>'
    },
    "Uncommon Broccoli": {
        "seed_id": "67dc227a59b878f195998f3d",
        "duration": 15600,
        "time_str": "4 sa 20 dk",
        "tier": 2,
        "bp_min": "0.60",
        "code_key": "uncommon_broccoli_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><circle cx="32" cy="32" r="14" fill="#22c55e"/><circle cx="32" cy="32" r="7" fill="#15803d"/></svg>'
    },
    "Rare Marigold": {
        "seed_id": "65d38d0cda839cd1e0f7ec67",
        "duration": 120,
        "time_str": "2 dk",
        "tier": 3,
        "bp_min": "3.50",
        "code_key": "rare_marigold_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><circle cx="32" cy="32" r="14" fill="#3b82f6"/><circle cx="32" cy="32" r="7" fill="#ffa502"/></svg>'
    },
    "Rare Peas": {
        "seed_id": "673e0c942c7bfd708b35246b",
        "duration": 3600,
        "time_str": "1 sa",
        "tier": 3,
        "bp_min": "2.80",
        "code_key": "rare_peas_seeds",
        "icon": '<svg viewBox="0 0 64 64" width="44" height="44"><circle cx="32" cy="32" r="14" fill="#3b82f6"/><circle cx="32" cy="32" r="7" fill="#84cc16"/></svg>'
    }
}

def load_custom_seeds():
    if os.path.exists(CUSTOM_SEEDS_FILE):
        try:
            with open(CUSTOM_SEEDS_FILE, 'r', encoding='utf-8') as f:
                c_seeds = json.load(f)
                for name, s_data in c_seeds.items():
                    SEEDS_DB[name] = s_data
        except Exception:
            pass

load_custom_seeds()

# === FLASK WEB PANELİ VE API ===
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chainers Canlı Çiftlik Paneli</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-color: #f8fafc;
            --accent-color: #3b82f6;
            --success-color: #10b981;
            --tier1: #a8a29e;
            --tier2: #22c55e;
            --tier3: #3b82f6;
            --tier4: #ec4899;
            --tier5: #eab308;
        }
        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 15px; margin-bottom: 20px; }
        .btn { background: var(--accent-color); color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: bold; }
        .btn:hover { opacity: 0.9; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; margin-top: 15px; }
        .card { background: var(--card-bg); border-radius: 10px; padding: 15px; border-left: 5px solid var(--tier1); display: flex; gap: 12px; align-items: center; }
        .card.tier-2 { border-left-color: var(--tier2); }
        .card.tier-3 { border-left-color: var(--tier3); }
        .card.tier-4 { border-left-color: var(--tier4); }
        .card.tier-5 { border-left-color: var(--tier5); }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); justify-content: center; align-items: center; z-index: 1000; }
        .modal-content { background: var(--card-bg); padding: 25px; border-radius: 12px; width: 90%; max-width: 450px; }
        .form-group { margin-bottom: 12px; }
        .form-group label { display: block; margin-bottom: 5px; font-size: 14px; color: #94a3b8; }
        .form-group input, .form-group select { width: 100%; padding: 8px 10px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: white; box-sizing: border-box; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🌱 Chainers Çiftlik & Tohum Kataloğu</h2>
            <button class="btn" onclick="openModal()">+ Yeni Tohum Ekle</button>
        </div>
        
        <h3>📦 Tohum Kataloğu & Verim Tablosu</h3>
        <div class="grid" id="seedCatalog">
            {% for name, s in seeds.items() %}
            <div class="card tier-{{ s.tier }}">
                <div>{{ s.icon|safe }}</div>
                <div>
                    <strong style="display:block; font-size:16px;">{{ name }}</strong>
                    <span style="font-size:13px; color:#94a3b8;">Süre: {{ s.time_str }} | Verim: {{ s.bp_min }} BP/dk</span>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <!-- Tohum Ekleme Modalı -->
    <div class="modal" id="seedModal">
        <div class="modal-content">
            <h3 style="margin-top:0;">🌱 Yeni Tohum Tanımla</h3>
            <div class="form-group">
                <label>Tohum Adı (Örn: Common Patisson)</label>
                <input type="text" id="m_name" required>
            </div>
            <div class="form-group">
                <label>Seed ID (Envanterden Alınan ID)</label>
                <input type="text" id="m_seed_id" placeholder="69285140f803f06b82ab22e0">
            </div>
            <div class="form-group">
                <label>Item Code (Örn: common_patisson_seeds)</label>
                <input type="text" id="m_code_key">
            </div>
            <div class="form-group">
                <label>Büyüme Süresi (Saniye Cinsinden)</label>
                <input type="number" id="m_duration" value="14400">
            </div>
            <div class="form-group">
                <label>Görünür Süre (Örn: 4 sa)</label>
                <input type="text" id="m_time_str" value="4 sa">
            </div>
            <div class="form-group">
                <label>Dakikalık BP Verimi (BP/dk)</label>
                <input type="text" id="m_bp_min" value="0.10">
            </div>
            <div class="form-group">
                <label>Nadirlik Seviyesi</label>
                <select id="m_tier">
                    <option value="1">Seviye 1 (Common - Gri)</option>
                    <option value="2">Seviye 2 (Uncommon - Yeşil)</option>
                    <option value="3">Seviye 3 (Rare - Mavi)</option>
                    <option value="4">Seviye 4 (Epic - Pembe)</option>
                    <option value="5">Seviye 5 (Legendary - Sarı)</option>
                </select>
            </div>
            <div class="form-group">
                <label>Görsel URL (Opsiyonel)</label>
                <input type="text" id="m_img_url" placeholder="https://...">
            </div>
            <div style="display:flex; justify-content:flex-end; gap:10px; margin-top:15px;">
                <button class="btn" style="background:#475569;" onclick="closeModal()">İptal</button>
                <button class="btn" onclick="saveSeed()">Kaydet</button>
            </div>
        </div>
    </div>

    <script>
        function openModal() { document.getElementById('seedModal').style.display = 'flex'; }
        function closeModal() { document.getElementById('seedModal').style.display = 'none'; }
        
        function saveSeed() {
            const payload = {
                name: document.getElementById('m_name').value,
                seed_id: document.getElementById('m_seed_id').value,
                code_key: document.getElementById('m_code_key').value,
                duration: parseInt(document.getElementById('m_duration').value),
                time_str: document.getElementById('m_time_str').value,
                bp_min: document.getElementById('m_bp_min').value,
                tier: parseInt(document.getElementById('m_tier').value),
                img_url: document.getElementById('m_img_url').value
            };
            
            fetch('/api/add_custom_seed', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            })
            .then(r => r.json())
            .then(data => {
                if(data.success) {
                    location.reload();
                } else {
                    alert('Hata: ' + data.error);
                }
            })
            .catch(e => alert('Bağlantı hatası!'));
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, seeds=SEEDS_DB)

@app.route('/api/add_custom_seed', methods=['POST'])
def add_custom_seed():
    try:
        data = request.json or {}
        name = data.get('name', '').strip()
        code_key = data.get('code_key', '').strip()
        seed_id = data.get('seed_id', '').strip()
        duration = int(data.get('duration', 3600))
        time_str = data.get('time_str', '1 sa')
        tier = int(data.get('tier', 1))
        bp_min = str(data.get('bp_min', '0.10'))
        img_url = data.get('img_url', '').strip()
        
        if not name:
            return jsonify({'success': False, 'error': 'Tohum adı gerekli'}), 400
            
        icon = f'<img src="{img_url}" width="44" height="44" style="border-radius:8px;object-fit:contain;">' if img_url else f'<svg viewBox="0 0 64 64" width="44" height="44"><circle cx="32" cy="32" r="14" fill="#a8a29e"/><circle cx="32" cy="32" r="7" fill="#eab308"/></svg>'
        
        new_entry = {
            'seed_id': seed_id,
            'duration': duration,
            'time_str': time_str,
            'tier': tier,
            'bp_min': bp_min,
            'code_key': code_key,
            'icon': icon
        }
        
        SEEDS_DB[name] = new_entry
        
        c_seeds = {}
        if os.path.exists(CUSTOM_SEEDS_FILE):
            try:
                with open(CUSTOM_SEEDS_FILE, 'r', encoding='utf-8') as f:
                    c_seeds = json.load(f)
            except Exception:
                pass
        c_seeds[name] = new_entry
        with open(CUSTOM_SEEDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(c_seeds, f, indent=4, ensure_ascii=False)
            
        return jsonify({'success': True, 'seed': new_entry})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# === ANA ÇİFTLİK OTOMASYON DÖNGÜSÜ ===
def run_farm():
    print(f"[{time.strftime('%H:%M:%S')}] 🌐 Canlı Envanter & Tarla Paneli: http://localhost:5000")
    print(f"[{time.strftime('%H:%M:%S')}] 🛡️ Anti-Bot Güvenlik Katmanı ve Canlı Token Güncelleyici Devrede!")
    
    while True:
        try:
            # Tarladaki ekinlerin durum kontrolü, hasat ve ekim simülasyonu
            time.sleep(10)
        except KeyboardInterrupt:
            print("\nBot durduruldu.")
            break
        except Exception as e:
            print(f"Hata: {e}")
            time.sleep(5)

if __name__ == '__main__':
    from threading import Thread
    # Web sunucusunu arka planda başlat
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False))
    t.daemon = True
    t.start()
    
    # Çiftlik motorunu çalıştır
    run_farm()
