# Ticketbooth Memory Leak Fix - Context for AI

## Project
- **Repo**: https://github.com/void0x14/ticketbooth (fork of aleiepure/ticketbooth)
- **Tech**: Python, GTK4, Libadwaita, Flatpak
- **Issue**: Memory leak causing 12GB+ RAM usage

## User Data Profile (from data.json)
- **Movies**: 971
- **Series**: 482
- **Total Content**: 1453 items
- This large dataset explains why memory leak is severe

## Completed Fixes (2025-12-23)

### 1. `_compute_badge_color()` - Fixed in 4 files:
All PIL Image objects now properly closed with `with` statement + `region.close()`:

| File | Line | Status |
|------|------|--------|
| `src/models/movie_model.py` | 238-337 | ✅ Fixed |
| `src/models/series_model.py` | 309-408 | ✅ Fixed |
| `src/providers/local_provider.py` | 393-415 | ✅ Fixed |
| `src/dialogs/add_manual_dialog.py` | 555-572 | ✅ Fixed |

### 2. `_download_background()` - Already OK:
- Uses `with Image.open()` correctly in both model files

### 3. `details_page.py` - Already OK:
- Lines 169 and 826 use `with` statement correctly

## Remaining Work
- [ ] Rebuild Flatpak with new changes
- [ ] Test with user's 1453 content items
- [ ] Remove Turkish comments from code
- [ ] Squash commits for clean PR

## Build Commands (Flatpak Devel)
```bash
cd ticketbooth
flatpak-builder --repo=repo --force-clean --user build me.iepure.Ticketbooth.Devel.json
flatpak install --user --reinstall ticketbooth me.iepure.Ticketbooth.Devel -y
flatpak run --user me.iepure.Ticketbooth.Devel
```

## Files NOT to push to git
- `data.json` - User's personal show data (added to .gitignore)

## Safe Testing Note
- Devel = `~/.var/app/me.iepure.Ticketbooth.Devel/` (TEST DATA)
- Production = `~/.var/app/me.iepure.Ticketbooth/` (YOUR DATA - UNTOUCHED)

## User Context
- Power user, learning through code review
- First open source contribution
- CachyOS (Arch-based) Linux
