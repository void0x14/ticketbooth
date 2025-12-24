# Progress - Ticketbooth Memory Leak & Bug Fix

## Tamamlanan ✅

### Round 1: Temel Performans Düzeltmeleri (062e0ba)
| Metrik | Önceki | Şimdi | İyileşme |
|--------|--------|-------|----------|
| Açılış RAM | 1.4 GB | 838 MB | %40 ↓ |
| 3 show sonrası | 3.1 GB | 860 MB | %72 ↓ |
| Arama | Donuyordu | Hızlı | Büyük |
| Show detay | ~17s | Daha hızlı | İyi |

**Değişiklikler:**
- `details_page.py` - _on_unmap + gereksiz refresh kaldırma
- `content_view.py` - arama refresh kaldırma  
- `series_model.py` - lazy loading (seasons)
- `season_model.py` - lazy loading (episodes)

### Round 2: Bug Fix (24 Aralık 2025)

#### TypeError Fix (5b6fbe1, d3d2908)
- **Sorun:** `strptime()` None argüman alınca crash
- **Çözüm:** `serie.last_air_date` ve `new_serie.last_air_date` için null check
- **Dosya:** `main_view.py`

#### AttributeError Fix (d3d2908)
- **Sorun:** Mark as Watched çalışmıyordu - `self.content = None`
- **Kök Neden:** `unmap` sinyali ExpanderRow açılırken tetikleniyordu
- **Çözüm:** `unmap` → `unrealize` sinyali
- **Dosya:** `details_page.py`

## Yapılacak 📋
- [ ] Tab geçişi performansı (global cache gerekiyor)
- [ ] Geri dönme butonu yavaşlığı

## Bilinen Sorunlar
1. **Tab geçişi ~10 saniye + 1.9 GB RAM**: `refresh_view` tüm modelleri yeniden yüklüyor
2. **Geri dönme butonu yavaş**: Analiz edilecek

## Öğrenilen Dersler
1. **Domino etkisi**: Basit değişiklik bile zincirleme sorunlara yol açabilir
2. **Adım adım test**: Her değişiklikten sonra TÜM özellikleri test et
3. **Plan onayı**: Değişiklik yapmadan ÖNCE plan yapıp kullanıcıya onaylat
4. **GTK Sinyalleri**: `unmap` vs `unrealize` farkını bil - `unmap` reparent'ta bile tetiklenir
5. **TMDB API**: `last_air_date` null dönebilir - her zaman null check yap
