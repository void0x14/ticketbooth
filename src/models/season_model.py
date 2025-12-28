# Copyright (C) 2023 Alessandro Iepure
#
# SPDX-License-Identifier: GPL-3.0-or-later

import glob
import os
import re
from typing import List

import requests
from gi.repository import GObject

import src.providers.local_provider as local
import src.providers.tmdb_provider as tmdb

from .. import shared  # type: ignore
from ..models.episode_model import EpisodeModel


class SeasonModel(GObject.GObject):
    """
    This class represents a season object stored in the db.

    Properties:
        episodes (List[EpisodeModel]): list of episodes in self
        episodes_number (int): number of episodes in self
        id (str): season id
        number (int): season number
        overview (str): season overview
        poster_path (str): uri of the season's poster
        show_id (int):  id of the show the searies belongs to
        title (str): season title

    Methods:
        None

    Signals:
        None
    """

    __gtype_name__ = 'SeasonModel'

    # =============================================================================
    # 🔧 LAZY LOADING DEĞİŞİKLİĞİ - EPISODES
    # =============================================================================
    # ESKİ: episodes = GObject.Property(type=object)
    # YENİ: _episodes private değişken, episodes property getter ile
    # 
    # NEDEN?
    # - Her sezon ortalama 10-20 bölüm içerir
    # - 482 dizi × 5 sezon × 10 bölüm = ~24,000 EpisodeModel
    # - Hepsini başta yüklemek çok yavaş ve RAM tüketen
    # - Lazy loading: Sadece gerektiğinde yükle
    # =============================================================================
    _episodes = None  # Private: Bölüm listesi
    _episodes_loaded = False  # Flag: Yüklendi mi?
    _episodes_from_api = False  # Flag: TMDB'den mi geldi?

    episodes_number = GObject.Property(type=int, default=0)
    id = GObject.Property(type=str, default='')
    number = GObject.Property(type=int, default=0)
    overview = GObject.Property(type=str, default='')
    poster_path = GObject.Property(type=str, default='')
    show_id = GObject.Property(type=str, default='')
    title = GObject.Property(type=str, default='')

    @property
    def episodes(self):
        """
        Bölüm listesini döndürür (Lazy Loading ile).
        
        @property dekoratörü sayesinde:
        - sezon.episodes yazmak bu fonksiyonu çalıştırır
        - Parantez gerekmez, değişken gibi kullanılır
        
        Returns:
            List[EpisodeModel]: Bölüm listesi
        """
        # TMDB'den geldiyse direkt döndür
        if self._episodes_from_api:
            return self._episodes
        
        # Henüz yüklenmediyse, şimdi yükle
        if not self._episodes_loaded:
            from ..providers import local_provider as local
            self._episodes = local.LocalProvider.get_season_episodes(
                self.show_id, self.number)
            self._episodes_loaded = True
        
        return self._episodes
    
    @episodes.setter
    def episodes(self, value):
        """
        Bölüm listesini ayarlar.
        
        Args:
            value: Yeni bölüm listesi veya None
        """
        self._episodes = value
        self._episodes_loaded = value is not None

    def __eq__(self, other) -> bool:
        """
        Custom comparing fuction, overrides '==' operator.

        Args:
            other: object to compare to

        Returns:
            bool result of the operation
        """

        if type(other) is not SeasonModel:
            return False

        if (self.episodes_number == other.episodes_number and
            self.id == other.id and
            self.number == other.number and
            self.overview == other.overview and
            self.poster_path == other.poster_path and
            self.show_id == other.show_id and
                self.title == other.title):
            return True
        else:
            return False

    def __init__(self, show_id: int = 0, d=None, t=None):
        super().__init__()

        if d is not None:
            self.episodes_number = d['episode_count']
            self.id = d['id']
            self.number = d['season_number']
            self.overview = re.sub(r'\s{2}', ' ', d['overview'])
            self.poster_path = self._download_poster(show_id, d['poster_path'])
            self.title = d['name']
            self.show_id = show_id

            # =============================================================================
            # TMDB'den gelen bölümleri hemen yükle (yeni sezon ekleniyor)
            # =============================================================================
            self._episodes_from_api = True
            self.episodes = self._parse_episodes(
                tmdb.TMDBProvider.get_season_episodes(show_id, self.number))
        else:
            self.episodes_number = t[0]  # type: ignore
            self.id = t[1]  # type: ignore
            self.number = t[2]  # type: ignore
            self.overview = t[3]  # type: ignore
            self.poster_path = t[4]  # type: ignore
            self.title = t[5]  # type: ignore
            self.show_id = t[6]  # type: ignore

            # =============================================================================
            # 🔧 LAZY LOADING - Veritabanından yükleme
            # =============================================================================
            # ESKİ: self.episodes = local.LocalProvider.get_season_episodes(...)
            # YENİ: Yüklemiyoruz, @property getter'a bırakıyoruz
            # =============================================================================
            if len(t) == 8:  # type: ignore
                self.episodes = t[7]    # type: ignore
            # else: Lazy loading - ilk erişimde yüklenecek

    def _download_poster(self, show_id: int, path: str) -> str:
        """
        Returns the uri of the poster image on the local filesystem, downloading if necessary.

        Args:
            path (str): path to dowload from

        Returns:
            str with the uri of the poster image
        """

        if not path:
            return f'resource://{shared.PREFIX}/blank_poster.jpg'

        if not os.path.exists(f'{shared.series_dir}/{show_id}/{self.number}'):
            os.makedirs(f'{shared.series_dir}/{show_id}/{self.number}')

        files = glob.glob(
            f'{path[1:-4]}.jpg', root_dir=f'{shared.series_dir}/{show_id}/{self.number}')
        if files:
            return f'file://{shared.series_dir}/{show_id}/{self.number}/{files[0]}'

        url = f'https://image.tmdb.org/t/p/w500{path}'
        try:
            r = requests.get(url)
            if r.status_code == 200:
                with open(f'{shared.series_dir}/{show_id}/{self.number}{path}', 'wb') as f:
                    f.write(r.content)
                return f'file://{shared.series_dir}/{show_id}/{self.number}{path}'
            else:
                return f'resource://{shared.PREFIX}/blank_poster.jpg'
        except (requests.exceptions.ConnectionError, requests.exceptions.SSLError):
            return f'resource://{shared.PREFIX}/blank_poster.jpg'

    def _parse_episodes(self, episodes: dict) -> List[EpisodeModel]:
        """
        Parses episode data comming from tmdb into a list of EpisodeModels.

        Args:
            episodes (dict): dict from the api

        Returns:
            List of EpisodeModels
        """

        episode_list = []

        for episode in episodes:
            episode_list.append(EpisodeModel(d=episode))
        return episode_list
