# Blueprints — Waktu Solat Malaysia (solat.my)

Drop-in [Home Assistant blueprints](https://www.home-assistant.io/docs/automation/using_blueprints/) for the `solat_my` integration. Each blueprint wraps an automation from [AUTOMATION.md](../../AUTOMATION.md) and exposes the entity IDs as inputs so you can pick the right sensors/players via the UI.

## Install

1. Select the **Import blueprint** button next to each blueprint in the table below. Or copy the YAML files in this folder to `<config>/blueprints/automation/solat_my/` on your Home Assistant instance. You can also import by URL in `Settings → Automations & Scenes → Blueprints → Import Blueprint`.
2. Reload blueprints or restart Home Assistant.
3. `Settings → Automations & Scenes → Create Automation → Use Blueprint` and pick one of the blueprints below.

## Available Blueprints

| File | Description | Import |
|------|-------------|--------|
| [azan_harian.yaml](azan_harian.yaml) | Main azan for all five prayer times with TTS/audio announcement + doa selepas azan. | [![Import azan_harian.yaml blueprint.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fmysolat%2Fhomeassistant%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsolat_my%2Fazan_harian.yaml) |
| [azan_jumaat.yaml](azan_jumaat.yaml) | Override Zohor with `azan_jumaat.mp3` on Fridays. | [![Import azan_jumaat.yaml blueprint.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fmysolat%2Fhomeassistant%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsolat_my%2Fazan_jumaat.yaml) |
| [peringatan_imsak.yaml](peringatan_imsak.yaml) | Reminder audio + notification at Imsak. | [![Import peringatan_imsak.yaml blueprint.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fmysolat%2Fhomeassistant%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsolat_my%2Fperingatan_imsak.yaml) |
| [peringatan_sebelum_solat.yaml](peringatan_sebelum_solat.yaml) | Notification and optional actions N minutes before a chosen prayer. | [![Import peringatan_sebelum_solat.yaml blueprint.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fmysolat%2Fhomeassistant%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsolat_my%2Fperingatan_sebelum_solat.yaml) |
| [azan_jeda_sambung.yaml](azan_jeda_sambung.yaml) | Pause every playing media player, play azan + doa, then resume. | [![Import azan_jeda_sambung.yaml blueprint.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fmysolat%2Fhomeassistant%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsolat_my%2Fazan_jeda_sambung.yaml) |
| [azan_multi_room.yaml](azan_multi_room.yaml) | Broadcast azan to multiple speakers simultaneously. | [![Import azan_multi_room.yaml blueprint.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fmysolat%2Fhomeassistant%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsolat_my%2Fazan_multi_room.yaml) |

## Notes

- All entity inputs default to the `waktu_solat` device slug. Override if you renamed the device.
- Audio files must live under `/media/azan/` and (for TTS audio mode) `/media/tts/`. See [AUTOMATION.md → Audio File Placement](../../AUTOMATION.md#audio-file-placement).
- Use `azan_jumaat` together with `azan_harian` only with **Langkau Zohor pada Jumaat** turned on.
- Announcement in `tts` mode needs a TTS entity. Pick one in **TTS**.
- Enter **Masa Sebelum** in `peringatan_sebelum_solat` as a negative duration, for example -15 minutes. A positive value fires after the prayer.
- **Notifikasi tambahan** takes any actions, for example `notify.mobile_app_phone`. It runs after the audio starts. `peringatan_sebelum_solat` has no audio, so it runs at once.
