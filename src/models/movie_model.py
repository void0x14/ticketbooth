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


class MovieModel(GObject.GObject):
    """
    This class represents a movie object stored in the db.

    Properties:
        activate_notification (bool): Provide notification if the movie is added to the watchlist before its release date.
        add_date (str): date of addition to the db (ISO format)
        backdrop_path (str): path where the background image is stored
        budget (float): movie budget
        color (bool): color of the poster badges, False being dark
        genres (List[str]): list of genres
        id (str): movie id
        manual (bool): if movie is added manually
        new_release (bool): if the movie has had its release
        original_language (LanguageModel): LanguageModel of the original language
        original_title (str): movie title in original language
        overview (str): movie overview, usually the main plot
        poster_path (str): path where the backgroud poster is stored
        recent_change (bool): indicates that new/soon_release was changed during the last check
        release_date (str): release date in YYYY-MM-DD format
        revenue (float): movie revenue
        runtime (int): movie runtime in minutes
        tagline (str): movie tagline
        soon_release (bool): if the movie has its release soon
        status (str): movie status, usually released or planned
        title (str): movie title
        watched (bool): if the movie has been market as watched
        notes (str): additional notes added by the user

    Methods:
        None

    Signals:
        None
    """

    __gtype_name__ = 'MovieModel'

    activate_notification = GObject.Property(type=bool, default=False)
    add_date = GObject.Property(type=str, default='')
    backdrop_path = GObject.Property(type=str, default='')
    budget = GObject.Property(type=float, default=0)
    color = GObject.Property(type=bool, default=False)
    genres = GObject.Property(type=GLib.strv_get_type())
    id = GObject.Property(type=str, default='')
    manual = GObject.Property(type=bool, default=False)
    new_release = GObject.Property(type=bool, default=False)
    original_language = GObject.Property(type=LanguageModel)
    original_title = GObject.Property(type=str, default='')
    overview = GObject.Property(type=str, default='')
    poster_path = GObject.Property(type=str, default='')
    recent_change = GObject.Property(type=bool, default=False)
    release_date = GObject.Property(type=str, default='')
    revenue = GObject.Property(type=float, default=0)
    runtime = GObject.Property(type=int, default=0)
    soon_release = GObject.Property(type=bool, default=False)
    status = GObject.Property(type=str, default='')
    tagline = GObject.Property(type=str, default='')
    title = GObject.Property(type=str, default='')
    watched = GObject.Property(type=bool, default=False)
    notes = GObject.Property(type=str, default='')

    def __init__(self, d=None, t=None):
        super().__init__()

        if d is not None:
            self.add_date = datetime.now().date()
            self.backdrop_path = self._download_background(
                path=d['backdrop_path'])
            self.budget = d['budget']
            self.genres = self._parse_genres(api_dict=d['genres'])
            self.id = d['id']
            self.manual = False
            self.new_release = False
            self.original_language = local.LocalProvider.get_language_by_code(
                d['original_language'])  # type: ignore
            self.original_title = d['original_title']
            self.overview = re.sub(r'\s{2}', ' ', d['overview'])
            self.poster_path, self.color = self._download_poster(
                path=d['poster_path'], color=False)
            self.recent_change = False
            self.release_date = d['release_date'] if d['release_date'] else None
            self.revenue = d['revenue']
            self.runtime = d['runtime']
            self.soon_release = datetime.strptime(self.release_date, '%Y-%m-%d') < datetime.strptime(self.add_date, '%Y-%m-%d') + timedelta(
                days=14) and datetime.strptime(self.release_date, '%Y-%m-%d') > datetime.strptime(self.add_date, '%Y-%m-%d') if self.release_date and self.add_date else False
            self.status = d['status']
            self.tagline = d['tagline']
            self.title = d['title']
            self.watched = False
            self.activate_notification = datetime.strptime(self.release_date, '%Y-%m-%d') > datetime.strptime(
                # if the release date is in the future activate notifications
                self.add_date, '%Y-%m-%d') if self.release_date and self.add_date else False
            self.notes = ''
        else:
            self.activate_notification = t["activate_notification"] # type: ignore
            self.add_date = t["add_date"]  # type: ignore
            self.backdrop_path = t["backdrop_path"]  # type: ignore
            self.budget = t["budget"]  # type: ignore
            self.color = t["color"] # type: ignore
            self.genres = self._parse_genres(
                db_str=t["genres"])  # type: ignore
            self.id = t["id"]  # type: ignore
            self.manual = t["manual"]  # type:ignore
            self.new_release = t["new_release"] #type: ignore
            self.original_language = local.LocalProvider.get_language_by_code(
                t["original_language"])  # type: ignore
            self.original_title = t["original_title"]  # type: ignore
            self.overview = t["overview"]  # type: ignore
            self.poster_path = t["poster_path"]  # type: ignore
            self.recent_change = t["recent_change"] # type: ignore
            self.release_date = t["release_date"]  # type: ignore
            self.revenue = t["revenue"]  # type: ignore
            self.runtime = t["runtime"]  # type: ignore
            self.soon_release = t["soon_release"] # type: ignore
            self.status = t["status"]  # type: ignore
            self.tagline = t["tagline"]  # type: ignore
            self.title = t["title"]  # type: ignore
            self.watched = t["watched"]  # type:ignore
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

    def _download_poster(self, path: str, color: bool) -> Tuple[str, bool]:
        """
        Returns the uri of the poster image on the local filesystem, downloading if necessary.

        Args:
            path (str): path to dowload from

        Returns:
            str with the uri of the poster image
        """

        if not path:
            return (f'resource://{shared.PREFIX}/blank_poster.jpg', False)

        files = glob.glob(f'{path[1:-4]}.jpg', root_dir=shared.poster_dir)
        if files:
            color = self._compute_badge_color(Path(f'{files[0]}'))
            return (f'file://{shared.poster_dir}/{files[0]}', color)

        url = f'https://image.tmdb.org/t/p/w500{path}'
        try:
            r = requests.get(url)
            if r.status_code == 200:
                with open(f'{shared.poster_dir}{path}', 'wb') as f:
                    f.write(r.content)
                color = self._compute_badge_color(Path(f'{path}'))
                return f'file://{shared.poster_dir}{path}', color
            else:
                return f'resource://{shared.PREFIX}/blank_poster.jpg', False
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
