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
- Dynamic pages pop'ta destroy ediliyor (libadwaita davranışı)
- Static pages: 1400+ içerik için uygun değil

### Round 4: Tab Geçişi Optimizasyonu (25 Aralık 2025 - fd053b2) ✅
- **Sorun:** Tab geçişleri yavaş (~28s ilk, ~5s sonraki). `Adw.ViewStack` widget'ları korumasına rağmen, her geçişte `refresh_view()` çağrılıp tüm widgetlar silinip yeniden oluşturuluyordu.
- **Çözüm:** `Gtk.GridView` + `Widget Recycling` implementasyonu (`fd053b2`).
- **Teknik Detay (Architecture):**
  - Eski yapı (`FlowBox` benzeri `Box` yapısı) $O(N)$ maliyetindeydi. Her tab geçişinde 1400+ widget `destroy` edilip baştan `create` ediliyordu.
  - Yeni yapı: `Gtk.GridView` ve `Gtk.SignalListItemFactory` kullanılarak **Widget Recycling** (Android'deki `RecyclerView` veya Java FX'teki `ListView` mantığı) getirildi.
  - Sadece ekranda görünen widgetlar bellekte tutulur, kaydırıldıkça modeller widgetlara "bind" edilir. Bu, tab geçişi maliyetini $O(N)$'den $O(Ekran kapasitesi)$ seviyesine indirdi.
- **Sonuç:** Hızlı tab geçişleri ve ciddi RAM tasarrufu.

### Round 5: Spinner Fix (25 Aralık 2025 - 76a9dbf) ✅
- **Sorun:** `AttributeError: 'Spinner' object has no attribute 'start'`
- **Kök Neden:** `Adw.Spinner` ≠ `Gtk.Spinner`
  - `Adw.Spinner` (libadwaita 1.6+): `start()`, `stop()`, `spinning` property YOK
  - Davranış: Görünür olduğunda otomatik döner
- **Çözüm:** `start()`/`stop()` çağrıları kaldırıldı, sadece `set_visible()` kullanılıyor
- **Kaynak:** [Adw.Spinner Docs](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/main/class.Spinner.html)

## Yapılacak 📋
Şu an aktif sorun yok.

### Round 6: Security Test Suite (27 Aralık 2025) ✅
- **Hedef:** Input validation, persistence ve business logic testleri
- **Otomasyon:** pytest ile 38 test oluşturuldu
- **Kapsam:**
  - T01-T04: Input validation (SQL Injection, Unicode, Rapid Fire)
  - T05-T07: Database persistence (CRUD, Cascade Delete)
  - T11-T12: Business logic (TMDB Mapping, Duplicate Prevention)
- **Sonuç:** 38/38 test başarılı ✅
- **Dosyalar:**
  - `tests/TEST_PLAN.md` - Kapsamlı test planı
  - `tests/test_input_validation.py` - Güvenlik testleri
  - `tests/test_persistence.py` - Veritabanı testleri
  - `tests/test_business_logic.py` - İş mantığı testleri

## Kalan Sorunlar (İLERİDE ÇÖZÜLECEK)
- **Spinner Animasyonu:** `Adw.Spinner` görünür ama dönmüyor (Main thread block? Libadwaita bug?)
- **UX Flicker:** Yeni içerik eklenirken "Loading content" overlay tüm ekranı kaplayıp posterleri gizliyor (Aggressive refresh?)

### Round 7: GridView Click Fix (27 Aralık 2025) ✅
- **Sorun:** Posterlere tıklandığında detay sayfası açılmıyordu.
- **Kök Neden 1:** `PosterButton.clicked` sinyali `GridView.activate` yerine bağlanmalıydı.
- **Kök Neden 2:** `window.get_application().add_navigation_page()` yöntemi yoktu.
- **Çözüm:** `self.get_ancestor(Adw.NavigationView).push(page)` kullanıldı.
- **Commit:** `7ae7d85`

## Bilinen Kısıtlamalar (Çözülemez)
1. **Geri dönme butonu yavaşlığı**: GTK4/libadwaita tasarlanmış davranışı

## Öğrenilen Dersler
1. **API Araştırması:** Kod yazmadan ÖNCE resmi dökümantasyonu kontrol et
2. **Adw vs Gtk:** libadwaita widget'ları farklı API'lere sahip olabilir
3. **Widget Recycling:** GridView ile performans büyük ölçüde artar
4. **GTK Sinyalleri:** `unmap` vs `unrealize` farkını bil
5. **TMDB API:** `last_air_date` null dönebilir - her zaman null check yap
