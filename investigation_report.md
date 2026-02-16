# Ticketbooth Navigasyon Sorunu: Risk Analizi ve Mimari İyileştirme Raporu

Bu rapor, "Çift Header Bar" sorununun çözümünde karşılaşılan riskleri, olası spagetti kod oluşumunu önlemek için yapılması gerekenleri ve mimari iyileştirme önerilerini içerir.

## 1. Risk ve Sorun Düzeltme Eğrisi Tablosu

Aşağıdaki tablo, olası çözüm yöntemlerini risk, karmaşıklık ve "Spagetti Kod" (kodun karmaşıklaşması ve yönetilemez hale gelmesi) olasılığı açısından değerlendirir.

| Çözüm Yöntemi | Uygulama Zorluğu | Spagetti Riski | Bakım Maliyeti (Teknik Borç) | Açıklama |
| :--- | :--- | :--- | :--- | :--- |
| **Yöntem A: Manuel Ebeveyn Gezintisi (Mevcut Deneme)** | Düşük | **Yüksek** | **Yüksek** | `get_parent()`, `get_root()` gibi fonksiyonlarla üst objeye ulaşmaya çalışmak. UI hiyerarşisi değişirse kod anında kırılır. Bileşenler birbirine sıkı sıkıya (tightly coupled) bağlanır. |
| **Yöntem B: Global Değişken / Singleton Kullanımı** | Düşük | **Çok Yüksek** | **Çok Yüksek** | Navigasyon objesini global bir değişkene atayıp her yerden erişmek. Durum yönetimi imkansızlaşır, debug etmek zorlaşır. Kesinlikle önerilmez. |
| **Yöntem C: Sinyal (Signal) Tabanlı Mimari (Önerilen)** | Orta | **Düşük** | **Düşük** | Alt bileşen (`ContentGridView`) sadece "Tıklandı" sinyali yayar. Navigasyonu kimin yapacağını bilmez. Üst bileşen (`MainView`) bu sinyali yakalar ve doğru yönlendirmeyi yapar. |
| **Yöntem D: Tam Mimari Değişikliği** | Yüksek | Orta | Orta | `Adw.NavigationView` yapısını tamamen kaldırıp `Adw.OverlaySplitView` gibi başka bir yapıya geçmek. Sorunu çözer ama çok efor gerektirir ve mevcut UI/UX akışını değiştirebilir. |

### Detaylı Risk Analizi

*   **Fonksiyon Bozma Riski:** `ContentGridView` içinde `get_root()` veya zincirleme `parent` çağrıları yapmak, bu sınıfın sadece kendi işini (listeleme) yapmasını engeller. Başka bir pencerede veya test ortamında `ContentGridView` tek başına kullanılmak istendiğinde, bu parent'ları bulamayacağı için uygulama çöker ("AttributeError: NoneType object has no attribute...").
*   **Spagetti Etkisi:** Eğer `ContentGridView` içine `if window.name == 'Main': ... else: ...` gibi koşullar eklemeye başlarsan, bu spagetti kodun başlangıcıdır. Kodun okunabilirliği azalır ve hata yapma ihtimali artar.

---

## 2. Araştırılması Gereken Konular ve Dokümantasyon

Bu sorunu "temiz" (clean code) prensiplerine uygun çözmek için aşağıdaki konuları araştırmalısın:

### A. GObject Signals (Sinyaller)
Kodun birbirine bağımlı olmasını (coupling) engellemenin en iyi yolu sinyallerdir.
*   **Araştır:** `GObject.Signal` nasıl tanımlanır? Python'da `__gsignals__` dictionary'si nasıl kullanılır?
*   **Hedef:** `ContentGridView` içinde `item-activated` gibi özel bir sinyal tanımlayıp, tıklanan filmin ID'sini bu sinyalle dışarı fırlatmayı öğrenmelisin.

### B. Libadwaita Navigation Patterns
Libadwaita'nın navigasyon mantığını tam kavramak için.
*   **Doküman:** [Adw.NavigationView](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/main/class.NavigationView.html) ve [Adw.NavigationPage](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/main/class.NavigationPage.html).
*   **Konu:** "Nested Navigation" (İç içe navigasyon) durumunda `push` ve `pop` işlemlerinin header bar'ları nasıl etkilediği. Özellikle "Navigation Controller" desenini incele.

### C. Dependency Injection (Bağımlılık Enjeksiyonu)
Eğer sinyal kullanmayacaksan, navigasyon kontrolcüsünü alt bileşene "parametresi" olarak geçme yöntemidir.
*   **Araştır:** Python'da `Dependency Injection` desenleri. `ContentGridView(navigation_controller=self.outer_nav)` şeklinde, objeyi oluştururken ona yetki verme.

---

## 3. Stratejik Yol Haritası: Önce Fix mi, Refactor mü?

**Soru:** "Kökünden mimariyi mi iyileştirmem gerekiyor yoksa önce fixleyip sonra mı?"

**Cevap:** Bu durumda **"Refactor yoluyla Fix"** (İyileştirerek Çözme) yapmalısın. Çünkü mevcut "yamalı" çözüm (parent arama) çalışmıyor ve daha fazla zorlamak kodu bozuyor.

### Önerilen Aksiyon Planı:

1.  **DUR:** `src/views/content_view.py` ve `src/views/content_grid_view.py` dosyalarında `get_ancestor` veya `get_root` ile parent arama kodlarını sil. Bu yol çıkmaz sokak.
2.  **Sinyal Tanımla:** `ContentGridView` sınıfına `movie-selected` veya `content-activated` adında yeni bir GObject sinyali ekle.
3.  **Sinyali Tetikle:** Kullanıcı bir filme tıkladığında, navigasyon kodu yazmak yerine `self.emit('content-activated', movie_object)` de.
4.  **Dinleyiciyi Kur (MainView):** `src/views/main_view.py` dosyasında, `ContentGridView` oluşturulduğu yere git.
    ```python
    # Örnek Mantık (Kod değil, pseudo-kavram)
    self.movies_dash = ContentGridView(...)
    self.movies_dash.connect('content-activated', self._on_movie_selected)
    ```
5.  **Navigasyonu Yönet (MainView):** `_on_movie_selected` fonksiyonunu `MainView` içine yaz. `MainView` zaten `self.movies_nav` (Outer Nav) objesine sahip olduğu için, push işlemini burada tertemiz bir şekilde yapabilirsin.

**Neden Bu Yöntem?**
*   **Risk:** Sıfıra yakın. `ContentGridView` bozulmaz, çünkü sadece "ben tıklandım" diye bağırıyor. Ne olacağına karışmıyor.
*   **Gelecek Yatırımı:** İleride `MainView` yerine başka bir görünüm gelse bile `ContentGridView` aynen kullanılabilir.
*   **Temizlik:** Spagetti kod oluşmaz.

### Sonuç
Mevcut yolda (parent traversing) ısrar etmek zaman kaybıdır ve risklidir. Mimariyi "Sinyal-Slot" (Event-Driven) yapısına çekerek sorunu kökten ve temiz bir şekilde çözmelisin. Araştırmanı **GObject Signals** üzerine yoğunlaştır.
