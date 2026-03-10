# Automation — Waktu Solat Malaysia (solat.my)

All automations use `platform: time` triggers pointing at prayer time sensors from the `solat_my` integration.
Entity IDs use the **Device Name** you set during setup (default: `Waktu Solat`). If you named your device differently, replace `waktu_solat` with your device name slug.

---

## No Helpers Required

The integration automatically creates all configuration entities when you add a zone:

| Entity | Description | Default |
|--------|-------------|---------|
| `number.waktu_solat_kelantangan_azan` | Azan volume (0.0 – 1.0) | `0.6` |
| `select.waktu_solat_pemain_media_azan` | Which media player plays the azan | First available |
| `text.waktu_solat_fail_audio_azan` | Comma-separated azan filenames | `azan1.mp3, azan2.mp3` |
| `text.waktu_solat_fail_audio_azan_subuh` | Comma-separated Subuh azan filenames | `azan_subuh.mp3` |
| `text.waktu_solat_fail_doa_selepas_azan` | Doa selepas azan filename | `doa_selepas_azan.mp3` |

Configure them via **Settings → Devices & Services → your device page**, or directly in any automation/dashboard. Change zone anytime via `select.waktu_solat_zon` — all sensors update instantly.

---

## Main Azan Automation

Handles all five prayer times in one automation. Plays different azan for Subuh, uses `media-source://` for audio from `/config/www/azan/`, then plays doa selepas azan.

```yaml
alias: "Azan Harian"
description: "Play azan for all prayer times via solat.my integration"
mode: single
triggers:
  - trigger: time
    at: sensor.waktu_solat_subuh
    id: subuh
  - trigger: time
    at: sensor.waktu_solat_zohor
    id: zohor
  - trigger: time
    at: sensor.waktu_solat_asar
    id: asar
  - trigger: time
    at: sensor.waktu_solat_maghrib
    id: maghrib
  - trigger: time
    at: sensor.waktu_solat_isyak
    id: isyak
conditions: []
actions:
  # Persistent notification
  - action: persistent_notification.create
    data:
      notification_id: solat_azan
      title: >
        🕋 Waktu Solat —
        {% set names = {'subuh': 'Subuh', 'zohor': 'Zohor', 'asar': 'Asar', 'maghrib': 'Maghrib', 'isyak': 'Isyak'} %}
        {{ names[trigger.id] }}
      message: >
        {% set names = {'subuh': 'Subuh', 'zohor': 'Zohor', 'asar': 'Asar', 'maghrib': 'Maghrib', 'isyak': 'Isyak'} %}
        {{ now().strftime('%-I:%M %p') }} — Sekarang telah masuk waktu
        {{ names[trigger.id] }} bagi kawasan ini dan kawasan yang sama waktu dengannya.

  # Mobile push notification
  - action: notify.notify
    data:
      title: >
        🕋 Waktu Solat —
        {% set names = {'subuh': 'Subuh', 'zohor': 'Zohor', 'asar': 'Asar', 'maghrib': 'Maghrib', 'isyak': 'Isyak'} %}
        {{ names[trigger.id] }}
      message: >
        {% set names = {'subuh': 'Subuh', 'zohor': 'Zohor', 'asar': 'Asar', 'maghrib': 'Maghrib', 'isyak': 'Isyak'} %}
        {{ now().strftime('%-I:%M %p') }} — Sekarang telah masuk waktu {{ names[trigger.id] }}.

  # Set volume
  # Set volume — skipped if media player does not support it (e.g. TV)
  - if:
      - condition: template
        value_template: >
          {{ state_attr(states('select.waktu_solat_pemain_media_azan'), 'supported_features') | int(0) | bitwise_and(4) > 0 }}
    then:
      - action: media_player.volume_set
        target:
          entity_id: "{{ states('select.waktu_solat_pemain_media_azan') }}"
        data:
          volume_level: "{{ states('number.waktu_solat_kelantangan_azan') | float }}"

  # TTS announcement
  - action: tts.google_translate_say
    data:
      entity_id: "{{ states('select.waktu_solat_pemain_media_azan') }}"
      language: id
      message: >
        {% set names = {'subuh': 'Subuh', 'zohor': 'Zohor', 'asar': 'Asar', 'maghrib': 'Maghrib', 'isyak': 'Isyak'} %}
        Sekarang telah masuk waktu {{ names[trigger.id] }}.

  - delay: "00:00:10"

  # Play azan audio (random selection from text entity)
  - action: media_player.play_media
    target:
      entity_id: "{{ states('select.waktu_solat_pemain_media_azan') }}"
    data:
      extra:
        title: >
          {% set names = {'subuh': 'Subuh', 'zohor': 'Zohor', 'asar': 'Asar', 'maghrib': 'Maghrib', 'isyak': 'Isyak'} %}
          Azan {{ names[trigger.id] }}
        thumb: "https://solat.my/icon-512.png"
      media:
        media_content_type: audio/mp3
        media_content_id: >
          {% if trigger.id == 'subuh' %}
            {{ "media-source://media_source/local/azan/" ~
               states('text.waktu_solat_fail_audio_azan_subuh').split(', ') | random }}
          {% else %}
            {{ "media-source://media_source/local/azan/" ~
               states('text.waktu_solat_fail_audio_azan').split(', ') | random }}
          {% endif %}
        metadata: {}

  # Wait for azan to finish, then play doa
  - choose:
      - conditions:
          - condition: trigger
            id: subuh
        sequence:
          - delay:
              minutes: 4
              seconds: 30
      - conditions:
          - condition: not
            conditions:
              - condition: trigger
                id: subuh
        sequence:
          - delay:
              minutes: 2
              seconds: 47

  # Play doa selepas azan
  - action: media_player.play_media
    alias: "Doa Selepas Azan"
    target:
      entity_id: "{{ states('select.waktu_solat_pemain_media_azan') }}"
    data:
      media:
        media_content_id: media-source://media_source/local/azan/doa_selepas_azan.mp3
        media_content_type: audio/mpeg
        metadata:
          title: doa_selepas_azan.mp3
          media_class: music
```

---

## Azan Jumaat (Friday Zohor Override)

Override the Zohor azan on Fridays with a special Jumaat azan file.

```yaml
alias: "Azan Zohor / Jumaat"
description: "Play Jumaat azan on Fridays, regular azan otherwise"
mode: single
triggers:
  - trigger: time
    at: sensor.waktu_solat_zohor
conditions: []
actions:
  - action: persistent_notification.create
    data:
      notification_id: solat_azan
      title: >
        🕋 Waktu Solat —
        {% if now().weekday() == 4 %}Jumaat{% else %}Zohor{% endif %}
      message: >
        {{ now().strftime('%-I:%M %p') }} — Sekarang telah masuk waktu
        {% if now().weekday() == 4 %}Jumaat{% else %}Zohor{% endif %}.

  # Set volume — skipped if media player does not support it (e.g. TV)
  - if:
      - condition: template
        value_template: >
          {{ state_attr(states('select.waktu_solat_pemain_media_azan'), 'supported_features') | int(0) | bitwise_and(4) > 0 }}
    then:
      - action: media_player.volume_set
        target:
          entity_id: "{{ states('select.waktu_solat_pemain_media_azan') }}"
        data:
          volume_level: "{{ states('number.waktu_solat_kelantangan_azan') | float }}"

  - action: media_player.play_media
    target:
      entity_id: "{{ states('select.waktu_solat_pemain_media_azan') }}"
    data:
      media:
        media_content_type: audio/mp3
        media_content_id: >
          {% if now().weekday() == 4 %}
            media-source://media_source/local/azan/azan_jumaat.mp3
          {% else %}
            {{ "media-source://media_source/local/azan/" ~
               states('text.waktu_solat_fail_audio_azan').split(', ') | random }}
          {% endif %}
        metadata: {}
```

---

## Imsak Reminder

Play a reminder or send a notification at Imsak time (start of fasting).

```yaml
alias: "Peringatan Imsak"
description: "Notify and play reminder at Imsak time"
mode: single
triggers:
  - trigger: time
    at: sensor.waktu_solat_imsak
conditions: []
actions:
  - action: persistent_notification.create
    data:
      notification_id: solat_imsak

      title: "🌙 Waktu Imsak"
      message: >
        {{ now().strftime('%-I:%M %p') }} — Sudah masuk waktu Imsak.
        Berhenti makan dan minum sekarang.

  - action: notify.notify
    data:
      title: "🌙 Waktu Imsak"
      message: "Sudah masuk waktu Imsak. Berhenti makan dan minum sekarang."

  - action: media_player.volume_set
    target:
      entity_id: "{{ states('select.waktu_solat_pemain_media_azan') }}"
    data:
      volume_level: 0.5

  - action: media_player.play_media
    target:
      entity_id: "{{ states('select.waktu_solat_pemain_media_azan') }}"
    data:
      media:
        media_content_id: media-source://media_source/local/azan/imsak_reminder.mp3
        media_content_type: audio/mp3
        metadata: {}
```

---

## Pre-Prayer Reminder (15 minutes before Maghrib)

Send a notification countdown before Maghrib — useful during Ramadan.

```yaml
alias: "Peringatan Sebelum Maghrib (15 minit)"
description: "Notify 15 minutes before Maghrib"
mode: single
triggers:
  - trigger: template
    value_template: >
      {{ (as_timestamp(states('sensor.waktu_solat_maghrib')) - as_timestamp(now())) | int == 900 }}
conditions: []
actions:
  - action: notify.notify
    data:
      title: "🕌 Peringatan Waktu Solat"
      message: >
        Maghrib dalam masa 15 minit pada pukul
        {{ as_timestamp(states('sensor.waktu_solat_maghrib')) | timestamp_custom('%H:%M') }}.
      data:
        push:
          sound: default
```

---

## Pause & Resume All Playing Devices

Automatically finds **every** media player that is currently playing (TV, speakers, etc.), pauses them all, plays the azan, then restores each device back to what it was doing.

```yaml
alias: "Azan Harian (Jeda Semua & Sambung Semula)"
description: "Pause all playing devices, play azan + doa, then resume everything"
mode: single
triggers:
  - trigger: time
    at: sensor.waktu_solat_subuh
    id: subuh
  - trigger: time
    at: sensor.waktu_solat_zohor
    id: zohor
  - trigger: time
    at: sensor.waktu_solat_asar
    id: asar
  - trigger: time
    at: sensor.waktu_solat_maghrib
    id: maghrib
  - trigger: time
    at: sensor.waktu_solat_isyak
    id: isyak
conditions: []
actions:
  # Step 1: Capture all currently playing media players into a variable
  - variables:
      peranti_bermain: >
        {{ states.media_player
           | selectattr('state', 'eq', 'playing')
           | map(attribute='entity_id')
           | list }}

  # Step 2: Snapshot + pause all playing devices (only if something is playing)
  - if:
      - condition: template
        value_template: "{{ peranti_bermain | length > 0 }}"
    then:
      - action: scene.create
        data:
          scene_id: sebelum_azan
          snapshot_entities: "{{ peranti_bermain }}"
      - action: media_player.media_pause
        continue_on_error: true
        target:
          entity_id: "{{ peranti_bermain }}"
      - delay: "00:00:02"

  # Step 3: Persistent notification
  - action: persistent_notification.create
    data:
      notification_id: solat_azan
      title: >
        🕋 Waktu Solat —
        {% set names = {'subuh': 'Subuh', 'zohor': 'Zohor', 'asar': 'Asar', 'maghrib': 'Maghrib', 'isyak': 'Isyak'} %}
        {{ names[trigger.id] }}
      message: >
        {% set names = {'subuh': 'Subuh', 'zohor': 'Zohor', 'asar': 'Asar', 'maghrib': 'Maghrib', 'isyak': 'Isyak'} %}
        {{ now().strftime('%-I:%M %p') }} — Sekarang telah masuk waktu {{ names[trigger.id] }}.

  # Step 4: Set volume — skipped for TVs / devices that don't support it
  - if:
      - condition: template
        value_template: >
          {{ state_attr(states('select.waktu_solat_pemain_media_azan'), 'supported_features') | int(0) | bitwise_and(4) > 0 }}
    then:
      - action: media_player.volume_set
        target:
          entity_id: "{{ states('select.waktu_solat_pemain_media_azan') }}"
        data:
          volume_level: "{{ states('number.waktu_solat_kelantangan_azan') | float }}"

  # Step 5: Play azan audio
  - action: media_player.play_media
    target:
      entity_id: "{{ states('select.waktu_solat_pemain_media_azan') }}"
    data:
      media:
        media_content_type: audio/mp3
        media_content_id: >
          {% if trigger.id == 'subuh' %}
            {{ "media-source://media_source/local/azan/" ~
               states('text.waktu_solat_fail_audio_azan_subuh').split(', ') | random }}
          {% else %}
            {{ "media-source://media_source/local/azan/" ~
               states('text.waktu_solat_fail_audio_azan').split(', ') | random }}
          {% endif %}
        metadata: {}

  # Step 6: Wait for azan to finish (Subuh is longer)
  - choose:
      - conditions:
          - condition: trigger
            id: subuh
        sequence:
          - delay:
              minutes: 4
              seconds: 30
    default:
      - delay:
          minutes: 2
          seconds: 47

  # Step 7: Play doa selepas azan
  - action: media_player.play_media
    alias: "Doa Selepas Azan"
    target:
      entity_id: "{{ states('select.waktu_solat_pemain_media_azan') }}"
    data:
      media:
        media_content_id: >
          media-source://media_source/local/azan/{{ states('text.waktu_solat_fail_doa_selepas_azan') }}
        media_content_type: audio/mpeg
        metadata:
          title: Doa Selepas Azan
          media_class: music

  # Step 8: Wait for doa to finish
  - wait_for_trigger:
      - trigger: state
        entity_id: "{{ states('select.waktu_solat_pemain_media_azan') }}"
        to: "idle"
    timeout:
      minutes: 2

  # Step 9: Resume all paused devices
  - if:
      - condition: template
        value_template: "{{ peranti_bermain | length > 0 }}"
    then:
      - delay: "00:00:02"
      - action: scene.turn_on
        target:
          entity_id: scene.sebelum_azan
```

---

## Multi-Room Azan

Broadcast azan to multiple speakers simultaneously.

```yaml
alias: "Azan Serentak (Multi-room)"
description: "Play azan on all speakers at prayer time"
mode: single
triggers:
  - trigger: time
    at: sensor.waktu_solat_subuh
    id: subuh
  - trigger: time
    at: sensor.waktu_solat_zohor
    id: zohor
  - trigger: time
    at: sensor.waktu_solat_asar
    id: asar
  - trigger: time
    at: sensor.waktu_solat_maghrib
    id: maghrib
  - trigger: time
    at: sensor.waktu_solat_isyak
    id: isyak
conditions: []
actions:
  - action: media_player.volume_set
    target:
      entity_id:
        - media_player.ruang_tamu
        - media_player.bilik_tidur
        - media_player.dapur
    data:
      volume_level: 0.65

  - action: media_player.play_media
    target:
      entity_id:
        - media_player.ruang_tamu
        - media_player.bilik_tidur
        - media_player.dapur
    data:
      media:
        media_content_type: audio/mp3
        media_content_id: >
          {% if trigger.id == 'subuh' %}
            {{ "media-source://media_source/local/azan/" ~
               states('text.waktu_solat_fail_audio_azan_subuh').split(', ') | random }}
          {% else %}
            {{ "media-source://media_source/local/azan/" ~
               states('text.waktu_solat_fail_audio_azan').split(', ') | random }}
          {% endif %}
        metadata: {}
```

---

## Audio File Placement

Put your audio files in `/media/azan/` (the Home Assistant media folder):

```
media/
└── azan/
    ├── azan1.mp3
    ├── azan2.mp3
    ├── azan_subuh1.mp3
    ├── azan_subuh2.mp3
    ├── azan_jumaat.mp3
    ├── imsak_reminder.mp3
    └── doa_selepas_azan.mp3
```

Files are served at `media-source://media_source/local/azan/<filename>` in automations.

> **Note:** `/config/www/azan/` is a different location — it serves static files over HTTP at
> `http://homeassistant.local:8123/local/azan/<filename>` (for Sonos/Alexa direct URL), but
> **cannot** be accessed via `media-source://`. Use `/media/azan/` for all automations here.

---

## Notes

| Speaker Type | `media_content_type` | Notes |
|---|---|---|
| Google Home / Nest | `audio/mp3` | Use `media-source://` path |
| Alexa (via Alexa Media Player) | `music` | Use direct HTTP URL |
| Sonos | `music` | Use direct HTTP URL |
| Generic / Cast | `audio/mp3` | Either path format works |

- **Weekdays:** Monday=0, Tuesday=1, Wednesday=2, Thursday=3, **Friday=4**, Saturday=5, Sunday=6
- The `at: sensor.*` trigger fires exactly when the sensor value (timestamp) matches the current time — no template needed
- Use `mode: single` to prevent overlapping azan if HA restarts at prayer time
- **TVs and volume_set:** TVs often do not support `media_player.volume_set`. All automations here guard against this using:
  ```yaml
  {{ state_attr(entity_id, 'supported_features') | int(0) | bitwise_and(4) > 0 }}
  ```
  Bit `4` = `VOLUME_SET`. If `0`, the step is skipped and the azan plays at whatever volume the TV is already set to.
