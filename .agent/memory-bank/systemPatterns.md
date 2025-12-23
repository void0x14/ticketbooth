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

## refresh_view() Problemi
**Kötü**: Her çağrıda tüm modeller yeniden oluşturuluyor
**Nerelerde çağrılır**:
- ~~details_page.py __init__~~ (KALDIRILDI ✅)
- ~~content_view.py arama~~ (KALDIRILDI ✅)
- main_view.py tab geçişi (TODO)
- content_view.py separate-watched değişimi
