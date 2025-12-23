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

## Kritik Dosyalar
| Dosya | Rol |
|-------|-----|
| `src/models/series_model.py` | Dizi veri modeli |
| `src/models/season_model.py` | Sezon veri modeli |
| `src/models/episode_model.py` | Bölüm veri modeli |
| `src/pages/details_page.py` | Show detay sayfası |
| `src/views/content_view.py` | Ana içerik görünümü |
| `src/views/main_view.py` | Ana pencere |
| `src/providers/local_provider.py` | Veritabanı işlemleri |

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
