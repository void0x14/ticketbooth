# Copyright (C) 2023 Alessandro Iepure
#
# SPDX-License-Identifier: GPL-3.0-or-later

import glob
import re
from datetime import datetime, timedelta
from typing import List, Tuple
from pathlib import Path

import requests
from gi.repository import GLib, GObject
from PIL import Image, ImageFilter, ImageStat

import src.providers.local_provider as local

from .. import shared  # type: ignore
from ..models.language_model import LanguageModel
from ..models.season_model import SeasonModel


class SeriesModel(GObject.GObject):
    """
    This class represents a series object stored in the db.

    Properties:
        add_date (str): date of addition to the db (ISO format)
        backdrop_path (str): uri of the background image
        color (bool): color of the poster badges, False being dark
        created_by (List[str]): list of creators
        episodes_number (int): number of total episodes
        genres (List[str]): list of genres
        id (str): series id
        in_production (bool): whether the series is still in production
        last_air_date (str): the date of the last aired episode
        manual (bool): if the series is added manually
        new_release (bool): whether the has seen a new release since the last check
        next_air_date (str) : used to notify user on upcoming releases
        original_language (LanguageModel): LanguageModel of the original language
        original_title (str): series title in original language
        overview (str): series overview
        poster_path (str): uri of the poster image
        recent_change (bool): indicates that new/soon_release has chagned in the last check
        release_date (str): first air date in YYYY-MM-DD format
        seasons_number (int): number of total seasons
        seasons (List[SeasonModel]): list of SeasonModels
        status (str): series status
        tagline (str): series tagline
        title (str): series title
        watched (bool): whether the series has been watched completely or not
        activate_notification (bool): whether the series should be checked for new releases
        notes (str): user notes

    Methods:
        None

    Signals:
        None
    """

    __gtype_name__ = 'SeriesModel'
    activate_notification = GObject.Property(type=bool, default=False)
    add_date = GObject.Property(type=str, default='')
    backdrop_path = GObject.Property(type=str, default='')
    color = GObject.Property(type=bool, default=True)
    created_by = GObject.Property(type=GLib.strv_get_type())
    episodes_number = GObject.Property(type=int, default=0)
    genres = GObject.Property(type=GLib.strv_get_type())
    id = GObject.Property(type=str, default='')
    in_production = GObject.Property(type=bool, default=True)
    last_air_date = GObject.Property(type=str, default='')
    last_episode_number = GObject.Property(type=str, default='')
    manual = GObject.Property(type=bool, default=False)
    new_release = GObject.Property(type=bool, default=False)
    next_air_date = release_date = GObject.Property(type=str, default='')
    original_language = GObject.Property(type=LanguageModel)
    original_title = GObject.Property(type=str, default='')
    overview = GObject.Property(type=str, default='')
    poster_path = GObject.Property(type=str, default='')
    recent_change = GObject.Property(type=bool, default=False)
    release_date = GObject.Property(type=str, default='')
    seasons_number = GObject.Property(type=int, default=0)
    # =============================================================================
    # 🔧 LAZY LOADING DEĞİŞİKLİĞİ
    # =============================================================================
    # ESKİ: seasons = GObject.Property(type=object)
    # YENİ: _seasons private değişken, seasons property getter ile
    # 
    # NEDEN LAZY LOADING?
    # - Kullanıcının 482 dizisi var
    # - Her dizi ortalama 5 sezon, 50 bölüm içerir
    # - Başlangıçta tümünü yüklemek = 24,000+ obje = YAVAS + ÇOK RAM
    # - Lazy loading = Sadece görüntülenen yükle = HIZLI + AZ RAM
    # =============================================================================
    _seasons = None  # Private değişken: Sezon listesi (başta boş)
    _seasons_loaded = False  # Flag: Sezonlar yüklendi mi?
    _seasons_from_api = False  # Flag: TMDB'den mi geldi?
    soon_release = GObject.Property(type=bool, default=False)
    status = GObject.Property(type=str, default='')
    tagline = GObject.Property(type=str, default='')
    title = GObject.Property(type=str, default='')
    watched = GObject.Property(type=bool, default=False)
    notes = GObject.Property(type=str, default='')

    @property
    def seasons(self):
        """
        Sezon listesini döndürür (Lazy Loading ile).
        
        =============================================================================
        LAZY LOADING NASIL ÇALIŞIR?
        =============================================================================
        
        1. İLK ERİŞİM:
           - _seasons_loaded = False ise
           - Veritabanından yükle (get_all_seasons)
           - _seasons'a kaydet
           - _seasons_loaded = True yap
        
        2. SONRAKİ ERİŞİMLER:
           - _seasons_loaded = True
           - Direkt _seasons'dan döndür (veritabanına gitmez!)
        
        Python'da @property dekoratörü:
        - Fonksiyonu değişken gibi kullanmamızı sağlar
        - dizi.seasons yazınca bu fonksiyon çalışır
        - Parantez gerekmez!
        
        Returns:
            List[SeasonModel]: Sezon listesi
        """
        # Eğer TMDB'den geldiyse, zaten yüklendi, direkt döndür
        if self._seasons_from_api:
            return self._seasons
        
        # Henüz yüklenmediyse, şimdi yükle (lazy loading)
        if not self._seasons_loaded:
            # Veritabanından sezonları yükle
            # local modülünü burada import ediyoruz (circular import'dan kaçınmak için)
            from ..providers import local_provider as local
            self._seasons = local.LocalProvider.get_all_seasons(self.id)
            self._seasons_loaded = True
        
        return self._seasons
    
    @seasons.setter
    def seasons(self, value):
        """
        Sezon listesini ayarlar.
        
        Bu setter şu durumlarda kullanılır:
        - TMDB'den yeni dizi eklenirken (_parse_seasons sonucu)
        - Manuel dizi düznlenirken
        - Cache temizleme sırasında (value = None)
        
        Args:
            value: Yeni sezon listesi veya None
        """
        self._seasons = value
        # Eğer değer atandıysa, yüklendi sayılır
        self._seasons_loaded = value is not None

    def __init__(self, d=None, t=None):
        super().__init__()

        if d is not None:
            self.add_date = datetime.now()
            self.backdrop_path = self._download_background(d['backdrop_path'])
            self.created_by = self._parse_creators(api_dict=d['created_by'])
            self.episodes_number = d['number_of_episodes']
            self.genres = self._parse_genres(api_dict=d['genres'])
            self.id = d['id']
            self.in_production = d['in_production']
            self.last_air_date = d['last_air_date'] if d['last_air_date'] else ""
            # NULL CHECK: TMDB bazen last_episode_to_air null döndürür
            if d.get('last_episode_to_air'):
                self.last_episode_number = f"{d['last_episode_to_air']['season_number']}.{d['last_episode_to_air']['episode_number']}"
            else:
                self.last_episode_number = ""
            self.manual = False
            self.new_release = False
            next_episode_to_air = d['next_episode_to_air']
            if next_episode_to_air == None:
                self.next_air_date = ""
            else:
                self.next_air_date = next_episode_to_air['air_date']
            self.original_language = local.LocalProvider.get_language_by_code(
                d['original_language'])  # type: ignore
            self.original_title = d['original_name']
            self.overview = re.sub(r'\s{2}', ' ', d['overview'])
            # Here the color is also set since it was easy to hook it into the poster download
            self.poster_path, self.color = self._download_poster(
                d['poster_path'])
            self.recent_change = False
            self.release_date = d['first_air_date']
            self.seasons_number = d['number_of_seasons']
            # =============================================================================
            # TMDB'den gelen sezonları hemen yükle (yeni dizi ekleniyor)
            # Lazy loading kullanmıyoruz çünkü TMDB'den tüm bilgi geldi
            # =============================================================================
            self._seasons_from_api = True  # TMDB'den geldi işareti
            self.seasons = self._parse_seasons(d['seasons'])
            self.status = d['status']
            self.tagline = d['tagline']
            self.title = d['name']
            self.watched = False
            self.activate_notification = self.in_production
            if self.next_air_date != '':
                self.soon_release = datetime.strptime(
                    self.next_air_date, '%Y-%m-%d') < datetime.now() + timedelta(days=6)
            else:
                self.soon_release = False
            self.notes = ''
        else:
            self.activate_notification = t["activate_notification"] # type: ignore
            self.add_date = t["add_date"]  # type: ignore
            self.backdrop_path = t["backdrop_path"]  # type: ignore
            self.created_by = self._parse_creators(
                db_str=t["created_by"])  # type: ignore
            self.color = t["color"]  # type: ignore
            self.episodes_number = t["episodes_number"]  # type: ignore
            self.genres = self._parse_genres(
                db_str=t["genres"])  # type: ignore
            self.id = t["id"]  # type: ignore
            self.in_production = t["in_production"]  # type: ignore
            self.last_air_date = t["last_air_date"]  # type: ignore
            self.last_episode_number = t["last_episode_number"]  # type: ignore
            self.manual = t["manual"]  # type: ignore
            self.new_release = t["new_release"]
            self.next_air_date = t["next_air_date"]
            self.original_language = local.LocalProvider.get_language_by_code(
                t["original_language"])  # type: ignore
            self.original_title = t["original_title"]  # type: ignore
            self.overview = t["overview"]  # type: ignore
            self.poster_path = t["poster_path"]  # type: ignore
            self.recent_change = t["recent_change"]  # type: ignore
            self.release_date = t["release_date"]  # type: ignore
            self.seasons_number = t["seasons_number"]  # type: ignore
            self.soon_release = t["soon_release"]  # type: ignore
            self.status = t["status"]  # type: ignore
            self.tagline = t["tagline"]  # type: ignore
            self.title = t["title"]  # type: ignore
            self.watched = t["watched"]  # type: ignore

            # =============================================================================
            # 🔧 LAZY LOADING - Veritabanından yükleme
            # =============================================================================
            # ESKİ KOD (HEMEN YÜKLİYORDU - YAVAS):
            # self.seasons = local.LocalProvider.get_all_seasons(self.id)
            #
            # YENİ KOD (LAZY - HIZLI):
            # Sezonları yüklemiyoruz! _seasons ve _seasons_loaded default olarak
            # None ve False. Kullanıcı seasons property'sine eriştiğinde
            # otomatik olarak yüklenecek (@property getter sayesinde)
            #
            # Eğer t["seasons"] varsa (len 28), direkt ata
            # =============================================================================
            if len(t) == 28:    # type: ignore
                self.seasons = t["seasons"]  # type: ignore
            # else durumunda bir şey yapmıyoruz - lazy loading devreye girecek
                
            self.notes = t["notes"]  # type: ignore

    def _parse_genres(self, api_dict: dict = {}, db_str: str = '') -> List[str]:
        """
        Function to parse genres into a list of strings. Genres are provided by the TMDB API as a dict and are stored in the local db as a comma-separated string.
        Providing both arguments is an error.

        Args:
            from_api (dict): dict from TMDB API
            from_db (str): string from local db

        Returns:
            list of strings
        """

        genres = []

        if api_dict:
            for genre in api_dict:
                genres.append(genre['name'])
            return genres

        if db_str:
            return db_str.split(',')

        return genres

    def _parse_creators(self, api_dict: dict = {}, db_str: str = '') -> List[str]:
        """
        Function to parse the creators into a list of strings. Creators are provided by the TMDB API as a dict and are stored in the local db as a comma-separated string.
        Providing both arguments is an error.

        Args:
            from_api (dict): dict from TMDB API
            from_db (str): string from local db

        Returns:
            list of strings
        """

        creators = []
        if api_dict:
            for creator in api_dict:
                creators.append(creator['name'])
            return creators

        if db_str:
            return db_str.split(',')

        return creators

    def _parse_seasons(self, api_dict: dict) -> List[SeasonModel]:
        """
        Function to parse the seasons data into a list of SeasonModels.

        Args:
            api_dict (dict): dict from TMDB API

        Returns:
            list of SeasonModel
        """

        seasons = []

        for season in api_dict:
            seasons.append(SeasonModel(show_id=self.id, d=season))
        return seasons

    def _download_background(self, path: str) -> str:
        """
        Returns the uri of the background image on the local filesystem, downloading if necessary.

        Args:
            path (str): path to dowload from

        Returns:
            str with the uri of the background image
        """

        if not path:
            return ''

        files = glob.glob(f'{path[1:-4]}.jpg', root_dir=shared.background_dir)
        if files:
            return f'file://{shared.background_dir}/{files[0]}'

        url = f'https://image.tmdb.org/t/p/w500{path}'
        try:
            r = requests.get(url)
            if r.status_code == 200:
                with open(f'{shared.background_dir}{path}', 'wb') as f:
                    f.write(r.content)

                with Image.open(f'{shared.background_dir}{path}') as image:
                    image = (
                        image.convert('RGB')
                        .filter(ImageFilter.GaussianBlur(20))
                    )

                    image.save(f'{shared.background_dir}{path}', 'JPEG')

                return f'file://{shared.background_dir}{path}'
            else:
                return ''
        except (requests.exceptions.ConnectionError, requests.exceptions.SSLError):
            return ''

    def _download_poster(self, path: str) -> Tuple[str, bool]:
        """
        Returns the uri of the poster image on the local filesystem, downloading if necessary.

        Args:
            path (str): path to dowload from

        Returns:
            str with the uri of the poster image
        """

        if not path:
            return f'resource://{shared.PREFIX}/blank_poster.jpg', False

        files = glob.glob(f'{path[1:-4]}.jpg', root_dir=shared.poster_dir)
        if files:
            color = self._compute_badge_color(Path(f'{files[0]}'))
            return f'file://{shared.poster_dir}/{files[0]}', color

        url = f'https://image.tmdb.org/t/p/w500{path}'
        try:
            r = requests.get(url)
            if r.status_code == 200:
                with open(f'{shared.poster_dir}{path}', 'wb') as f:
                    f.write(r.content)
                color = self._compute_badge_color(Path(f'{path}'))
                return f'file://{shared.poster_dir}{path}', color
            else:
                return f'resource://{shared.PREFIX}/blank_poster.jpg', color
        except (requests.exceptions.ConnectionError, requests.exceptions.SSLError):
            return f'resource://{shared.PREFIX}/blank_poster.jpg', False

    def _compute_badge_color(self, path: str) -> bool:
        """
        Poster'ın sağ üst köşesinin parlaklığına göre badge rengini hesaplar.
        
        MANTIK: Poster'ın köşesi koyuysa → açık renk badge kullan (okunabilirlik için)
                Poster'ın köşesi açıksa → koyu renk badge kullan
        
        Args:
            path (str): Poster dosyasının göreceli yolu (örn: "/abc123.jpg")
            
        Returns:
            bool: True = açık renk badge kullan (koyu arka plan)
                  False = koyu renk badge kullan (açık arka plan)
        """
        
        # Varsayılan değer: koyu badge (False)
        # Eğer bir hata olursa bu değer döner
        color_light = False
        
        # TRY bloğu: Dosya açma işlemi başarısız olabilir
        # Örnek hatalar: dosya yok, bozuk resim, izin hatası
        try:
            # WITH STATEMENT (Context Manager):
            # ════════════════════════════════════════════════════════════════
            # "with" kullandığımızda Python şunu garanti eder:
            # 1. Blok başında: Image.open() çalışır, dosya açılır
            # 2. Blok sonunda: Otomatik olarak im.__exit__() çağrılır → dosya kapanır
            # 3. HATA OLSA BİLE dosya kapanır (finally gibi davranır)
            # 
            # ESKİ KOD (HATALI):
            #   im = Image.open(...)  ← Dosya açık kalıyordu, asla kapanmıyordu
            #
            # YENİ KOD (DOĞRU):
            #   with Image.open(...) as im:  ← Blok bitince otomatik kapanır
            # ════════════════════════════════════════════════════════════════
            with Image.open(Path(f'{shared.poster_dir}/{path}')) as im:
                
                # BOX: Kırpılacak bölgenin koordinatları
                # Format: (sol, üst, sağ, alt)
                # ════════════════════════════════════════════════════════════
                # im.size[0] = resmin genişliği (piksel)
                # im.size[1] = resmin yüksekliği (piksel)
                # 
                # Örnek: 500x750 piksel bir poster için:
                # box = (500-175, 0, 500, 175) = (325, 0, 500, 175)
                # Bu, sağ üst köşeden 175x175 piksellik bir kare alır
                # ════════════════════════════════════════════════════════════
                box = (im.size[0]-175, 0, im.size[0], 175)
                
                # CROP: Resmin belirtilen bölgesini kırp
                # Bu işlem YENİ bir Image objesi oluşturur (region)
                # ÖNEMLİ: Bu da bellekte yer kaplar ve kapatılmalı!
                region = im.crop(box)
                
                # İÇ TRY-FINALLY: region objesinin temizliği için
                # Median hesaplama sırasında hata olsa bile region kapatılmalı
                try:
                    # IMAGESTAT: PIL'in istatistik modülü
                    # .median = her renk kanalı (R, G, B) için ortanca değer
                    # Örnek sonuç: [128, 130, 125] (R=128, G=130, B=125)
                    median = ImageStat.Stat(region).median
                    
                    # PARLAKLIK HESABI:
                    # ════════════════════════════════════════════════════════
                    # sum(median) = R + G + B (örn: 128+130+125 = 383)
                    # 
                    # Eğer sum < 3 * 128 (384) ise → resim karanlık
                    # Eğer sum >= 384 ise → resim aydınlık
                    #
                    # 128 = 8-bit renk aralığının ortası (0-255)
                    # 3 kanal × 128 = 384 = "ortalama parlaklık" eşiği
                    # ════════════════════════════════════════════════════════
                    if sum(median) < 3 * 128:
                        # Koyu arka plan tespit edildi → açık renk badge kullan
                        color_light = True
                        
                finally:
                    # REGION.CLOSE(): Kırpılmış bölgenin belleğini serbest bırak
                    # ════════════════════════════════════════════════════════
                    # im.crop() yeni bir Image objesi oluşturur
                    # Bu obje de dosya handle'ı tutabilir (özellikle büyük resimlerde)
                    # finally bloğu: Hata olsa bile bu satır MUTLAKA çalışır
                    # ════════════════════════════════════════════════════════
                    region.close()
                    
            # WITH bloğu bitti → im otomatik olarak kapatıldı (im.close() çağrıldı)
            
        except (OSError, IOError):
            # HATA YAKALAMA:
            # ════════════════════════════════════════════════════════════════
            # OSError: Dosya bulunamadı, disk hatası, izin sorunu
            # IOError: Bozuk resim dosyası, okunamayan format
            # 
            # pass = Hiçbir şey yapma, varsayılan değeri (color_light=False) döndür
            # Kullanıcı deneyimi: Uygulama çökmek yerine koyu badge gösterir
            # ════════════════════════════════════════════════════════════════
            pass
        
        # Hesaplanan değeri döndür
        return color_light
