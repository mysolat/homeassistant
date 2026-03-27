# Changelog

All notable changes to this project will be documented in this file.

## [1.0.1] - 2026-03-27

### Fixed
- Prevented `Waktu Solat Semasa` and `Waktu Solat Seterusnya` sensors from appearing stuck by adding minute-level local state refresh for both entities.
- Improved date boundary handling by using Home Assistant timezone when selecting daily prayer data.
- Guarded next-prayer countdown from showing negative seconds during transition boundaries.
