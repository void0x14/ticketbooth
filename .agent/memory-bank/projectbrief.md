# Project Brief - Ticketbooth Memory Leak Fix

## Proje Amacı
Ticketbooth uygulamasındaki memory leak ve performans sorunlarını düzeltmek.

## Kullanıcı Profili
- 971 film + 482 dizi = 1453 içerik
- CachyOS (Arch tabanlı) Linux
- Flatpak ile development

## Temel Sorunlar (Başlangıç)
1. Uygulama açılışı yavaş (~1 dakika)
2. Show detaylarına girme yavaş (~17 saniye)
3. RAM sürekli artıyor (7+ GB'a kadar)
4. Arama donuyor
5. Tab geçişi çok yavaş

## Hedefler
- RAM kullanımını minimize et
- Uygulama hızını artır
- Memory leak'leri tamamen kapat
