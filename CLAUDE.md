# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Summary

Horus is a VFX review application built on top of **Open RV 3.0+** for the SWA animation pipeline. It runs as a Python script injected into Open RV (`rv -pyeval ...`) that adds three modular **PySide2** dock widgets — Search/Media Library (Navigator), Comments & Annotations, and Timeline Playlist — and is shipped as a single `horus-rv.exe` built with PyInstaller.

The application does NOT run standalone; `horus_rv_launcher.py` finds the local `rv.exe`, then injects `rv_horus_integration.py` into the RV Python interpreter via a temp file.

## Common Commands

All commands assume Python 3.8+ and are run from the repo root.

### Development run (no executable)
```bash
# Launches Open RV and injects the UI; equivalent to horus-rv.exe
python horus_rv_launcher.py

# Or invoke RV directly (Windows fallback, see horus-rv.bat)
"D:\Program Files\stage\app\bin\rv.exe" -pyeval "exec(open('rv_horus_integration.py').read())"
```

### Build the executable
```bash
# Quick build
python build_horus_rv_exe.py

# Build with version metadata + distribution package (used by CI)
python scripts/build_with_version.py --clean
python scripts/build_with_version.py --bump-build      # bumps build number first
python scripts/build_with_version.py --version-only    # update version, do not build
```
Output: `dist/horus-rv.exe`. PyInstaller bundles the core `.py` files, `version.json`, `swa_project_config.json`, and `sample_db/` (see `build_horus_rv_exe.py:44-72` for the exact include list).

### Versioning and releases
```bash
python horus_version.py --show                         # current version
python horus_version.py --info                         # full version info (git hash/branch, build)
python horus_version.py --bump {major|minor|patch|build}

python scripts/version_bump.py --bump patch            # bump + commit version.json
python scripts/version_bump.py --bump minor --tag      # also create v<x.y.z> tag
python scripts/version_bump.py --bump major --tag --push
python scripts/version_bump.py --bump patch --dry-run

python scripts/release_manager.py changelog <version>  # generate CHANGELOG-<version>.md
```
Pushing a tag matching `v*` triggers `.github/workflows/release.yml`, which builds `horus-rv.exe` on `windows-latest` and creates a GitHub Release.

### Lint / format / type-check
The CI (`.github/workflows/branch-protection.yml`) and `.pre-commit-config.yaml` enforce:
```bash
black --check --diff .
isort --check-only --diff .
flake8 . --select=E9,F63,F7,F82                # syntax/undefined names — must pass
flake8 . --max-complexity=10 --max-line-length=127 --exit-zero
mypy .                                          # via pre-commit
pre-commit run --all-files                      # run everything locally
```

### Tests
There is no pytest suite in the repository at the moment. Demo/manual scripts:
```bash
python scripts/demo_horus_media_browser.py      # standalone Qt demo of the media browser
```

## Architecture

### Runtime composition
```
horus-rv.exe (PyInstaller bundle of horus_rv_launcher.py)
   │
   ├─ finds rv.exe on disk (horus_rv_launcher.find_openrv_executable)
   ├─ reads rv_horus_integration.py from _MEIPASS (or local file in dev)
   ├─ rewrites paths so sample_db/ and src/ point to the bundled copies
   │  (horus_rv_launcher.update_integration_paths)
   ├─ writes the patched script to a tempfile, then runs:
   │     rv.exe -flags ModeManagerPreload=horus_mode \
   │            -pyeval "exec(open(<tempfile>).read())"
   └─ inside RV: rv_horus_integration creates dock widgets via PySide2
```

The launcher is the **only** entry point that should be modified for startup behavior — `rv_horus_integration.py` is injected, not imported normally, so it has access to `rv.commands` / `rv.qtutils` only at runtime inside Open RV.

### Module map
| File | Role |
|---|---|
| `horus_rv_launcher.py` | Launcher; locates RV, injects UI script, handles PyInstaller `_MEIPASS` paths. |
| `rv_horus_integration.py` | UI layer (~6k lines). Creates Navigator, Comments, and Timeline Playlist docks; manages dock visibility/geometry persistence (`save_ui_state` → `%APPDATA%/Horus/ui_state.json` on Windows, `~/.config/Horus/` elsewhere). |
| `horus_file_system.py` | File-system abstraction. `FileSystemProvider` ABC with `LocalFileSystemProvider` (V:/W: mounts) and an SSH provider. `auto_detect()` chooses based on `PREFERRED_ACCESS_MODE`. |
| `horus_comments.py` | `HorusCommentManager` — shot-level comments stored at `{shot}/.horus/{shot}_comments.json`; annotation PNGs at `{shot}/{dept}/annotations/{version}/`. |
| `horus_playlists.py` | `HorusPlaylistManager` — single project-level playlist file at `{project_root}/SWA/all/scene/.horus/playlists.json`. |
| `horus_version.py` | Semantic versioning (`MAJOR.MINOR.PATCH[-PRERELEASE]+BUILD`). Single source of truth = `version.json`. |
| `build_horus_rv_exe.py` | Plain PyInstaller wrapper. |
| `scripts/build_with_version.py` | CI build entry — writes `build_info.json`, runs PyInstaller, archives `dist/horus-<ver>-<platform>.zip`. |
| `scripts/version_bump.py` | Version bump + git tag + push. Refuses to run on a dirty working tree unless `--force`. |
| `scripts/release_manager.py` | Generates `CHANGELOG-<version>.md` from git log between tags. |

### Project / pipeline data layout
Configured in `horus_file_system.py:30-66`. Defaults:
- Linux project / image roots: `/mnt/igloo_swa_v`, `/mnt/igloo_swa_w`
- Windows project / image roots: `V:`, `W:`
- SSH host: `10.100.128.193` (`ec2-user`, key auto-discovered, including `~/.ssh/CaveTeam.pem`)
- Project name: `SWA`, scene path: `all/scene`, Horus data dir: `.horus`

Layout on the file server (see `docs/HORUS_TECHNICAL_DOCUMENTATION.md` §3 for the full tree):
```
{project_root}/SWA/all/scene/
├── {Episode}/
│   ├── .horus/status/{sequence}_status.json   # per-sequence status cache
│   └── {sequence}/{shot}/
│       ├── .horus/{shot}_comments.json        # per-shot comments
│       └── {department}/
│           ├── output/{shot}_{dept}_{ver}.mov
│           ├── version/{ver}/...exr           # image sequences (W:)
│           └── annotations/{ver}/{file}.{frame}.png
└── .horus/playlists.json                      # project-wide playlists
```

**Dual media source**: every media item has both a MOV (`V:` / `igloo_swa_v`) and an image sequence (`W:` / `igloo_swa_w`). They share one status, one comment thread, one version. The Navigator's "Image Seq | MOV" toggle only changes which file RV plays; it must not affect status/comment lookups. Item dict shape lives in `docs/HORUS_TECHNICAL_DOCUMENTATION.md` §3.3.

### File-naming and key conventions (enforced by code, not lint)
- Media filename: `{Shot}_{Department}_{Version}.{ext}` (e.g. `SH0010_comp_v003.mov`).
- Status keyed by `{Shot}_{Department}_{Version}`. Statuses are: `wip` (default), `submit`, `approved`, `need fix`, `on hold`.
- The current user comes from `HORUS_USER` env var, falling back to `USERNAME` (`horus_comments.get_current_user`).
- `sample_db/` is the read-only fallback bundled with the executable; do not write user data there.

## Working in this repo

### Branching and PRs
- All development on the per-task branch listed in instructions (e.g. `claude/...`). Do not push to `main`, `develop`, or `staging`.
- Branch-naming check in CI requires PR branches to match `^(feature|bugfix|hotfix|release|experiment)/[a-z0-9-]+$` (`.github/workflows/branch-protection.yml`).
- `version_bump.py` aborts on a dirty tree — commit or stash first, or pass `--force`.

### Editing `rv_horus_integration.py`
- It's monolithic (~6k lines) and uses **module-level globals** (`search_dock`, `comments_dock`, `timeline_playlist_dock`, `media_grid_dock`, `_ui_state_cache`, `_ui_state_loading`). Any new dock or persisted state needs to be added in all four places: globals, `save_ui_state`, `restore_ui_state`, and the menu wiring.
- The launcher checks for required functions before exec'ing (`horus_rv_launcher.py:191-207`). If you rename one of `create_search_panel`, `create_media_grid_panel`, `create_comments_panel`, `create_timeline_panel`, `create_timeline_playlist_panel`, `load_timeline_playlist_data`, `populate_playlist_tree`, or `create_new_playlist`, also update that list.
- Feature flag `ENABLE_TIMELINE_PLAYLIST = True` in the integration script is checked by the launcher (`horus_rv_launcher.py:209-213`).
- `update_integration_paths` in the launcher rewrites `os.path.join("sample_db" ...` and `os.path.join(project_root, 'src', 'packages' ...` strings — keep these literal in the integration script so the rewrite still matches.

### Adding files to the build
PyInstaller bundling is driven by explicit lists in `build_horus_rv_exe.py` (core/config files) and `scripts/build_with_version.py` (distribution copy). New runtime-required `.py` or data files must be added in **both** places, and to `_MEIPASS` lookups via `get_resource_path()` for runtime access.

### Code style
- PEP 8 + Black (line length effectively 127 in flake8, but Black formats to its default 88 — let Black win).
- Google-style docstrings on public functions/classes (per `docs/horus-architecture-design.md` §7.2).
- `.augment/rules/` and `docs/dont_use/` contain older design docs; `docs/HORUS_TECHNICAL_DOCUMENTATION.md` is the current source of truth for data schemas.
