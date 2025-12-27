# Tech Context - Ticketbooth

## Teknolojiler
- **Dil**: Python 3.13
- **UI Framework**: GTK4 + Libadwaita (Adw)
- **Build**: Flatpak + Meson
- **Veritabanı**: SQLite3
- **Resim işleme**: PIL (Pillow)
- **API**: TMDB

## Build Komutları
```bash
# Devel build
flatpak-builder --user --install --force-clean build-dir me.iepure.Ticketbooth.Devel.json

# Çalıştır
flatpak run --user me.iepure.Ticketbooth.Devel
```

## Kritik Dosyalar ve Öğretici Satırlar
Bu projenin mimarisini ve atılan adımları anlamak için hazırlanan özel kılavuz: 
👉 [ticketbooth-ogretici.md](file:///home/ulactube/Documents/ticketbooth/.agent/ticketbooth-ogretici.md)

| Dosya | Rol | Önemli Bilgi |
|-------|-----|--------------|
| `src/models/series_model.py` | Dizi veri modeli | Lazy Loading mimarisi burada. |
| `src/pages/details_page.py` | Show detay sayfası | Memory Leak (unrealize) fixi burada. |
| `src/views/content_grid_view.py` | Ana içerik görünümü | GridView & Virtualization (Recycling) burada. |
| `src/providers/local_provider.py` | Veritabanı işlemleri | SQLite şeması ve migration burada. |
| `src/views/main_view.py` | Ana pencere | API hata yönetimi ve Tab kontrolü burada. |

## GObject Property Sistemi
```python
# GTK'da property tanımlama:
seasons = GObject.Property(type=object)

# Lazy loading için @property kullanılır:
@property
def seasons(self):
    if not self._seasons_loaded:
        self._seasons = load_from_db()
        self._seasons_loaded = True
    return self._seasons
```
