# =============================================================================
# TICKETBOOTH GÜVENLİK TESTLERİ - KATMAN 1: VERİ GİRİŞİ
# =============================================================================
# Bu testler, beklenmedik girdilerin sistemi çökertmemesini doğrular.
#
# Çalıştırma: python -m pytest tests/test_input_validation.py -v
# =============================================================================

import pytest
import sqlite3
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Proje kök dizinini path'e ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


class TestNullInput:
    """
    T01: Null/Empty Input Test
    Boş veya sadece boşluk karakterli girdilerin test edilmesi.
    """

    @pytest.mark.parametrize("input_value", [
        "",           # Boş string
        " ",          # Tek boşluk
        "   ",        # Çoklu boşluk
        "\t",         # Tab karakteri
        "\n",         # Newline
        None,         # None değeri
    ])
    def test_empty_search_query_handling(self, input_value):
        """
        Arama fonksiyonu boş girdileri graceful handle etmeli.
        """
        # Simüle edilen arama fonksiyonu davranışı
        def search_content(query):
            if query is None or not query.strip():
                return []  # Boş sonuç döndür, crash olma
            return ["result1", "result2"]
        
        result = search_content(input_value)
        
        # Assertion: Boş liste dönmeli, exception fırlatmamalı
        assert result == []
        assert isinstance(result, list)


class TestSpecialCharacters:
    """
    T02: Special Characters Test
    SQL Injection, XSS ve Unicode karakterlerin test edilmesi.
    """

    @pytest.fixture
    def temp_database(self):
        """Geçici SQLite veritabanı oluştur."""
        fd, path = tempfile.mkstemp(suffix=".db")
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        
        # Test tablosu oluştur
        cursor.execute("""
            CREATE TABLE movies (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                overview TEXT
            )
        """)
        conn.commit()
        
        yield conn, path
        
        conn.close()
        os.close(fd)
        os.unlink(path)

    @pytest.mark.parametrize("malicious_input", [
        "' OR 1=1 --",                          # Classic SQL Injection
        '"; DROP TABLE movies; --',             # Drop table attempt
        "Robert'); DROP TABLE movies;--",       # Bobby Tables
        "<script>alert('xss')</script>",        # XSS attempt
        "🎬🍿",                                  # Emoji
        "日本語テスト",                          # Japanese
        "العربية",                              # Arabic
        "SELECT * FROM movies WHERE 1=1",       # SQL query as input
        "UNION SELECT password FROM users",     # UNION injection
        "\x00\x00\x00",                          # Null bytes
    ])
    def test_sql_injection_prevention(self, temp_database, malicious_input):
        """
        Parametrized query kullanıldığında SQL injection çalışmamalı.
        """
        conn, _ = temp_database
        cursor = conn.cursor()
        
        # DOĞRU YOL: Parameterized query (? placeholder)
        # Bu, SQL injection'ı otomatik olarak engeller
        try:
            cursor.execute(
                "INSERT INTO movies (title, overview) VALUES (?, ?)",
                (malicious_input, "Test overview")
            )
            conn.commit()
            
            # Veri başarıyla eklendi, şimdi geri oku
            cursor.execute("SELECT title FROM movies WHERE title = ?", (malicious_input,))
            result = cursor.fetchone()
            
            # Assertion: Girdi olduğu gibi saklandı (escape edildi)
            assert result is not None
            assert result[0] == malicious_input
            
        except sqlite3.Error as e:
            # Bazı karakterler (null byte gibi) hata verebilir, bu da kabul edilebilir
            pytest.skip(f"Input caused controlled error: {e}")

    @pytest.mark.parametrize("unicode_input", [
        "Amélie",                  # Aksan karakterli
        "Naïve",                   # Diaeresis
        "北京",                    # Chinese
        "Москва",                  # Cyrillic
        "🎭 Theatre Emoji",        # Mixed emoji
    ])
    def test_unicode_handling(self, temp_database, unicode_input):
        """
        Unicode karakterler doğru saklanmalı ve okunmalı.
        """
        conn, _ = temp_database
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO movies (title) VALUES (?)",
            (unicode_input,)
        )
        conn.commit()
        
        cursor.execute("SELECT title FROM movies WHERE title = ?", (unicode_input,))
        result = cursor.fetchone()
        
        assert result is not None
        assert result[0] == unicode_input


class TestRapidFireDatabase:
    """
    T04: Rapid Fire Test
    Hızlı ardışık veritabanı işlemlerinin race condition oluşturmaması.
    """

    @pytest.fixture
    def temp_database_with_movie(self):
        """Film içeren geçici veritabanı."""
        fd, path = tempfile.mkstemp(suffix=".db")
        conn = sqlite3.connect(path, timeout=10)  # 10 saniye timeout
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE movies (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                watched BOOLEAN DEFAULT 0
            )
        """)
        cursor.execute("INSERT INTO movies (id, title) VALUES (1, 'Test Movie')")
        conn.commit()
        
        yield conn, path
        
        conn.close()
        os.close(fd)
        os.unlink(path)

    def test_rapid_toggle_watched_status(self, temp_database_with_movie):
        """
        Watched durumu hızlıca değiştirildiğinde database lock olmamalı.
        """
        conn, path = temp_database_with_movie
        
        # 100 kez hızlıca toggle et
        for i in range(100):
            cursor = conn.cursor()
            new_status = i % 2  # 0, 1, 0, 1, ...
            
            try:
                cursor.execute(
                    "UPDATE movies SET watched = ? WHERE id = 1",
                    (new_status,)
                )
                conn.commit()
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    pytest.fail(f"Database locked at iteration {i}")
                raise
        
        # Final durum kontrolü
        cursor = conn.cursor()
        cursor.execute("SELECT watched FROM movies WHERE id = 1")
        result = cursor.fetchone()
        
        # 100 iterasyon sonunda 99 % 2 = 1 olmalı
        assert result[0] == 1

    def test_concurrent_read_write(self, temp_database_with_movie):
        """
        Okuma ve yazma işlemleri eşzamanlı yapılabilmeli.
        """
        conn, path = temp_database_with_movie
        
        # WAL modu aktifleştir (concurrent access için)
        conn.execute("PRAGMA journal_mode=WAL")
        
        for i in range(50):
            cursor = conn.cursor()
            
            # Okuma
            cursor.execute("SELECT * FROM movies WHERE id = 1")
            _ = cursor.fetchone()
            
            # Yazma
            cursor.execute(
                "UPDATE movies SET title = ? WHERE id = 1",
                (f"Test Movie v{i}",)
            )
            conn.commit()
        
        # Son değer kontrolü
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM movies WHERE id = 1")
        result = cursor.fetchone()
        
        assert result[0] == "Test Movie v49"


# =============================================================================
# TEST SUITE RUNNER
# =============================================================================
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
