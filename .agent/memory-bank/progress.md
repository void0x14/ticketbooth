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
(Liste Boş)

### Round 7: GridView Click Fix (27 Aralık 2025) ✅
- **Sorun:** Posterlere tıklandığında detay sayfası açılmıyordu.
- **Kök Neden 1:** `PosterButton.clicked` sinyali `GridView.activate` yerine bağlanmalıydı.
- **Kök Neden 2:** `window.get_application().add_navigation_page()` yöntemi yoktu.
- **Kök Neden 3:** `DetailsView(movie=model, t=...)` yanlış parametre kullanımı.
- **Çözüm:** `DetailsView(model, self)` + `page.connect('deleted', ...)` kullanıldı.
- **Commit:** `192c012`

### Round 8: g_list_store_splice Race Condition Fix (27 Aralık 2025) ✅
- **Sorun:** `g_list_store_splice: assertion 'position + n_removals <= n_items' failed`
- **Kök Neden:** `refresh_view()` çağrıldığında `_store.remove_all()` yapılıyor ama arka planda çalışan `_load_next_chunk` hala boşaltılmış store'a yazmaya çalışıyordu.
- **Çözüm:** `GLib.timeout_add` source ID takibi (`_load_source_id`) ve `refresh_view`'da `GLib.source_remove()` ile iptal.
- **Dosya:** `content_grid_view.py`

### Round 9: Scroll Performance Fixes (27 Aralık 2025) ✅
- **Sorun 1:** Drag scroll jitter - imleç ile sürüklerken ileri-geri zıplama
- **Sorun 2:** Yavaş wheel scroll - fiziksel fare scroll'u gecikmeli
- **Sorun 3:** Reverse scroll delay - aşağı-yukarı yön değişiminde takılma  
- **Kök Neden:** GridView görünürken `splice()` çağrılıyor → layout recomputation
- **Çözüm 1:** `kinetic_scrolling=False` eklendi (`0c58136`)
- **Çözüm 2:** `reset_state()` çağrısı `update_content()`'tan kaldırıldı
- **Çözüm 3:** GridView visibility `_finalize_loading()`'e taşındı - tüm modeller yüklendikten sonra göster (`207766d`)
- **Kaynaklar:** GTK4 Docs - GListStore.splice(), SignalListItemFactory lifecycle

### Round 10: Silent Refresh Fix (27 Aralık 2025) - KISMEN BAŞARISIZ
- **Sorun:** Show eklerken "Loading content..." overlay görünüyordu
- **İlk Çözüm:** `show_loading=False` parametresi eklendi
- **Sonuç:** Overlay gitti ama store boşaltıldığı için arka plan boş kaldı (Round 11'de çözüldü)
- **Commit:** `2d3c6ff`

### Round 11: Aggressive Refresh Removal & Critical Fixes (27 Aralık 2025) ✅
- **Sorun 1:** Arama dialog'u açıkken arka plan boş/gri
- **Sorun 2:** Show eklenirken dialog donuyor
- **Sorun 3:** Poster'a hızlı/çift tıklayınca detay sayfası iki kez açılıyor
- **Sorun 4:** Loglarda `UNIQUE constraint failed`, `UnidentifiedImageError` ve `Gtk-CRITICAL` hataları
- **Çözüm:** 
  - `win.refresh` kaldırıldı, silent refresh yapıldı (Commit `1eae5c5`)
  - `ContentGridView` debounce (1sn)
  - `IntegrityError` ve `PIL` error handling
  - `Gtk-CRITICAL`: `SearchResultRow` `Gtk.ListBoxRow`'dan `Gtk.Box`'a çevrildi.
- **Commit:** `1eae5c5`, `df5520b`

## Learned Lessons
1. **GTK4 ListBox vs ListView:** `Gtk.ListBoxRow` SADECE `Gtk.ListBox` içinde kullanılmalıdır. `Gtk.ListView` kullanıyorsanız (model-based), row widget'ı `Gtk.Box` veya `Adw.Bin` olmalıdır. Aksi takdirde focus yönetimi sırasında `box != NULL` assertion hataları alınır çünkü row bir ListBox parent bulamaz.
2. **Flatpak Build Caching:** kod değişiklikleri bazen Flatpak build'ine yansımaz. Kritik fixlerde mutlaka `.flatpak-builder` ve `build-dir` klasörlerini manuel silmek (`rm -rf`) ve clean build almak gerekir.

## Çözülmüş Eski Kısıtlamalar

### Geri Dönme Butonu Yavaşlığı (Artık Hızlı) ✅
- **Eski Durum:** Pop/push işlemleri yavaştı
- **Kök Neden:** FlowBox benzeri yapı 1400+ widget oluşturuyordu
- **Çözüm (Dolaylı):** GridView migrasyonu (Round 4) widget sayısını ~25'e düşürdü
- **Kaynak:** GNOME Docs - "GtkFlowBox does not implement virtualization"

## Kalan Performans İyileştirmeleri (İLERİDE)
1. **Scrollbar fast drag takılması**: `GtkPicture.set_file()` senkron yükleme yapıyor. GTK4 Docs async `GdkTexture` önerir ama karmaşık refactoring gerektirir.

## Öğrenilen Dersler
1. **API Araştırması:** Kod yazmadan ÖNCE resmi dökümantasyonu kontrol et
2. **Adw vs Gtk:** libadwaita widget'ları farklı API'lere sahip olabilir
3. **Widget Recycling:** GridView ile performans büyük ölçüde artar
4. **GTK Sinyalleri:** `unmap` vs `unrealize` farkını bil
5. **TMDB API:** `last_air_date` null dönebilir - her zaman null check yap
6. **Fish Shell Git:** Multi-line commit için her paragraf ayrı `-m` flag gerektirir
7. **Virtualization Etkisi:** GridView migrasyonu geri dönme butonu yavaşlığını da dolaylı olarak çözdü
