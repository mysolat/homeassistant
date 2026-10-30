const { BACKGROUND_COLOR_PRESETS, mergeBasicEditorConfig } = await import(
  `./mimbar-model.mjs${new URL(import.meta.url).search}`
);

const ENTITY_FIELDS = [
  ["subuh", "Subuh"],
  ["syuruk", "Syuruk"],
  ["zohor", "Zohor"],
  ["asar", "Asar"],
  ["maghrib", "Maghrib"],
  ["isyak", "Isyak"],
  ["hijri", "Tarikh Hijri"],
  ["current", "Waktu semasa"],
];

export class MimbarPrayerScreenEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._fields = new Map();
  }

  setConfig(config) {
    this._config = structuredClone(config);
    this._buildDomOnce();
    this._syncFields();
  }

  set hass(hass) {
    this._hass = hass;
  }

  _buildDomOnce() {
    if (this._form) {
      return;
    }

    const style = document.createElement("style");
    style.textContent = `
      :host { color: var(--primary-text-color); display: block; }
      form { display: grid; gap: 20px; max-width: 760px; padding: 8px 0; }
      fieldset { border: 1px solid var(--divider-color); border-radius: 12px; display: grid; gap: 14px; margin: 0; padding: 18px; }
      legend { font-size: 16px; font-weight: 700; padding: 0 6px; }
      .grid { display: grid; gap: 14px; grid-template-columns: repeat(2, minmax(0, 1fr)); }
      label { display: grid; font-size: 14px; font-weight: 650; gap: 7px; line-height: 1.35; }
      input, select { background: var(--card-background-color); border: 1px solid var(--divider-color); border-radius: 8px; box-sizing: border-box; color: var(--primary-text-color); font: inherit; font-size: 14px; min-height: 42px; padding: 9px 11px; width: 100%; }
      input:focus-visible, select:focus-visible { outline: 3px solid var(--primary-color); outline-offset: 2px; }
      .hint { color: var(--secondary-text-color); font-size: 12px; line-height: 1.5; margin: 0; }
      @media (max-width: 540px) { .grid { grid-template-columns: 1fr; } }
    `;

    this._form = document.createElement("form");
    this._form.addEventListener("submit", (event) => event.preventDefault());

    const identity = this._createFieldset("Maklumat paparan");
    identity.append(
      this._createField("title", "Nama masjid"),
      this._createField("location", "Lokasi"),
      this._createField("message", "Pesanan masjid"),
      this._createTimeFormatField(),
    );

    const entities = this._createFieldset("Entiti Solat.my");
    const entityGrid = document.createElement("div");
    entityGrid.className = "grid";
    for (const [key, label] of ENTITY_FIELDS) {
      entityGrid.append(this._createField(`entities.${key}`, label));
    }
    entities.append(entityGrid);

    const background = this._createFieldset("Latar belakang");
    const backgroundGrid = document.createElement("div");
    backgroundGrid.className = "grid";
    backgroundGrid.append(
      this._createBackgroundModeField(),
      this._createBackgroundColorField(),
      this._createField("background.image", "Imej sendiri (/local/...)")
    );
    const backgroundHint = document.createElement("p");
    backgroundHint.className = "hint";
    backgroundHint.textContent = "Pilih Latar masjid untuk imej Mimbar, Warna untuk salah satu lima warna, atau Imej sendiri dan masukkan laluan /local/.";
    background.append(backgroundGrid, backgroundHint);

    const hint = document.createElement("p");
    hint.className = "hint";
    hint.textContent = "Imsak, Dhuha, Iqamah dan slaid kekal dalam YAML lanjutan.";

    this._form.append(identity, background, entities, hint);
    this.shadowRoot.append(style, this._form);
  }

  _createFieldset(label) {
    const fieldset = document.createElement("fieldset");
    const legend = document.createElement("legend");
    legend.textContent = label;
    fieldset.append(legend);
    return fieldset;
  }

  _createField(name, labelText) {
    const label = document.createElement("label");
    const labelTextNode = document.createElement("span");
    labelTextNode.textContent = labelText;
    const input = document.createElement("input");
    input.name = name;
    input.type = "text";
    input.autocomplete = "off";
    input.addEventListener("input", () => this._emitChange());
    label.append(labelTextNode, input);
    this._fields.set(name, input);
    return label;
  }

  _createTimeFormatField() {
    const label = document.createElement("label");
    const labelText = document.createElement("span");
    labelText.textContent = "Format masa";
    const select = document.createElement("select");
    select.name = "time_format";
    for (const [value, text] of [["24h", "24 jam"], ["12h", "12 jam"]]) {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = text;
      select.append(option);
    }
    select.addEventListener("change", () => this._emitChange());
    label.append(labelText, select);
    this._fields.set("time_format", select);
    return label;
  }

  _createBackgroundModeField() {
    const label = document.createElement("label");
    const labelText = document.createElement("span");
    labelText.textContent = "Jenis latar";
    const select = document.createElement("select");
    select.name = "background.mode";
    for (const [value, text] of [["courtyard", "Latar masjid Mimbar"], ["color", "Warna latar"], ["image", "Imej sendiri"]]) {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = text;
      select.append(option);
    }
    select.addEventListener("change", () => this._emitChange());
    label.append(labelText, select);
    this._fields.set("background.mode", select);
    return label;
  }

  _createBackgroundColorField() {
    const label = document.createElement("label");
    const labelText = document.createElement("span");
    labelText.textContent = "Warna latar";
    const select = document.createElement("select");
    select.name = "background.color";
    for (const [value, text] of Object.entries(BACKGROUND_COLOR_PRESETS)) {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = text;
      select.append(option);
    }
    select.addEventListener("change", () => this._emitChange());
    label.append(labelText, select);
    this._fields.set("background.color", select);
    return label;
  }

  _syncFields() {
    for (const [name, field] of this._fields) {
      if (this.shadowRoot.activeElement === field) {
        continue;
      }
      field.value = String(this._readConfigValue(name) ?? this._fieldFallback(name));
    }
  }

  _readConfigValue(name) {
    if (name === "background.mode") {
      return this._config?.background?.mode ?? (this._config?.background?.images?.length ? "image" : "courtyard");
    }
    if (name === "background.color") {
      return this._config?.background?.color ?? "forest";
    }
    if (name === "background.image") {
      return this._config?.background?.images?.[0];
    }
    const [group, key] = name.split(".");
    return key ? this._config?.[group]?.[key] : this._config?.[group];
  }

  _fieldFallback(name) {
    return name === "time_format" ? "24h" : "";
  }

  _readFields() {
    const entities = {};
    for (const [key] of ENTITY_FIELDS) {
      entities[key] = this._fields.get(`entities.${key}`).value.trim();
    }

    const background = {
      mode: this._fields.get("background.mode").value,
      color: this._fields.get("background.color").value,
    };
    const image = this._fields.get("background.image").value.trim();
    if (image) {
      background.images = [image];
    }

    return {
      title: this._fields.get("title").value.trim(),
      location: this._fields.get("location").value.trim(),
      message: this._fields.get("message").value.trim(),
      time_format: this._fields.get("time_format").value,
      background,
      entities,
    };
  }

  _emitChange() {
    const config = mergeBasicEditorConfig(this._config ?? { entities: {} }, this._readFields());
    this._config = structuredClone(config);
    this.dispatchEvent(
      new CustomEvent("config-changed", {
        bubbles: true,
        composed: true,
        detail: { config },
      }),
    );
  }
}

if (!customElements.get("solat-my-mimbar-card-editor")) {
  customElements.define("solat-my-mimbar-card-editor", MimbarPrayerScreenEditor);
}
