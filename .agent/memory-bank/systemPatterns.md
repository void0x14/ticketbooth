# System Patterns - Ticketbooth

## Mimari Akış
```
Kullanıcı show'a tıklıyor
    ↓
content_view.py: _on_clicked()
    ↓
details_page.py: __init__()
    ↓
local_provider.py: get_series_by_id()
    ↓
series_model.py: SeriesModel(t=result)
    ↓
[Lazy Loading ile] seasons property erişildiğinde:
    ↓
local_provider.py: get_all_seasons()
    ↓
season_model.py: SeasonModel(t=result)
    ↓
[Lazy Loading ile] episodes property erişildiğinde:
    ↓
local_provider.py: get_season_episodes()
```

## Memory Leak Pattern (ÇÖZÜLDÜ)
**Problem**: Her show girişinde obje zincirleri oluşuyor, çıkışta temizlenmiyor
**Çözüm**: `_on_unmap` sinyalinde referansları None yapma

## Lazy Loading Pattern (UYGULANDIDI)
```python
_seasons = None
_seasons_loaded = False

@property
def seasons(self):
    if not self._seasons_loaded:
        self._seasons = load()
        self._seasons_loaded = True
    return self._seasons
```

## refresh_view() Problemi ve Silent Refresh Çözümü
**Kötü**: `win.refresh()` tüm arayüzü "Loading content..." overlay'i ile kilitler ve modelleri sıfırdan oluşturur.
**Çözüm (Silent Refresh)**: Arka planda veri eklenirken `show_loading=False` parametresi ile overlay gösterilmez. Kullanıcı arayüzü kullanılabilir kalır.
**Kullanım**:
- `SearchResultRow`: İçerik eklendikten sonra ana sayfayı agresif (`win.refresh`) yenilemez.
- `ContentGridView`: Sadece veri değiştiğinde `splice` ile güncelleme yapar.

## Widget Recycling Pattern (Gtk.GridView)
Eski `Box`/`FlowBox` yapısı tüm elemanları bellekte tutarken, yeni `Gtk.GridView` sadece ekranda görünenleri oluşturur.
- **Factory**: `Gtk.SignalListItemFactory`
- **Bind**: Model verisini widget'a bağlar (ucuz işlem).
- **Unbind**: Widget'ı temizler, tekrar kullanıma hazırlar.
- **Scroll**: `kinetic_scrolling=False` ile performans optimize edildi.
