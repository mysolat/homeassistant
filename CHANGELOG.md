# Changelog

All notable changes to this project will be documented in this file.

## [1.0.5] - 2026-09-19

### Added
- **Paparan Mimbar Skrin Penuh** — full-screen `custom:solat-my-mimbar-card` for TVs and kiosk dashboards: local next-prayer countdown (including the after-Isyak rollover), current and next prayer highlight, optional Imsak/Dhuha and Ramadan rail, adhan/iqamah/quiet-time lifecycle, and message or image slides. Malay-only; it never controls azan audio.
- Five device controls for the card: `select.waktu_solat_warna_latar_mimbar` (five colour presets), `select.waktu_solat_paparan_latar_mimbar` (background image on/off), `number.waktu_solat_kejelasan_latar_mimbar` (0–100), `text.waktu_solat_imej_latar_mimbar` (a `/local/...` image), and `select.waktu_solat_format_masa_mimbar` (`24h` or `12h`, shown as AM/PM).
- The integration now serves the card and loads it on every dashboard automatically; no dashboard resource is needed. Its URL carries a hash of the card files, so browsers pick up updates.
- DASHBOARD.md: paste-ready Mimbar dashboard using the default entity IDs, with an optional extended version (Iqamah countdown, notices).

### Changed
- `manifest.json` now lists `frontend` and `http` under `after_dependencies`.
- README entity counts corrected to 23 per device and the new controls added to the entity tables.

### Upgrade note
- If you added `/api/solat_my/mimbar/solat-my-mimbar-card.js` as a dashboard resource by hand, remove it, or the card loads twice. Restart Home Assistant and hard-refresh your browser after updating.

## [1.0.3] - 2026-05-10

### Added
- `select.waktu_solat_mod_pengumuman_azan` — new entity to choose announcement mode before azan (`tts` or `audio`)
- Pre-recorded TTS audio files for all five prayer times (`tts_subuh.mp3`, `tts_zohor.mp3`, `tts_asar.mp3`, `tts_maghrib.mp3`, `tts_isyak.mp3`) shipped under `media/tts/`
- [DASHBOARD.md](DASHBOARD.md) — dedicated dashboard documentation with Mushroom Card layouts (3×2 grid and vertical timeline)
- [AUTOMATION.md](AUTOMATION.md) — full automation examples including Jumaat override, Imsak reminder, pause/resume all devices, and multi-room broadcast

### Changed
- README updated to reference AUTOMATION.md and DASHBOARD.md instead of inline stub examples
- Entity count corrected from 16 to 17

## [1.0.2] - 2026-03-27

### Fixed
- Made `Pemain Media Azan` selection persistent across Home Assistant restarts by storing the selected media player in config entry options.
- Prevented startup discovery order from overriding user-selected media player with the first discovered device.
- Kept selected media player sticky even when target player is temporarily unavailable during boot.

## [1.0.1] - 2026-03-27

### Fixed
- Prevented `Waktu Solat Semasa` and `Waktu Solat Seterusnya` sensors from appearing stuck by adding minute-level local state refresh for both entities.
- Improved date boundary handling by using Home Assistant timezone when selecting daily prayer data.
- Guarded next-prayer countdown from showing negative seconds during transition boundaries.
