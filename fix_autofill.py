with open("/data/data/com.termux/files/home/chainers-farm/bot.py", "r", encoding="utf-8") as f:
    text = f.read()

# Eski onLibrarySelectChange fonksiyonunu bul ve doğrudan isim + seviye eşleştirmeli akıllı motorla değiştir
old_func_start = "function onLibrarySelectChange() {"

new_func = """function onLibrarySelectChange() {
            const cropName = document.getElementById("libraryCropSelect").value;
            if (!cropName || !CROPS_LIB[cropName]) return;

            const cData = CROPS_LIB[cropName];
            const tier = document.getElementById("inputSeedTier").value || "1";
            
            document.getElementById("inputSeedName").value = cropName;
            document.getElementById("inputSeedImage").value = cData.image || "";

            const tierPrefixes = { "1": "common_", "2": "uncommon_", "3": "rare_", "4": "epic_", "5": "legendary_" };
            const cleanSlug = cropName.toLowerCase().trim().replace(/\\s+/g, "_");
            const pref = tierPrefixes[tier] || "common_";
            
            // Olası kod varyasyonları (örn: rare_onion_seeds veya rare_ghost_food)
            const codeCand1 = pref + cleanSlug + "_seeds";
            const codeCand2 = pref + cleanSlug;

            if (cData.tiers && cData.tiers[tier]) {
                const tInfo = cData.tiers[tier];
                document.getElementById("inputSeedHours").value = tInfo.hours || 0;
                document.getElementById("inputSeedMinutes").value = tInfo.minutes || 0;
                document.getElementById("inputSeedBp").value = tInfo.bp_min || "0.50";
                
                let resolvedCode = tInfo.code || "";
                if (!resolvedCode) {
                    if (typeof SEED_CATALOG_IDS !== "undefined" && SEED_CATALOG_IDS[codeCand1]) {
                        resolvedCode = codeCand1;
                    } else if (typeof SEED_CATALOG_IDS !== "undefined" && SEED_CATALOG_IDS[codeCand2]) {
                        resolvedCode = codeCand2;
                    } else {
                        resolvedCode = codeCand1;
                    }
                }
                document.getElementById("inputSeedCode").value = resolvedCode;

                let autoId = "";
                if (typeof SEED_CATALOG_IDS !== "undefined") {
                    autoId = SEED_CATALOG_IDS[resolvedCode] || SEED_CATALOG_IDS[codeCand1] || SEED_CATALOG_IDS[codeCand2] || "";
                }
                if (!autoId && tInfo.id) autoId = tInfo.id;
                if (!autoId && tInfo.seed_id) autoId = tInfo.seed_id;

                document.getElementById("inputSeedId").value = autoId;
            } else {
                // Tier tanımı eksikse bile ID ve kodu yine de doldur
                let autoId = "";
                if (typeof SEED_CATALOG_IDS !== "undefined") {
                    autoId = SEED_CATALOG_IDS[codeCand1] || SEED_CATALOG_IDS[codeCand2] || "";
                }
                document.getElementById("inputSeedCode").value = codeCand1;
                document.getElementById("inputSeedId").value = autoId;
            }
        }"""

# onLibrarySelectChange başlangıcından fonksiyonun bitişine kadar olan yeri güvenle değiştir
if old_func_start in text:
    idx_start = text.find(old_func_start)
    # Fonksiyonun bittiği yer: sonraki 'function onTierChange'
    idx_end = text.find("function onTierChange()", idx_start)
    if idx_end != -1:
        text = text[:idx_start] + new_func + "\n        " + text[idx_end:]
        with open("/data/data/com.termux/files/home/chainers-farm/bot.py", "w", encoding="utf-8") as f:
            f.write(text)
        print("✅ onLibrarySelectChange motoru isim + seviye eşleştirmesiyle başarıyla güncellendi!")
    else:
        print("⚠️ onTierChange konumu bulunamadı.")
else:
    print("⚠️ onLibrarySelectChange fonksiyonu bulunamadı.")
