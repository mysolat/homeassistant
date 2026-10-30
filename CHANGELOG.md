# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **Uji Azan** and **Henti Azan** buttons play the configured azan now, or stop it, so you can check the player, volume and file without waiting for a prayer.

### Changed
- The full-screen display is now called **Skrin Solat**. Its card type is `custom:solat-my-skrin-solat-card`. The old type `custom:solat-my-mimbar-card` still works. Existing entity IDs stay the same, and only their names change.

### Fixed
- The azan media player list now updates only when a media player is added or removed. Before, it ran on every state change in Home Assistant.

## [1.0.9] - 2026-10-30

### Changed
- Brand images follow Home Assistant's brand standard: `icon.png` and `dark_icon.png` are 256×256, with 512×512 `@2x` versions. The duplicate logo files are removed; Home Assistant uses the icon in their place.
- The READMEs have My Home Assistant buttons to open the repository in HACS, start the integration setup, and import each blueprint.

## [1.0.8] - 2026-10-30

### Added
- When you add the integration, the zone is pre-selected from Home Assistant's home location (sent to solat.my rounded to about 1 km). Outside Malaysia, or if the lookup fails, it falls back to `SGR01`.
- Six automation blueprints in `blueprints/automation/solat_my/`, importable by URL.

### Changed
- `peringatan_sebelum_solat` takes `time_before` (a negative duration, for example -15 minutes) instead of `minutes_before`.
- `azan_harian`, `peringatan_imsak` and `peringatan_sebelum_solat` take an optional `notify_actions` input instead of a `notify_service` name.

## [1.0.7] - 2026-10-30

### Fixed
- An API reply that is not valid JSON now retries in 5 minutes like any other API error. Before, it waited 12 hours, and on the last day of the month it could fail the whole update.

### Changed
- The coordinator now uses Home Assistant's config entry lifecycle (`config_entry=`, `entry.runtime_data`, `async_on_unload`). Unloading the integration now runs Home Assistant's own coordinator cleanup.

## [1.0.6] - 2026-10-30

### Fixed
- The zone chosen with `select.waktu_solat_zon` now survives a restart. Before, the sensors went back to the setup zone's times until the next month.
- Prayer times are always Malaysian time (`Asia/Kuala_Lumpur`), whatever time zone Home Assistant uses.
- The `bearing` attribute shows `291° 7′ 23″` instead of HTML entities.
- On the last day of each month the integration downloads next month's prayer times, so the change of month needs no network.
- After an API error the integration retries in 5 minutes instead of 12 hours.
- If the API reply lacks today's date, the sensors go unavailable and the log names the date. Before, they silently showed another day's times.

### Removed
- The empty **Configure** (options) dialog. On current Home Assistant it failed to open, and on older versions submitting it erased the saved azan media player. Change the zone with `select.waktu_solat_zon`.

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
