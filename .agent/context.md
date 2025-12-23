# Ticketbooth Memory Leak Fix - Context for AI

## Project
- **Repo**: https://github.com/void0x14/ticketbooth (fork of aleiepure/ticketbooth)
- **Tech**: Python, GTK4, Libadwaita, Flatpak
- **Issue**: Memory leak causing 12GB+ RAM usage

## Already Completed (Windows)
1. ✅ Full codebase analysis done - see `implementation_plan.md` in artifacts
2. ✅ Fixed `_compute_badge_color()` in:
   - `src/models/movie_model.py`
   - `src/models/series_model.py`
3. ✅ Committed: `75e9e13` - "fix(memory): prevent PIL Image handle leaks"
4. ✅ Pushed to fork

## Remaining Quick Fixes (Not Yet Done)
- [ ] `_download_background()` - both model files
- [ ] `_download_poster()` - both model files  

## Current Goal
Build and test the Devel version on Linux to verify fixes work.

## Build Commands (from CONTRIBUTING.md)
```bash
git clone https://github.com/void0x14/ticketbooth
flatpak-builder --repo=/path/to/repo/dir --force-clean --user /path/to/build/dir me.iepure.Ticketbooth.Devel.json
flatpak remote-add --user ticketbooth ticketbooth --no-gpg-verify
flatpak install --user ticketbooth me.iepure.Ticketbooth.Devel
flatpak run --user me.iepure.Ticketbooth.Devel
```

## Safe Testing Note
- Devel version uses separate data folder: `~/.var/app/me.iepure.Ticketbooth.Devel/`
- Production data in `~/.var/app/me.iepure.Ticketbooth/` is NOT touched

## User Context
- Power user, not a developer
- First time contributing to open source
- Goal: Fix issues and submit pull request to original repo
