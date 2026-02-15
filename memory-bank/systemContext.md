# System Context

## Technical Stack
- **Language**: Python
- **UI Framework**: Gtk / Libadwaita (intended for GNOME/Linux)
- **Data Source**: TMDB API
- **Build System**: Meson
- **Packaging**: Flatpak (Application ID: `me.iepure.Ticketbooth`)
- **Database**: SQLite (using parameterized queries)

## Key Technical Decisions
- **Widget Recycling**: Implemented in `ContentGridView` to optimize performance and prevent memory leaks.
- **Language Standardization**: The codebase is being refactored to use English for variables, comments, and logic to align with international development standards.
- **Logging**: Uses Python's standard `logging` library, with fixes for previous namespace conflicts.

## External Dependencies
- Python libraries (defined in `requirements.txt` and `pypi-dependencies.json`)
- TMDB API for media metadata.
