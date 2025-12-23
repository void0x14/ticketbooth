# Active Context - Ticketbooth

## Şu An Üzerinde Çalışılan
**Geri dönme butonu yavaşlığı**

## Son Yapılan Değişiklikler
1. `details_page.py` - `_on_unmap` cache temizleme eklendi
2. `details_page.py` - Gereksiz `refresh_view()` kaldırıldı
3. `content_view.py` - Arama'daki gereksiz `refresh_view()` kaldırıldı
4. `series_model.py` - seasons lazy loading eklendi
5. `season_model.py` - episodes lazy loading eklendi

## Sonraki Adımlar
1. [ŞİMDİ] Geri dönme butonu yavaşlığını analiz et ve düzelt
2. [SONRA] Tab geçişi performansı (daha köklü değişiklik gerekiyor)
3. [SONRA] Yeni show ekleme RAM artışı

## Önemli Notlar
- Tab geçişi için global model cache gerekiyor - ayrı issue olarak planlanmalı
- Her değişiklikten sonra Flatpak build + test gerekli
- Türkçe yorumlar eklenecek (PR öncesi İngilizce'ye çevrilecek)
