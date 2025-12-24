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
- `details_page.py` - cache temizleme + gereksiz refresh kaldırma
- `content_view.py` - arama refresh kaldırma  
- `series_model.py` - lazy loading (seasons)
- `season_model.py` - lazy loading (episodes)

### Round 2: Bug Fix (24 Aralık 2025)

#### TypeError Fix (5b6fbe1, d3d2908)
- **Sorun:** `strptime()` None argüman alınca crash
- **Çözüm:** `serie.last_air_date` ve `new_serie.last_air_date` için null check
- **Dosya:** `main_view.py`

#### AttributeError Fix (d3d2908)
- **Sorun:** Mark as Watched - `self.content = None`
- **Kök Neden:** `unmap` sinyali ExpanderRow açılırken tetikleniyordu
- **Çözüm:** `unmap` → `unrealize` sinyali
- **Dosya:** `details_page.py`

### Round 3: Geri Dönme Butonu Analizi (24 Aralık 2025)

**Sonuç: GTK4 Kısıtlaması - Scope Dışı**

- Eleme testi: unrealize callback → NEDEN DEĞİL
- Derinlemesine araştırma: Dynamic pages pop'ta destroy ediliyor (libadwaita dokümantasyonu)
- Static pages: Ticketbooth için uygun değil (1400+ içerik)
- Cairo renderer: Hız yok + RAM artışı + kasma

## Yapılacak 📋
- [ ] Tab geçişi performansı (AÇIK SORUN - Çözüm bulunamadı)

## Devam Eden Araştırma: Tab Geçişi (24 Aralık 2025)

### Sorun
- Movies → TV Series: İlk geçiş ~28s, sonrakiler ~5s
- TV Series → Movies: ~5s

### Denenen Çözümler (Başarısız)
1. **Smart Refresh (Signature Karşılaştırma):**
   - `LocalProvider.get_content_signature()` eklendi
   - `ContentView.refresh_view()` içinde signature karşılaştırması
   - **Sonuç:** Çalışmadı - süreler aynı kaldı

2. **Diff Update & Async Loading:**
   - `_children_map` ile widget takibi
   - `_update_content()` ile diff mantığı
   - `GLib.idle_add()` ile async widget oluşturma
   - **Sonuç:** Çalışmadı - posterler akarak yüklenmedi, süreler aynı

3. **Tab geçişinde refresh devre dışı:**
   - `_check_needs_refresh` içinde refresh_view comment out
   - **Sonuç:** UI bozuldu

### Kök Neden (Henüz Çözülemedi)
- `refresh_view()` her tab geçişinde tüm widget'ları siliyor
- `Adw.ViewStack` widget'ları korumasına rağmen, kod manuel olarak siliyor
- Neden Diff/Async çalışmadı belirsiz

### Sonraki Adım
- Gemini ile daha kapsamlı araştırma yapılacak

## Bilinen Kısıtlamalar (Çözülemez)
1. **Geri dönme butonu yavaşlığı**: GTK4/libadwaita tasarlanmış davranışı
   - Dynamic pages pop'ta destroy ediliyor
   - Karmaşık widget hierarchy destroy maliyeti

## Öğrenilen Dersler
1. **Domino etkisi**: Basit değişiklik bile zincirleme sorunlara yol açabilir
2. **Adım adım test**: Her değişiklikten sonra TÜM özellikleri test et
3. **Plan onayı**: Değişiklik yapmadan ÖNCE plan yapıp kullanıcıya onaylat
4. **GTK Sinyalleri**: `unmap` vs `unrealize` farkını bil
5. **TMDB API**: `last_air_date` null dönebilir - her zaman null check yap
6. **libadwaita**: Dynamic pages pop'ta destroy ediliyor - performans kısıtlaması
7. **Tab Geçişi**: Widget silip yeniden oluşturma çok maliyetli - diff mantığı teorik olarak doğru ama uygulamada sorunlar çıktı
