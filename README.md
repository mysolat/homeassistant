# Waktu Solat Malaysia — Home Assistant Custom Integration

A proper Home Assistant custom component that fetches Malaysian prayer times directly from the **solat.my API** (powered by JAKIM e-Solat).

<img width="999" height="874" alt="Image" src="https://github.com/user-attachments/assets/d6332e0d-331c-4d95-8d99-4f78c4935fdc" />

<img width="1170" height="865" alt="Image" src="https://github.com/user-attachments/assets/173634ae-7af2-4cfb-8450-d594df49c7d2" />

## Features

- **26 entities** created automatically per device — no helpers needed:
  - **8 prayer time sensors** (Imsak, Subuh, Syuruk, Dhuha, Zohor, Asar, Maghrib, Isyak)
  - **Tarikh Hijri** — formatted Hijri date with month name in Malay
  - **Waktu Solat Seterusnya** — next upcoming prayer with countdown
  - **Waktu Solat Semasa** — current prayer period
  - **Zon** — select entity to switch zone live (all 59 zones, updates all sensors instantly)
  - **Pemain Media Azan** — auto-populated media player selector
  - **Mod Pengumuman Azan** — announcement mode before azan (`tts` or `audio`)
  - **Kelantangan Azan** — volume slider (0.0–1.0)
  - **Fail Audio Azan / Subuh / Doa** — configurable audio filenames
  - **Uji Main Azan / Uji Henti Azan** — buttons that play the azan now, or stop it
  - **Kalendar Solat** — calendar with the five prayer times as events, for calendar triggers in automations and the Calendar panel
  - **Skrin Solat display controls** — background colour, image visibility, clarity, local image, and 12h/24h time for the full-screen Skrin Solat card
- Supports **59 Malaysian zones** (all JAKIM zones + W.P.)
- UI-based setup — just enter a name and pick a starting zone
- Multiple devices supported (e.g., "Rumah" and "Pejabat")
- Data sourced from `https://solat.my/api` → JAKIM e-Solat. The integration also saves the whole year's timetable on disk. If solat.my is unreachable, it reads prayer times from that copy.
- **Skrin Solat** — an optional, Malay-only TV/dashboard card with a local `HH:MM:SS` next-adhan countdown, current-prayer highlight, optional Imsak/Dhuha/Ramadan rail, and native device controls for background, image visibility, and 12/24-hour display time

## Installation

### Via HACS (Recommended)

[![Open your Home Assistant instance and open this repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=mysolat&repository=homeassistant&category=integration)

1. Select the button above, or in HACS add this repository as a custom repository
2. Search for "Waktu Solat Malaysia" and install
3. Restart Home Assistant

### Manual

1. Copy the `custom_components/solat_my/` folder into your HA `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

[![Open your Home Assistant instance and start setting up Waktu Solat Malaysia.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=solat_my)

1. Select the button above, or go to **Settings → Devices & Services → Add Integration**
2. Search for **"Waktu Solat Malaysia"**
3. Enter a **Device Name** (default: `Waktu Solat`) — this becomes the entity ID prefix
4. Select the **starting zone** (e.g., `SGR01 — Selangor - Gombak, Petaling, ...`)
   The zone is pre-selected from your Home Assistant home location. The integration sends that location, rounded to about 1 km, to solat.my once. You can choose a different zone.
5. Click Submit — all 26 entities appear immediately

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
| `sensor.waktu_solat_waktu_solat_seterusnya` | Waktu Solat Seterusnya | Waktu solat seterusnya + kiraan detik (selepas Isyak: Subuh esok) |
| `sensor.waktu_solat_waktu_solat_semasa` | Waktu Solat Semasa | Tempoh waktu solat semasa |

### Configuration Entities

| Entity ID | Name | Description |
|-----------|------|-------------|
| `select.waktu_solat_zon` | Zon | Active zone — change to switch all sensors instantly |
| `select.waktu_solat_pemain_media_azan` | Pemain Media Azan | Media player for azan playback |
| `select.waktu_solat_mod_pengumuman_azan` | Mod Pengumuman Azan | Announcement mode before azan (`tts` or `audio`) |
| `number.waktu_solat_kelantangan_azan` | Kelantangan Azan | Azan volume (0.0–1.0 slider) |
| `text.waktu_solat_fail_audio_azan` | Fail Audio Azan | Comma-separated azan filenames |
| `text.waktu_solat_fail_audio_azan_subuh` | Fail Audio Azan Subuh | Comma-separated Subuh azan filenames |
| `text.waktu_solat_fail_doa_selepas_azan` | Fail Doa Selepas Azan | Doa audio filename |
| `select.waktu_solat_skrin_warna_latar` | Skrin Warna Latar | Skrin Solat background colour (`forest`, `midnight`, `slate`, `burgundy`, `indigo`) |
| `select.waktu_solat_skrin_paparan_latar` | Skrin Paparan Latar | Show or hide the Skrin Solat background image (`on` / `off`) |
| `number.waktu_solat_skrin_kejelasan_latar` | Skrin Kejelasan Latar | Skrin Solat background clarity (0–100 slider) |
| `text.waktu_solat_skrin_imej_latar` | Skrin Imej Latar | Optional `/local/...` image that replaces the courtyard |
| `select.waktu_solat_skrin_format_masa` | Skrin Format Masa | Skrin Solat time format (`24h` or `12h`) |

### Buttons

| Entity ID | Name | Description |
|-----------|------|-------------|
| `button.waktu_solat_uji_main_azan` | Uji Main Azan | Plays the first file of **Fail Audio Azan** now, on **Pemain Media Azan** at **Kelantangan Azan** volume. Use it to check your setup without waiting for a prayer |
| `button.waktu_solat_uji_henti_azan` | Uji Henti Azan | Stops **Pemain Media Azan** |

### Calendar

| Entity ID | Name | Description |
|-----------|------|-------------|
| `calendar.waktu_solat_kalendar_solat` | Kalendar Solat | Subuh, Zohor, Asar, Maghrib and Isyak as calendar events. Each event starts when the prayer time begins. It lasts 10 minutes for display only. Imsak, Syuruk and Dhuha are not events |

## Dashboard Cards

See [DASHBOARD.md](DASHBOARD.md) for ready-to-paste Mushroom Card layouts and the full-screen Skrin Solat card. The Skrin Solat card is served and loaded by this integration, so there is no dashboard resource to add; put it in a Panel view and map its timestamp, Hijri, and current-prayer entities explicitly. Configure its normal background on the matching Solat.my device through **Skrin Warna Latar**, **Skrin Paparan Latar**, **Skrin Kejelasan Latar**, and **Skrin Imej Latar**; use **Skrin Format Masa** to choose 24-hour or 12-hour display time. The courtyard stays behind colour changes unless you turn the background off or provide a local replacement image. It calculates the next main prayer locally, including the after-Isyak Subuh rollover, and never controls azan audio.
<img width="671" height="572" alt="Image" src="https://github.com/user-attachments/assets/13ac5b24-b76c-4253-8ec0-5007ec247d3d" />
<img width="1816" height="1164" alt="skrin_solat_1" src="https://github.com/user-attachments/assets/f4b6f7fa-8b0e-427a-b810-22f142a6a657" />
<img width="411" height="836" alt="skrin_solat_3" src="https://github.com/user-attachments/assets/f0554761-106f-4279-9608-cbffc0c80a7b" />

## Azan Automations

See [AUTOMATION.md](AUTOMATION.md) for full automation examples including:

- Main azan for all five prayer times
- Jumaat (Friday) override
- Imsak reminder
- Pre-prayer countdown notification
- Pause all devices during azan, then resume
- Multi-room broadcast

### Calendar trigger

**Kalendar Solat** starts one event when each prayer time begins, as JAKIM publishes it. The 10-minute length of an event is for display only. It does not say when the prayer time ends. Use `event: start` in a calendar trigger. The offset `"-0:10:00"` runs the automation 10 minutes before the prayer time.

This automation sends a reminder 10 minutes before Maghrib:

```yaml
triggers:
  - trigger: calendar
    event: start
    offset: "-0:10:00"
    entity_id: calendar.waktu_solat_kalendar_solat
conditions:
  - condition: template
    value_template: "{{ trigger.calendar_event.summary == 'Maghrib' }}"
actions:
  - action: notify.notify
    data:
      message: "Maghrib dalam 10 minit."
```

### Blueprints

Import the same automations as ready-made blueprints. Setup notes are in [blueprints/automation/solat_my/README.md](blueprints/automation/solat_my/README.md).

| Blueprint | What it does | Import |
|---|---|---|
| [azan_harian](blueprints/automation/solat_my/azan_harian.yaml) | Azan for all five prayer times, with announcement and doa | [![Import azan_harian.yaml blueprint.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fmysolat%2Fhomeassistant%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsolat_my%2Fazan_harian.yaml) |
| [azan_jumaat](blueprints/automation/solat_my/azan_jumaat.yaml) | Azan Jumaat at Zohor on Fridays | [![Import azan_jumaat.yaml blueprint.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fmysolat%2Fhomeassistant%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsolat_my%2Fazan_jumaat.yaml) |
| [peringatan_imsak](blueprints/automation/solat_my/peringatan_imsak.yaml) | Reminder at Imsak | [![Import peringatan_imsak.yaml blueprint.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fmysolat%2Fhomeassistant%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsolat_my%2Fperingatan_imsak.yaml) |
| [peringatan_sebelum_solat](blueprints/automation/solat_my/peringatan_sebelum_solat.yaml) | Reminder before a chosen prayer | [![Import peringatan_sebelum_solat.yaml blueprint.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fmysolat%2Fhomeassistant%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsolat_my%2Fperingatan_sebelum_solat.yaml) |
| [azan_jeda_sambung](blueprints/automation/solat_my/azan_jeda_sambung.yaml) | Pause playing speakers, play azan and doa, then resume | [![Import azan_jeda_sambung.yaml blueprint.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fmysolat%2Fhomeassistant%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsolat_my%2Fazan_jeda_sambung.yaml) |
| [azan_multi_room](blueprints/automation/solat_my/azan_multi_room.yaml) | Azan on several speakers at once | [![Import azan_multi_room.yaml blueprint.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fmysolat%2Fhomeassistant%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsolat_my%2Fazan_multi_room.yaml) |

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
