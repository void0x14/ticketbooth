# Active Context - Ticketbooth

## Şu An Üzerinde Çalışılan
**Oturum Kapatıldı** - 24 Aralık 2025

## Son Durum
Çalışan versiyon: commit d3d2908

### Bugün Yapılanlar:
1. **TypeError Fix** ✅ - `strptime()` None argüman hatası düzeltildi
2. **AttributeError Fix** ✅ - `unmap` → `unrealize` sinyali
3. **Geri Dönme Butonu Analizi** ✅ - GTK4 kısıtlaması olarak kabul edildi

### Çalışan Özellikler:
- ✅ TypeError artık oluşmuyor
- ✅ Mark as Watched çalışıyor
- ✅ Arama çalışıyor
- ✅ Show detayları açılıyor

### Kabul Edilen Kısıtlamalar:
- Geri dönme butonu yavaşlığı → GTK4/libadwaita tasarlanmış davranışı
  - Dynamic pages pop'ta destroy ediliyor
  - Static pages 1400+ içerik için uygun değil
  - Cairo renderer işe yaramadı

## Kalan Sorunlar (İLERİDE ÇÖZÜLECEK)
- Tab geçişi yavaş (~10s, 1.9GB) - Global cache gerekiyor

## Son Commit'ler
```
d3d2908 fix: handle None last_air_date and use unrealize signal
5b6fbe1 fix: handle None last_air_date in notification list update (part 1)
ae89bb4 docs: update memory bank before back button test
```
