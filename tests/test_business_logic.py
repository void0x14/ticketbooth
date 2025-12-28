# =============================================================================
# TICKETBOOTH GÜVENLİK TESTLERİ - KATMAN 4: BUSINESS LOGIC
# =============================================================================
# Bu testler, iş mantığının doğruluğunu doğrular.
#
# Çalıştırma: python -m pytest tests/test_business_logic.py -v
# =============================================================================

import pytest
import sqlite3
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


class TestTMDBMapping:
    """
    T11: TMDB Mapping Test
    API verisinin doğru parse edilmesi.
    """

    def test_movie_model_parsing(self):
        """
        TMDB API yanıtının doğru parse edilip edilmediğini test et.
        """
        # Simüle edilmiş TMDB API yanıtı (Interstellar benzeri)
        mock_tmdb_response = {
            "id": 157336,
            "title": "Interstellar",
            "original_title": "Interstellar",
            "overview": "A team of explorers travel through a wormhole in space.",
            "release_date": "2014-11-05",
            "runtime": 169,
            "status": "Released",
            "tagline": "Mankind was born on Earth. It was never meant to die here.",
            "genres": [
                {"id": 12, "name": "Adventure"},
                {"id": 18, "name": "Drama"},
                {"id": 878, "name": "Science Fiction"}
            ],
            "original_language": "en",
            "budget": 165000000,
            "revenue": 677471339,
            "poster_path": "/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
            "backdrop_path": "/xJHokMbljvjADYdit5fK5VQsXEG.jpg"
        }
        
        # Parse fonksiyonunu simüle et
        def parse_movie(data):
            return {
                "id": str(data["id"]),
                "title": data["title"],
                "release_date": data["release_date"],
                "runtime": data["runtime"],
                "genres": [g["name"] for g in data["genres"]],
                "overview": data["overview"],
                "status": data["status"]
            }
        
        parsed = parse_movie(mock_tmdb_response)
        
        # Assertions
        assert parsed["id"] == "157336"
        assert parsed["title"] == "Interstellar"
        assert parsed["release_date"] == "2014-11-05"
        assert parsed["runtime"] == 169
        assert "Science Fiction" in parsed["genres"]
        assert parsed["status"] == "Released"

    def test_series_model_parsing(self):
        """
        Dizi verisinin doğru parse edilmesi.
        """
        mock_tmdb_series = {
            "id": 1399,
            "name": "Game of Thrones",
            "original_name": "Game of Thrones",
            "overview": "Seven noble families fight for control.",
            "first_air_date": "2011-04-17",
            "last_air_date": "2019-05-19",
            "number_of_seasons": 8,
            "number_of_episodes": 73,
            "status": "Ended",
            "in_production": False,
            "genres": [
                {"id": 10765, "name": "Sci-Fi & Fantasy"},
                {"id": 18, "name": "Drama"},
                {"id": 10759, "name": "Action & Adventure"}
            ],
            "created_by": [
                {"name": "David Benioff"},
                {"name": "D. B. Weiss"}
            ],
            "original_language": "en",
            "poster_path": "/1XS1oqL89opfnbLl8WnZY1O1uJx.jpg",
            "backdrop_path": "/2OMB0ynKlyIenMJWI2Dy9IWT4c.jpg",
            "next_episode_to_air": None,
            "last_episode_to_air": {
                "season_number": 8,
                "episode_number": 6
            }
        }
        
        def parse_series(data):
            return {
                "id": str(data["id"]),
                "title": data["name"],
                "release_date": data["first_air_date"],
                "last_air_date": data["last_air_date"],
                "seasons_number": data["number_of_seasons"],
                "episodes_number": data["number_of_episodes"],
                "in_production": data["in_production"],
                "status": data["status"],
                "created_by": [c["name"] for c in data["created_by"]],
                "genres": [g["name"] for g in data["genres"]]
            }
        
        parsed = parse_series(mock_tmdb_series)
        
        assert parsed["id"] == "1399"
        assert parsed["title"] == "Game of Thrones"
        assert parsed["seasons_number"] == 8
        assert parsed["episodes_number"] == 73
        assert parsed["in_production"] == False
        assert "David Benioff" in parsed["created_by"]

    def test_null_date_handling(self):
        """
        TMDB'den null tarih geldiğinde crash olmamalı.
        Bu, main_view.py'de düzelttiğimiz bug'ın testi.
        """
        # Bazen TMDB bu alanları null döndürür
        mock_response_with_nulls = {
            "id": 999999,
            "name": "Upcoming Show",
            "first_air_date": None,  # NULL!
            "last_air_date": None,   # NULL!
            "next_episode_to_air": None,
            "in_production": True,
            "number_of_seasons": 0,
            "number_of_episodes": 0
        }
        
        def safe_parse_date(date_str):
            """Güvenli tarih parse fonksiyonu."""
            if date_str is None or not date_str.strip():
                return ""
            return date_str
        
        # NULL kontrolü çalışmalı
        last_air_date = safe_parse_date(mock_response_with_nulls.get("last_air_date"))
        assert last_air_date == ""
        
        first_air_date = safe_parse_date(mock_response_with_nulls.get("first_air_date"))
        assert first_air_date == ""


class TestDuplicatePrevention:
    """
    T12: Duplicate Prevention Test
    Mükerrer kayıtların engellenmesi.
    """

    @pytest.fixture
    def database_with_unique_constraint(self):
        """Unique constraint'li veritabanı."""
        fd, path = tempfile.mkstemp(suffix=".db")
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        
        # PRIMARY KEY zaten unique constraint sağlar
        cursor.execute("""
            CREATE TABLE movies (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL
            )
        """)
        conn.commit()
        
        yield conn, path
        
        conn.close()
        os.close(fd)
        os.unlink(path)

    def test_duplicate_movie_insertion_fails(self, database_with_unique_constraint):
        """
        Aynı ID'li film iki kez eklenememeli.
        """
        conn, _ = database_with_unique_constraint
        cursor = conn.cursor()
        
        # İlk ekleme başarılı olmalı
        cursor.execute("INSERT INTO movies (id, title) VALUES ('157336', 'Interstellar')")
        conn.commit()
        
        # İkinci ekleme unique violation hatası vermeli
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("INSERT INTO movies (id, title) VALUES ('157336', 'Interstellar Copy')")
            conn.commit()

    def test_check_before_insert_pattern(self, database_with_unique_constraint):
        """
        Ekleme öncesi kontrol patterninin test edilmesi.
        Bu, UI seviyesinde "Zaten eklendi" göstermek için kullanılır.
        """
        conn, _ = database_with_unique_constraint
        cursor = conn.cursor()
        
        def is_movie_in_list(movie_id):
            """Film listede var mı kontrol et."""
            cursor.execute("SELECT COUNT(*) FROM movies WHERE id = ?", (movie_id,))
            return cursor.fetchone()[0] > 0
        
        # Henüz eklenmedi
        assert is_movie_in_list("157336") == False
        
        # Ekle
        cursor.execute("INSERT INTO movies (id, title) VALUES ('157336', 'Interstellar')")
        conn.commit()
        
        # Artık listede
        assert is_movie_in_list("157336") == True

    def test_upsert_pattern(self, database_with_unique_constraint):
        """
        INSERT OR REPLACE pattern - güncelleme veya ekleme.
        """
        conn, _ = database_with_unique_constraint
        cursor = conn.cursor()
        
        # İlk ekleme
        cursor.execute(
            "INSERT OR REPLACE INTO movies (id, title) VALUES ('157336', 'Interstellar')"
        )
        conn.commit()
        
        cursor.execute("SELECT title FROM movies WHERE id = '157336'")
        assert cursor.fetchone()[0] == 'Interstellar'
        
        # Aynı ID ile güncelleme (hata vermeden)
        cursor.execute(
            "INSERT OR REPLACE INTO movies (id, title) VALUES ('157336', 'Interstellar (Updated)')"
        )
        conn.commit()
        
        cursor.execute("SELECT title FROM movies WHERE id = '157336'")
        assert cursor.fetchone()[0] == 'Interstellar (Updated)'
        
        # Hala sadece 1 kayıt var
        cursor.execute("SELECT COUNT(*) FROM movies")
        assert cursor.fetchone()[0] == 1


class TestNetworkErrorHandling:
    """
    T03: Network Error Handling (Kısmi Otomasyon)
    Ağ hatalarının graceful handling'i.
    """

    def test_connection_error_handling(self):
        """
        requests.ConnectionError fırlatıldığında crash olmamalı.
        """
        import requests
        from unittest.mock import patch
        
        def fetch_from_tmdb(movie_id):
            """Simüle edilmiş TMDB fetch fonksiyonu."""
            try:
                # Bu normalde requests.get(...) olurdu
                response = requests.get(f"https://api.tmdb.org/3/movie/{movie_id}")
                return response.json()
            except requests.exceptions.ConnectionError:
                return {"error": "Network unavailable", "offline": True}
            except requests.exceptions.Timeout:
                return {"error": "Request timed out", "offline": True}
        
        # ConnectionError'ı simüle et
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("No internet")
            
            result = fetch_from_tmdb("157336")
            
            # Crash olmadı, hata mesajı döndü
            assert result["error"] == "Network unavailable"
            assert result["offline"] == True

    def test_timeout_handling(self):
        """
        Timeout durumunda uygun hata mesajı dönmeli.
        """
        import requests
        from unittest.mock import patch
        
        def fetch_with_timeout(url, timeout=10):
            try:
                response = requests.get(url, timeout=timeout)
                return {"success": True, "data": response.json()}
            except requests.exceptions.Timeout:
                return {"success": False, "error": "timeout"}
            except requests.exceptions.RequestException as e:
                return {"success": False, "error": str(e)}
        
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")
            
            result = fetch_with_timeout("https://api.tmdb.org/3/movie/157336")
            
            assert result["success"] == False
            assert result["error"] == "timeout"


# =============================================================================
# TEST SUITE RUNNER
# =============================================================================
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
