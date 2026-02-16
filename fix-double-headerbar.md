# Fix: Double Header Bar Bug

## Problem
Show detaylarına girildiğinde iki ayrı header bar görünüyor:
1. **Üst bar** — Movies / TV Series tab switcher (MainView'den)
2. **Alt bar** — Back butonu + "Broke" başlığı (DetailsView'den)

## Root Cause (Kök Neden)

Sorun **iç içe geçmiş (nested) NavigationView'lerden** kaynaklanıyor.

### Widget Hiyerarşisi

```
TicketboothWindow (Adw.ApplicationWindow)
└── Adw.ViewStack (_win_stack)
    └── MainView (Adw.Bin)
        └── Adw.NavigationView          ← DIŞ NAV (main_view.blp:42)
            └── Adw.NavigationPage ("Ticket Booth")
                └── Adw.ToolbarView
                    ├── [top] HeaderBar #1 (Movies/TV Series tabs)  ← HER ZAMAN GÖRÜNÜR
                    └── content: Box
                        └── Adw.ViewStack (_tab_stack)
                            ├── movies_nav (Adw.NavigationView)     ← İÇ NAV (main_view.py:57)
                            │   ├── NavigationPage (ContentGridView) [VISIBLE]
                            │   └── NavigationPage (DetailsView)     [PUSH EDİLDİĞİNDE]
                            │       └── Adw.ToolbarView
                            │           ├── [top] HeaderBar #2       ← İKİNCİ BAR
                            │           └── content: details...
                            └── series_nav (Adw.NavigationView)     ← İÇ NAV (main_view.py:71)
```

### Neden Oluyor?

`content_grid_view.py` satır 331:
```python
nav_view = self.get_ancestor(Adw.NavigationView)  # İÇ NAV'ı buluyor!
nav_view.push(nav_page)  # DetailsView İÇ NAV'a push ediliyor
```

`get_ancestor(Adw.NavigationView)` **en yakın** NavigationView atayı döndürür. ContentGridView `movies_nav` (İÇ NAV) içinde olduğu için, DetailsView İÇ NAV'a push ediliyor. İÇ NAV, HeaderBar #1'in **altında** olduğu için, her iki header bar da görünür.

## Fix Stratejisi

DetailsView'i İÇ NAV yerine **DIŞ NAV**'a push etmek. Böylece DIŞ NAV yeni sayfayı gösterdiğinde, HeaderBar #1'i içeren ToolbarView gizlenecek ve sadece DetailsView'in kendi HeaderBar'ı görünecek.

## Değiştirilecek Dosyalar

### 1. `src/views/content_grid_view.py` — 2 fonksiyon

#### a) `_on_item_activated` (satır 319-334)

**Mevcut kod:**
```python
nav_view = self.get_ancestor(Adw.NavigationView)
if nav_view:
    nav_page = Adw.NavigationPage(child=page, title=model.title)
    nav_view.push(nav_page)
```

**Yeni kod:**
```python
inner_nav = self.get_ancestor(Adw.NavigationView)
if inner_nav:
    outer_nav = inner_nav.get_ancestor(Adw.NavigationView)
    target_nav = outer_nav or inner_nav
    nav_page = Adw.NavigationPage(child=page, title=model.title)
    target_nav.push(nav_page)
```

#### b) `_on_child_clicked` (satır 336-364)

**Mevcut kod:**
```python
nav_view = self.get_ancestor(Adw.NavigationView)
if nav_view:
    nav_page = Adw.NavigationPage(child=page, title=content.title)
    nav_view.push(nav_page)
```

**Yeni kod:**
```python
inner_nav = self.get_ancestor(Adw.NavigationView)
if inner_nav:
    outer_nav = inner_nav.get_ancestor(Adw.NavigationView)
    target_nav = outer_nav or inner_nav
    nav_page = Adw.NavigationPage(child=page, title=content.title)
    target_nav.push(nav_page)
```

### 2. `src/views/content_view.py` — 1 fonksiyon

#### `_on_clicked` (satır 356)

**Mevcut kod:**
```python
self.get_ancestor(Adw.NavigationView).push(page)
```

**Yeni kod:**
```python
inner_nav = self.get_ancestor(Adw.NavigationView)
if inner_nav:
    outer_nav = inner_nav.get_ancestor(Adw.NavigationView)
    target_nav = outer_nav or inner_nav
    target_nav.push(page)
```

### 3. `src/pages/details_page.py` — Değişiklik gerekmeyebilir

DetailsView DIŞ NAV'a push edildiğinde, `self.get_ancestor(Adw.NavigationView)` zaten DIŞ NAV'ı bulacak.

Kontrol edilmesi gereken satırlar:
- **Satır 727-730** (`_on_edit_saved`): `get_previous_page(self)` → DIŞ NAV'dan önceki sayfa = root "Ticket Booth" page. `replace([root_page, new_details])` → Doğru çalışır.
- **Satır 815-818** (`_on_update_done`): Aynı pattern. Doğru çalışır.
- **Satır 869** (`pop()`): DIŞ NAV'dan pop → root "Ticket Booth" page'e döner. Doğru çalışır.

## Test Senaryoları

1. **Ana test:** Film/dizi posteri tıkla → Tek header bar görünmeli (DetailsView'inki)
2. **Geri butonu:** Details'den geri dön → Ana görünüm normal gelmeli
3. **Edit:** Manuel eklenen içerikte Edit → Save → Sayfa refresh olmalı
4. **Update:** TMDB içerikte Update Metadata → Başarılı güncelleme
5. **Delete:** Silme → Listeye geri dönüp refresh olmalı
6. **Episode navigation:** Dizi detaylarında bölüm düzenleme → NavigationView doğru çalışmalı

## Risk Değerlendirmesi

| Risk | Seviye | Açıklama |
|------|--------|----------|
| `get_previous_page` yanlış sayfa dönebilir | Orta | DIŞ NAV'da root page farklı, test gerekli |
| EpisodeRow'daki `get_ancestor(NavigationView)` | Düşük | episode_row.py:212 — DetailsView içinden çağrılıyor, aynı NAV'da kalır |
| ContentView (eski) uyumsuzluk | Düşük | Aktif kullanılmıyor ama safety fix yapılmalı |

## Uygulama Sırası

1. `content_grid_view.py` düzenle (2 fonksiyon)
2. `content_view.py` düzenle (1 fonksiyon)
3. `details_page.py` kontrol et (değişiklik gerekirse uygula)
4. Flatpak build & test
5. Tüm test senaryolarını çalıştır
