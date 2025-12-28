# =============================================================================
# TICKETBOOTH GÜVENLİK TESTLERİ - KATMAN 2: VERİTABANI KALICILIĞI
# =============================================================================
# Bu testler, veritabanı işlemlerinin tutarlılığını doğrular.
#
# Çalıştırma: python -m pytest tests/test_persistence.py -v
# =============================================================================

import pytest
import sqlite3
import tempfile
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


class TestDeletionLogic:
    """
    T07: Deletion Logic Test
    Silme işleminin tutarlı olması.
    """

    @pytest.fixture
    def populated_database(self):
        """Film ve ilişkili verilerle dolu veritabanı."""
        fd, path = tempfile.mkstemp(suffix=".db")
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        
        # Tablo yapısını oluştur (Ticketbooth şemasına benzer)
        cursor.execute("""
            CREATE TABLE movies (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                poster_path TEXT,
                watched BOOLEAN DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE series (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                poster_path TEXT,
                watched BOOLEAN DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE seasons (
                id TEXT PRIMARY KEY,
                show_id TEXT,
                title TEXT,
                FOREIGN KEY (show_id) REFERENCES series(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE episodes (
                id TEXT PRIMARY KEY,
                show_id TEXT,
                season_number INTEGER,
                title TEXT,
                watched BOOLEAN DEFAULT 0,
                FOREIGN KEY (show_id) REFERENCES series(id) ON DELETE CASCADE
            )
        """)
        
        # Test verileri ekle
        cursor.execute("""
            INSERT INTO movies (id, title, poster_path) 
            VALUES ('157336', 'Interstellar', '/poster.jpg')
        """)
        
        cursor.execute("""
            INSERT INTO series (id, title, poster_path) 
            VALUES ('1399', 'Game of Thrones', '/got_poster.jpg')
        """)
        
        cursor.execute("""
            INSERT INTO seasons (id, show_id, title) 
            VALUES ('s1', '1399', 'Season 1')
        """)
        
        cursor.execute("""
            INSERT INTO episodes (id, show_id, season_number, title) 
            VALUES ('ep1', '1399', 1, 'Winter is Coming')
        """)
        
        conn.commit()
        
        yield conn, path
        
        conn.close()
        os.close(fd)
        os.unlink(path)

    def test_movie_deletion_removes_all_data(self, populated_database):
        """
        Film silindiğinde ilgili tüm veriler temizlenmeli.
        """
        conn, _ = populated_database
        cursor = conn.cursor()
        
        # Film silmeden önce kontrol
        cursor.execute("SELECT COUNT(*) FROM movies WHERE id = '157336'")
        assert cursor.fetchone()[0] == 1
        
        # Film sil
        cursor.execute("DELETE FROM movies WHERE id = '157336'")
        conn.commit()
        
        # Film silindikten sonra kontrol
        cursor.execute("SELECT COUNT(*) FROM movies WHERE id = '157336'")
        assert cursor.fetchone()[0] == 0

    def test_series_deletion_cascades_to_episodes(self, populated_database):
        """
        Dizi silindiğinde sezonlar ve bölümler de silinmeli (CASCADE).
        """
        conn, _ = populated_database
        
        # Önce foreign key'leri aktifleştir
        conn.execute("PRAGMA foreign_keys = ON")
        
        cursor = conn.cursor()
        
        # Silmeden önce kontrol
        cursor.execute("SELECT COUNT(*) FROM seasons WHERE show_id = '1399'")
        assert cursor.fetchone()[0] == 1
        
        cursor.execute("SELECT COUNT(*) FROM episodes WHERE show_id = '1399'")
        assert cursor.fetchone()[0] == 1
        
        # Diziyi sil
        cursor.execute("DELETE FROM series WHERE id = '1399'")
        conn.commit()
        
        # CASCADE sonrası kontrol
        cursor.execute("SELECT COUNT(*) FROM seasons WHERE show_id = '1399'")
        assert cursor.fetchone()[0] == 0
        
        cursor.execute("SELECT COUNT(*) FROM episodes WHERE show_id = '1399'")
        assert cursor.fetchone()[0] == 0

    def test_deletion_is_idempotent(self, populated_database):
        """
        Aynı kayıt iki kez silinmeye çalışılırsa hata olmamalı.
        """
        conn, _ = populated_database
        cursor = conn.cursor()
        
        # İlk silme
        cursor.execute("DELETE FROM movies WHERE id = '157336'")
        conn.commit()
        
        # İkinci silme (aynı ID) - hata vermemeli
        try:
            cursor.execute("DELETE FROM movies WHERE id = '157336'")
            conn.commit()
        except sqlite3.Error as e:
            pytest.fail(f"Duplicate deletion raised error: {e}")
        
        # Etkilenen satır sayısı 0 olmalı
        assert cursor.rowcount == 0


class TestWatchlistCRUD:
    """
    T05: Watchlist CRUD Test
    Temel CRUD işlemlerinin test edilmesi.
    """

    @pytest.fixture
    def empty_database(self):
        """Boş veritabanı."""
        fd, path = tempfile.mkstemp(suffix=".db")
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE movies (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                release_date TEXT,
                watched BOOLEAN DEFAULT 0,
                add_date TEXT
            )
        """)
        conn.commit()
        
        yield conn, path
        
        conn.close()
        os.close(fd)
        os.unlink(path)

    def test_create_movie(self, empty_database):
        """Film ekleme işlemi."""
        conn, _ = empty_database
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO movies (id, title, release_date, add_date)
            VALUES ('157336', 'Interstellar', '2014-11-07', '2025-12-27')
        """)
        conn.commit()
        
        cursor.execute("SELECT * FROM movies WHERE id = '157336'")
        result = cursor.fetchone()
        
        assert result is not None
        assert result[1] == 'Interstellar'
        assert result[2] == '2014-11-07'

    def test_read_movie(self, empty_database):
        """Film okuma işlemi."""
        conn, _ = empty_database
        cursor = conn.cursor()
        
        # Önce ekle
        cursor.execute("""
            INSERT INTO movies (id, title, release_date)
            VALUES ('157336', 'Interstellar', '2014-11-07')
        """)
        conn.commit()
        
        # Sonra oku
        cursor.execute("SELECT title, release_date FROM movies WHERE id = '157336'")
        result = cursor.fetchone()
        
        assert result[0] == 'Interstellar'
        assert result[1] == '2014-11-07'

    def test_update_watched_status(self, empty_database):
        """Film watched durumu güncelleme."""
        conn, _ = empty_database
        cursor = conn.cursor()
        
        # Ekle
        cursor.execute("INSERT INTO movies (id, title) VALUES ('157336', 'Interstellar')")
        conn.commit()
        
        # Watched = True yap
        cursor.execute("UPDATE movies SET watched = 1 WHERE id = '157336'")
        conn.commit()
        
        cursor.execute("SELECT watched FROM movies WHERE id = '157336'")
        assert cursor.fetchone()[0] == 1
        
        # Watched = False yap
        cursor.execute("UPDATE movies SET watched = 0 WHERE id = '157336'")
        conn.commit()
        
        cursor.execute("SELECT watched FROM movies WHERE id = '157336'")
        assert cursor.fetchone()[0] == 0

    def test_delete_movie(self, empty_database):
        """Film silme işlemi."""
        conn, _ = empty_database
        cursor = conn.cursor()
        
        # Ekle
        cursor.execute("INSERT INTO movies (id, title) VALUES ('157336', 'Interstellar')")
        conn.commit()
        
        # Var mı kontrol et
        cursor.execute("SELECT COUNT(*) FROM movies WHERE id = '157336'")
        assert cursor.fetchone()[0] == 1
        
        # Sil
        cursor.execute("DELETE FROM movies WHERE id = '157336'")
        conn.commit()
        
        # Silindi mi kontrol et
        cursor.execute("SELECT COUNT(*) FROM movies WHERE id = '157336'")
        assert cursor.fetchone()[0] == 0


# =============================================================================
# TEST SUITE RUNNER
# =============================================================================
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
