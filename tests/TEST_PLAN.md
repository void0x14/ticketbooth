# Ticketbooth Güvenlik ve Dayanıklılık Test Planı
**Tarih:** 27 Aralık 2025  
**Hazırlayan:** System Administrator (AI)  
**Kullanıcı:** VOID  

---

## Test Matrisi Özeti

| Katman | Test No | Test Adı | Otomasyon | Durum |
|--------|---------|----------|-----------|-------|
| 1 | T01 | Null Input | ✅ pytest | ⬜ |
| 1 | T02 | Special Characters | ✅ pytest | ⬜ |
| 1 | T03 | Network Cut | 🔧 Manuel | ⬜ |
| 1 | T04 | Rapid Fire | ✅ pytest | ⬜ |
| 2 | T05 | Watchlist CRUD | 🔧 Manuel | ⬜ |
| 2 | T06 | Poster Cache | 🔧 Manuel | ⬜ |
| 2 | T07 | Deletion Logic | ✅ pytest | ⬜ |
| 3 | T08 | Resize Stress | 🔧 Manuel | ⬜ |
| 3 | T09 | Dark/Light Mode | 🔧 Manuel | ⬜ |
| 3 | T10 | Flatpak Sandbox | 🔧 Manuel | ⬜ |
| 4 | T11 | TMDB Mapping | ✅ pytest | ⬜ |
| 4 | T12 | Duplicate Prevention | ✅ pytest | ⬜ |

---

## KATMAN 1: VERİ GİRİŞİ VE API DAYANIKLILIĞI

### T01: Null Input Test
**Hedef:** Boş veya sadece boşluk karakterli girdilerin sistemi çökertmemesi.

**Otomatik Test:** `tests/test_input_validation.py::test_null_input`

**Manuel Prosedür:**
1. Uygulamayı aç: `flatpak run --user me.iepure.Ticketbooth.Devel`
2. Arama çubuğuna odaklan
3. Hiçbir şey yazmadan Enter'a bas
4. Sadece boşluk karakteri yaz ve Enter'a bas

**Beklenen Sonuç:**
- [x] Uygulama çökmedi
- [x] Boş sonuç veya "Sonuç bulunamadı" mesajı gösterildi
- [x] Konsola hata basılmadı

---

### T02: Special Characters (SQL Injection / Unicode)
**Hedef:** Özel karakterlerin backend'i kırmaması.

**Test Girdileri:**
```
' OR 1=1 --
"; DROP TABLE movies; --
<script>alert('xss')</script>
🎬🍿
日本語テスト
```

**Otomatik Test:** `tests/test_input_validation.py::test_special_characters`

**Manuel Prosedür:**
1. Arama çubuğuna yukarıdaki girdileri sırayla yaz
2. Her girdi için Enter'a bas

**Beklenen Sonuç:**
- [x] Uygulama çökmedi
- [x] SQLite veritabanı bozulmadı
- [x] TMDB API çağrısı normal döndü (boş sonuç veya hata mesajı)

**Risk Değerlendirmesi:**
- SQLite parameterized queries kullanıyorsa: DÜŞÜK
- String concatenation kullanıyorsa: KRİTİK

---

### T03: Network Cut (Çevrimdışı Mod)
**Hedef:** İnternet kesintisinde graceful degradation.

**Manuel Prosedür:**
1. İnterneti kes: `nmcli networking off`
2. Uygulamayı aç
3. Bir film araması yap
4. Mevcut bir filmin detayına tıkla
5. İnterneti aç: `nmcli networking on`

**Beklenen Sonuç:**
- [x] "Bağlantı hatası" veya "Offline mode" mesajı
- [x] Uygulama donmadı (UI responsive kaldı)
- [x] Segfault/crash olmadı
- [x] Yerel veritabanındaki içerikler görüntülenebildi

---

### T04: Rapid Fire (Stress Test)
**Hedef:** Hızlı ardışık işlemlerin race condition oluşturmaması.

**Otomatik Test:** `tests/test_input_validation.py::test_rapid_fire_database`

**Manuel Prosedür:**
1. Listedeki bir filme tıkla
2. "Mark as Watched" butonuna 10 kez hızlıca tıkla
3. "Delete" sonra "Cancel" butonlarına hızlıca tıkla

**Beklenen Sonuç:**
- [x] "Database is locked" hatası alınmadı
- [x] UI tutarlı kaldı (watched durumu doğru)
- [x] Veritabanı bozulmadı

---

## KATMAN 2: VERİTABANI VE DURUM KORUMA

### T05: Watchlist CRUD
**Hedef:** Veri kalıcılığının doğrulanması.

**Manuel Prosedür:**
1. Uygulamayı aç
2. Bir film ara ve listeye ekle
3. Filmin ID'sini not al (TMDB ID)
4. Uygulamayı normal şekilde kapat (X butonu)
5. Uygulamayı tekrar aç
6. Eklenen filmi listede ara

**Beklenen Sonuç:**
- [x] Film listede duruyor
- [x] Tüm metadata (başlık, yıl, poster) korunmuş
- [x] watched/unwatched durumu korunmuş

---

### T06: Poster Cache
**Hedef:** Offline modda görsellerin görüntülenmesi.

**Manuel Prosedür:**
1. İnternet açıkken birkaç film ekle
2. İnterneti kes
3. Uygulamayı kapat ve tekrar aç
4. Eklenen filmlerin posterlerine bak

**Beklenen Sonuç:**
- [x] Posterler görüntülendi (cache çalışıyor)
- [x] Placeholder gösterilmedi

**Cache Lokasyonu:** `~/.var/app/me.iepure.Ticketbooth.Devel/data/posters/`

---

### T07: Deletion Logic
**Hedef:** Silme işleminin tutarlı olması.

**Otomatik Test:** `tests/test_persistence.py::test_deletion_logic`

**Manuel Prosedür:**
1. Bir filmi listeye ekle
2. O filmi sil
3. Aynı filmi tekrar arat
4. Arama sonuçlarına bak

**Beklenen Sonuç:**
- [x] "Eklendi" ibaresi/ikonu kalkmış
- [x] Film tekrar eklenebilir durumda
- [x] Veritabanından tamamen silindi

---

## KATMAN 3: UI/UX & FLATPAK DAVRANIŞI

### T08: Resize Stress
**Hedef:** Responsive tasarımın test edilmesi.

**Manuel Prosedür:**
1. Pencereyi minimum boyuta küçült (yaklaşık 360x400)
2. Grid görünümünün düzenine bak
3. Pencereyi maksimum boyuta büyüt
4. Grid görünümünün düzenine bak

**Beklenen Sonuç:**
- [x] Posterler üst üste binmedi
- [x] Grid column sayısı dinamik olarak değişti
- [x] Libadwaita Clamp düzgün çalıştı

---

### T09: Dark/Light Mode
**Hedef:** Tema geçişinin canlı olması.

**Manuel Prosedür:**
1. GNOME Settings > Appearance > Dark seç
2. Uygulamanın renklerine bak
3. Light'a geç
4. Uygulamanın renklerine bak

**Beklenen Sonuç:**
- [x] Tema anında değişti (restart gerekmedi)
- [x] Tüm elementler doğru renklendi
- [x] Kontrast okunabilir kaldı

---

### T10: Flatpak Sandbox
**Hedef:** İzolasyonun test edilmesi.

**Manuel Prosedür:**
1. Flatpak izinlerini kontrol et:
   ```bash
   flatpak info --show-permissions me.iepure.Ticketbooth.Devel
   ```
2. Uygulamanın dosya erişim isteklerini izle:
   ```bash
   flatpak run --log-session-bus me.iepure.Ticketbooth.Devel
   ```

**Beklenen Sonuç:**
- [x] Sadece gerekli izinler var (network, dconf)
- [x] Sandbox dışına dosya erişimi yok
- [x] Portal üzerinden dosya seçimi (export gibi)

---

## KATMAN 4: BUSINESS LOGIC

### T11: TMDB Mapping
**Hedef:** API verisinin doğru parse edilmesi.

**Otomatik Test:** `tests/test_business_logic.py::test_tmdb_mapping`

**Manuel Prosedür:**
1. "Interstellar" filmini arat
2. Sonuçlardan Interstellar (2014) seç
3. Detay sayfasındaki bilgileri TMDB web sitesiyle karşılaştır:
   - Yıl: 2014
   - Yönetmen: Christopher Nolan
   - Süre: 169 dakika

**Beklenen Sonuç:**
- [x] Tüm veriler TMDB ile eşleşiyor
- [x] Türkçe/İngilizce dil ayarı doğru uygulanmış

---

### T12: Duplicate Prevention
**Hedef:** Mükerrer kayıtların engellenmesi.

**Otomatik Test:** `tests/test_business_logic.py::test_duplicate_prevention`

**Manuel Prosedür:**
1. Bir filmi listeye ekle
2. Aynı filmi tekrar arat
3. "Ekle" butonuna tıklamayı dene

**Beklenen Sonuç:**
- [x] UI seviyesinde engellendi (buton disabled veya "Zaten eklendi")
- [x] Veya: Veritabanı seviyesinde unique constraint hatası
- [x] Mükerrer kayıt oluşmadı

---

## Test Sonuç Özeti

| Sonuç | Sayı |
|-------|------|
| ✅ Başarılı | 0 |
| ❌ Başarısız | 0 |
| ⬜ Beklemede | 12 |

---

## Notlar

- Otomatik testler `tests/` klasöründe bulunmaktadır.
- Testleri çalıştırmak için: `python -m pytest tests/ -v`
- Manuel testler için Flatpak sandbox içinde çalıştırın.
