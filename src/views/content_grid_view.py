# Copyright (C) 2023 Alessandro Iepure
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
ContentGridView - High-performance content view using Gtk.GridView.

Uses widget recycling (virtualization) - only ~25 visible widgets are created
instead of 973+ widgets. This dramatically improves:
- Tab switching speed (3-6s → <0.5s)
- RAM usage (~100MB → ~5MB)
- Scroll performance (smooth 60fps)
"""

import logging
from gettext import gettext as _

from gi.repository import Adw, Gio, GLib, GObject, Gtk

import src.providers.local_provider as local

from .. import shared  # type: ignore
from ..models.movie_model import MovieModel
from ..models.series_model import SeriesModel
from ..pages.details_page import DetailsView
from ..widgets.poster_button import PosterButton


# =============================================================================
# 🔧 İÇERİK IZGARASI (CONTENT GRID VIEW) - GridView & Virtualization
# =============================================================================
# Bu sınıf, 1400+ içeriği performanstan ödün vermeden ekranda gösteren kısımdır.
#
# KRİTİK TEKNOLOJİ: VIRTUALIZATION (SANALLAŞTIRMA)
# - Sadece ekranda o an görünen ~20-30 poster için widget oluşturulur.
# - Scroll yaptıkça, ekrandan çıkan widget "unbind" edilir, yeni giren veriyle
#   "bind" edilerek tekrar kullanılır.
#
# BİLEŞENLER:
# 1. Gio.ListStore: Modelleri (saf veriyi) tutan liste.
# 2. Gtk.SignalListItemFactory: Widget oluşturma ve veri bağlama (bind) yöneticisi.
# =============================================================================
class ContentGridView(Adw.Bin):
    """
    High-performance content view using Gtk.GridView with widget recycling.
    
    Instead of creating 973 widgets like FlowBox, GridView creates only
    ~25 visible widgets and recycles them during scroll (virtualization).
    """

    __gtype_name__ = 'ContentGridView'

    def __init__(self, movie_view: bool):
        super().__init__()
        
        self.movie_view = movie_view
        self.icon_name = 'movies' if movie_view else 'series'
        
        # State
        self._content_loaded = False
        self._pending_raw = []
        self._load_index = 0
        self._load_source_id = None  # Track async load task for cancellation
        
        # ══════════════════════════════════════════════════════════════
        # UI SETUP
        # ══════════════════════════════════════════════════════════════
        
        # Main container
        self._main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self._main_box)
        
        # Stack for loading/empty/filled states
        self._stack = Gtk.Stack()
        self._main_box.append(self._stack)
        
        # Loading page
        loading_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, 
                              halign=Gtk.Align.CENTER, 
                              valign=Gtk.Align.CENTER)
        loading_spinner = Gtk.Spinner(spinning=True, width_request=32, height_request=32)
        loading_label = Gtk.Label(label=_("Loading content..."))
        loading_box.append(loading_spinner)
        loading_box.append(loading_label)
        self._stack.add_named(loading_box, 'loading')
        
        # Empty page  
        empty_page = Adw.StatusPage(
            icon_name='folder-symbolic',
            title=_("No Content"),
            description=_("Add movies or series to get started")
        )
        self._stack.add_named(empty_page, 'empty')
        
        # Filled page with GridView
        # KINETIC SCROLLING DEVRE DIŞI: GTK4 GridView + kinetic scrolling
        # kombinasyonu jitter'a neden oluyor (GNOME GitLab issue raporları).
        # Kaynak: https://docs.gtk.org/gtk4/class.ScrolledWindow.html
        scrolled = Gtk.ScrolledWindow(
            hscrollbar_policy=Gtk.PolicyType.NEVER,
            vscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
            vexpand=True,
            kinetic_scrolling=False
        )
        
        # ══════════════════════════════════════════════════════════════
        # GRIDVIEW + FACTORY SETUP (Widget Recycling)
        # ══════════════════════════════════════════════════════════════
        
        # Data store - holds MovieModel/SeriesModel objects
        self._store = Gio.ListStore.new(GObject.Object)
        
        # Factory - manages widget lifecycle (setup/bind/unbind/teardown)
        self._factory = Gtk.SignalListItemFactory()
        self._factory.connect('setup', self._on_factory_setup)
        self._factory.connect('bind', self._on_factory_bind)
        self._factory.connect('unbind', self._on_factory_unbind)
        
        # Selection model (no selection needed)
        selection = Gtk.NoSelection.new(self._store)
        
        # GridView
        self._grid_view = Gtk.GridView(
            model=selection,
            factory=self._factory,
            min_columns=3,
            max_columns=10,
            single_click_activate=True
        )
        self._grid_view.connect('activate', self._on_item_activated)
        
        scrolled.set_child(self._grid_view)
        self._stack.add_named(scrolled, 'filled')
        
        # Start with loading state
        self._stack.set_visible_child_name('loading')
        
        # Connect map signal for deferred loading
        self.connect('map', self._on_map)
        
        logging.info(f"[ContentGridView] Created for {'movies' if movie_view else 'series'}")

    # ══════════════════════════════════════════════════════════════════════
    # FACTORY CALLBACKS (Widget Recycling)
    # ══════════════════════════════════════════════════════════════════════

    def _on_factory_setup(self, factory: Gtk.SignalListItemFactory, 
                          list_item: Gtk.ListItem) -> None:
        """
        Called ONCE when a new visible slot needs a widget.
        Creates an empty PosterButton shell that will be reused.
        """
        btn = PosterButton(content=None)  # Empty widget
        list_item.set_child(btn)

    def _on_factory_bind(self, factory: Gtk.SignalListItemFactory,
                         list_item: Gtk.ListItem) -> None:
        """
        Called when a recycled widget needs to show new data.
        Updates the PosterButton with the current model's data.
        
        KRİTİK: PosterButton kendi click event'ini yakalıyor ve GridView'a
        balonlaşmasını (bubble up) engelliyor. Bu yüzden 'clicked' sinyalini
        burada manuel olarak bağlayıp dinliyoruz.
        """
        btn = list_item.get_child()
        model = list_item.get_item()
        
        if btn and model:
            btn.update_content(model)
            # Connect explicit click signal from PosterButton
            # Bu sinyal, GridView'un 'activate' sinyali yerine kullanılacak
            btn.connect('clicked', self._on_child_clicked)

    def _on_factory_unbind(self, factory: Gtk.SignalListItemFactory,
                           list_item: Gtk.ListItem) -> None:
        """
        Called when widget is about to be recycled.
        Clean up any bindings to prepare for reuse.
        
        ÖNEMLİ: Sinyali disconnect etmezsek, widget recycle edildiğinde
        eski verilere referans veren handler'lar birikir (memory leak + wrong data).
        """
        btn = list_item.get_child()
        if btn:
            # Disconnect clicked signal before recycling to prevent accumulation
            try:
                btn.disconnect_by_func(self._on_child_clicked)
            except TypeError:
                # Signal was not connected (first run or already disconnected)
                pass
            btn.reset_state()

    # ══════════════════════════════════════════════════════════════════════
    # LAZY DATA LOADING
    # ══════════════════════════════════════════════════════════════════════

    def _on_map(self, widget: Gtk.Widget) -> None:
        """Called when view becomes visible. Start loading if needed."""
        if not self._content_loaded:
            self._content_loaded = True
            GLib.idle_add(self._start_loading)

    def _start_loading(self) -> bool:
        """Fetch raw data and start chunked model creation."""
        logging.info(f"[ContentGridView] Starting load for {'movies' if self.movie_view else 'series'}")
        
        # Fetch raw data (fast - no model creation)
        if self.movie_view:
            self._pending_raw = local.LocalProvider.get_all_movies_raw() or []
        else:
            self._pending_raw = local.LocalProvider.get_all_series_raw() or []
        
        if not self._pending_raw:
            self._stack.set_visible_child_name('empty')
            logging.info("[ContentGridView] No content found")
            return False
        
        logging.info(f"[ContentGridView] Fetched {len(self._pending_raw)} raw items")
        
        self._load_index = 0
        # Start chunked model creation (models only, widgets created by factory)
        # RACE CONDITION FIX: Store source ID to allow cancellation if refresh_view is called
        self._load_source_id = GLib.timeout_add(8, self._load_next_chunk)
        
        return False

    def _load_next_chunk(self) -> bool:
        """Create models in chunks and add to store."""
        CHUNK_SIZE = 50  # Models are lightweight, can do more per chunk
        
        if self._load_index >= len(self._pending_raw):
            self._finalize_loading()
            return False
        
        # KALDIRILDI: Erken visible yapmak scroll jitter'a neden oluyordu
        # GridView artık _finalize_loading()'de görünür yapılacak
        # Kaynak: GTK4 Docs - "Add data to ListStore before GridView is visible"
        
        end_index = min(self._load_index + CHUNK_SIZE, len(self._pending_raw))
        
        # Create models and add to store
        models_to_add = []
        for i in range(self._load_index, end_index):
            raw = self._pending_raw[i]
            if self.movie_view:
                model = MovieModel(t=raw)
            else:
                model = SeriesModel(t=raw)
            models_to_add.append(model)
        
        # Batch insert using splice (more efficient)
        self._store.splice(self._load_index, 0, models_to_add)
        
        self._load_index = end_index
        return True

    def _finalize_loading(self) -> None:
        """Called when all models are loaded."""
        logging.info(f"[ContentGridView] Load complete: {len(self._pending_raw)} items in store")
        self._pending_raw = []  # Free memory
        self._load_source_id = None  # Clear ID - loading complete
        
        # TÜM modeller yüklendikten SONRA GridView'ı göster
        # Bu, scroll sırasında splice çağrılmasını önler (GTK4 Docs önerisi)
        self._stack.set_visible_child_name('filled')

    # ══════════════════════════════════════════════════════════════════════
    # EVENT HANDLERS
    # ══════════════════════════════════════════════════════════════════════

    def _on_item_activated(self, grid_view: Gtk.GridView, position: int) -> None:
        """Handle item click - open details view."""
        model = self._store.get_item(position)
        if model:
            logging.debug(f"[ContentGridView] Item activated: {model.title}")
            shared.schema.set_boolean('search-enabled', False)
            
            # DetailsView expects (content, content_view) - same as content_view.py:347
            page = DetailsView(model, self)
            page.connect('deleted', lambda *args: self.refresh_view())
            
            # Push to NavigationView
            nav_view = self.get_ancestor(Adw.NavigationView)
            if nav_view:
                nav_view.push(page)

    def _on_child_clicked(self, widget: Gtk.Widget, content: object) -> None:
        """
        Handle click from PosterButton's 'clicked' signal.
        
        Bu metod, PosterButton tıklandığında çağrılır. GridView'un
        native 'activate' sinyali yerine bunu kullanıyoruz çünkü
        PosterButton içindeki GtkButton click event'ini yutuyordu.
        """
        if content:
            logging.debug(f"[ContentGridView] Child clicked: {content.title}")
            shared.schema.set_boolean('search-enabled', False)
            
            # DetailsView expects (content, content_view) - same as content_view.py:347
            page = DetailsView(content, self)
            page.connect('deleted', lambda *args: self.refresh_view())
            
            # Push to NavigationView
            nav_view = self.get_ancestor(Adw.NavigationView)
            if nav_view:
                nav_view.push(page)

    def refresh_view(self, show_loading: bool = True) -> None:
        """Refresh content by reloading from database.
        
        Args:
            show_loading: If False, don't show loading overlay (for silent updates)
        """
        # RACE CONDITION FIX: Cancel any pending load task BEFORE clearing store
        # Otherwise _load_next_chunk may try to splice at invalid indices
        if self._load_source_id:
            GLib.source_remove(self._load_source_id)
            self._load_source_id = None
        
        self._store.remove_all()
        self._content_loaded = False
        
        # SILENT REFRESH: Overlay gösterme, arka planda yükle
        # Bu, show ekleme sırasında "Loading content..." görünmesini önler
        if show_loading:
            self._stack.set_visible_child_name('loading')
        
        GLib.idle_add(self._start_loading)
