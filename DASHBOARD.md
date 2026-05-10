# Dashboard — Waktu Solat Malaysia (solat.my)

Dashboard cards for displaying prayer times. Requires **Mushroom Cards** (HACS).

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
