# Copyright (C) 2023 Alessandro Iepure
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
PosterButton - Widget for displaying movie/series poster in grid views.

Supports widget recycling for Gtk.GridView:
- update_content(): Update widget with new model data
- reset_state(): Clear state before recycling
"""

from gi.repository import Gio, GObject, Gtk
from pathlib import Path
from .. import shared  # type: ignore
from ..models.movie_model import MovieModel
from ..models.series_model import SeriesModel


@Gtk.Template(resource_path=shared.PREFIX + '/ui/widgets/poster_button.ui')
# =============================================================================
# 🔧 POSTER BUTONU (POSTER BUTTON) - Geri Dönüşüm İşçisi
# =============================================================================
# Bu widget, ana ekrandaki her bir film/dizi karesidir.
# GridView'un "Recycling" (Geri Dönüşüm) mekanizmasının en önemli parçasıdır.
#
# NEDEN ÖNEMLİ?
# - Her scroll yaptığında yeni buton OLUŞTURULMAZ.
# - update_content() metodu ile mevcut butonun içindeki veriler (başlık, resim)
#   sadece değiştirilir. Bu sayede işlemci yorulmaz, RAM şişmez.
#
# KRİTİK METODLAR:
# 1. update_content: Yeni film verisini butona giydirir.
# 2. reset_state: Butonu eski verilerden temizler (yeni veri gelmeden önce).
# =============================================================================
class PosterButton(Gtk.Box):
    """
    Widget shown in the main view with poster, title, and release year.

    Properties:
        title (str): content's title
        year (str): content's release year
        tmdb_id (str): content's tmdb id
        poster_path (str): content's poster uri

    Methods:
        update_content(): Update widget for new model (recycling)
        reset_state(): Clear state before recycling

    Signals:
        clicked(content: MovieModel or SeriesModel): emited when the user clicks on the widget
    """

    __gtype_name__ = 'PosterButton'

    _poster_box = Gtk.Template.Child()
    _picture = Gtk.Template.Child()
    _spinner = Gtk.Template.Child()
    _year_lbl = Gtk.Template.Child()
    _status_lbl = Gtk.Template.Child()
    _watched_lbl = Gtk.Template.Child()
    _new_release_badge = Gtk.Template.Child()
    _soon_release_badge = Gtk.Template.Child()
    _watched_badge = Gtk.Template.Child()


    # Properties
    title = GObject.Property(type=str, default='')
    year = GObject.Property(type=str, default='')
    status = GObject.Property(type=str, default='')
    tmdb_id = GObject.Property(type=str, default='')
    poster_path = GObject.Property(type=str, default='')
    watched = GObject.Property(type=bool, default=False)
    content = GObject.Property(type=object, default=None)

    __gsignals__ = {
        'clicked': (GObject.SIGNAL_RUN_FIRST, None, (object,)),
    }

    def __init__(self, content: MovieModel | SeriesModel | None = None):
        super().__init__()
        
        # Initialize state variables
        self.activate_notification = False
        self.badge_color_light = False
        self.new_release = False
        self.soon_release = False
        self.recent_change = False
        
        # If content provided, update immediately
        if content is not None:
            self.update_content(content)

    def update_content(self, content: MovieModel | SeriesModel) -> None:
        """
        Update widget with new model data.
        Called by GridView's bind callback for widget recycling.
        
        NOT: reset_state() burada ÇAĞRILMIYOR çünkü GTK4 factory lifecycle'ına
        göre unbind zaten bind'dan önce çalışıyor ve reset orada yapılıyor.
        Kaynak: https://docs.gtk.org/gtk4/class.SignalListItemFactory.html
        """
        # Store content reference
        self.content = content
        
        # Update properties from model
        self.activate_notification = content.activate_notification
        self.title = content.title
        self.badge_color_light = content.color
        self.year = content.release_date[0:4] if content.release_date else ''
        self.tmdb_id = content.id
        self.poster_path = content.poster_path
        self.watched = content.watched
        self.status = content.status
        self.new_release = content.new_release
        self.soon_release = content.soon_release
        self.recent_change = content.recent_change
        
        # Apply visual state
        self._apply_visual_state()

    def reset_state(self) -> None:
        """
        Reset widget state before recycling.
        Called by GridView's unbind callback.
        """
        # Clear content reference
        self.content = None
        
        # Reset properties
        self.title = ''
        self.year = ''
        self.status = ''
        self.tmdb_id = ''
        self.poster_path = ''
        self.watched = False
        self.activate_notification = False
        self.badge_color_light = False
        self.new_release = False
        self.soon_release = False
        self.recent_change = False
        
        # Reset visual state
        self._reset_visual_state()

    def _apply_visual_state(self) -> None:
        """Apply visual properties based on current content."""
        # Set poster image
        if self.poster_path:
            self._picture.set_file(Gio.File.new_for_uri(self.poster_path))
        self._spinner.set_visible(False)
        
        # Handle badges
        badge_visible = False
        if self.activate_notification:
            if self.recent_change:
                self._poster_box.add_css_class("pulse")
                self._picture.add_css_class("shadow")
            
            if self.new_release:
                self._new_release_badge.set_visible(True)
                badge_visible = True
                if self.badge_color_light:
                    self._new_release_badge.add_css_class("light")
                else:
                    self._new_release_badge.add_css_class("dark")
            elif self.soon_release:
                self._soon_release_badge.set_visible(True)
                badge_visible = True
                if self.badge_color_light:
                    self._soon_release_badge.add_css_class("light")
                else:
                    self._soon_release_badge.add_css_class("dark")
        
        # Year label
        if self.year:
            self._year_lbl.set_visible(True)
        else:
            self._year_lbl.set_visible(False)
        
        # Status label
        if self.status:
            self._status_lbl.set_visible(True)
        else:
            self._status_lbl.set_visible(False)
        
        # Watched badge
        if self.watched and not badge_visible:
            self._watched_badge.set_visible(True)
            if self.badge_color_light:
                self._watched_badge.add_css_class("light")
            else:
                self._watched_badge.add_css_class("dark")

    def _reset_visual_state(self) -> None:
        """Reset all visual state for recycling."""
        # Clear image and show spinner (Adw.Spinner auto-spins when visible)
        self._picture.set_file(None)
        self._spinner.set_visible(True)
        
        # Reset badges
        self._new_release_badge.set_visible(False)
        self._soon_release_badge.set_visible(False)
        self._watched_badge.set_visible(False)
        
        # Remove css classes
        self._poster_box.remove_css_class("pulse")
        self._picture.remove_css_class("shadow")
        self._new_release_badge.remove_css_class("light")
        self._new_release_badge.remove_css_class("dark")
        self._soon_release_badge.remove_css_class("light")
        self._soon_release_badge.remove_css_class("dark")
        self._watched_badge.remove_css_class("light")
        self._watched_badge.remove_css_class("dark")
        
        # Reset labels visibility
        self._year_lbl.set_visible(True)
        self._status_lbl.set_visible(True)

    @Gtk.Template.Callback('_on_map')
    def _on_map(self, user_data: object | None) -> None:
        """
        Callback for the 'map' signal.
        For GridView recycling, visual state is set in update_content().
        This is kept for backward compatibility with FlowBox.
        """
        # Only apply if content exists and not using GridView recycling
        if self.content and self.poster_path:
            self._apply_visual_state()

    @Gtk.Template.Callback('_on_poster_btn_clicked')
    def _on_poster_btn_clicked(self, user_data: object | None) -> None:
        if self.content:
            self.emit('clicked', self.content)

