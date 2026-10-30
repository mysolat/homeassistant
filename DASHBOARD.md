# Dashboard — Waktu Solat Malaysia (solat.my)

Dashboard cards for displaying prayer times. Layouts 1 and 2 require **Mushroom Cards** (HACS); the full-screen Mimbar card does not.

> **Note:** Replace `waktu_solat` in entity IDs if you renamed your device.

---

## How to Add a Card

1. Open your dashboard → click the **pencil icon** (Edit)
2. Click **Add Card** → scroll to the bottom → **Manual**
3. Paste one of the YAML blocks below → **Save**

---

## Layout 1: The Premium Grid (3×2)

A balanced, dashboard-friendly view with a prominent current time badge and a 3×2 grid of prayer times. Features live colored icon badges for 'Current' (teal check) and 'Next' (orange timer) prayers.

```yaml
type: vertical-stack
cards:
  - type: custom:mushroom-title-card
    title: >-
      {{ now().strftime('%I:%M') }} {{ 'PG' if now().hour < 12 else 'PTG' }}, {{ ['Isnin','Selasa','Rabu','Khamis','Jumaat','Sabtu','Ahad'][now().weekday()] }}
    subtitle: >-
      {{ now().strftime('%d') }} {{ ['Jan','Feb','Mac','Apr','Mei','Jun','Jul','Ogos','Sep','Okt','Nov','Dis'][now().month - 1] }} {{ now().year }} | {{ states('sensor.waktu_solat_tarikh_hijri') }}
    alignment: center

  - type: custom:mushroom-template-card
    primary: '🕌 Waktu Sekarang: {{ states(''sensor.waktu_solat_waktu_solat_semasa'') }}'
    secondary: >-
      {% set next_p = states('sensor.waktu_solat_waktu_solat_seterusnya') %}
      {% set cd = state_attr('sensor.waktu_solat_waktu_solat_seterusnya', 'countdown') %}
      {% if next_p not in ('Selesai', 'unknown', 'unavailable') %} Seterusnya {{ next_p }} dalam {{ cd }} {% else %} Selesai {% endif %}
    icon: ''
    layout: vertical
    badge_icon: mdi:circle
    badge_color: teal
    tap_action:
      action: more-info
      entity: select.waktu_solat_mod_pengumuman_azan

  - type: grid
    columns: 3
    square: false
    cards:
      - type: custom:mushroom-template-card
        primary: '{{ state_attr(''sensor.waktu_solat_subuh'', ''time_24h'') }}'
        secondary: Subuh
        icon: mdi:weather-night-partly-cloudy
        icon_color: indigo
        badge_icon: >-
          {% if states('sensor.waktu_solat_waktu_solat_semasa') == 'Subuh' %} mdi:check-circle {% elif states('sensor.waktu_solat_waktu_solat_seterusnya') == 'Subuh' %} mdi:timer-sand {% endif %}
        badge_color: >-
          {% if states('sensor.waktu_solat_waktu_solat_semasa') == 'Subuh' %} teal {% elif states('sensor.waktu_solat_waktu_solat_seterusnya') == 'Subuh' %} orange {% endif %}
        layout: vertical
        
      - type: custom:mushroom-template-card
        primary: '{{ state_attr(''sensor.waktu_solat_syuruk'', ''time_24h'') }}'
        secondary: Syuruk
        icon: mdi:weather-sunset-up
        icon_color: amber
        badge_icon: >-
          {% if states('sensor.waktu_solat_waktu_solat_semasa') == 'Syuruk' %} mdi:check-circle {% elif states('sensor.waktu_solat_waktu_solat_seterusnya') == 'Syuruk' %} mdi:timer-sand {% endif %}
        badge_color: >-
          {% if states('sensor.waktu_solat_waktu_solat_semasa') == 'Syuruk' %} teal {% elif states('sensor.waktu_solat_waktu_solat_seterusnya') == 'Syuruk' %} orange {% endif %}
        layout: vertical
        
      - type: custom:mushroom-template-card
        primary: '{{ state_attr(''sensor.waktu_solat_zohor'', ''time_24h'') }}'
        secondary: Zohor
        icon: mdi:weather-sunny
        icon_color: orange
        badge_icon: >-
          {% if states('sensor.waktu_solat_waktu_solat_semasa') == 'Zohor' %} mdi:check-circle {% elif states('sensor.waktu_solat_waktu_solat_seterusnya') == 'Zohor' %} mdi:timer-sand {% endif %}
        badge_color: >-
          {% if states('sensor.waktu_solat_waktu_solat_semasa') == 'Zohor' %} teal {% elif states('sensor.waktu_solat_waktu_solat_seterusnya') == 'Zohor' %} orange {% endif %}
        layout: vertical
        
      - type: custom:mushroom-template-card
        primary: '{{ state_attr(''sensor.waktu_solat_asar'', ''time_24h'') }}'
        secondary: Asar
        icon: mdi:weather-partly-cloudy
        icon_color: deep-orange
        badge_icon: >-
          {% if states('sensor.waktu_solat_waktu_solat_semasa') == 'Asar' %} mdi:check-circle {% elif states('sensor.waktu_solat_waktu_solat_seterusnya') == 'Asar' %} mdi:timer-sand {% endif %}
        badge_color: >-
          {% if states('sensor.waktu_solat_waktu_solat_semasa') == 'Asar' %} teal {% elif states('sensor.waktu_solat_waktu_solat_seterusnya') == 'Asar' %} orange {% endif %}
        layout: vertical
        
      - type: custom:mushroom-template-card
        primary: '{{ state_attr(''sensor.waktu_solat_maghrib'', ''time_24h'') }}'
        secondary: Maghrib
        icon: mdi:weather-sunset-down
        icon_color: red
        badge_icon: >-
          {% if states('sensor.waktu_solat_waktu_solat_semasa') == 'Maghrib' %} mdi:check-circle {% elif states('sensor.waktu_solat_waktu_solat_seterusnya') == 'Maghrib' %} mdi:timer-sand {% endif %}
        badge_color: >-
          {% if states('sensor.waktu_solat_waktu_solat_semasa') == 'Maghrib' %} teal {% elif states('sensor.waktu_solat_waktu_solat_seterusnya') == 'Maghrib' %} orange {% endif %}
        layout: vertical
        
      - type: custom:mushroom-template-card
        primary: '{{ state_attr(''sensor.waktu_solat_isyak'', ''time_24h'') }}'
        secondary: Isyak
        icon: mdi:weather-night
        icon_color: blue
        badge_icon: >-
          {% if states('sensor.waktu_solat_waktu_solat_semasa') == 'Isyak' %} mdi:check-circle {% elif states('sensor.waktu_solat_waktu_solat_seterusnya') == 'Isyak' %} mdi:timer-sand {% endif %}
        badge_color: >-
          {% if states('sensor.waktu_solat_waktu_solat_semasa') == 'Isyak' %} teal {% elif states('sensor.waktu_solat_waktu_solat_seterusnya') == 'Isyak' %} orange {% endif %}
        layout: vertical

  - type: custom:mushroom-template-card
    primary: ''
    secondary: '📍 Zon: {{ state_attr(''sensor.waktu_solat_subuh'',''zone'') }} {% if state_attr(''sensor.waktu_solat_subuh'', ''zone_desc'') %}({{ state_attr(''sensor.waktu_solat_subuh'', ''zone_desc'').split('' - '')[0] }}){% endif %}'
    icon: ''
    layout: vertical
    tap_action: { action: none }
```

---

## Layout 2: The Sleek Timeline

Excellent for mobile views. A vertical list of prayers with colored icons and badge indicators (teal check = current, orange timer = next).

```yaml
type: vertical-stack
cards:
  - type: custom:mushroom-title-card
    title: >-
      {{ now().strftime('%I:%M') }} {{ 'PG' if now().hour < 12 else 'PTG' }}, {{ ['Isnin','Selasa','Rabu','Khamis','Jumaat','Sabtu','Ahad'][now().weekday()] }}
    subtitle: >-
      {{ now().strftime('%d') }} {{ ['Jan','Feb','Mac','Apr','Mei','Jun','Jul','Ogos','Sep','Okt','Nov','Dis'][now().month - 1] }} {{ now().year }} | {{ states('sensor.waktu_solat_tarikh_hijri') }}
    alignment: center

  - type: custom:mushroom-template-card
    primary: '🕌 Waktu Sekarang: {{ states(''sensor.waktu_solat_waktu_solat_semasa'') }}'
    secondary: >-
      {% set next_p = states('sensor.waktu_solat_waktu_solat_seterusnya') %}
      {% set cd = state_attr('sensor.waktu_solat_waktu_solat_seterusnya', 'countdown') %}
      {% if next_p not in ('Selesai', 'unknown', 'unavailable') %} Seterusnya {{ next_p }} dalam {{ cd }} {% else %} Selesai {% endif %}
    icon: ''
    layout: vertical
    badge_icon: mdi:circle
    badge_color: teal
    tap_action:
      action: more-info
      entity: select.waktu_solat_mod_pengumuman_azan

  - type: custom:mushroom-template-card
    primary: Subuh
    secondary: '{{ state_attr(''sensor.waktu_solat_subuh'', ''time_24h'') }}'
    icon: mdi:weather-night-partly-cloudy
    icon_color: indigo
    badge_icon: >-
      {% if states('sensor.waktu_solat_waktu_solat_semasa') == 'Subuh' %} mdi:check-circle {% elif states('sensor.waktu_solat_waktu_solat_seterusnya') == 'Subuh' %} mdi:timer-sand {% endif %}
    badge_color: >-
      {% if states('sensor.waktu_solat_waktu_solat_semasa') == 'Subuh' %} teal {% elif states('sensor.waktu_solat_waktu_solat_seterusnya') == 'Subuh' %} orange {% endif %}

  - type: custom:mushroom-template-card
    primary: Syuruk
    secondary: '{{ state_attr(''sensor.waktu_solat_syuruk'', ''time_24h'') }}'
    icon: mdi:weather-sunset-up
    icon_color: amber
    badge_icon: >-
      {% if states('sensor.waktu_solat_waktu_solat_semasa') == 'Syuruk' %} mdi:check-circle {% elif states('sensor.waktu_solat_waktu_solat_seterusnya') == 'Syuruk' %} mdi:timer-sand {% endif %}
    badge_color: >-
      {% if states('sensor.waktu_solat_waktu_solat_semasa') == 'Syuruk' %} teal {% elif states('sensor.waktu_solat_waktu_solat_seterusnya') == 'Syuruk' %} orange {% endif %}

  - type: custom:mushroom-template-card
    primary: Zohor
    secondary: '{{ state_attr(''sensor.waktu_solat_zohor'', ''time_24h'') }}'
    icon: mdi:weather-sunny
    icon_color: orange
    badge_icon: >-
      {% if states('sensor.waktu_solat_waktu_solat_semasa') == 'Zohor' %} mdi:check-circle {% elif states('sensor.waktu_solat_waktu_solat_seterusnya') == 'Zohor' %} mdi:timer-sand {% endif %}
    badge_color: >-
      {% if states('sensor.waktu_solat_waktu_solat_semasa') == 'Zohor' %} teal {% elif states('sensor.waktu_solat_waktu_solat_seterusnya') == 'Zohor' %} orange {% endif %}

  - type: custom:mushroom-template-card
    primary: Asar
    secondary: '{{ state_attr(''sensor.waktu_solat_asar'', ''time_24h'') }}'
    icon: mdi:weather-partly-cloudy
    icon_color: deep-orange
    badge_icon: >-
      {% if states('sensor.waktu_solat_waktu_solat_semasa') == 'Asar' %} mdi:check-circle {% elif states('sensor.waktu_solat_waktu_solat_seterusnya') == 'Asar' %} mdi:timer-sand {% endif %}
    badge_color: >-
      {% if states('sensor.waktu_solat_waktu_solat_semasa') == 'Asar' %} teal {% elif states('sensor.waktu_solat_waktu_solat_seterusnya') == 'Asar' %} orange {% endif %}

  - type: custom:mushroom-template-card
    primary: Maghrib
    secondary: '{{ state_attr(''sensor.waktu_solat_maghrib'', ''time_24h'') }}'
    icon: mdi:weather-sunset-down
    icon_color: red
    badge_icon: >-
      {% if states('sensor.waktu_solat_waktu_solat_semasa') == 'Maghrib' %} mdi:check-circle {% elif states('sensor.waktu_solat_waktu_solat_seterusnya') == 'Maghrib' %} mdi:timer-sand {% endif %}
    badge_color: >-
      {% if states('sensor.waktu_solat_waktu_solat_semasa') == 'Maghrib' %} teal {% elif states('sensor.waktu_solat_waktu_solat_seterusnya') == 'Maghrib' %} orange {% endif %}

  - type: custom:mushroom-template-card
    primary: Isyak
    secondary: '{{ state_attr(''sensor.waktu_solat_isyak'', ''time_24h'') }}'
    icon: mdi:weather-night
    icon_color: blue
    badge_icon: >-
      {% if states('sensor.waktu_solat_waktu_solat_semasa') == 'Isyak' %} mdi:check-circle {% elif states('sensor.waktu_solat_waktu_solat_seterusnya') == 'Isyak' %} mdi:timer-sand {% endif %}
    badge_color: >-
      {% if states('sensor.waktu_solat_waktu_solat_semasa') == 'Isyak' %} teal {% elif states('sensor.waktu_solat_waktu_solat_seterusnya') == 'Isyak' %} orange {% endif %}

  - type: custom:mushroom-template-card
    primary: ''
    secondary: '📍 Zon: {{ state_attr(''sensor.waktu_solat_subuh'',''zone'') }} {% if state_attr(''sensor.waktu_solat_subuh'', ''zone_desc'') %}({{ state_attr(''sensor.waktu_solat_subuh'', ''zone_desc'').split('' - '')[0] }}){% endif %}'
    icon: ''
    layout: vertical
    tap_action: { action: none }
```

---

## Paparan Mimbar Skrin Penuh

A full-screen prayer display for a TV or kiosk. The card is built into the integration and loads by itself. After installing or updating, restart Home Assistant and hard-refresh your browser.

### Set up

1. Open **Settings → Dashboards → Add dashboard → New dashboard from scratch**, name it `Mimbar`, and open it.
2. Click the pencil (Edit), then **⋮ → Raw configuration editor**. Replace everything with this and **Save**:

```yaml
title: Mimbar Waktu Solat
views:
  - title: Mimbar
    path: mimbar
    panel: true
    cards:
      - type: custom:solat-my-mimbar-card
        title: Waktu Solat
        message: Sila rapatkan saf dan matikan nada telefon.
        fasting_context: auto
        entities:
          imsak: sensor.waktu_solat_imsak
          subuh: sensor.waktu_solat_subuh
          syuruk: sensor.waktu_solat_syuruk
          dhuha: sensor.waktu_solat_dhuha
          zohor: sensor.waktu_solat_zohor
          asar: sensor.waktu_solat_asar
          maghrib: sensor.waktu_solat_maghrib
          isyak: sensor.waktu_solat_isyak
          hijri: sensor.waktu_solat_tarikh_hijri
          current: sensor.waktu_solat_waktu_solat_semasa
        background:
          source: integration
```

3. Choose the colour, image, and 12h/24h format on the Solat.my device page (see [Background choices](#background-choices)).

Renamed your device? Replace `waktu_solat` in the entity IDs.

**Troubleshooting**

- **Card missing** ("Custom element doesn't exist"): restart Home Assistant and hard-refresh. If it is still missing, add it by hand: turn on **Advanced mode** in your profile, then **Settings → Dashboards → ⋮ → Resources → Add resource**, URL `/api/solat_my/mimbar/solat-my-mimbar-card.js`, type **JavaScript module**.
- **Upgrading from an earlier build** where you added that resource by hand: delete it, or the card loads twice.

Want more? The card also supports `location`, an Iqamah countdown (`iqama`), adhan and quiet-time lengths, and rotating notices (`slides`). To use them, follow the same steps but paste this whole dashboard in step 2 instead. The Ramadan cue needs `imsak` and a Hijri entity whose `month` attribute is `09`.

```yaml
title: Mimbar Waktu Solat
views:
  - title: Mimbar
    path: mimbar
    panel: true
    cards:
      - type: custom:solat-my-mimbar-card
        entities:
          subuh: sensor.waktu_solat_subuh
          syuruk: sensor.waktu_solat_syuruk
          zohor: sensor.waktu_solat_zohor
          asar: sensor.waktu_solat_asar
          maghrib: sensor.waktu_solat_maghrib
          isyak: sensor.waktu_solat_isyak
          hijri: sensor.waktu_solat_tarikh_hijri
          current: sensor.waktu_solat_waktu_solat_semasa
          imsak: sensor.waktu_solat_imsak
          dhuha: sensor.waktu_solat_dhuha
        title: Masjid Al-Hidayah
        location: Putrajaya
        message: Sila rapatkan saf dan matikan nada telefon.
        # time_format: 12h  # optional; overrides the device's Format Masa Mimbar
        fasting_context: auto
        background:
          source: integration
        iqama:
          subuh: 20
          zohor: 15
          asar: 15
          maghrib: 10
          isyak: 15
          jumaat: 30
        adhan_duration: 2
        silence_duration: 15
        slides:
          - type: message
            ms: Sila kekalkan kebersihan dan ketenangan masjid.
          # Image slides need a file under /config/www (served as /local/...):
          # - type: image
          #   src: /local/makluman-program.jpg
          #   alt: Makluman program masjid
        slide_interval_seconds: 60
```

`iqama.jumaat` replaces the Zohor offset on Friday and changes its display label to `Jumaat`. Omit an Iqamah key when the mosque has no local congregation offset. Backgrounds and slides never fetch remote content, and the card never changes zone, media-player, announcement, volume, or audio settings.

### Background choices

For the normal setup, open the Solat.my device page and use **Warna Latar Mimbar**, **Paparan Latar Mimbar**, **Kejelasan Latar Mimbar** (0–100), **Imej Latar Mimbar**, and **Format Masa Mimbar**. The colour selector offers `forest`, `midnight`, `slate`, `burgundy`, and `indigo`; it never replaces the included Mimbar courtyard. **Paparan Latar Mimbar** turns that image layer on or off. A valid owner-provided `/local/...` value in **Imej Latar Mimbar** replaces the courtyard while it is on. **Format Masa Mimbar** offers `24h` and `12h`; an explicit `time_format: 24h` or `time_format: 12h` in the card YAML takes priority. These controls affect Mimbar cards mapped to that device and work without editing dashboard YAML.

Home Assistant's view-level background and opacity controls affect wallpaper behind the dashboard view. They do not change this full-screen card's background.

To make one screen differ from its Solat.my device, replace the card's `background:` lines (`source: integration`) with one of these:

```yaml
# Colour-only background
background:
  mode: color
  color: midnight
  opacity: 60

# One or more owner images under /config/www
background:
  mode: image
  images:
    - /local/masjid-senja.jpg
    - /local/masjid-pagi.jpg
  position: center
  rotation_seconds: 60
```
