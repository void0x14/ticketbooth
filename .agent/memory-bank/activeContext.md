# Active Context - Ticketbooth

## Şu An Üzerinde Çalışılan
**Bug Fix Tamamlandı** - TypeError ve AttributeError düzeltildi

## Mevcut Durum (24 Aralık 2025)
Çalışan versiyon: commit d3d2908

### Düzeltilen Hatalar:
1. **TypeError: strptime() None** → `last_air_date` null check eklendi
2. **AttributeError: NoneType has no id** → `unmap` → `unrealize` sinyali

### Çalışan Özellikler:
- ✅ Mark as Watched çalışıyor
- ✅ Arama çalışıyor  
- ✅ Show detayları açılıyor
- ✅ TypeError artık oluşmuyor

### Performans (062e0ba'dan beri):
- RAM: 1.4 GB → 838 MB (%40 azalma)
- 3 show sonrası: 3.1 GB → 860 MB (%72 azalma)

## Kalan Sorunlar (İLERİDE ÇÖZÜLECEK)
- Tab geçişi yavaş (~10s, 1.9GB) - Global cache gerekiyor
- Geri dönme butonu biraz yavaş

## Son Commit'ler
```
d3d2908 fix: handle None last_air_date and use unrealize signal
5b6fbe1 fix: handle None last_air_date in notification list update (part 1)
062e0ba perf: fix memory leak with lazy loading and cache cleanup
```
