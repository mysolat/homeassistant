# Waktu Solat Malaysia — Home Assistant Custom Integration

A proper Home Assistant custom component that fetches Malaysian prayer times directly from the **solat.my API** (powered by JAKIM e-Solat).

## Features

- **16 entities** created automatically per device — no helpers needed:
  - **8 prayer time sensors** (Imsak, Subuh, Syuruk, Dhuha, Zohor, Asar, Maghrib, Isyak)
  - **Tarikh Hijri** — formatted Hijri date with month name in Malay
  - **Waktu Solat Seterusnya** — next upcoming prayer with countdown
  - **Waktu Solat Semasa** — current prayer period
  - **Zon** — select entity to switch zone live (all 59 zones, updates all sensors instantly)
  - **Pemain Media Azan** — auto-populated media player selector
  - **Kelantangan Azan** — volume slider (0.0–1.0)
  - **Fail Audio Azan / Subuh / Doa** — configurable audio filenames
- Supports **59 Malaysian zones** (all JAKIM zones + W.P.)
- UI-based setup — just enter a name and pick a starting zone
- Multiple devices supported (e.g., "Rumah" and "Pejabat")
- Data sourced from `https://solat.my/api` → JAKIM e-Solat

## Installation

### Via HACS (Recommended)

1. In HACS, add this repository as a custom repository
2. Search for "Waktu Solat Malaysia" and install
3. Restart Home Assistant

### Manual

1. Copy the `custom_components/solat_my/` folder into your HA `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **"Waktu Solat Malaysia"**
3. Enter a **Device Name** (default: `Waktu Solat`) — this becomes the entity ID prefix
4. Select the **starting zone** (e.g., `SGR01 — Selangor - Gombak, Petaling, ...`)
5. Click Submit — all 16 entities appear immediately

> **To change zone later:** go to the device page and change the **Zon** select entity. All prayer time sensors update instantly without a restart.

## Entities Created

The following entities are created under device **"Waktu Solat"** (default name):

### Sensors

| Entity ID | Name | Description |
|-----------|------|-------------|
| `sensor.waktu_solat_imsak` | Imsak | Waktu Imsak (timestamp) |
| `sensor.waktu_solat_subuh` | Subuh | Waktu Subuh (timestamp) |
| `sensor.waktu_solat_syuruk` | Syuruk | Waktu Syuruk (timestamp) |
| `sensor.waktu_solat_dhuha` | Dhuha | Waktu Dhuha (timestamp) |
| `sensor.waktu_solat_zohor` | Zohor | Waktu Zohor (timestamp) |
| `sensor.waktu_solat_asar` | Asar | Waktu Asar (timestamp) |
| `sensor.waktu_solat_maghrib` | Maghrib | Waktu Maghrib (timestamp) |
| `sensor.waktu_solat_isyak` | Isyak | Waktu Isyak (timestamp) |
| `sensor.waktu_solat_tarikh_hijri` | Tarikh Hijri | Tarikh Hijri berformat |
| `sensor.waktu_solat_waktu_solat_seterusnya` | Waktu Solat Seterusnya | Waktu solat seterusnya + kiraan detik |
| `sensor.waktu_solat_waktu_solat_semasa` | Waktu Solat Semasa | Tempoh waktu solat semasa |

### Configuration Entities

| Entity ID | Name | Description |
|-----------|------|-------------|
| `select.waktu_solat_zon` | Zon | Active zone — change to switch all sensors instantly |
| `select.waktu_solat_pemain_media_azan` | Pemain Media Azan | Media player for azan playback |
| `number.waktu_solat_kelantangan_azan` | Kelantangan Azan | Azan volume (0.0–1.0 slider) |
| `text.waktu_solat_fail_audio_azan` | Fail Audio Azan | Comma-separated azan filenames |
| `text.waktu_solat_fail_audio_azan_subuh` | Fail Audio Azan Subuh | Comma-separated Subuh azan filenames |
| `text.waktu_solat_fail_doa_selepas_azan` | Fail Doa Selepas Azan | Doa audio filename |

## Example Dashboard Card

```yaml
type: entities
title: Waktu Solat
entities:
  - entity: sensor.waktu_solat_waktu_solat_semasa
    name: Waktu Semasa
  - entity: sensor.waktu_solat_waktu_solat_seterusnya
    name: Waktu Seterusnya
  - entity: sensor.waktu_solat_imsak
    name: Imsak
    format: time
  - entity: sensor.waktu_solat_subuh
    name: Subuh
    format: time
  - entity: sensor.waktu_solat_syuruk
    name: Syuruk
    format: time
  - entity: sensor.waktu_solat_dhuha
    name: Dhuha
    format: time
  - entity: sensor.waktu_solat_zohor
    name: Zohor
    format: time
  - entity: sensor.waktu_solat_asar
    name: Asar
    format: time
  - entity: sensor.waktu_solat_maghrib
    name: Maghrib
    format: time
  - entity: sensor.waktu_solat_isyak
    name: Isyak
    format: time
  - entity: sensor.waktu_solat_tarikh_hijri
    name: Tarikh Hijri
```

## Azan Automation Example

```yaml
automation:
  - alias: "Azan Subuh"
    trigger:
      - platform: time
        at: sensor.waktu_solat_subuh
    action:
      - service: media_player.play_media
        target:
          entity_id: media_player.your_speaker
        data:
          media_content_id: /local/audio/azan_subuh.mp3
          media_content_type: music

  - alias: "Azan Zohor"
    trigger:
      - platform: time
        at: sensor.waktu_solat_zohor
    action:
      - service: media_player.play_media
        target:
          entity_id: media_player.your_speaker
        data:
          media_content_id: /local/audio/azan.mp3
          media_content_type: music
```

## Supported Zones

All 59 JAKIM prayer time zones are supported:

| Code | Location |
|------|----------|
| JHR01–JHR04 | Johor |
| KDH01–KDH07 | Kedah |
| KTN01–KTN02 | Kelantan |
| MLK01 | Melaka |
| NGS01–NGS03 | Negeri Sembilan |
| PHG01–PHG06 | Pahang |
| PLS01 | Perlis |
| PNG01 | Pulau Pinang |
| PRK01–PRK07 | Perak |
| SBH01–SBH09 | Sabah |
| SGR01–SGR03 | Selangor |
| SWK01–SWK09 | Sarawak |
| TRG01–TRG04 | Terengganu |
| WLY01 | W.P. Kuala Lumpur & Putrajaya |
| WLY02 | W.P. Labuan |

## API Credits

Prayer time data is provided by [solat.my](https://solat.my) which sources data from [JAKIM e-Solat](https://www.e-solat.gov.my/).
