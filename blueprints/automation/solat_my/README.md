# Blueprints — Waktu Solat Malaysia (solat.my)

Drop-in [Home Assistant blueprints](https://www.home-assistant.io/docs/automation/using_blueprints/) for the `solat_my` integration. Each blueprint wraps an automation from [AUTOMATION.md](../../AUTOMATION.md) and exposes the entity IDs as inputs so you can pick the right sensors/players via the UI.

## Install

1. Copy the YAML files in this folder to `<config>/blueprints/automation/solat_my/` on your Home Assistant instance, **or** import via URL once a release is published:

   `Settings → Automations & Scenes → Blueprints → Import Blueprint`

2. Reload blueprints or restart Home Assistant.
3. `Settings → Automations & Scenes → Create Automation → Use Blueprint` and pick one of the blueprints below.

## Available Blueprints

| File | Description |
|------|-------------|
| [azan_harian.yaml](azan_harian.yaml) | Main azan for all five prayer times with TTS/audio announcement + doa selepas azan. |
| [azan_jumaat.yaml](azan_jumaat.yaml) | Override Zohor with `azan_jumaat.mp3` on Fridays. |
| [peringatan_imsak.yaml](peringatan_imsak.yaml) | Reminder audio + notification at Imsak. |
| [peringatan_sebelum_solat.yaml](peringatan_sebelum_solat.yaml) | Push notification N minutes before a chosen prayer. |
| [azan_jeda_sambung.yaml](azan_jeda_sambung.yaml) | Pause every playing media player, play azan + doa, then resume. |
| [azan_multi_room.yaml](azan_multi_room.yaml) | Broadcast azan to multiple speakers simultaneously. |

## Notes

- All entity inputs default to the `waktu_solat` device slug. Override if you renamed the device.
- Audio files must live under `/media/azan/` and (for TTS audio mode) `/media/tts/`. See [AUTOMATION.md → Audio File Placement](../../AUTOMATION.md#audio-file-placement).
- `mode: single` prevents overlapping runs if Home Assistant restarts at prayer time.
