export const REQUIRED_ENTITY_KEYS = [
  "subuh",
  "syuruk",
  "zohor",
  "asar",
  "maghrib",
  "isyak",
  "hijri",
  "current",
];

export const MAIN_PRAYER_KEYS = ["subuh", "zohor", "asar", "maghrib", "isyak"];
export const SCHEDULE_ROWS = ["subuh", "syuruk", "zohor", "asar", "maghrib", "isyak"];
export const SCHEDULE_PRAYER_ICONS = {
  subuh: "mdi:weather-sunset-up",
  syuruk: "mdi:white-balance-sunny",
  zohor: "mdi:weather-sunny",
  asar: "mdi:weather-partly-cloudy",
  maghrib: "mdi:weather-sunset-down",
  isyak: "mdi:weather-night",
};
export const MIMBAR_COURTYARD_BACKGROUND_URL = "/api/solat_my/mimbar/assets/mimbar-courtyard.png";
export const BACKGROUND_COLOR_PRESETS = {
  forest: "Hutan",
  midnight: "Tengah malam",
  slate: "Batu tulis",
  burgundy: "Delima",
  indigo: "Nila",
};
export const MIMBAR_THEME_TOKENS = {
  forest: {
    accent: "oklch(0.88 0.08 151)",
    accentStrong: "oklch(0.96 0.035 151)",
    accentSoft: "oklch(0.58 0.07 151 / 0.16)",
    accentLine: "oklch(0.76 0.08 151 / 0.34)",
    glassStart: "oklch(0.5 0.09 151 / 0.34)",
    glassMid: "oklch(0.32 0.07 151 / 0.4)",
    glassDeep: "oklch(0.15 0.04 151 / 0.75)",
    glassGlow: "oklch(0.66 0.1 151 / 0.18)",
    glassSheen: "oklch(0.98 0.02 151 / 0.28)",
    glassSheenAccent: "oklch(0.88 0.08 151 / 0.18)",
    currentFill: "oklch(0.4 0.055 151 / 0.16)",
    nextFill: "oklch(0.49 0.08 151 / 0.42)",
    ambientStart: "oklch(0.45 0.07 151 / 0.28)",
    ambientEnd: "oklch(0.28 0.045 151 / 0.08)",
    railSurface: "oklch(0.13 0.035 151 / 0.9)",
    countdownHours: "oklch(0.8 0.1 151)",
    countdownMinutes: "oklch(0.9 0.04 151)",
    countdownSeconds: "oklch(0.74 0.09 178)",
    ringOuter: "oklch(0.72 0.09 151 / 0.5)",
    ringInner: "oklch(0.82 0.05 151 / 0.42)",
  },
  midnight: {
    accent: "oklch(0.85 0.11 252)",
    accentStrong: "oklch(0.96 0.035 252)",
    accentSoft: "oklch(0.54 0.08 252 / 0.16)",
    accentLine: "oklch(0.76 0.1 252 / 0.34)",
    glassStart: "oklch(0.48 0.1 252 / 0.38)",
    glassMid: "oklch(0.3 0.09 252 / 0.44)",
    glassDeep: "oklch(0.15 0.05 252 / 0.76)",
    glassGlow: "oklch(0.62 0.1 252 / 0.2)",
    glassSheen: "oklch(0.97 0.02 252 / 0.3)",
    glassSheenAccent: "oklch(0.85 0.11 252 / 0.2)",
    currentFill: "oklch(0.38 0.06 252 / 0.16)",
    nextFill: "oklch(0.46 0.1 252 / 0.44)",
    ambientStart: "oklch(0.42 0.08 252 / 0.3)",
    ambientEnd: "oklch(0.25 0.045 252 / 0.1)",
    railSurface: "oklch(0.13 0.045 252 / 0.9)",
    countdownHours: "oklch(0.79 0.12 252)",
    countdownMinutes: "oklch(0.9 0.035 252)",
    countdownSeconds: "oklch(0.75 0.1 220)",
    ringOuter: "oklch(0.72 0.11 252 / 0.5)",
    ringInner: "oklch(0.82 0.05 252 / 0.42)",
  },
  slate: {
    accent: "oklch(0.85 0.04 218)",
    accentStrong: "oklch(0.96 0.018 218)",
    accentSoft: "oklch(0.54 0.035 218 / 0.16)",
    accentLine: "oklch(0.76 0.04 218 / 0.34)",
    glassStart: "oklch(0.48 0.04 218 / 0.34)",
    glassMid: "oklch(0.3 0.035 218 / 0.42)",
    glassDeep: "oklch(0.16 0.025 218 / 0.76)",
    glassGlow: "oklch(0.62 0.045 218 / 0.18)",
    glassSheen: "oklch(0.98 0.012 218 / 0.3)",
    glassSheenAccent: "oklch(0.85 0.04 218 / 0.18)",
    currentFill: "oklch(0.38 0.03 218 / 0.14)",
    nextFill: "oklch(0.45 0.04 218 / 0.36)",
    ambientStart: "oklch(0.4 0.035 218 / 0.24)",
    ambientEnd: "oklch(0.24 0.02 218 / 0.08)",
    railSurface: "oklch(0.15 0.02 218 / 0.9)",
    countdownHours: "oklch(0.8 0.05 220)",
    countdownMinutes: "oklch(0.9 0.018 220)",
    countdownSeconds: "oklch(0.74 0.06 235)",
    ringOuter: "oklch(0.72 0.05 220 / 0.48)",
    ringInner: "oklch(0.82 0.025 220 / 0.4)",
  },
  burgundy: {
    accent: "oklch(0.85 0.1 8)",
    accentStrong: "oklch(0.96 0.032 8)",
    accentSoft: "oklch(0.54 0.08 8 / 0.16)",
    accentLine: "oklch(0.76 0.09 8 / 0.34)",
    glassStart: "oklch(0.48 0.1 8 / 0.38)",
    glassMid: "oklch(0.3 0.085 8 / 0.44)",
    glassDeep: "oklch(0.16 0.045 8 / 0.76)",
    glassGlow: "oklch(0.62 0.1 8 / 0.2)",
    glassSheen: "oklch(0.98 0.015 8 / 0.3)",
    glassSheenAccent: "oklch(0.85 0.1 8 / 0.2)",
    currentFill: "oklch(0.38 0.06 8 / 0.16)",
    nextFill: "oklch(0.46 0.1 8 / 0.44)",
    ambientStart: "oklch(0.42 0.08 8 / 0.3)",
    ambientEnd: "oklch(0.24 0.045 8 / 0.1)",
    railSurface: "oklch(0.14 0.04 8 / 0.9)",
    countdownHours: "oklch(0.8 0.11 8)",
    countdownMinutes: "oklch(0.9 0.035 8)",
    countdownSeconds: "oklch(0.74 0.09 345)",
    ringOuter: "oklch(0.72 0.1 8 / 0.5)",
    ringInner: "oklch(0.82 0.05 8 / 0.42)",
  },
  indigo: {
    accent: "oklch(0.86 0.1 295)",
    accentStrong: "oklch(0.96 0.035 295)",
    accentSoft: "oklch(0.54 0.08 295 / 0.16)",
    accentLine: "oklch(0.76 0.09 295 / 0.34)",
    glassStart: "oklch(0.48 0.1 295 / 0.38)",
    glassMid: "oklch(0.3 0.085 295 / 0.44)",
    glassDeep: "oklch(0.15 0.05 295 / 0.76)",
    glassGlow: "oklch(0.62 0.1 295 / 0.2)",
    glassSheen: "oklch(0.98 0.018 295 / 0.3)",
    glassSheenAccent: "oklch(0.86 0.1 295 / 0.2)",
    currentFill: "oklch(0.38 0.06 295 / 0.16)",
    nextFill: "oklch(0.46 0.1 295 / 0.44)",
    ambientStart: "oklch(0.42 0.08 295 / 0.3)",
    ambientEnd: "oklch(0.24 0.045 295 / 0.1)",
    railSurface: "oklch(0.13 0.045 295 / 0.9)",
    countdownHours: "oklch(0.81 0.11 295)",
    countdownMinutes: "oklch(0.91 0.035 295)",
    countdownSeconds: "oklch(0.75 0.1 260)",
    ringOuter: "oklch(0.72 0.1 295 / 0.5)",
    ringInner: "oklch(0.82 0.05 295 / 0.42)",
  },
};

const CURRENT_PRAYER_KEYS = {
  Imsak: "imsak",
  Subuh: "subuh",
  Syuruk: "syuruk",
  Dhuha: "dhuha",
  Zohor: "zohor",
  Asar: "asar",
  Maghrib: "maghrib",
  Isyak: "isyak",
};

const PRAYER_LABELS = {
  imsak: "Imsak",
  subuh: "Subuh",
  syuruk: "Syuruk",
  dhuha: "Dhuha",
  zohor: "Zohor",
  asar: "Asar",
  maghrib: "Maghrib",
  isyak: "Isyak",
};

export function assertMimbarConfig(config) {
  for (const key of REQUIRED_ENTITY_KEYS) {
    if (typeof config?.entities?.[key] !== "string" || !config.entities[key].trim()) {
      throw new Error(`entities.${key} is required`);
    }
  }

  for (const key of ["imsak", "dhuha"]) {
    if (key in config.entities && (typeof config.entities[key] !== "string" || !config.entities[key].trim())) {
      throw new Error(`entities.${key} must be a non-empty entity ID`);
    }
  }

  if (config.time_format !== undefined && !["12h", "24h"].includes(config.time_format)) {
    throw new Error("time_format must be 12h or 24h");
  }

  if (config.fasting_context !== undefined && !["auto", "off"].includes(config.fasting_context)) {
    throw new Error("fasting_context must be auto or off");
  }

  validateBackground(config.background);
  validateSlides(config.slides);
  validateNonNegativeOption(config, "adhan_duration");
  validateNonNegativeOption(config, "silence_duration");
  validatePositiveOption(config, "slide_interval_seconds");
  validateIqama(config.iqama);
}

export function formatCountdown(seconds) {
  const totalSeconds = Math.max(0, Math.floor(Number.isFinite(seconds) ? seconds : 0));
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const remainingSeconds = totalSeconds % 60;

  return [hours, minutes, remainingSeconds]
    .map((part) => String(part).padStart(2, "0"))
    .join(":");
}

export function resolveMimbarBackground(background = {}, integrationSettings = {}) {
  const source = background?.source ?? "card";
  const selectedTheme = source === "integration"
    ? integrationSettings?.theme in BACKGROUND_COLOR_PRESETS ? integrationSettings.theme : "midnight"
    : background?.mode ?? (background?.images?.length ? "image" : "color");
  const opacity = normaliseBackgroundOpacity(
    source === "integration" ? integrationSettings?.opacity : background?.opacity,
  );

  if (selectedTheme === "courtyard") {
    return { mode: "courtyard", color: "forest", opacity };
  }

  if (selectedTheme === "image") {
    return { mode: "image", color: "forest", opacity };
  }

  const color = selectedTheme in BACKGROUND_COLOR_PRESETS
    ? selectedTheme
    : background?.color in BACKGROUND_COLOR_PRESETS
      ? background.color
      : "forest";
  return { mode: "color", color, opacity };
}

export function resolveMimbarTimeFormat(cardTimeFormat, integrationTimeFormat) {
  if (["12h", "24h"].includes(cardTimeFormat)) {
    return cardTimeFormat;
  }
  return ["12h", "24h"].includes(integrationTimeFormat) ? integrationTimeFormat : "24h";
}

export function resolveMimbarTheme(color) {
  return MIMBAR_THEME_TOKENS[color] ?? MIMBAR_THEME_TOKENS.midnight;
}

export function resolveIntegrationBackgroundImages(integrationSettings = {}) {
  if (integrationSettings?.visibility === "off") {
    return [];
  }

  return isLocalAsset(integrationSettings?.image)
    ? [integrationSettings.image]
    : [MIMBAR_COURTYARD_BACKGROUND_URL];
}

export function backgroundVeilOpacity(clarity) {
  return Number((1 - normaliseBackgroundOpacity(clarity) * 0.0065).toFixed(3));
}

export function mergeBasicEditorConfig(config, values) {
  return {
    ...config,
    ...values,
    background: values.background === undefined
      ? config.background
      : { ...config.background, ...values.background },
    entities: {
      ...config.entities,
      ...values.entities,
    },
  };
}

export function buildPrayerView({ config, states, now, timeZone = "Asia/Kuala_Lumpur" }) {
  assertMimbarConfig(config);

  const displayMetadata = {
    localClock: formatLocalClock(now, timeZone, config.time_format),
    gregorianDate: new Intl.DateTimeFormat("ms-MY", {
      timeZone,
      weekday: "long",
      day: "numeric",
      month: "long",
      year: "numeric",
    }).format(now),
    hijriDate: states?.[config.entities.hijri]?.state ?? "",
    location:
      states?.[config.entities.subuh]?.attributes?.zone_desc ??
      states?.[config.entities.subuh]?.attributes?.zone ??
      "",
  };

  const prayerTimes = Object.fromEntries(
    SCHEDULE_ROWS.map((key) => [key, parseTimestamp(states?.[config.entities[key]]?.state)]),
  );

  if (SCHEDULE_ROWS.some((key) => prayerTimes[key] === null)) {
    return { status: "fault", message: "Waktu tidak tersedia", ...displayMetadata };
  }

  if (hasStaleMainPrayerTime(prayerTimes, now, timeZone)) {
    return { status: "fault", message: "Waktu tidak dikemas kini", ...displayMetadata };
  }

  const next = nextMainPrayer(prayerTimes, now);
  const currentKey = CURRENT_PRAYER_KEYS[states?.[config.entities.current]?.state];

  return {
    status: "ready",
    schedule: SCHEDULE_ROWS.map((key) => ({
      key,
      label: PRAYER_LABELS[key],
      at: new Date(prayerTimes[key]),
      time: formatPrayerTime(prayerTimes[key], config.time_format, timeZone),
      isPast: new Date(prayerTimes[key]).valueOf() <= now.valueOf(),
    })),
    next,
    countdownSeconds: Math.max(0, Math.floor((next.at.valueOf() - now.valueOf()) / 1000)),
    current: currentKey
      ? { key: currentKey, location: SCHEDULE_ROWS.includes(currentKey) ? "schedule" : "rail" }
      : null,
    ...displayMetadata,
  };
}

export function formatPrayerTime(value, timeFormat = "24h", timeZone = "Asia/Kuala_Lumpur") {
  return new Intl.DateTimeFormat(timeFormat === "12h" ? "en-US" : "ms-MY", {
    timeZone,
    hour: "2-digit",
    minute: "2-digit",
    ...(timeFormat === "12h" ? { hour12: true } : { hourCycle: "h23" }),
  }).format(value);
}

export function formatLocalClock(value, timeZone = "Asia/Kuala_Lumpur", timeFormat = "24h") {
  return formatPrayerTime(value, timeFormat, timeZone);
}

export function splitDayPeriod(text) {
  const match = /^(.*\S)\s+(AM|PM)$/.exec(text);
  return match ? { clock: match[1], period: match[2] } : { clock: text, period: "" };
}

export function resolveLifecycle({
  prayerTimes,
  iqama = {},
  adhanDurationMinutes = 2,
  silenceDurationMinutes = 15,
  now,
}) {
  if (!(now instanceof Date) || Number.isNaN(now.valueOf())) {
    return { kind: "normal" };
  }

  const adhanDuration = normaliseMinutes(adhanDurationMinutes, 2);
  const silenceDuration = normaliseMinutes(silenceDurationMinutes, 15);
  const activePrayers = Object.entries(prayerTimes ?? {})
    .filter(([, at]) => at instanceof Date && !Number.isNaN(at.valueOf()) && at <= now)
    .sort(([, left], [, right]) => right.valueOf() - left.valueOf());

  for (const [key, at] of activePrayers) {
    const elapsedMilliseconds = now.valueOf() - at.valueOf();
    const adhanEndsAt = adhanDuration * 60_000;

    if (elapsedMilliseconds < adhanEndsAt) {
      return { kind: "adhan", key, at: new Date(at) };
    }

    const iqamaOffset = Number(iqama?.[key]);
    if (!Number.isFinite(iqamaOffset) || iqamaOffset < 0) {
      continue;
    }

    const iqamaStartsAt = iqamaOffset * 60_000;
    if (elapsedMilliseconds < iqamaStartsAt) {
      return {
        kind: "iqamah",
        key,
        at: new Date(at.valueOf() + iqamaStartsAt),
      };
    }

    if (elapsedMilliseconds < iqamaStartsAt + silenceDuration * 60_000) {
      return { kind: "silence", key, at: new Date(at) };
    }
  }

  return { kind: "normal" };
}

export function buildLowerRail({ config, states, now }) {
  const secondary = ["imsak", "dhuha"].flatMap((key) => {
    const entityId = config?.entities?.[key];
    const at = parseTimestamp(states?.[entityId]?.state);

    return at ? [{ key, label: PRAYER_LABELS[key], at }] : [];
  });
  const imsak = secondary.find((item) => item.key === "imsak")?.at;
  const maghrib = parseTimestamp(states?.[config?.entities?.maghrib]?.state);
  const hijriMonth = states?.[config?.entities?.hijri]?.attributes?.month;
  const fasting = fastingContext({
    enabled: (config?.fasting_context ?? "auto") === "auto",
    hijriMonth,
    imsak,
    maghrib,
    now,
  });

  return {
    secondary,
    fasting,
    content: Array.isArray(config?.slides) ? { type: "slides", slides: config.slides } : {
      type: "message",
      message: config?.message ?? "",
    },
  };
}

export function isLocalAsset(path) {
  return typeof path === "string" && path.startsWith("/local/") && !/[\r\n]/.test(path);
}

function parseTimestamp(value) {
  if (typeof value !== "string") {
    return null;
  }

  const timestamp = new Date(value);
  return Number.isNaN(timestamp.valueOf()) ? null : timestamp;
}

function hasStaleMainPrayerTime(prayerTimes, now, timeZone) {
  const today = calendarDay(now, timeZone);
  const localHour = Number(
    new Intl.DateTimeFormat("en-GB", { timeZone, hour: "2-digit", hourCycle: "h23" }).format(now),
  );

  return MAIN_PRAYER_KEYS.some((key) => {
    const daysBeforeToday = calendarDay(prayerTimes[key], timeZone) - today;
    return daysBeforeToday < 0 && !(daysBeforeToday === -1 && localHour === 0);
  });
}

function calendarDay(value, timeZone) {
  const parts = new Intl.DateTimeFormat("en-GB", {
    timeZone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(value);
  const byType = Object.fromEntries(parts.map((part) => [part.type, part.value]));
  return Date.UTC(Number(byType.year), Number(byType.month) - 1, Number(byType.day)) / 86_400_000;
}

function normaliseMinutes(value, fallback) {
  return Number.isFinite(value) && value >= 0 ? value : fallback;
}

function validateBackground(background) {
  if (background === undefined) {
    return;
  }

  if (!background || typeof background !== "object" || Array.isArray(background)) {
    throw new Error("background must be an object");
  }

  if (background.source !== undefined && !["card", "integration"].includes(background.source)) {
    throw new Error("background.source must be card or integration");
  }

  const mode = background.mode ?? (background.images?.length ? "image" : "color");
  if (!["courtyard", "image", "color"].includes(mode)) {
    throw new Error("background.mode must be courtyard, image or color");
  }

  if (background.color !== undefined && !(background.color in BACKGROUND_COLOR_PRESETS)) {
    throw new Error("background.color must be a supported preset");
  }

  if (background.images !== undefined) {
    if (!Array.isArray(background.images) || background.images.length === 0) {
      throw new Error("background.images must contain local images");
    }

    for (const image of background.images) {
      if (!isLocalAsset(image)) {
        throw new Error("background images must use /local/ paths");
      }
    }
  }

  if (mode === "image" && (!Array.isArray(background.images) || background.images.length === 0)) {
    throw new Error("background.images are required when background.mode is image");
  }

  if (background.rotation_seconds !== undefined && !isPositiveFinite(background.rotation_seconds)) {
    throw new Error("background.rotation_seconds must be positive");
  }

  if (
    background.opacity !== undefined
    && (!Number.isFinite(background.opacity) || background.opacity < 0 || background.opacity > 100)
  ) {
    throw new Error("background.opacity must be between 0 and 100");
  }
}

function normaliseBackgroundOpacity(value) {
  const opacity = Number(value);
  return Number.isFinite(opacity) && opacity >= 0 && opacity <= 100 ? opacity : 76;
}

function validateSlides(slides) {
  if (slides === undefined) {
    return;
  }

  if (!Array.isArray(slides)) {
    throw new Error("slides must be an array");
  }

  for (const slide of slides) {
    if (!slide || typeof slide !== "object" || Array.isArray(slide)) {
      throw new Error("each slide must be an object");
    }

    if (Object.prototype.hasOwnProperty.call(slide, "ar")) {
      throw new Error("Arabic slide fields are not supported");
    }

    if (slide.type === "message") {
      if (typeof slide.ms !== "string" || !slide.ms.trim()) {
        throw new Error("message slides require non-empty ms text");
      }
      continue;
    }

    if (slide.type === "image") {
      if (!isLocalAsset(slide.src)) {
        throw new Error("image slides must use /local/ paths");
      }
      if (typeof slide.alt !== "string" || !slide.alt.trim()) {
        throw new Error("image slides require non-empty alt text");
      }
      continue;
    }

    throw new Error("slide type must be message or image");
  }
}

function validateNonNegativeOption(config, key) {
  if (config[key] !== undefined && !isNonNegativeFinite(config[key])) {
    throw new Error(`${key} must be a non-negative number`);
  }
}

function validatePositiveOption(config, key) {
  if (config[key] !== undefined && !isPositiveFinite(config[key])) {
    throw new Error(`${key} must be a positive number`);
  }
}

function validateIqama(iqama) {
  if (iqama === undefined) {
    return;
  }

  if (!iqama || typeof iqama !== "object" || Array.isArray(iqama)) {
    throw new Error("iqama must be an object");
  }

  for (const [prayer, offset] of Object.entries(iqama)) {
    if (!isNonNegativeFinite(offset)) {
      throw new Error(`iqama.${prayer} must be a non-negative number`);
    }
  }
}

function isNonNegativeFinite(value) {
  return Number.isFinite(value) && value >= 0;
}

function isPositiveFinite(value) {
  return Number.isFinite(value) && value > 0;
}

function fastingContext({ enabled, hijriMonth, imsak, maghrib, now }) {
  if (
    !enabled ||
    hijriMonth !== "09" ||
    !(imsak instanceof Date) ||
    !(maghrib instanceof Date) ||
    !(now instanceof Date) ||
    Number.isNaN(now.valueOf())
  ) {
    return null;
  }

  if (now < imsak) {
    return { kind: "sahur", key: "imsak", at: new Date(imsak) };
  }

  if (now < maghrib) {
    return { kind: "berbuka", key: "maghrib", at: new Date(maghrib) };
  }

  return null;
}

function nextMainPrayer(prayerTimes, now) {
  for (const key of MAIN_PRAYER_KEYS) {
    if (prayerTimes[key] > now) {
      return { key, at: new Date(prayerTimes[key]) };
    }
  }

  const tomorrowSubuh = new Date(prayerTimes.subuh);
  tomorrowSubuh.setUTCDate(tomorrowSubuh.getUTCDate() + 1);
  return { key: "subuh", at: tomorrowSubuh };
}
