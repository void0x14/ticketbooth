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
- RAM kullanımını minimize et (Tamamlandı: GridView Recycling)
- Uygulama hızını artır (Tamamlandı: Lazy Loading & Async)
- Memory leak'leri tamamen kapat (Tamamlandı: Signal Cleanup)
- Stabilite ve UX iyileştirmeleri (Devam Ediyor)

## Başarımlar (27 Aralık 2025 itibarıyla)
- Açılış süresi optimize edildi.
- 1400+ içerik ile anlık tab geçişi sağlandı.
- Kritik crash ve donma sorunları (GTK Critical, IntegrityError) çözüldü.
- RAM kullanımı 800MB civarında stabil.
