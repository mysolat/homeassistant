# Changelog

All notable changes to this project will be documented in this file.

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
