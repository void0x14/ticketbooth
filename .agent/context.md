# Ticketbooth Memory Leak Fix - Context for AI

## Project
- **Repo**: https://github.com/void0x14/ticketbooth (fork of aleiepure/ticketbooth)
- **Tech**: Python, GTK4, Libadwaita, Flatpak
- **Issue**: Memory leak causing 12GB+ RAM usage

## Completed So Far
1. ✅ Full codebase analysis - root cause identified
2. ✅ Fixed `_compute_badge_color()` in both model files:
   - `src/models/movie_model.py`
   - `src/models/series_model.py`
3. ✅ Added detailed Turkish learning comments (to be removed before PR)
4. ✅ Windows test passed - memory reduction verified

## Current State of Code
- Functions have TURKISH comments for learning purposes
- Before PR: Remove Turkish comments, squash commits, use English

## Remaining Work
- [ ] Linux Flatpak build & test
- [ ] Fix `_download_background()` and `_download_poster()` (similar issue)
- [ ] Remove Turkish comments, add clean English comments
- [ ] Squash/clean commits for clean PR

## Build Commands (Flatpak Devel - SAFE, separate data folder)
```bash
cd ticketbooth
flatpak-builder --repo=repo --force-clean --user build me.iepure.Ticketbooth.Devel.json
flatpak remote-add --user ticketbooth repo --no-gpg-verify --if-not-exists
flatpak install --user ticketbooth me.iepure.Ticketbooth.Devel
flatpak run --user me.iepure.Ticketbooth.Devel
```

## Safe Testing Note
- Devel = `~/.var/app/me.iepure.Ticketbooth.Devel/` (TEST DATA)
- Production = `~/.var/app/me.iepure.Ticketbooth/` (YOUR DATA - UNTOUCHED)

## Commit Cleanup Plan (Before PR)
```bash
# Squash all commits into one clean commit
git rebase -i HEAD~N  # N = number of commits to squash
# Or reset and recommit:
git reset --soft origin/main~1  # Go back to before our changes
# Make clean changes, commit with English message
```

## User Context
- Power user, learning through code review
- First open source contribution
- Wants to understand every line before pushing
