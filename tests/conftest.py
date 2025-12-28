# =============================================================================
# TICKETBOOTH TEST SUITE - CONFTEST (Shared Fixtures)
# =============================================================================
# Tüm test dosyalarında kullanılabilecek ortak fixture'lar.
# =============================================================================

import pytest
import sqlite3
import tempfile
import os


@pytest.fixture(scope="session")
def project_root():
    """Proje kök dizini."""
    from pathlib import Path
    return Path(__file__).parent.parent


@pytest.fixture
def temp_db():
    """
    Geçici SQLite veritabanı.
    
    Her test için temiz bir veritabanı oluşturur ve test sonunda temizler.
    """
    fd, path = tempfile.mkstemp(suffix=".db")
    conn = sqlite3.connect(path)
    
    yield conn, path
    
    conn.close()
    os.close(fd)
    os.unlink(path)


@pytest.fixture
def ticketbooth_schema(temp_db):
    """
    Ticketbooth şemasına uygun veritabanı.
    
    Gerçek uygulamanın tablo yapısını simüle eder.
    """
    conn, path = temp_db
    cursor = conn.cursor()
    
    # Movies tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            original_title TEXT,
            overview TEXT,
            poster_path TEXT,
            backdrop_path TEXT,
            release_date TEXT,
            runtime INTEGER,
            status TEXT,
            tagline TEXT,
            genres TEXT,
            budget INTEGER,
            revenue INTEGER,
            watched BOOLEAN DEFAULT 0,
            manual BOOLEAN DEFAULT 0,
            add_date TEXT,
            notes TEXT DEFAULT '',
            new_release BOOLEAN DEFAULT 0,
            soon_release BOOLEAN DEFAULT 0,
            recent_change BOOLEAN DEFAULT 0,
            activate_notification BOOLEAN DEFAULT 0,
            color BOOLEAN DEFAULT 0,
            original_language TEXT
        )
    """)
    
    # Series tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS series (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            original_title TEXT,
            overview TEXT,
            poster_path TEXT,
            backdrop_path TEXT,
            release_date TEXT,
            last_air_date TEXT,
            next_air_date TEXT,
            seasons_number INTEGER,
            episodes_number INTEGER,
            status TEXT,
            tagline TEXT,
            genres TEXT,
            created_by TEXT,
            in_production BOOLEAN DEFAULT 0,
            watched BOOLEAN DEFAULT 0,
            manual BOOLEAN DEFAULT 0,
            add_date TEXT,
            notes TEXT DEFAULT '',
            new_release BOOLEAN DEFAULT 0,
            soon_release BOOLEAN DEFAULT 0,
            recent_change BOOLEAN DEFAULT 0,
            activate_notification BOOLEAN DEFAULT 0,
            color BOOLEAN DEFAULT 0,
            original_language TEXT,
            last_episode_number TEXT DEFAULT ''
        )
    """)
    
    # Seasons tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seasons (
            id TEXT PRIMARY KEY,
            show_id TEXT,
            number INTEGER,
            title TEXT,
            overview TEXT,
            poster_path TEXT,
            episodes_number INTEGER,
            FOREIGN KEY (show_id) REFERENCES series(id) ON DELETE CASCADE
        )
    """)
    
    # Episodes tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS episodes (
            id TEXT PRIMARY KEY,
            show_id TEXT,
            season_number INTEGER,
            number INTEGER,
            title TEXT,
            overview TEXT,
            still_path TEXT,
            runtime INTEGER,
            watched BOOLEAN DEFAULT 0,
            FOREIGN KEY (show_id) REFERENCES series(id) ON DELETE CASCADE
        )
    """)
    
    # Languages tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS languages (
            iso_639_1 TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)
    
    # Temel diller ekle
    cursor.execute("INSERT OR IGNORE INTO languages VALUES ('en', 'English')")
    cursor.execute("INSERT OR IGNORE INTO languages VALUES ('tr', 'Turkish')")
    
    conn.commit()
    conn.execute("PRAGMA foreign_keys = ON")
    
    yield conn, path


@pytest.fixture
def sample_movie_data():
    """Test için örnek film verisi."""
    return {
        "id": "157336",
        "title": "Interstellar",
        "original_title": "Interstellar",
        "overview": "A team of explorers travel through a wormhole in space.",
        "poster_path": "file:///test/poster.jpg",
        "backdrop_path": "file:///test/backdrop.jpg",
        "release_date": "2014-11-05",
        "runtime": 169,
        "status": "Released",
        "tagline": "Mankind was born on Earth.",
        "genres": "Adventure,Drama,Science Fiction",
        "budget": 165000000,
        "revenue": 677471339,
        "original_language": "en"
    }


@pytest.fixture
def sample_series_data():
    """Test için örnek dizi verisi."""
    return {
        "id": "1399",
        "title": "Game of Thrones",
        "original_title": "Game of Thrones",
        "overview": "Seven noble families fight for control.",
        "poster_path": "file:///test/got_poster.jpg",
        "backdrop_path": "file:///test/got_backdrop.jpg",
        "release_date": "2011-04-17",
        "last_air_date": "2019-05-19",
        "next_air_date": "",
        "seasons_number": 8,
        "episodes_number": 73,
        "status": "Ended",
        "tagline": "Winter is coming.",
        "genres": "Sci-Fi & Fantasy,Drama,Action & Adventure",
        "created_by": "David Benioff,D. B. Weiss",
        "in_production": False,
        "original_language": "en",
        "last_episode_number": "8.6"
    }


# =============================================================================
# CUSTOM MARKERS
# =============================================================================
def pytest_configure(config):
    """Custom pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "network: marks tests that require network access"
    )
    config.addinivalue_line(
        "markers", "gtk: marks tests that require GTK (skip in CI)"
    )
